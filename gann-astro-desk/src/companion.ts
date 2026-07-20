export const COMPANION_CLIENT_CONTRACT = 'GANN_ASTRO_ANDROID_COMPANION_CLIENT_V1' as const
export const COMPANION_SESSION_CONTRACT = 'GANN_ASTRO_COMPANION_SESSION_V1' as const

export type CompanionCapabilities = {
  contract: 'GANN_ASTRO_COMPANION_CAPABILITIES_V1'
  chartRead: boolean
  reviewWrite: boolean
  aiDrafts: boolean
  codexBridge: boolean
  executionAllowed: false
}

export type CompanionSession = {
  contract: typeof COMPANION_SESSION_CONTRACT
  baseUrl: string
  accessToken: string
  expiresAtUtc: string
  executionAllowed: false
  capabilities: CompanionCapabilities
}

let activeSession: CompanionSession | null = null

export function getCompanionSession(): CompanionSession | null {
  return activeSession
}

export function clearCompanionSession(): void {
  activeSession = null
}

export function setCompanionSession(session: CompanionSession): void {
  validateCompanionSession(session)
  activeSession = session
}

export function normalizeCompanionBaseUrl(value: string, allowInsecure = false): string {
  const parsed = new URL(value.trim())
  if (parsed.username || parsed.password || parsed.search || parsed.hash) {
    throw new Error('Server address cannot contain credentials, a query, or a fragment')
  }
  if (parsed.pathname !== '/' && parsed.pathname !== '') {
    throw new Error('Server address must not contain a path')
  }
  if (parsed.protocol !== 'https:' && !(allowInsecure && parsed.protocol === 'http:')) {
    throw new Error('The companion connection requires HTTPS')
  }
  return `${parsed.protocol}//${parsed.host}`
}

export function validateCompanionSession(session: CompanionSession): CompanionSession {
  if (session.contract !== COMPANION_SESSION_CONTRACT) {
    throw new Error(`Unsupported companion session contract: ${String(session.contract)}`)
  }
  normalizeCompanionBaseUrl(session.baseUrl, import.meta.env.DEV)
  if (typeof session.accessToken !== 'string' || session.accessToken.length < 32) {
    throw new Error('Companion session did not provide a valid access token')
  }
  if (!Number.isFinite(Date.parse(session.expiresAtUtc))) {
    throw new Error('Companion session did not provide a valid expiry')
  }
  if (session.executionAllowed || session.capabilities.executionAllowed) {
    throw new Error('Companion session violated the execution lock')
  }
  return session
}

export async function pairCompanion(input: {
  baseUrl: string
  pairingCode: string
  deviceName: string
}): Promise<CompanionSession> {
  const baseUrl = normalizeCompanionBaseUrl(input.baseUrl, import.meta.env.DEV)
  const pairingCode = input.pairingCode.trim()
  const deviceName = input.deviceName.trim()
  if (!/^[A-Z0-9-]{6,20}$/i.test(pairingCode)) {
    throw new Error('Enter the one-time pairing code shown on the laptop')
  }
  if (deviceName.length < 2 || deviceName.length > 64) {
    throw new Error('Device name must be between 2 and 64 characters')
  }

  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 15_000)
  let response: Response
  try {
    response = await fetch(`${baseUrl}/companion/v1/pair`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contract: COMPANION_CLIENT_CONTRACT,
        pairingCode,
        deviceName,
        requestedCapabilities: ['chart_read', 'review_write', 'ai_drafts', 'codex_bridge'],
        executionRequested: false,
      }),
      signal: controller.signal,
    })
  } finally {
    window.clearTimeout(timeout)
  }

  const payload = await response.json() as { ok?: boolean; error?: string; session?: CompanionSession }
  if (!response.ok || !payload.ok || !payload.session) {
    throw new Error(payload.error || `Pairing failed: ${response.status}`)
  }
  const session = validateCompanionSession({ ...payload.session, baseUrl })
  setCompanionSession(session)
  return session
}
