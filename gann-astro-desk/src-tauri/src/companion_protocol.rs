use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use chacha20poly1305::{
    aead::{Aead, KeyInit, Payload},
    ChaCha20Poly1305, Nonce,
};
use hkdf::Hkdf;
use hmac::{Hmac, Mac};
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
#[cfg(any(not(mobile), test))]
use std::time::{Duration, SystemTime};
#[cfg(any(not(mobile), test))]
use time::{format_description::well_known::Rfc3339, OffsetDateTime};

pub const CLIENT_CONTRACT: &str = "GANN_ASTRO_ANDROID_COMPANION_CLIENT_V2";
pub const CHALLENGE_CONTRACT: &str = "GANN_ASTRO_PAIRING_CHALLENGE_V1";
pub const PAIRING_ENVELOPE_CONTRACT: &str = "GANN_ASTRO_PAIRING_ENVELOPE_V1";
pub const SESSION_CONTRACT: &str = "GANN_ASTRO_COMPANION_SESSION_V2";
#[cfg(any(not(mobile), test))]
pub const CAPABILITIES_CONTRACT: &str = "GANN_ASTRO_COMPANION_CAPABILITIES_V2";
#[cfg(any(not(mobile), test))]
pub const STREAM_CONTRACT: &str = "GANN_ASTRO_COMPANION_STREAM_V1";
#[cfg(any(not(mobile), test))]
pub const GATEWAY_CONTRACT: &str = "GANN_ASTRO_RUST_COMPANION_GATEWAY_V1";

const PAIRING_KDF_INFO: &[u8] = b"gann-astro-companion-pairing-v1";
const PAIRING_PROOF_DOMAIN: &[u8] = b"gann-astro-companion-proof-v1";
const PAIRING_ENVELOPE_DOMAIN: &[u8] = b"gann-astro-companion-envelope-v1";

pub fn install_crypto_provider() -> Result<(), String> {
    if rustls::crypto::CryptoProvider::get_default().is_some() {
        return Ok(());
    }
    rustls::crypto::ring::default_provider()
        .install_default()
        .map_err(|_| "Unable to install the Rustls ring crypto provider".to_string())
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "camelCase")]
pub struct CompanionCapabilities {
    pub contract: String,
    pub chart_read: bool,
    pub review_write: bool,
    pub ai_drafts: bool,
    pub codex_bridge: bool,
    pub execution_allowed: bool,
}

impl CompanionCapabilities {
    #[cfg(any(not(mobile), test))]
    pub fn locked_for(requested: &[String]) -> Self {
        let includes = |name: &str| requested.iter().any(|value| value == name);
        Self {
            contract: CAPABILITIES_CONTRACT.to_string(),
            chart_read: includes("chart_read"),
            review_write: includes("review_write"),
            ai_drafts: includes("ai_drafts"),
            codex_bridge: includes("codex_bridge"),
            execution_allowed: false,
        }
    }

    #[cfg(test)]
    pub fn locked() -> Self {
        Self::locked_for(&[
            "chart_read".to_string(),
            "review_write".to_string(),
            "ai_drafts".to_string(),
            "codex_bridge".to_string(),
        ])
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PairingChallenge {
    pub contract: String,
    pub challenge_id: String,
    pub server_nonce: String,
    pub salt: String,
    pub certificate_sha256: String,
    pub expires_at_utc: String,
    pub execution_allowed: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PairingRequest {
    pub contract: String,
    pub challenge_id: String,
    pub client_nonce: String,
    pub device_name: String,
    pub requested_capabilities: Vec<String>,
    pub execution_requested: bool,
    pub proof: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PairingEnvelope {
    pub contract: String,
    pub nonce: String,
    pub ciphertext: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PairingResponse {
    pub ok: bool,
    pub error: Option<String>,
    pub envelope: Option<PairingEnvelope>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct EncryptedSession {
    pub contract: String,
    pub session_id: String,
    pub access_token: String,
    pub expires_at_utc: String,
    pub certificate_der: String,
    pub certificate_sha256: String,
    pub capabilities: CompanionCapabilities,
    pub execution_allowed: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PublicCompanionSession {
    pub contract: String,
    pub session_id: String,
    pub base_url: String,
    pub expires_at_utc: String,
    pub certificate_sha256: String,
    pub transport: String,
    pub capabilities: CompanionCapabilities,
    pub execution_allowed: bool,
}

#[derive(Clone)]
pub struct PairingKeys {
    pub proof: [u8; 32],
    pub encryption: [u8; 32],
}

pub fn random_bytes<const N: usize>() -> Result<[u8; N], String> {
    let mut output = [0_u8; N];
    getrandom::fill(&mut output)
        .map_err(|error| format!("Secure random source failed: {error}"))?;
    Ok(output)
}

#[cfg(any(not(mobile), test))]
pub fn random_url_token<const N: usize>() -> Result<String, String> {
    Ok(URL_SAFE_NO_PAD.encode(random_bytes::<N>()?))
}

#[cfg(any(not(mobile), test))]
pub fn random_pairing_code() -> Result<String, String> {
    const ALPHABET: &[u8; 32] = b"ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
    let bytes = random_bytes::<12>()?;
    let symbols = bytes
        .iter()
        .map(|value| ALPHABET[usize::from(*value & 31)] as char)
        .collect::<Vec<_>>();
    Ok(symbols
        .chunks(4)
        .map(|chunk| chunk.iter().collect::<String>())
        .collect::<Vec<_>>()
        .join("-"))
}

pub fn normalize_pairing_code(value: &str) -> Result<String, String> {
    let normalized = value
        .chars()
        .filter(|character| *character != '-')
        .map(|character| character.to_ascii_uppercase())
        .collect::<String>();
    if normalized.len() != 12
        || !normalized
            .bytes()
            .all(|value| matches!(value, b'A'..=b'H' | b'J'..=b'N' | b'P'..=b'Z' | b'2'..=b'9'))
    {
        return Err(
            "Pairing code must contain the three four-character groups shown on the laptop"
                .to_string(),
        );
    }
    Ok(normalized)
}

pub fn derive_pairing_keys(
    code: &str,
    salt: &[u8],
    server_nonce: &[u8],
) -> Result<PairingKeys, String> {
    let code = normalize_pairing_code(code)?;
    let mut hkdf_salt = Vec::with_capacity(salt.len() + server_nonce.len());
    hkdf_salt.extend_from_slice(salt);
    hkdf_salt.extend_from_slice(server_nonce);
    let hkdf = Hkdf::<Sha256>::new(Some(&hkdf_salt), code.as_bytes());
    let mut material = [0_u8; 64];
    hkdf.expand(PAIRING_KDF_INFO, &mut material)
        .map_err(|_| "Unable to derive pairing keys".to_string())?;
    let mut proof = [0_u8; 32];
    let mut encryption = [0_u8; 32];
    proof.copy_from_slice(&material[..32]);
    encryption.copy_from_slice(&material[32..]);
    material.fill(0);
    Ok(PairingKeys { proof, encryption })
}

fn append_field(output: &mut Vec<u8>, value: &[u8]) {
    let length = u32::try_from(value.len()).unwrap_or(u32::MAX);
    output.extend_from_slice(&length.to_be_bytes());
    output.extend_from_slice(value);
}

pub fn pairing_proof_payload(
    challenge_id: &str,
    server_nonce: &str,
    client_nonce: &str,
    certificate_sha256: &str,
    device_name: &str,
    requested_capabilities: &[String],
    execution_requested: bool,
) -> Vec<u8> {
    let mut capabilities = requested_capabilities.to_vec();
    capabilities.sort();
    capabilities.dedup();
    let mut output = Vec::new();
    append_field(&mut output, PAIRING_PROOF_DOMAIN);
    append_field(&mut output, challenge_id.as_bytes());
    append_field(&mut output, server_nonce.as_bytes());
    append_field(&mut output, client_nonce.as_bytes());
    append_field(&mut output, certificate_sha256.as_bytes());
    append_field(&mut output, device_name.as_bytes());
    append_field(&mut output, capabilities.join(",").as_bytes());
    append_field(&mut output, &[u8::from(execution_requested)]);
    output
}

#[cfg(any(mobile, test))]
pub fn pairing_proof(key: &[u8; 32], payload: &[u8]) -> Result<Vec<u8>, String> {
    let mut mac = <Hmac<Sha256> as Mac>::new_from_slice(key)
        .map_err(|_| "Unable to initialize pairing proof".to_string())?;
    mac.update(payload);
    Ok(mac.finalize().into_bytes().to_vec())
}

#[cfg(any(not(mobile), test))]
pub fn verify_pairing_proof(key: &[u8; 32], payload: &[u8], proof: &[u8]) -> Result<(), String> {
    let mut mac = <Hmac<Sha256> as Mac>::new_from_slice(key)
        .map_err(|_| "Unable to initialize pairing proof".to_string())?;
    mac.update(payload);
    mac.verify_slice(proof)
        .map_err(|_| "Pairing proof was rejected".to_string())
}

fn envelope_aad(challenge_id: &str, device_name: &str) -> Vec<u8> {
    let mut output = Vec::new();
    append_field(&mut output, PAIRING_ENVELOPE_DOMAIN);
    append_field(&mut output, challenge_id.as_bytes());
    append_field(&mut output, device_name.as_bytes());
    output
}

#[cfg(any(not(mobile), test))]
pub fn encrypt_session(
    key: &[u8; 32],
    challenge_id: &str,
    device_name: &str,
    session: &EncryptedSession,
) -> Result<PairingEnvelope, String> {
    let cipher = ChaCha20Poly1305::new_from_slice(key)
        .map_err(|_| "Unable to initialize the pairing envelope".to_string())?;
    let nonce = random_bytes::<12>()?;
    let plaintext = serde_json::to_vec(session)
        .map_err(|error| format!("Unable to encode the pairing session: {error}"))?;
    let ciphertext = cipher
        .encrypt(
            Nonce::from_slice(&nonce),
            Payload {
                msg: &plaintext,
                aad: &envelope_aad(challenge_id, device_name),
            },
        )
        .map_err(|_| "Unable to encrypt the pairing session".to_string())?;
    Ok(PairingEnvelope {
        contract: PAIRING_ENVELOPE_CONTRACT.to_string(),
        nonce: URL_SAFE_NO_PAD.encode(nonce),
        ciphertext: URL_SAFE_NO_PAD.encode(ciphertext),
    })
}

#[cfg(any(mobile, test))]
pub fn decrypt_session(
    key: &[u8; 32],
    challenge_id: &str,
    device_name: &str,
    envelope: &PairingEnvelope,
) -> Result<EncryptedSession, String> {
    if envelope.contract != PAIRING_ENVELOPE_CONTRACT {
        return Err(format!(
            "Unsupported pairing envelope: {}",
            envelope.contract
        ));
    }
    let nonce = decode_url(&envelope.nonce)?;
    if nonce.len() != 12 {
        return Err("Pairing envelope nonce has the wrong length".to_string());
    }
    let ciphertext = decode_url(&envelope.ciphertext)?;
    let cipher = ChaCha20Poly1305::new_from_slice(key)
        .map_err(|_| "Unable to initialize the pairing envelope".to_string())?;
    let plaintext = cipher
        .decrypt(
            Nonce::from_slice(&nonce),
            Payload {
                msg: &ciphertext,
                aad: &envelope_aad(challenge_id, device_name),
            },
        )
        .map_err(|_| "Pairing response authentication failed".to_string())?;
    serde_json::from_slice(&plaintext)
        .map_err(|error| format!("Pairing response is invalid: {error}"))
}

pub fn decode_url(value: &str) -> Result<Vec<u8>, String> {
    URL_SAFE_NO_PAD
        .decode(value)
        .map_err(|error| format!("Invalid base64url value: {error}"))
}

pub fn encode_url(value: impl AsRef<[u8]>) -> String {
    URL_SAFE_NO_PAD.encode(value)
}

pub fn sha256(value: impl AsRef<[u8]>) -> [u8; 32] {
    Sha256::digest(value.as_ref()).into()
}

pub fn sha256_hex(value: impl AsRef<[u8]>) -> String {
    sha256(value)
        .iter()
        .map(|byte| format!("{byte:02X}"))
        .collect::<String>()
}

#[cfg(any(not(mobile), test))]
pub fn rfc3339_after(duration: Duration) -> String {
    let at = SystemTime::now()
        .checked_add(duration)
        .unwrap_or(SystemTime::now());
    let datetime = OffsetDateTime::from(at);
    datetime
        .format(&Rfc3339)
        .unwrap_or_else(|_| datetime.unix_timestamp().to_string())
}

#[cfg(any(not(mobile), test))]
pub fn now_rfc3339() -> String {
    OffsetDateTime::now_utc()
        .format(&Rfc3339)
        .unwrap_or_else(|_| OffsetDateTime::now_utc().unix_timestamp().to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pairing_code_normalization_rejects_ambiguous_or_short_codes() {
        assert_eq!(
            normalize_pairing_code("ABCD-EFGH-JK23").unwrap(),
            "ABCDEFGHJK23"
        );
        assert!(normalize_pairing_code("ABCD-EFGH-IJKL").is_err());
        assert!(normalize_pairing_code("ABCD").is_err());
    }

    #[test]
    fn proof_and_envelope_round_trip_and_detect_tampering() {
        let salt = [4_u8; 16];
        let server_nonce = [8_u8; 24];
        let keys = derive_pairing_keys("ABCD-EFGH-JK23", &salt, &server_nonce).unwrap();
        let capabilities = vec!["chart_read".to_string(), "review_write".to_string()];
        let payload = pairing_proof_payload(
            "challenge",
            "server",
            "client",
            "AA11",
            "Phone",
            &capabilities,
            false,
        );
        let proof = pairing_proof(&keys.proof, &payload).unwrap();
        verify_pairing_proof(&keys.proof, &payload, &proof).unwrap();

        let session = EncryptedSession {
            contract: SESSION_CONTRACT.to_string(),
            session_id: "session".to_string(),
            access_token: "token".repeat(8),
            expires_at_utc: "2030-01-01T00:00:00Z".to_string(),
            certificate_der: encode_url(b"certificate"),
            certificate_sha256: sha256_hex(b"certificate"),
            capabilities: CompanionCapabilities::locked(),
            execution_allowed: false,
        };
        let envelope = encrypt_session(&keys.encryption, "challenge", "Phone", &session).unwrap();
        let opened = decrypt_session(&keys.encryption, "challenge", "Phone", &envelope).unwrap();
        assert_eq!(opened.session_id, "session");

        let mut tampered = envelope;
        tampered.ciphertext.push('A');
        assert!(decrypt_session(&keys.encryption, "challenge", "Phone", &tampered).is_err());
    }
}
