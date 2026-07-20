# Android Companion Architecture

## Status

The first Android artifact is a pairing shell and shared research UI. It does not
yet connect because the authenticated Rust companion gateway is deliberately not
implemented in the Python backend. Order placement remains unavailable.

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
- `GANN_ASTRO_ANDROID_COMPANION_CLIENT_V1` identifies companion requests.
- `GANN_ASTRO_COMPANION_SESSION_V1` describes a short-lived, memory-only session.
- `GANN_ASTRO_COMPANION_CAPABILITIES_V1` advertises the workstation boundary and
  keeps direct Python exposure disabled.

## Pairing Flow

1. Windows starts the future Rust gateway on a private network interface with TLS.
2. The desktop app displays an expiring one-time pairing code and certificate
   fingerprint or trusted local hostname.
3. Android submits the code to `POST /companion/v1/pair` over HTTPS.
4. The gateway returns a short-lived bearer token with read/review/AI scopes and
   no execution scope.
5. The token stays in memory for this milestone. Encrypted Android Keystore
   persistence may be added only after rotation and revoke behavior are tested.

## Gateway Requirements

The gateway must be a small Rust service in front of the loopback-only Python
backend. It must provide TLS, pairing-code expiry, device revocation, per-route
scopes, request-size limits, rate limits, audit records, and WebSocket streaming.
It must never proxy arbitrary URLs or expose the Python token to Android.

## Data Channels

- REST snapshots for symbols, chart ranges, event evidence, reviews, settings,
  and saved drawings.
- WebSocket deltas for live closed bars, active events, analysis progress, and
  streamed AI responses.
- Mutation endpoints use idempotency keys and optimistic version numbers so a
  reconnect cannot duplicate notes or silently overwrite newer desktop work.

## Build

Android SDK, NDK, JDK, Gradle cache, Rust toolchains, and build outputs are kept on
`D:`. Run `packaging/build_tauri_android.ps1`; it regenerates the ignored Tauri
Android wrapper when needed and publishes a debug APK plus manifest under
`D:\GannFinancialAstro\mobile\release_candidate`.

## Next Milestones

1. Implement the disabled-by-default Rust TLS gateway and desktop pairing dialog.
2. Add certificate trust, revoke/rotate, and reconnect tests.
3. Add mobile chart layout and touch-tool adaptations without forking research
   logic.
4. Add offline read cache and conflict-safe review synchronization.
5. Run physical-device screenshot, gesture, reconnect, sleep/wake, and network
   loss tests before calling the companion usable.
