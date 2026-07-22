# Android Companion Architecture

## Status

Version 0.10.20 is a release candidate with a native Rust HTTPS/WSS companion
transport. The Windows app keeps Python and MT5 on loopback, exposes only an
explicit research-route allowlist, and opens pairing only when the user requests
it. Android performs the pairing handshake and all later requests in Rust; the
WebView never receives the bearer token or private certificate. Order placement
remains unavailable. Network-level automated tests pass, while physical-device
validation is still required before this candidate is called usable.

## Ownership Boundary

| Capability | Android companion | Windows workstation |
| --- | --- | --- |
| Charts, touch drawings, parameters, review forms | Primary UI and short cache | Authoritative storage and replay |
| MT5 market data | Never connects directly | MetaTrader 5 terminal and normalized snapshots |
| Swiss Ephemeris, Shadbala, Drik, rules | Displays evidence | Computes and versions evidence |
| Astrology and candlestick LLMs | Chat surface and streamed response | Ollama models, RAG, verifier, lesson ledger |
| Codex collaboration | Chat and annotation surface | Codex bridge and workspace access |
| Trade execution | Locked | Locked until separately certified and armed |

## Runtime Contracts

- `GANN_ASTRO_RUNTIME_PROFILE_V1` prevents the Android build from starting the
  packaged Python sidecar.
- `GANN_ASTRO_ANDROID_COMPANION_CLIENT_V2` identifies proof-bound pairing
  requests.
- `GANN_ASTRO_PAIRING_CHALLENGE_V1` and
  `GANN_ASTRO_PAIRING_ENVELOPE_V1` protect the bootstrap handshake.
- `GANN_ASTRO_COMPANION_SESSION_V2` describes a 12-hour, revocable session.
- `GANN_ASTRO_ANDROID_SECURE_SESSION_V1` keeps that session in an encrypted
  Android-native store whose encryption key is protected by Android Keystore.
- `GANN_ASTRO_COMPANION_CAPABILITIES_V2` advertises least-privilege research
  scopes and keeps direct Python exposure disabled.
- `GANN_ASTRO_COMPANION_STREAM_V1` identifies bounded WSS status messages.
- `GANN_ASTRO_RUST_COMPANION_GATEWAY_V1` identifies the Windows gateway.

## Pairing Flow

1. Windows starts a self-signed Rust TLS gateway on LAN and Tailscale interfaces while Python
   remains bound to `127.0.0.1` with its private sidecar token.
2. The user opens Android Companion. Windows displays labeled LAN and Tailscale
   HTTPS addresses, prefers Tailscale when available, and shows a certificate
   fingerprint plus a 12-character code valid for five minutes.
3. Android requests a 90-second challenge. HKDF-SHA256 derives proof and
   encryption keys from the one-time code, challenge salt, and server nonce.
4. Android sends an HMAC proof that binds both nonces, device identity,
   requested scopes, the TLS certificate fingerprint, and `execution=false`.
5. Windows accepts no more than five failed proofs. A successful request receives
   a ChaCha20-Poly1305 envelope containing the certificate and bearer token.
6. Android validates the envelope, pins the certificate in native Rust, verifies
   the authenticated status endpoint, then uses only pinned HTTPS/WSS.
7. The token and pinned certificate remain outside the WebView. Android stores
   their encrypted session envelope through an Android Keystore-backed native
   store, so force-stop or process restart can restore a still-valid session.
   Explicit Disconnect, expiry, gateway rejection, desktop revocation, changed
   certificate, corrupt storage, or any unsafe capability claim erases it and
   returns Android to the pairing screen.

## Private Remote Operation

- Tailscale is the supported away-from-Wi-Fi path. Both devices must be signed
  into the same private tailnet, and Android must not exclude Gann Astro Mobile
  through app-based split tunneling.
- Start Tailscale before Gann Astro Desk. Gateway certificates are generated in
  memory at desktop startup, so the desktop app must be restarted after a new
  Tailscale address first becomes available.
- The desktop panel labels the Tailscale endpoint and selects it by default. A
  LAN endpoint remains available for local fallback.
- Windows Firewall permits this executable on TCP 9443 from `100.64.0.0/10`
  only. No router port forwarding or public-network allow rule is required.
- For a long shift, keep the laptop plugged in and awake, Tailscale running in
  unattended mode, and Gann Astro Desk open. A still-valid protected pairing
  survives an Android force-stop, but expires after 12 hours. Restarting the
  desktop invalidates its in-memory gateway sessions and requires pairing again.
- The Android shell uses viewport safe-area insets on both the pairing screen
  and paired workspace, keeping controls clear of status and navigation bars.

## Gateway Requirements

The implemented gateway provides TLS, pairing expiry, challenge origin binding,
device revocation, exact requested scopes, request/response limits, 240-request
per-minute session limits, bounded WSS delivery, and rotating JSONL audit logs.
Unsafe path encodings and dot-segments are rejected before allowlist matching.
Generation, artifact promotion, scans, MT5 history mutation, and every execution,
order, or trade route are blocked. The gateway never proxies arbitrary URLs or
exposes the Python token to Android.

## Data Channels

- REST snapshots for symbols, chart ranges, event evidence, reviews, settings,
  and saved drawings.
- WebSocket status frames currently carry bounded MT5/market status snapshots
  every three seconds and an explicit resync message if a slow phone falls
  behind. Closed-bar, active-event, and AI token deltas remain later milestones.
- Mutation endpoints use idempotency keys and optimistic version numbers so a
  reconnect cannot duplicate notes or silently overwrite newer desktop work.

## Build

Android SDK, NDK, JDK, Gradle cache, Rust toolchains, and build outputs are kept on
`D:`. Run `packaging/build_tauri_android.ps1`; it regenerates the ignored Tauri
Android wrapper when needed and publishes a debug APK plus manifest under
`D:\GannFinancialAstro\mobile\release_candidate`. The manifest labels the APK a
candidate until installation, pairing, reconnect, and lifecycle tests pass on a
physical phone.

## Next Milestones

1. Run physical-device install, first pair, wrong-code lockout, revoke, secure
   force-stop restore, laptop restart, Wi-Fi loss, sleep/wake, and
   certificate-change tests for the 0.10.20 Android candidate.
2. Add a small connection-state surface and manual reconnect control to the
   paired mobile workspace.
3. Add mobile chart layout and touch-tool adaptations without forking research
   logic.
4. Add an encrypted offline read cache and conflict-safe review synchronization.
5. Extend WSS with timestamp-safe closed bars, active events, and analysis
   progress after the snapshot path is stable on real hardware.
