use crate::companion_protocol::{
    decode_url, derive_pairing_keys, encode_url, encrypt_session, now_rfc3339,
    pairing_proof_payload, random_bytes, random_pairing_code, random_url_token, rfc3339_after,
    sha256, sha256_hex, verify_pairing_proof, CompanionCapabilities, EncryptedSession,
    PairingChallenge, PairingRequest, PairingResponse, PublicCompanionSession, CHALLENGE_CONTRACT,
    CLIENT_CONTRACT, GATEWAY_CONTRACT, SESSION_CONTRACT, STREAM_CONTRACT,
};
use axum::{
    body::Bytes,
    extract::{
        ws::{Message, WebSocket},
        ConnectInfo, DefaultBodyLimit, State, WebSocketUpgrade,
    },
    http::{header, HeaderMap, Method, StatusCode, Uri},
    response::{IntoResponse, Response},
    routing::{any, get, post},
    Json, Router,
};
use axum_server::{tls_rustls::RustlsConfig, Handle};
use futures_util::StreamExt;
use rcgen::{CertificateParams, DistinguishedName, DnType, KeyPair, SanType};
use serde::Serialize;
use serde_json::{json, Value};
use std::{
    collections::HashMap,
    fs::{self, OpenOptions},
    io::Write,
    net::{IpAddr, Ipv4Addr, SocketAddr, TcpListener},
    path::PathBuf,
    sync::{
        atomic::{AtomicU64, Ordering},
        Arc, Mutex,
    },
    time::{Duration, SystemTime},
};
use tokio::sync::broadcast;
use uuid::Uuid;

const DEFAULT_GATEWAY_PORT: u16 = 9443;
const PAIRING_WINDOW_TTL: Duration = Duration::from_secs(5 * 60);
const CHALLENGE_TTL: Duration = Duration::from_secs(90);
const SESSION_TTL: Duration = Duration::from_secs(12 * 60 * 60);
const MAX_PAIRING_ATTEMPTS: u8 = 5;
const MAX_CHALLENGES: usize = 16;
const MAX_REQUEST_BYTES: usize = 8 * 1024 * 1024;
const MAX_RESPONSE_BYTES: usize = 32 * 1024 * 1024;
const AUDIT_ROTATE_BYTES: u64 = 5 * 1024 * 1024;
const SESSION_RATE_WINDOW: Duration = Duration::from_secs(60);
const MAX_SESSION_REQUESTS_PER_WINDOW: u16 = 240;

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct GatewayInfo {
    pub contract: &'static str,
    pub status: &'static str,
    pub urls: Vec<String>,
    pub port: u16,
    pub certificate_sha256: String,
    pub pairing_active: bool,
    pub pairing_expires_at_utc: Option<String>,
    pub paired_sessions: usize,
    pub execution_allowed: bool,
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PairingWindowInfo {
    pub contract: &'static str,
    pub urls: Vec<String>,
    pub pairing_code: String,
    pub certificate_sha256: String,
    pub expires_at_utc: String,
    pub execution_allowed: bool,
}

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct GatewaySessionInfo {
    pub session_id: String,
    pub device_name: String,
    pub created_at_utc: String,
    pub expires_at_utc: String,
    pub last_seen_at_utc: String,
    pub remote_address: String,
    pub execution_allowed: bool,
}

struct ChallengeRecord {
    server_nonce: Vec<u8>,
    server_nonce_encoded: String,
    salt: Vec<u8>,
    expires_at: SystemTime,
    remote_ip: IpAddr,
}

struct PairingWindow {
    code: String,
    expires_at: SystemTime,
    expires_at_utc: String,
    attempts: u8,
    challenges: HashMap<String, ChallengeRecord>,
}

#[derive(Clone)]
struct SessionRecord {
    session_id: String,
    device_name: String,
    created_at_utc: String,
    expires_at: SystemTime,
    expires_at_utc: String,
    last_seen_at_utc: String,
    remote_address: String,
    capabilities: CompanionCapabilities,
    rate_window_started: SystemTime,
    rate_requests: u16,
}

#[derive(Clone, Copy)]
enum RequiredCapability {
    ChartRead,
    ReviewWrite,
    AiDrafts,
    CodexBridge,
}

struct GatewayCore {
    urls: Vec<String>,
    port: u16,
    certificate_der: Vec<u8>,
    certificate_sha256: String,
    backend_port: u16,
    backend_token: String,
    backend_client: reqwest::Client,
    pairing: Mutex<Option<PairingWindow>>,
    sessions: Mutex<HashMap<[u8; 32], SessionRecord>>,
    stream_tx: broadcast::Sender<String>,
    sequence: AtomicU64,
    audit_path: PathBuf,
}

pub struct CompanionGatewayState {
    core: Arc<GatewayCore>,
    handle: Handle<SocketAddr>,
}

#[derive(Serialize)]
struct ErrorBody {
    ok: bool,
    error: String,
}

#[derive(Debug)]
struct GatewayError {
    status: StatusCode,
    message: String,
}

impl GatewayError {
    fn new(status: StatusCode, message: impl Into<String>) -> Self {
        Self {
            status,
            message: message.into(),
        }
    }
}

impl IntoResponse for GatewayError {
    fn into_response(self) -> Response {
        (
            self.status,
            Json(ErrorBody {
                ok: false,
                error: self.message,
            }),
        )
            .into_response()
    }
}

impl CompanionGatewayState {
    pub fn spawn(
        backend_port: u16,
        backend_token: String,
        data_root: PathBuf,
    ) -> Result<Self, String> {
        let listener = bind_gateway_listener()?;
        let port = listener
            .local_addr()
            .map_err(|error| format!("Unable to inspect companion listener: {error}"))?
            .port();
        listener
            .set_nonblocking(true)
            .map_err(|error| format!("Unable to configure companion listener: {error}"))?;
        let addresses = companion_addresses();
        let (certificate_der, private_key_der) = generate_certificate(&addresses)?;
        let certificate_sha256 = sha256_hex(&certificate_der);
        let urls = addresses
            .iter()
            .filter(|address| !address.is_loopback())
            .map(|address| format!("https://{address}:{port}"))
            .collect::<Vec<_>>();
        let urls = if urls.is_empty() {
            vec![format!("https://127.0.0.1:{port}")]
        } else {
            urls
        };
        let backend_client = reqwest::Client::builder()
            .connect_timeout(Duration::from_secs(3))
            .timeout(Duration::from_secs(45))
            .redirect(reqwest::redirect::Policy::none())
            .build()
            .map_err(|error| format!("Unable to create companion proxy client: {error}"))?;
        let (stream_tx, _) = broadcast::channel(32);
        let audit_path = data_root.join("logs").join("companion_gateway_audit.jsonl");
        if let Some(parent) = audit_path.parent() {
            fs::create_dir_all(parent)
                .map_err(|error| format!("Unable to create companion audit directory: {error}"))?;
        }
        let core = Arc::new(GatewayCore {
            urls,
            port,
            certificate_der,
            certificate_sha256,
            backend_port,
            backend_token,
            backend_client,
            pairing: Mutex::new(None),
            sessions: Mutex::new(HashMap::new()),
            stream_tx,
            sequence: AtomicU64::new(0),
            audit_path,
        });
        let tls_config = tauri::async_runtime::block_on(RustlsConfig::from_der(
            vec![core.certificate_der.clone()],
            private_key_der,
        ))
        .map_err(|error| format!("Unable to configure companion TLS: {error}"))?;
        let handle = Handle::<SocketAddr>::new();
        let app = gateway_router(core.clone());
        let server_handle = handle.clone();
        tauri::async_runtime::spawn(async move {
            let server = match axum_server::from_tcp_rustls(listener, tls_config) {
                Ok(server) => server,
                Err(error) => {
                    eprintln!("Unable to initialize companion TLS listener: {error}");
                    return;
                }
            };
            if let Err(error) = server
                .handle(server_handle)
                .serve(app.into_make_service_with_connect_info::<SocketAddr>())
                .await
            {
                eprintln!("Companion gateway stopped: {error}");
            }
        });
        spawn_stream_publisher(core.clone());
        core.audit("gateway_started", json!({"port": port, "urls": core.urls}));
        Ok(Self { core, handle })
    }

    pub fn info(&self) -> GatewayInfo {
        self.core.info()
    }

    pub fn start_pairing(&self) -> Result<PairingWindowInfo, String> {
        self.core.start_pairing()
    }

    pub fn sessions(&self) -> Vec<GatewaySessionInfo> {
        self.core.sessions()
    }

    pub fn revoke(&self, session_id: &str) -> bool {
        self.core.revoke(session_id)
    }

    pub fn shutdown(&self) {
        self.core.audit("gateway_shutdown_requested", json!({}));
        self.handle.graceful_shutdown(Some(Duration::from_secs(3)));
    }
}

impl GatewayCore {
    fn info(&self) -> GatewayInfo {
        self.prune_sessions();
        let (pairing_active, pairing_expires_at_utc) = self
            .pairing
            .lock()
            .ok()
            .and_then(|pairing| {
                pairing.as_ref().map(|window| {
                    (
                        window.expires_at > SystemTime::now(),
                        window.expires_at_utc.clone(),
                    )
                })
            })
            .unwrap_or((false, String::new()));
        let paired_sessions = self
            .sessions
            .lock()
            .map(|sessions| sessions.len())
            .unwrap_or(0);
        GatewayInfo {
            contract: GATEWAY_CONTRACT,
            status: "ready",
            urls: self.urls.clone(),
            port: self.port,
            certificate_sha256: self.certificate_sha256.clone(),
            pairing_active,
            pairing_expires_at_utc: pairing_active.then_some(pairing_expires_at_utc),
            paired_sessions,
            execution_allowed: false,
        }
    }

    fn start_pairing(&self) -> Result<PairingWindowInfo, String> {
        let code = random_pairing_code()?;
        let expires_at = SystemTime::now()
            .checked_add(PAIRING_WINDOW_TTL)
            .ok_or_else(|| "Unable to calculate pairing expiry".to_string())?;
        let expires_at_utc = rfc3339_after(PAIRING_WINDOW_TTL);
        let mut pairing = self
            .pairing
            .lock()
            .map_err(|_| "Companion pairing state is unavailable".to_string())?;
        *pairing = Some(PairingWindow {
            code: code.clone(),
            expires_at,
            expires_at_utc: expires_at_utc.clone(),
            attempts: 0,
            challenges: HashMap::new(),
        });
        self.audit("pairing_started", json!({"expiresAtUtc": expires_at_utc}));
        Ok(PairingWindowInfo {
            contract: GATEWAY_CONTRACT,
            urls: self.urls.clone(),
            pairing_code: code,
            certificate_sha256: self.certificate_sha256.clone(),
            expires_at_utc,
            execution_allowed: false,
        })
    }

    fn sessions(&self) -> Vec<GatewaySessionInfo> {
        self.prune_sessions();
        self.sessions
            .lock()
            .map(|sessions| {
                sessions
                    .values()
                    .map(|session| GatewaySessionInfo {
                        session_id: session.session_id.clone(),
                        device_name: session.device_name.clone(),
                        created_at_utc: session.created_at_utc.clone(),
                        expires_at_utc: session.expires_at_utc.clone(),
                        last_seen_at_utc: session.last_seen_at_utc.clone(),
                        remote_address: session.remote_address.clone(),
                        execution_allowed: false,
                    })
                    .collect()
            })
            .unwrap_or_default()
    }

    fn revoke(&self, session_id: &str) -> bool {
        let Ok(mut sessions) = self.sessions.lock() else {
            return false;
        };
        let before = sessions.len();
        sessions.retain(|_, session| session.session_id != session_id);
        let revoked = sessions.len() != before;
        if revoked {
            self.audit("session_revoked", json!({"sessionId": session_id}));
        }
        revoked
    }

    fn prune_sessions(&self) {
        if let Ok(mut sessions) = self.sessions.lock() {
            let now = SystemTime::now();
            sessions.retain(|_, session| session.expires_at > now);
        }
    }

    fn authenticate(
        &self,
        headers: &HeaderMap,
        remote: SocketAddr,
    ) -> Result<SessionRecord, GatewayError> {
        let authorization = headers
            .get(header::AUTHORIZATION)
            .and_then(|value| value.to_str().ok())
            .ok_or_else(|| {
                GatewayError::new(StatusCode::UNAUTHORIZED, "Companion token is required")
            })?;
        let token = authorization
            .strip_prefix("Bearer ")
            .filter(|value| value.len() >= 32)
            .ok_or_else(|| {
                GatewayError::new(StatusCode::UNAUTHORIZED, "Companion token is invalid")
            })?;
        let token_hash = sha256(token.as_bytes());
        let mut sessions = self.sessions.lock().map_err(|_| {
            GatewayError::new(
                StatusCode::SERVICE_UNAVAILABLE,
                "Session store is unavailable",
            )
        })?;
        let now = SystemTime::now();
        sessions.retain(|_, session| session.expires_at > now);
        let session = sessions.get_mut(&token_hash).ok_or_else(|| {
            GatewayError::new(
                StatusCode::UNAUTHORIZED,
                "Companion session is expired or revoked",
            )
        })?;
        if now
            .duration_since(session.rate_window_started)
            .unwrap_or(SESSION_RATE_WINDOW)
            >= SESSION_RATE_WINDOW
        {
            session.rate_window_started = now;
            session.rate_requests = 0;
        }
        if session.rate_requests >= MAX_SESSION_REQUESTS_PER_WINDOW {
            return Err(GatewayError::new(
                StatusCode::TOO_MANY_REQUESTS,
                "Companion request rate limit reached",
            ));
        }
        session.rate_requests = session.rate_requests.saturating_add(1);
        session.last_seen_at_utc = now_rfc3339();
        session.remote_address = remote.to_string();
        Ok(session.clone())
    }

    fn session_is_active(&self, session_id: &str) -> bool {
        let Ok(mut sessions) = self.sessions.lock() else {
            return false;
        };
        let now = SystemTime::now();
        sessions.retain(|_, session| session.expires_at > now);
        sessions
            .values()
            .any(|session| session.session_id == session_id)
    }

    fn audit(&self, name: &str, details: Value) {
        if let Ok(metadata) = fs::metadata(&self.audit_path) {
            if metadata.len() >= AUDIT_ROTATE_BYTES {
                let backup = self.audit_path.with_extension("jsonl.1");
                let _ = fs::remove_file(&backup);
                let _ = fs::rename(&self.audit_path, backup);
            }
        }
        let event = json!({
            "atUtc": now_rfc3339(),
            "kind": "companion_gateway",
            "name": name,
            "details": details,
            "executionAllowed": false,
        });
        if let Ok(mut handle) = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.audit_path)
        {
            let _ = writeln!(handle, "{event}");
        }
    }
}

fn bind_gateway_listener() -> Result<TcpListener, String> {
    TcpListener::bind((Ipv4Addr::UNSPECIFIED, DEFAULT_GATEWAY_PORT))
        .or_else(|_| TcpListener::bind((Ipv4Addr::UNSPECIFIED, 0)))
        .map_err(|error| format!("Unable to bind the companion TLS gateway: {error}"))
}

fn companion_addresses() -> Vec<IpAddr> {
    let mut addresses = vec![IpAddr::V4(Ipv4Addr::LOCALHOST)];
    if let Ok(interfaces) = local_ip_address::list_afinet_netifas() {
        for (_, address) in interfaces {
            if address.is_loopback() || address.is_unspecified() {
                continue;
            }
            if let IpAddr::V4(ipv4) = address {
                if ipv4.octets()[0] == 169 && ipv4.octets()[1] == 254 {
                    continue;
                }
                addresses.push(IpAddr::V4(ipv4));
            }
        }
    }
    addresses.sort_by_key(ToString::to_string);
    addresses.dedup();
    addresses
}

fn generate_certificate(addresses: &[IpAddr]) -> Result<(Vec<u8>, Vec<u8>), String> {
    let mut params = CertificateParams::new(vec!["localhost".to_string()])
        .map_err(|error| format!("Unable to initialize companion certificate: {error}"))?;
    params.distinguished_name = DistinguishedName::new();
    params
        .distinguished_name
        .push(DnType::CommonName, "Gann Astro Desk Companion");
    for address in addresses {
        params.subject_alt_names.push(SanType::IpAddress(*address));
    }
    let key = KeyPair::generate()
        .map_err(|error| format!("Unable to generate companion TLS key: {error}"))?;
    let certificate = params
        .self_signed(&key)
        .map_err(|error| format!("Unable to sign companion TLS certificate: {error}"))?;
    Ok((certificate.der().to_vec(), key.serialize_der()))
}

fn gateway_router(core: Arc<GatewayCore>) -> Router {
    Router::new()
        .route("/companion/v1/pair/challenge", get(pairing_challenge))
        .route("/companion/v1/pair", post(pair_device))
        .route("/companion/v1/status", get(companion_status))
        .route("/companion/v1/stream", any(companion_stream))
        .route("/api/{*path}", any(proxy_request))
        .route("/codex-api/{*path}", any(proxy_request))
        .layer(DefaultBodyLimit::max(MAX_REQUEST_BYTES))
        .with_state(core)
}

async fn pairing_challenge(
    State(core): State<Arc<GatewayCore>>,
    ConnectInfo(remote): ConnectInfo<SocketAddr>,
) -> Result<Json<PairingChallenge>, GatewayError> {
    let mut pairing = core.pairing.lock().map_err(|_| {
        GatewayError::new(
            StatusCode::SERVICE_UNAVAILABLE,
            "Pairing state is unavailable",
        )
    })?;
    let window = pairing
        .as_mut()
        .filter(|window| window.expires_at > SystemTime::now())
        .ok_or_else(|| {
            GatewayError::new(
                StatusCode::FORBIDDEN,
                "Open Companion Mode on the laptop first",
            )
        })?;
    window
        .challenges
        .retain(|_, challenge| challenge.expires_at > SystemTime::now());
    if window.challenges.len() >= MAX_CHALLENGES {
        return Err(GatewayError::new(
            StatusCode::TOO_MANY_REQUESTS,
            "Too many outstanding pairing challenges",
        ));
    }
    let challenge_id = random_url_token::<18>()
        .map_err(|error| GatewayError::new(StatusCode::INTERNAL_SERVER_ERROR, error))?;
    let server_nonce = random_bytes::<24>()
        .map_err(|error| GatewayError::new(StatusCode::INTERNAL_SERVER_ERROR, error))?;
    let salt = random_bytes::<16>()
        .map_err(|error| GatewayError::new(StatusCode::INTERNAL_SERVER_ERROR, error))?;
    let server_nonce_encoded = encode_url(server_nonce);
    let salt_encoded = encode_url(salt);
    let expires_at = SystemTime::now()
        .checked_add(CHALLENGE_TTL)
        .unwrap_or(SystemTime::now());
    window.challenges.insert(
        challenge_id.clone(),
        ChallengeRecord {
            server_nonce: server_nonce.to_vec(),
            server_nonce_encoded: server_nonce_encoded.clone(),
            salt: salt.to_vec(),
            expires_at,
            remote_ip: remote.ip(),
        },
    );
    drop(pairing);
    core.audit(
        "pairing_challenge_issued",
        json!({"remoteIp": remote.ip().to_string()}),
    );
    Ok(Json(PairingChallenge {
        contract: CHALLENGE_CONTRACT.to_string(),
        challenge_id,
        server_nonce: server_nonce_encoded,
        salt: salt_encoded,
        certificate_sha256: core.certificate_sha256.clone(),
        expires_at_utc: rfc3339_after(CHALLENGE_TTL),
        execution_allowed: false,
    }))
}

async fn pair_device(
    State(core): State<Arc<GatewayCore>>,
    ConnectInfo(remote): ConnectInfo<SocketAddr>,
    Json(request): Json<PairingRequest>,
) -> Result<Json<PairingResponse>, GatewayError> {
    validate_pairing_request(&request)?;
    let client_nonce = decode_url(&request.client_nonce)
        .map_err(|_| GatewayError::new(StatusCode::BAD_REQUEST, "Client nonce is invalid"))?;
    if client_nonce.len() != 24 {
        return Err(GatewayError::new(
            StatusCode::BAD_REQUEST,
            "Client nonce has the wrong length",
        ));
    }
    let supplied_proof = decode_url(&request.proof)
        .map_err(|_| GatewayError::new(StatusCode::BAD_REQUEST, "Pairing proof is invalid"))?;
    let (challenge, code) = {
        let mut pairing = core.pairing.lock().map_err(|_| {
            GatewayError::new(
                StatusCode::SERVICE_UNAVAILABLE,
                "Pairing state is unavailable",
            )
        })?;
        let window = pairing
            .as_mut()
            .filter(|window| window.expires_at > SystemTime::now())
            .ok_or_else(|| {
                GatewayError::new(StatusCode::FORBIDDEN, "Pairing window has expired")
            })?;
        if window.attempts >= MAX_PAIRING_ATTEMPTS {
            *pairing = None;
            return Err(GatewayError::new(
                StatusCode::TOO_MANY_REQUESTS,
                "Pairing was locked after repeated failures; open a new code on the laptop",
            ));
        }
        let challenge = window
            .challenges
            .remove(&request.challenge_id)
            .filter(|challenge| challenge.expires_at > SystemTime::now())
            .ok_or_else(|| GatewayError::new(StatusCode::FORBIDDEN, "Pairing challenge expired"))?;
        if challenge.remote_ip != remote.ip() {
            window.attempts += 1;
            return Err(GatewayError::new(
                StatusCode::FORBIDDEN,
                "Pairing challenge changed network origin",
            ));
        }
        (challenge, window.code.clone())
    };
    let keys = derive_pairing_keys(&code, &challenge.salt, &challenge.server_nonce)
        .map_err(|error| GatewayError::new(StatusCode::FORBIDDEN, error))?;
    let proof_payload = pairing_proof_payload(
        &request.challenge_id,
        &challenge.server_nonce_encoded,
        &request.client_nonce,
        &core.certificate_sha256,
        &request.device_name,
        &request.requested_capabilities,
        request.execution_requested,
    );
    if verify_pairing_proof(&keys.proof, &proof_payload, &supplied_proof).is_err() {
        if let Ok(mut pairing) = core.pairing.lock() {
            if let Some(window) = pairing.as_mut() {
                window.attempts = window.attempts.saturating_add(1);
                if window.attempts >= MAX_PAIRING_ATTEMPTS {
                    *pairing = None;
                }
            }
        }
        core.audit(
            "pairing_rejected",
            json!({"remoteIp": remote.ip().to_string()}),
        );
        return Err(GatewayError::new(
            StatusCode::FORBIDDEN,
            "Pairing proof was rejected",
        ));
    }
    let access_token = random_url_token::<32>()
        .map_err(|error| GatewayError::new(StatusCode::INTERNAL_SERVER_ERROR, error))?;
    let token_hash = sha256(access_token.as_bytes());
    let session_id = Uuid::new_v4().to_string();
    let created_at_utc = now_rfc3339();
    let expires_at = SystemTime::now()
        .checked_add(SESSION_TTL)
        .unwrap_or(SystemTime::now());
    let expires_at_utc = rfc3339_after(SESSION_TTL);
    let capabilities = CompanionCapabilities::locked_for(&request.requested_capabilities);
    let encrypted_session = EncryptedSession {
        contract: SESSION_CONTRACT.to_string(),
        session_id: session_id.clone(),
        access_token,
        expires_at_utc: expires_at_utc.clone(),
        certificate_der: encode_url(&core.certificate_der),
        certificate_sha256: core.certificate_sha256.clone(),
        capabilities: capabilities.clone(),
        execution_allowed: false,
    };
    let envelope = encrypt_session(
        &keys.encryption,
        &request.challenge_id,
        &request.device_name,
        &encrypted_session,
    )
    .map_err(|error| GatewayError::new(StatusCode::INTERNAL_SERVER_ERROR, error))?;
    core.sessions
        .lock()
        .map_err(|_| {
            GatewayError::new(
                StatusCode::SERVICE_UNAVAILABLE,
                "Session store is unavailable",
            )
        })?
        .insert(
            token_hash,
            SessionRecord {
                session_id: session_id.clone(),
                device_name: request.device_name.clone(),
                created_at_utc,
                expires_at,
                expires_at_utc: expires_at_utc.clone(),
                last_seen_at_utc: now_rfc3339(),
                remote_address: remote.to_string(),
                capabilities,
                rate_window_started: SystemTime::now(),
                rate_requests: 0,
            },
        );
    if let Ok(mut pairing) = core.pairing.lock() {
        *pairing = None;
    }
    core.audit(
        "device_paired",
        json!({"sessionId": session_id, "deviceName": request.device_name, "remoteIp": remote.ip().to_string()}),
    );
    Ok(Json(PairingResponse {
        ok: true,
        error: None,
        envelope: Some(envelope),
    }))
}

fn validate_pairing_request(request: &PairingRequest) -> Result<(), GatewayError> {
    if request.contract != CLIENT_CONTRACT {
        return Err(GatewayError::new(
            StatusCode::BAD_REQUEST,
            "Unsupported companion client contract",
        ));
    }
    if request.execution_requested {
        return Err(GatewayError::new(
            StatusCode::FORBIDDEN,
            "Trade execution is locked",
        ));
    }
    if request.device_name.len() < 2
        || request.device_name.len() > 64
        || request.device_name.chars().any(char::is_control)
    {
        return Err(GatewayError::new(
            StatusCode::BAD_REQUEST,
            "Device name is invalid",
        ));
    }
    let allowed = ["chart_read", "review_write", "ai_drafts", "codex_bridge"];
    if request.requested_capabilities.is_empty()
        || request
            .requested_capabilities
            .iter()
            .any(|capability| !allowed.contains(&capability.as_str()))
    {
        return Err(GatewayError::new(
            StatusCode::BAD_REQUEST,
            "Requested capability is not allowed",
        ));
    }
    Ok(())
}

async fn companion_status(
    State(core): State<Arc<GatewayCore>>,
    ConnectInfo(remote): ConnectInfo<SocketAddr>,
    headers: HeaderMap,
) -> Result<Json<Value>, GatewayError> {
    let session = core.authenticate(&headers, remote)?;
    Ok(Json(json!({
        "ok": true,
        "gateway": core.info(),
        "session": PublicCompanionSession {
            contract: SESSION_CONTRACT.to_string(),
            session_id: session.session_id,
            base_url: String::new(),
            expires_at_utc: session.expires_at_utc,
            certificate_sha256: core.certificate_sha256.clone(),
            transport: "native_pinned_https_wss".to_string(),
            capabilities: session.capabilities,
            execution_allowed: false,
        }
    })))
}

async fn proxy_request(
    State(core): State<Arc<GatewayCore>>,
    ConnectInfo(remote): ConnectInfo<SocketAddr>,
    method: Method,
    uri: Uri,
    headers: HeaderMap,
    body: Bytes,
) -> Result<Response, GatewayError> {
    let session = core.authenticate(&headers, remote)?;
    let path = uri.path();
    if !proxy_path_is_safe(path) {
        return Err(GatewayError::new(
            StatusCode::BAD_REQUEST,
            "Companion request path is unsafe",
        ));
    }
    let required = classify_proxy_route(&method, path).ok_or_else(|| {
        core.audit(
            "proxy_denied",
            json!({"method": method.as_str(), "path": path, "sessionId": session.session_id}),
        );
        GatewayError::new(
            StatusCode::FORBIDDEN,
            "This operation is not available to the companion app",
        )
    })?;
    ensure_capability(&session.capabilities, required)?;
    if body.len() > MAX_REQUEST_BYTES {
        return Err(GatewayError::new(
            StatusCode::PAYLOAD_TOO_LARGE,
            "Companion request is too large",
        ));
    }
    let path_and_query = uri
        .path_and_query()
        .map(|value| value.as_str())
        .unwrap_or(path);
    let target = format!("http://127.0.0.1:{}{path_and_query}", core.backend_port);
    let mut request = core
        .backend_client
        .request(method.clone(), target)
        .header("X-Gann-Astro-Token", &core.backend_token)
        .header(header::ACCEPT, "application/json");
    if !body.is_empty() {
        request = request
            .header(header::CONTENT_TYPE, "application/json")
            .body(body);
    }
    let response = request.send().await.map_err(|error| {
        GatewayError::new(
            StatusCode::BAD_GATEWAY,
            format!("Private backend request failed: {error}"),
        )
    })?;
    if response
        .content_length()
        .is_some_and(|length| length > MAX_RESPONSE_BYTES as u64)
    {
        return Err(GatewayError::new(
            StatusCode::BAD_GATEWAY,
            "Private backend response exceeded the companion limit",
        ));
    }
    let status = response.status();
    let payload = response.bytes().await.map_err(|error| {
        GatewayError::new(
            StatusCode::BAD_GATEWAY,
            format!("Unable to read private backend response: {error}"),
        )
    })?;
    if payload.len() > MAX_RESPONSE_BYTES {
        return Err(GatewayError::new(
            StatusCode::BAD_GATEWAY,
            "Private backend response exceeded the companion limit",
        ));
    }
    Ok((
        status,
        [
            (header::CONTENT_TYPE, "application/json"),
            (header::CACHE_CONTROL, "no-store"),
        ],
        payload,
    )
        .into_response())
}

fn classify_proxy_route(method: &Method, path: &str) -> Option<RequiredCapability> {
    if path.contains("/orders")
        || path.contains("/trade")
        || path.contains("/execution")
        || path.ends_with("/activate")
        || path.contains("history-snapshots")
        || path.starts_with("/api/generation")
        || path.starts_with("/api/prospective-refresh")
        || path.ends_with("/scan")
    {
        return None;
    }
    if path.starts_with("/codex-api/") || path.starts_with("/api/codex/") {
        return match method {
            &Method::GET | &Method::POST => Some(RequiredCapability::CodexBridge),
            _ => None,
        };
    }
    if path == "/api/snapshots" && method == Method::POST {
        return Some(RequiredCapability::CodexBridge);
    }
    if path.starts_with("/api/local-jyotish/")
        || path.starts_with("/api/local-candlestick/")
        || path.starts_with("/api/rsi/")
        || path.starts_with("/api/market-synthesis/")
        || path.starts_with("/api/chakra-lab/")
    {
        return match method {
            &Method::GET | &Method::POST => Some(RequiredCapability::AiDrafts),
            _ => None,
        };
    }
    if path == "/api/annotations"
        || path.starts_with("/api/annotations/")
        || path.starts_with("/api/chart-layouts")
        || path.starts_with("/api/drawing-templates")
        || path.starts_with("/api/parameter-profiles")
        || path == "/api/workspace-preferences"
        || (path.starts_with("/api/events/") && path.ends_with("/review"))
        || path == "/api/runtime-diagnostics/frontend"
    {
        return match method {
            &Method::GET => Some(RequiredCapability::ChartRead),
            &Method::POST | &Method::PUT | &Method::DELETE => Some(RequiredCapability::ReviewWrite),
            _ => None,
        };
    }
    let chart_read = path == "/api/chart"
        || path == "/api/parameters/schema"
        || path == "/api/data-artifacts"
        || path == "/api/mt5/status"
        || path == "/api/price-sources"
        || path == "/api/shadow-ledger"
        || path == "/api/candlestick-shadow"
        || path == "/api/runtime-diagnostics"
        || path == "/api/companion/capabilities"
        || path.starts_with("/api/families/")
        || path.starts_with("/api/events/")
        || path.starts_with("/api/chart-layouts/");
    if chart_read && method == Method::GET {
        return Some(RequiredCapability::ChartRead);
    }
    if path == "/api/decisions" && method == Method::POST {
        return Some(RequiredCapability::ChartRead);
    }
    None
}

fn proxy_path_is_safe(path: &str) -> bool {
    let lowercase = path.to_ascii_lowercase();
    path.starts_with('/')
        && !path.starts_with("//")
        && !path.contains('\\')
        && !lowercase.contains("%2e")
        && !lowercase.contains("%2f")
        && !lowercase.contains("%5c")
        && !path.split('/').any(|segment| matches!(segment, "." | ".."))
}

fn ensure_capability(
    capabilities: &CompanionCapabilities,
    required: RequiredCapability,
) -> Result<(), GatewayError> {
    let allowed = match required {
        RequiredCapability::ChartRead => capabilities.chart_read,
        RequiredCapability::ReviewWrite => capabilities.review_write,
        RequiredCapability::AiDrafts => capabilities.ai_drafts,
        RequiredCapability::CodexBridge => capabilities.codex_bridge,
    };
    if allowed && !capabilities.execution_allowed {
        Ok(())
    } else {
        Err(GatewayError::new(
            StatusCode::FORBIDDEN,
            "Companion capability is unavailable",
        ))
    }
}

async fn companion_stream(
    State(core): State<Arc<GatewayCore>>,
    ConnectInfo(remote): ConnectInfo<SocketAddr>,
    headers: HeaderMap,
    websocket: WebSocketUpgrade,
) -> Result<Response, GatewayError> {
    let session = core.authenticate(&headers, remote)?;
    ensure_capability(&session.capabilities, RequiredCapability::ChartRead)?;
    let receiver = core.stream_tx.subscribe();
    let session_id = session.session_id.clone();
    let expires_in = session
        .expires_at
        .duration_since(SystemTime::now())
        .unwrap_or_default();
    core.audit(
        "stream_connected",
        json!({"sessionId": session_id, "remote": remote.to_string()}),
    );
    Ok(websocket
        .protocols(["gann-astro-stream-v1"])
        .max_message_size(64 * 1024)
        .max_frame_size(64 * 1024)
        .on_upgrade(move |socket| stream_socket(core, session_id, socket, receiver, expires_in))
        .into_response())
}

async fn stream_socket(
    core: Arc<GatewayCore>,
    session_id: String,
    mut socket: WebSocket,
    mut receiver: broadcast::Receiver<String>,
    expires_in: Duration,
) {
    let hello = json!({
        "contract": STREAM_CONTRACT,
        "kind": "stream_ready",
        "atUtc": now_rfc3339(),
        "executionAllowed": false,
    })
    .to_string();
    if socket.send(Message::Text(hello.into())).await.is_err() {
        return;
    }
    let expiry = tokio::time::sleep(expires_in);
    tokio::pin!(expiry);
    loop {
        tokio::select! {
            _ = &mut expiry => break,
            broadcast = receiver.recv() => {
                if !core.session_is_active(&session_id) {
                    break;
                }
                let payload = match broadcast {
                    Ok(payload) => payload,
                    Err(broadcast::error::RecvError::Lagged(skipped)) => json!({
                        "contract": STREAM_CONTRACT,
                        "kind": "stream_resync_required",
                        "skipped": skipped,
                        "atUtc": now_rfc3339(),
                        "executionAllowed": false,
                    }).to_string(),
                    Err(broadcast::error::RecvError::Closed) => break,
                };
                match tokio::time::timeout(Duration::from_secs(5), socket.send(Message::Text(payload.into()))).await {
                    Ok(Ok(())) => {}
                    _ => break,
                }
            }
            inbound = socket.next() => {
                match inbound {
                    Some(Ok(Message::Ping(value))) => {
                        if socket.send(Message::Pong(value)).await.is_err() { break; }
                    }
                    Some(Ok(Message::Close(_))) | None | Some(Err(_)) => break,
                    Some(Ok(_)) => {}
                }
            }
        }
    }
    core.audit("stream_disconnected", json!({"sessionId": session_id}));
}

fn spawn_stream_publisher(core: Arc<GatewayCore>) {
    tauri::async_runtime::spawn(async move {
        let mut interval = tokio::time::interval(Duration::from_secs(3));
        loop {
            interval.tick().await;
            let sequence = core.sequence.fetch_add(1, Ordering::Relaxed) + 1;
            let target = format!("http://127.0.0.1:{}/api/mt5/status", core.backend_port);
            let backend = match core
                .backend_client
                .get(target)
                .header("X-Gann-Astro-Token", &core.backend_token)
                .send()
                .await
            {
                Ok(response) => response.json::<Value>().await.ok(),
                Err(_) => None,
            };
            let payload = json!({
                "contract": STREAM_CONTRACT,
                "kind": "market_status",
                "sequence": sequence,
                "atUtc": now_rfc3339(),
                "payload": backend,
                "executionAllowed": false,
            })
            .to_string();
            let _ = core.stream_tx.send(payload);
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::companion_protocol::{decrypt_session, pairing_proof};
    use http::HeaderValue;
    use rustls::{ClientConfig, RootCertStore};
    use rustls_pki_types::CertificateDer;
    use tokio_tungstenite::{
        connect_async_tls_with_config, tungstenite::client::IntoClientRequest, Connector,
    };

    fn test_core() -> Arc<GatewayCore> {
        let addresses = vec![IpAddr::V4(Ipv4Addr::LOCALHOST)];
        let (certificate_der, _) = generate_certificate(&addresses).unwrap();
        test_core_with_certificate(certificate_der, 9443)
    }

    fn test_core_with_certificate(certificate_der: Vec<u8>, port: u16) -> Arc<GatewayCore> {
        let (stream_tx, _) = broadcast::channel(32);
        Arc::new(GatewayCore {
            urls: vec![format!("https://127.0.0.1:{port}")],
            port,
            certificate_sha256: sha256_hex(&certificate_der),
            certificate_der,
            backend_port: 9,
            backend_token: "private-test-token".to_string(),
            backend_client: reqwest::Client::new(),
            pairing: Mutex::new(None),
            sessions: Mutex::new(HashMap::new()),
            stream_tx,
            sequence: AtomicU64::new(0),
            audit_path: std::env::temp_dir().join(format!(
                "gann-astro-companion-test-{}.jsonl",
                Uuid::new_v4()
            )),
        })
    }

    async fn pair_test_device(
        core: Arc<GatewayCore>,
        remote: SocketAddr,
        requested_capabilities: Vec<String>,
    ) -> EncryptedSession {
        let pairing = core.start_pairing().unwrap();
        let Json(challenge) = pairing_challenge(State(core.clone()), ConnectInfo(remote))
            .await
            .unwrap();
        let salt = decode_url(&challenge.salt).unwrap();
        let server_nonce = decode_url(&challenge.server_nonce).unwrap();
        let keys = derive_pairing_keys(&pairing.pairing_code, &salt, &server_nonce).unwrap();
        let client_nonce = encode_url([7_u8; 24]);
        let device_name = "Test phone".to_string();
        let payload = pairing_proof_payload(
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
            proof: encode_url(pairing_proof(&keys.proof, &payload).unwrap()),
        };
        let Json(response) = pair_device(State(core), ConnectInfo(remote), Json(request))
            .await
            .unwrap();
        decrypt_session(
            &keys.encryption,
            &challenge.challenge_id,
            &device_name,
            &response.envelope.unwrap(),
        )
        .unwrap()
    }

    fn bearer_headers(token: &str) -> HeaderMap {
        let mut headers = HeaderMap::new();
        headers.insert(
            header::AUTHORIZATION,
            format!("Bearer {token}").parse().unwrap(),
        );
        headers
    }

    #[test]
    fn proxy_allowlist_blocks_execution_and_generation_surfaces() {
        assert!(classify_proxy_route(&Method::GET, "/api/chart").is_some());
        assert!(classify_proxy_route(&Method::POST, "/api/annotations").is_some());
        assert!(classify_proxy_route(&Method::POST, "/api/snapshots").is_some());
        assert!(classify_proxy_route(&Method::GET, "/api/companion/capabilities").is_some());
        assert!(classify_proxy_route(&Method::POST, "/api/generation/jobs").is_none());
        assert!(classify_proxy_route(&Method::POST, "/api/mt5/history-snapshots").is_none());
        assert!(classify_proxy_route(&Method::POST, "/api/data-artifacts/a/activate").is_none());
        assert!(classify_proxy_route(&Method::POST, "/api/orders").is_none());
        assert!(!proxy_path_is_safe("/api/events/../orders"));
        assert!(!proxy_path_is_safe("/api/events/%2e%2e/orders"));
        assert!(proxy_path_is_safe("/api/events/case-43"));
    }

    #[test]
    fn generated_certificate_covers_loopback_and_has_stable_fingerprint() {
        let addresses = vec![IpAddr::V4(Ipv4Addr::LOCALHOST)];
        let (certificate, key) = generate_certificate(&addresses).unwrap();
        assert!(certificate.len() > 200);
        assert!(key.len() > 100);
        assert_eq!(sha256_hex(&certificate).len(), 64);
    }

    #[test]
    fn gateway_state_starts_outside_a_tokio_context() {
        crate::companion_protocol::install_crypto_provider().unwrap();
        let data_root = std::env::temp_dir().join(format!(
            "gann-astro-companion-startup-test-{}",
            Uuid::new_v4()
        ));
        let gateway =
            CompanionGatewayState::spawn(9, "private-startup-test-token".to_string(), data_root)
                .unwrap();
        assert!(gateway.info().port > 0);
        gateway.shutdown();
    }

    #[tokio::test]
    async fn pairing_issues_encrypted_least_privilege_session_and_revoke_is_immediate() {
        let core = test_core();
        let remote = SocketAddr::from(([127, 0, 0, 1], 43120));
        let encrypted =
            pair_test_device(core.clone(), remote, vec!["chart_read".to_string()]).await;
        assert!(encrypted.capabilities.chart_read);
        assert!(!encrypted.capabilities.review_write);
        assert!(!encrypted.capabilities.ai_drafts);
        assert!(!encrypted.capabilities.codex_bridge);
        assert!(!encrypted.execution_allowed);

        let status = companion_status(
            State(core.clone()),
            ConnectInfo(remote),
            bearer_headers(&encrypted.access_token),
        )
        .await;
        assert!(status.is_ok());
        assert!(core.session_is_active(&encrypted.session_id));
        assert!(core.revoke(&encrypted.session_id));
        assert!(!core.session_is_active(&encrypted.session_id));

        let denied = companion_status(
            State(core),
            ConnectInfo(remote),
            bearer_headers(&encrypted.access_token),
        )
        .await;
        assert!(matches!(denied, Err(error) if error.status == StatusCode::UNAUTHORIZED));
    }

    #[tokio::test]
    async fn pairing_window_locks_after_five_invalid_proofs() {
        let core = test_core();
        let remote = SocketAddr::from(([127, 0, 0, 1], 43121));
        core.start_pairing().unwrap();
        for _ in 0..MAX_PAIRING_ATTEMPTS {
            let Json(challenge) = pairing_challenge(State(core.clone()), ConnectInfo(remote))
                .await
                .unwrap();
            let request = PairingRequest {
                contract: CLIENT_CONTRACT.to_string(),
                challenge_id: challenge.challenge_id,
                client_nonce: encode_url([3_u8; 24]),
                device_name: "Wrong-code phone".to_string(),
                requested_capabilities: vec!["chart_read".to_string()],
                execution_requested: false,
                proof: encode_url([0_u8; 32]),
            };
            let result = pair_device(State(core.clone()), ConnectInfo(remote), Json(request)).await;
            assert!(matches!(result, Err(error) if error.status == StatusCode::FORBIDDEN));
        }
        assert!(!core.info().pairing_active);
        let challenge = pairing_challenge(State(core), ConnectInfo(remote)).await;
        assert!(matches!(challenge, Err(error) if error.status == StatusCode::FORBIDDEN));
    }

    #[tokio::test]
    async fn authenticated_session_is_rate_limited() {
        let core = test_core();
        let remote = SocketAddr::from(([127, 0, 0, 1], 43122));
        let encrypted =
            pair_test_device(core.clone(), remote, vec!["chart_read".to_string()]).await;
        let headers = bearer_headers(&encrypted.access_token);
        for _ in 0..MAX_SESSION_REQUESTS_PER_WINDOW {
            assert!(core.authenticate(&headers, remote).is_ok());
        }
        let limited = core.authenticate(&headers, remote);
        assert!(matches!(limited, Err(error) if error.status == StatusCode::TOO_MANY_REQUESTS));
    }

    #[tokio::test(flavor = "multi_thread", worker_threads = 2)]
    async fn real_https_pairing_and_pinned_wss_stream_round_trip() {
        crate::companion_protocol::install_crypto_provider().unwrap();
        let listener = TcpListener::bind((Ipv4Addr::LOCALHOST, 0)).unwrap();
        let port = listener.local_addr().unwrap().port();
        listener.set_nonblocking(true).unwrap();
        let addresses = vec![IpAddr::V4(Ipv4Addr::LOCALHOST)];
        let (certificate_der, private_key_der) = generate_certificate(&addresses).unwrap();
        let core = test_core_with_certificate(certificate_der.clone(), port);
        let tls = RustlsConfig::from_der(vec![certificate_der.clone()], private_key_der)
            .await
            .unwrap();
        let handle = Handle::<SocketAddr>::new();
        let shutdown_handle = handle.clone();
        let router = gateway_router(core.clone());
        let server = axum_server::from_tcp_rustls(listener, tls).unwrap();
        let server_task = tokio::spawn(async move {
            server
                .handle(handle)
                .serve(router.into_make_service_with_connect_info::<SocketAddr>())
                .await
        });

        let pairing = core.start_pairing().unwrap();
        let base_url = format!("https://127.0.0.1:{port}");
        let bootstrap = reqwest::Client::builder()
            .danger_accept_invalid_certs(true)
            .redirect(reqwest::redirect::Policy::none())
            .build()
            .unwrap();
        let challenge = bootstrap
            .get(format!("{base_url}/companion/v1/pair/challenge"))
            .send()
            .await
            .unwrap()
            .json::<PairingChallenge>()
            .await
            .unwrap();
        let salt = decode_url(&challenge.salt).unwrap();
        let server_nonce = decode_url(&challenge.server_nonce).unwrap();
        let keys = derive_pairing_keys(&pairing.pairing_code, &salt, &server_nonce).unwrap();
        let client_nonce = encode_url([5_u8; 24]);
        let device_name = "TLS test phone".to_string();
        let requested_capabilities = vec!["chart_read".to_string()];
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
            proof: encode_url(pairing_proof(&keys.proof, &proof_payload).unwrap()),
        };
        let pairing_response = bootstrap
            .post(format!("{base_url}/companion/v1/pair"))
            .json(&request)
            .send()
            .await
            .unwrap()
            .json::<PairingResponse>()
            .await
            .unwrap();
        let encrypted = decrypt_session(
            &keys.encryption,
            &challenge.challenge_id,
            &device_name,
            &pairing_response.envelope.unwrap(),
        )
        .unwrap();
        assert_eq!(sha256_hex(&certificate_der), encrypted.certificate_sha256);

        let pinned_certificate = reqwest::Certificate::from_der(&certificate_der).unwrap();
        let pinned_client = reqwest::Client::builder()
            .tls_built_in_root_certs(false)
            .add_root_certificate(pinned_certificate)
            .build()
            .unwrap();
        let status = pinned_client
            .get(format!("{base_url}/companion/v1/status"))
            .bearer_auth(&encrypted.access_token)
            .send()
            .await
            .unwrap();
        assert_eq!(status.status(), StatusCode::OK);

        let mut roots = RootCertStore::empty();
        roots.add(CertificateDer::from(certificate_der)).unwrap();
        let tls_client = ClientConfig::builder()
            .with_root_certificates(roots)
            .with_no_client_auth();
        let mut websocket_request = format!("wss://127.0.0.1:{port}/companion/v1/stream")
            .into_client_request()
            .unwrap();
        websocket_request.headers_mut().insert(
            header::AUTHORIZATION,
            HeaderValue::from_str(&format!("Bearer {}", encrypted.access_token)).unwrap(),
        );
        websocket_request.headers_mut().insert(
            header::SEC_WEBSOCKET_PROTOCOL,
            HeaderValue::from_static("gann-astro-stream-v1"),
        );
        let (mut socket, response) = connect_async_tls_with_config(
            websocket_request,
            None,
            false,
            Some(Connector::Rustls(Arc::new(tls_client))),
        )
        .await
        .unwrap();
        assert_eq!(response.status(), StatusCode::SWITCHING_PROTOCOLS);
        let hello = socket.next().await.unwrap().unwrap().into_text().unwrap();
        assert!(hello.contains(STREAM_CONTRACT));
        assert!(hello.contains("stream_ready"));

        assert!(core.revoke(&encrypted.session_id));
        let _ = core
            .stream_tx
            .send(json!({"kind": "test_tick"}).to_string());
        let closed = tokio::time::timeout(Duration::from_secs(2), socket.next()).await;
        assert!(closed.is_ok(), "revoked stream did not close promptly");

        shutdown_handle.graceful_shutdown(None);
        let _ = tokio::time::timeout(Duration::from_secs(2), server_task).await;
    }
}
