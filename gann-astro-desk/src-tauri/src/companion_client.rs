use crate::companion_protocol::{
    decode_url, decrypt_session, derive_pairing_keys, encode_url, pairing_proof,
    pairing_proof_payload, random_bytes, sha256_hex, EncryptedSession, PairingChallenge,
    PairingRequest, PairingResponse, PublicCompanionSession, CHALLENGE_CONTRACT, CLIENT_CONTRACT,
    SESSION_CONTRACT,
};
use futures_util::StreamExt;
use http::{header, HeaderValue, Method, StatusCode};
use rustls::{ClientConfig, RootCertStore};
use rustls_pki_types::CertificateDer;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::sync::{
    atomic::{AtomicU64, Ordering},
    Arc, Mutex,
};
use std::time::Duration;
use tauri::{AppHandle, Emitter, State};
use tokio_tungstenite::{
    connect_async_tls_with_config,
    tungstenite::{client::IntoClientRequest, Error as WebSocketError, Message},
    Connector,
};
use url::Url;

const MAX_RESPONSE_BYTES: usize = 32 * 1024 * 1024;

enum StreamFailure {
    SessionInvalid(String),
    Retry(String),
}

#[derive(Clone)]
struct PairedCompanion {
    public: PublicCompanionSession,
    access_token: String,
    certificate_der: Vec<u8>,
    client: reqwest::Client,
}

pub struct MobileCompanionState {
    paired: Mutex<Option<PairedCompanion>>,
    stream_generation: Arc<AtomicU64>,
}

impl Default for MobileCompanionState {
    fn default() -> Self {
        Self {
            paired: Mutex::new(None),
            stream_generation: Arc::new(AtomicU64::new(0)),
        }
    }
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct PairCommandInput {
    pub base_url: String,
    pub pairing_code: String,
    pub device_name: String,
}

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct NativeRequestInput {
    pub path: String,
    pub method: String,
    pub body: Option<String>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
pub struct NativeResponse {
    pub status: u16,
    pub payload: Value,
}

#[tauri::command]
pub async fn companion_pair(
    input: PairCommandInput,
    state: State<'_, MobileCompanionState>,
) -> Result<PublicCompanionSession, String> {
    let base_url = normalize_base_url(&input.base_url)?;
    let device_name = input.device_name.trim().to_string();
    if device_name.len() < 2 || device_name.len() > 64 || device_name.chars().any(char::is_control)
    {
        return Err("Device name must be between 2 and 64 printable characters".to_string());
    }
    let bootstrap = reqwest::Client::builder()
        .danger_accept_invalid_certs(true)
        .connect_timeout(Duration::from_secs(5))
        .timeout(Duration::from_secs(20))
        .redirect(reqwest::redirect::Policy::none())
        .build()
        .map_err(|error| format!("Unable to initialize pairing transport: {error}"))?;
    let challenge_response = bootstrap
        .get(format!("{base_url}/companion/v1/pair/challenge"))
        .send()
        .await
        .map_err(|error| format!("Unable to reach the laptop pairing gateway: {error}"))?;
    let challenge_status = challenge_response.status();
    let challenge_payload = challenge_response
        .bytes()
        .await
        .map_err(|error| format!("Unable to read pairing challenge: {error}"))?;
    if !challenge_status.is_success() {
        return Err(error_from_payload(
            &challenge_payload,
            "Laptop pairing window is unavailable",
        ));
    }
    let challenge: PairingChallenge = serde_json::from_slice(&challenge_payload)
        .map_err(|error| format!("Laptop pairing challenge is invalid: {error}"))?;
    if challenge.contract != CHALLENGE_CONTRACT || challenge.execution_allowed {
        return Err("Laptop returned an unsupported or unsafe pairing challenge".to_string());
    }
    let salt = decode_url(&challenge.salt)?;
    let server_nonce = decode_url(&challenge.server_nonce)?;
    let keys = derive_pairing_keys(&input.pairing_code, &salt, &server_nonce)?;
    let client_nonce = encode_url(random_bytes::<24>()?);
    let requested_capabilities = vec![
        "chart_read".to_string(),
        "review_write".to_string(),
        "ai_drafts".to_string(),
        "codex_bridge".to_string(),
    ];
    let proof_payload = pairing_proof_payload(
        &challenge.challenge_id,
        &challenge.server_nonce,
        &client_nonce,
        &challenge.certificate_sha256,
        &device_name,
        &requested_capabilities,
        false,
    );
    let request = PairingRequest {
        contract: CLIENT_CONTRACT.to_string(),
        challenge_id: challenge.challenge_id.clone(),
        client_nonce,
        device_name: device_name.clone(),
        requested_capabilities,
        execution_requested: false,
        proof: encode_url(pairing_proof(&keys.proof, &proof_payload)?),
    };
    let pair_response = bootstrap
        .post(format!("{base_url}/companion/v1/pair"))
        .json(&request)
        .send()
        .await
        .map_err(|error| format!("Unable to complete laptop pairing: {error}"))?;
    let pair_status = pair_response.status();
    let pair_payload = pair_response
        .bytes()
        .await
        .map_err(|error| format!("Unable to read laptop pairing response: {error}"))?;
    if !pair_status.is_success() {
        return Err(error_from_payload(
            &pair_payload,
            "Laptop rejected the pairing request",
        ));
    }
    let paired: PairingResponse = serde_json::from_slice(&pair_payload)
        .map_err(|error| format!("Laptop pairing response is invalid: {error}"))?;
    let envelope = paired.envelope.filter(|_| paired.ok).ok_or_else(|| {
        paired
            .error
            .unwrap_or_else(|| "Laptop did not issue a pairing session".to_string())
    })?;
    let encrypted = decrypt_session(
        &keys.encryption,
        &challenge.challenge_id,
        &device_name,
        &envelope,
    )?;
    validate_encrypted_session(&encrypted, &challenge.certificate_sha256)?;
    let certificate_der = decode_url(&encrypted.certificate_der)?;
    let certificate = reqwest::Certificate::from_der(&certificate_der)
        .map_err(|error| format!("Laptop certificate is invalid: {error}"))?;
    let pinned_client = reqwest::Client::builder()
        .tls_built_in_root_certs(false)
        .add_root_certificate(certificate)
        .connect_timeout(Duration::from_secs(5))
        .timeout(Duration::from_secs(45))
        .redirect(reqwest::redirect::Policy::none())
        .build()
        .map_err(|error| format!("Unable to initialize pinned companion transport: {error}"))?;
    let status = pinned_client
        .get(format!("{base_url}/companion/v1/status"))
        .bearer_auth(&encrypted.access_token)
        .header("X-Gann-Astro-Client", CLIENT_CONTRACT)
        .send()
        .await
        .map_err(|error| format!("Pinned laptop certificate check failed: {error}"))?;
    if !status.status().is_success() {
        return Err("Laptop session did not pass the pinned HTTPS verification".to_string());
    }
    let public = PublicCompanionSession {
        contract: SESSION_CONTRACT.to_string(),
        session_id: encrypted.session_id,
        base_url,
        expires_at_utc: encrypted.expires_at_utc,
        certificate_sha256: encrypted.certificate_sha256,
        transport: "native_pinned_https_wss".to_string(),
        capabilities: encrypted.capabilities,
        execution_allowed: false,
    };
    let paired = PairedCompanion {
        public: public.clone(),
        access_token: encrypted.access_token,
        certificate_der,
        client: pinned_client,
    };
    *state
        .paired
        .lock()
        .map_err(|_| "Mobile companion state is unavailable".to_string())? = Some(paired);
    state.stream_generation.fetch_add(1, Ordering::SeqCst);
    Ok(public)
}

#[tauri::command]
pub async fn companion_request(
    input: NativeRequestInput,
    state: State<'_, MobileCompanionState>,
) -> Result<NativeResponse, String> {
    validate_relative_path(&input.path)?;
    let method = Method::from_bytes(input.method.to_ascii_uppercase().as_bytes())
        .map_err(|_| "Companion request method is invalid".to_string())?;
    if !matches!(
        method,
        Method::GET | Method::POST | Method::PUT | Method::DELETE
    ) {
        return Err("Companion request method is not allowed".to_string());
    }
    let paired = state
        .paired
        .lock()
        .map_err(|_| "Mobile companion state is unavailable".to_string())?
        .clone()
        .ok_or_else(|| "Pair the laptop before requesting workspace data".to_string())?;
    let mut request = paired
        .client
        .request(method, format!("{}{}", paired.public.base_url, input.path))
        .bearer_auth(&paired.access_token)
        .header("X-Gann-Astro-Client", CLIENT_CONTRACT)
        .header(header::ACCEPT, "application/json");
    if let Some(body) = input.body.filter(|body| !body.is_empty()) {
        request = request
            .header(header::CONTENT_TYPE, "application/json")
            .body(body);
    }
    let response = request
        .send()
        .await
        .map_err(|error| format!("Companion request failed: {error}"))?;
    if response
        .content_length()
        .is_some_and(|length| length > MAX_RESPONSE_BYTES as u64)
    {
        return Err("Companion response exceeded the mobile limit".to_string());
    }
    let status = response.status().as_u16();
    let payload = response
        .bytes()
        .await
        .map_err(|error| format!("Unable to read companion response: {error}"))?;
    if payload.len() > MAX_RESPONSE_BYTES {
        return Err("Companion response exceeded the mobile limit".to_string());
    }
    let payload = serde_json::from_slice(&payload)
        .map_err(|error| format!("Companion response is not JSON: {error}"))?;
    Ok(NativeResponse { status, payload })
}

#[tauri::command]
pub fn companion_session(
    state: State<'_, MobileCompanionState>,
) -> Result<Option<PublicCompanionSession>, String> {
    Ok(state
        .paired
        .lock()
        .map_err(|_| "Mobile companion state is unavailable".to_string())?
        .as_ref()
        .map(|paired| paired.public.clone()))
}

#[tauri::command]
pub fn companion_disconnect(state: State<'_, MobileCompanionState>) -> Result<(), String> {
    state.stream_generation.fetch_add(1, Ordering::SeqCst);
    *state
        .paired
        .lock()
        .map_err(|_| "Mobile companion state is unavailable".to_string())? = None;
    Ok(())
}

#[tauri::command]
pub fn companion_start_stream(
    app: AppHandle,
    state: State<'_, MobileCompanionState>,
) -> Result<(), String> {
    let paired = state
        .paired
        .lock()
        .map_err(|_| "Mobile companion state is unavailable".to_string())?
        .clone()
        .ok_or_else(|| "Pair the laptop before starting the live stream".to_string())?;
    let generation = state.stream_generation.fetch_add(1, Ordering::SeqCst) + 1;
    let generation_counter = state.stream_generation.clone();
    tauri::async_runtime::spawn(async move {
        let mut backoff = Duration::from_secs(1);
        while generation_counter.load(Ordering::SeqCst) == generation {
            match stream_once(&app, &paired).await {
                Ok(()) => backoff = Duration::from_secs(1),
                Err(StreamFailure::SessionInvalid(error)) => {
                    let _ = app.emit(
                        "companion-session-invalid",
                        serde_json::json!({
                            "error": error,
                            "executionAllowed": false,
                        }),
                    );
                    break;
                }
                Err(StreamFailure::Retry(error)) => {
                    let _ = app.emit(
                        "companion-stream-state",
                        serde_json::json!({
                            "state": "reconnecting",
                            "error": error,
                            "executionAllowed": false,
                        }),
                    );
                }
            }
            if generation_counter.load(Ordering::SeqCst) != generation {
                break;
            }
            tokio::time::sleep(backoff).await;
            backoff = (backoff * 2).min(Duration::from_secs(10));
        }
    });
    Ok(())
}

async fn stream_once(app: &AppHandle, paired: &PairedCompanion) -> Result<(), StreamFailure> {
    let mut roots = RootCertStore::empty();
    roots
        .add(CertificateDer::from(paired.certificate_der.clone()))
        .map_err(|error| {
            StreamFailure::Retry(format!("Unable to pin laptop certificate for WSS: {error}"))
        })?;
    let tls = ClientConfig::builder()
        .with_root_certificates(roots)
        .with_no_client_auth();
    let mut url = Url::parse(&paired.public.base_url)
        .map_err(|error| StreamFailure::Retry(format!("Companion URL is invalid: {error}")))?;
    url.set_scheme("wss")
        .map_err(|_| StreamFailure::Retry("Unable to construct companion WSS URL".to_string()))?;
    url.set_path("/companion/v1/stream");
    let mut request = url.as_str().into_client_request().map_err(|error| {
        StreamFailure::Retry(format!("Unable to create companion WSS request: {error}"))
    })?;
    request.headers_mut().insert(
        header::AUTHORIZATION,
        HeaderValue::from_str(&format!("Bearer {}", paired.access_token))
            .map_err(|_| StreamFailure::Retry("Companion token is invalid".to_string()))?,
    );
    request.headers_mut().insert(
        header::SEC_WEBSOCKET_PROTOCOL,
        HeaderValue::from_static("gann-astro-stream-v1"),
    );
    let connection =
        connect_async_tls_with_config(request, None, false, Some(Connector::Rustls(Arc::new(tls))))
            .await;
    let (mut socket, _) = match connection {
        Ok(connection) => connection,
        Err(WebSocketError::Http(response)) if response.status() == StatusCode::UNAUTHORIZED => {
            return Err(StreamFailure::SessionInvalid(
                "Companion session expired or was revoked on the laptop".to_string(),
            ));
        }
        Err(error) => {
            return Err(StreamFailure::Retry(format!(
                "Companion WSS connection failed: {error}"
            )));
        }
    };
    let _ = app.emit(
        "companion-stream-state",
        serde_json::json!({
            "state": "connected",
            "executionAllowed": false,
        }),
    );
    while let Some(message) = socket.next().await {
        match message
            .map_err(|error| StreamFailure::Retry(format!("Companion WSS read failed: {error}")))?
        {
            Message::Text(text) => {
                if let Ok(payload) = serde_json::from_str::<Value>(&text) {
                    let _ = app.emit("companion-stream", payload);
                }
            }
            Message::Close(_) => break,
            _ => {}
        }
    }
    Ok(())
}

fn normalize_base_url(value: &str) -> Result<String, String> {
    let parsed =
        Url::parse(value.trim()).map_err(|error| format!("Laptop address is invalid: {error}"))?;
    if parsed.scheme() != "https"
        || parsed.host().is_none()
        || parsed.username() != ""
        || parsed.password().is_some()
        || parsed.query().is_some()
        || parsed.fragment().is_some()
        || !matches!(parsed.path(), "" | "/")
    {
        return Err(
            "Laptop address must be an HTTPS origin without credentials or a path".to_string(),
        );
    }
    let host = parsed
        .host_str()
        .ok_or_else(|| "Laptop address has no host".to_string())?;
    let authority = if host.contains(':') {
        format!("[{host}]")
    } else {
        host.to_string()
    };
    Ok(format!(
        "https://{authority}:{}",
        parsed.port_or_known_default().unwrap_or(443)
    ))
}

fn validate_encrypted_session(
    session: &EncryptedSession,
    expected_fingerprint: &str,
) -> Result<(), String> {
    if session.contract != SESSION_CONTRACT
        || session.execution_allowed
        || session.capabilities.execution_allowed
    {
        return Err("Laptop returned an unsupported or unsafe companion session".to_string());
    }
    let certificate = decode_url(&session.certificate_der)?;
    let actual = sha256_hex(&certificate);
    if actual != session.certificate_sha256 || actual != expected_fingerprint {
        return Err(
            "Laptop certificate fingerprint did not survive the encrypted handshake".to_string(),
        );
    }
    if session.access_token.len() < 32 || session.session_id.is_empty() {
        return Err("Laptop companion session is incomplete".to_string());
    }
    Ok(())
}

fn validate_relative_path(path: &str) -> Result<(), String> {
    let uri = path
        .parse::<http::Uri>()
        .map_err(|_| "Companion request path is invalid".to_string())?;
    let normalized_path = uri.path();
    let lowercase = normalized_path.to_ascii_lowercase();
    if path.len() > 4096
        || uri.scheme().is_some()
        || uri.authority().is_some()
        || !(normalized_path.starts_with("/api/") || normalized_path.starts_with("/codex-api/"))
        || path.contains(char::is_whitespace)
        || normalized_path.starts_with("//")
        || normalized_path.contains('\\')
        || lowercase.contains("%2e")
        || lowercase.contains("%2f")
        || lowercase.contains("%5c")
        || normalized_path
            .split('/')
            .any(|segment| matches!(segment, "." | ".."))
    {
        return Err("Companion request path is invalid".to_string());
    }
    Ok(())
}

fn error_from_payload(payload: &[u8], fallback: &str) -> String {
    serde_json::from_slice::<Value>(payload)
        .ok()
        .and_then(|value| {
            value
                .get("error")
                .and_then(Value::as_str)
                .map(str::to_string)
        })
        .unwrap_or_else(|| fallback.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn mobile_url_and_path_validation_reject_credentials_and_absolute_targets() {
        assert_eq!(
            normalize_base_url("https://192.168.1.4:9443/").unwrap(),
            "https://192.168.1.4:9443"
        );
        assert!(normalize_base_url("http://192.168.1.4:9443").is_err());
        assert!(normalize_base_url("https://user@example.com:9443").is_err());
        assert!(validate_relative_path("/api/chart?symbol=USDJPY").is_ok());
        assert!(validate_relative_path("https://example.com/api/chart").is_err());
        assert!(validate_relative_path("/api/events/../orders").is_err());
        assert!(validate_relative_path("/api/events/%2e%2e/orders").is_err());
    }
}
