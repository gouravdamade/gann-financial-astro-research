export const COMPANION_CLIENT_CONTRACT = 'GANN_ASTRO_ANDROID_COMPANION_CLIENT_V2' as const
export const COMPANION_SESSION_CONTRACT = 'GANN_ASTRO_COMPANION_SESSION_V2' as const

export type CompanionCapabilities = {
  contract: 'GANN_ASTRO_COMPANION_CAPABILITIES_V2'
  chartRead: boolean
  reviewWrite: boolean
  aiDrafts: boolean
  codexBridge: boolean
  executionAllowed: false
}

export type CompanionSession = {
  contract: typeof COMPANION_SESSION_CONTRACT
  sessionId: string
  baseUrl: string
  expiresAtUtc: string
  certificateSha256: string
  transport: 'native_pinned_https_wss'
  capabilities: CompanionCapabilities
  executionAllowed: false
}

export type NativeCompanionResponse = {
  status: number
  payload: unknown
}

let activeSession: CompanionSession | null = null

function isTauriRuntime(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}

export function getCompanionSession(): CompanionSession | null {
  return activeSession
}

export function clearCompanionSession(): void {
  activeSession = null
}

export function formatCompanionError(
  reason: unknown,
  fallback = 'Unable to pair with the laptop',
): string {
  if (reason instanceof Error && reason.message.trim()) return reason.message.trim()
  if (typeof reason === 'string' && reason.trim()) return reason.trim()
  if (reason && typeof reason === 'object' && 'message' in reason) {
    const message = (reason as { message?: unknown }).message
    if (typeof message === 'string' && message.trim()) return message.trim()
  }
  return fallback
}

export function setCompanionSession(session: CompanionSession): void {
  validateCompanionSession(session)
  activeSession = session
}

export function normalizeCompanionBaseUrl(value: string): string {
  const parsed = new URL(value.trim())
  if (parsed.username || parsed.password || parsed.search || parsed.hash) {
    throw new Error('Server address cannot contain credentials, a query, or a fragment')
  }
  if (parsed.pathname !== '/' && parsed.pathname !== '') {
    throw new Error('Server address must not contain a path')
  }
  if (parsed.protocol !== 'https:') {
    throw new Error('The companion connection requires HTTPS')
  }
  return `${parsed.protocol}//${parsed.host}`
}

export function validateCompanionSession(session: CompanionSession): CompanionSession {
  if (session.contract !== COMPANION_SESSION_CONTRACT) {
    throw new Error(`Unsupported companion session contract: ${String(session.contract)}`)
  }
  normalizeCompanionBaseUrl(session.baseUrl)
  if (!session.sessionId || !/^[A-F0-9]{64}$/i.test(session.certificateSha256)) {
    throw new Error('Companion session did not provide a valid identity')
  }
  const expiry = Date.parse(session.expiresAtUtc)
  if (!Number.isFinite(expiry) || expiry <= Date.now()) {
    throw new Error('Companion session is expired')
  }
  if (session.transport !== 'native_pinned_https_wss') {
    throw new Error('Companion session did not enable the pinned native transport')
  }
  if (session.executionAllowed !== false || session.capabilities.executionAllowed !== false) {
    throw new Error('Companion session violated the execution lock')
  }
  return session
}

export async function pairCompanion(input: {
  baseUrl: string
  pairingCode: string
  deviceName: string
}): Promise<CompanionSession> {
  if (!isTauriRuntime()) {
    throw new Error('Secure companion pairing is available only in the native Android app')
  }
  const baseUrl = normalizeCompanionBaseUrl(input.baseUrl)
  const pairingCode = input.pairingCode.trim().toUpperCase()
  const deviceName = input.deviceName.trim()
  if (!/^[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}$/.test(pairingCode)) {
    throw new Error('Enter all three groups from the one-time code shown on the laptop')
  }
  if (deviceName.length < 2 || deviceName.length > 64) {
    throw new Error('Device name must be between 2 and 64 characters')
  }
  const { invoke } = await import('@tauri-apps/api/core')
  const session = await invoke<CompanionSession>('companion_pair', {
    input: { baseUrl, pairingCode, deviceName },
  })
  setCompanionSession(session)
  return session
}

export async function restoreCompanionSession(): Promise<CompanionSession | null> {
  if (!isTauriRuntime()) return null
  const { invoke } = await import('@tauri-apps/api/core')
  const session = await invoke<CompanionSession | null>('companion_session')
  if (session) setCompanionSession(session)
  return session
}

export async function startCompanionStream(): Promise<void> {
  if (!isTauriRuntime() || !activeSession) return
  const { invoke } = await import('@tauri-apps/api/core')
  await invoke('companion_start_stream')
}

export async function disconnectCompanion(): Promise<void> {
  clearCompanionSession()
  if (!isTauriRuntime()) return
  const { invoke } = await import('@tauri-apps/api/core')
  await invoke('companion_disconnect')
}

export async function nativeCompanionRequest(input: {
  path: string
  method: string
  body?: string
}): Promise<NativeCompanionResponse> {
  if (!isTauriRuntime() || !activeSession) {
    throw new Error('The native companion transport is not paired')
  }
  const { invoke } = await import('@tauri-apps/api/core')
  return invoke<NativeCompanionResponse>('companion_request', { input })
}
