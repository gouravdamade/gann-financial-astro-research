export const COMPANION_GATEWAY_CONTRACT = 'GANN_ASTRO_RUST_COMPANION_GATEWAY_V1' as const

export type CompanionGatewayEndpoint = {
  url: string
  address: string
  interfaceName: string
  network: 'tailscale' | 'lan' | 'loopback'
  recommended: boolean
  remoteAccess: boolean
}

export type CompanionGatewayInfo = {
  contract: typeof COMPANION_GATEWAY_CONTRACT
  status: 'ready'
  urls: string[]
  endpoints?: CompanionGatewayEndpoint[]
  port: number
  certificateSha256: string
  pairingActive: boolean
  pairingExpiresAtUtc: string | null
  pairedSessions: number
  executionAllowed: false
}

export type CompanionPairingWindow = {
  contract: typeof COMPANION_GATEWAY_CONTRACT
  urls: string[]
  endpoints?: CompanionGatewayEndpoint[]
  pairingCode: string
  certificateSha256: string
  expiresAtUtc: string
  executionAllowed: false
}

export function companionEndpoints(
  value: Pick<CompanionGatewayInfo | CompanionPairingWindow, 'endpoints' | 'urls'> | null,
): CompanionGatewayEndpoint[] {
  if (!value) return []
  if (value.endpoints?.length) {
    return [...value.endpoints].sort((left, right) => {
      if (left.recommended !== right.recommended) return left.recommended ? -1 : 1
      return left.url.localeCompare(right.url)
    })
  }
  return value.urls.map((url, index) => ({
    url,
    address: new URL(url).hostname,
    interfaceName: 'Network adapter',
    network: 'lan',
    recommended: index === 0,
    remoteAccess: false,
  }))
}

export function companionEndpointLabel(endpoint: CompanionGatewayEndpoint): string {
  const network = endpoint.network === 'tailscale'
    ? 'Tailscale remote'
    : endpoint.network === 'loopback'
      ? 'This laptop only'
      : 'Local Wi-Fi/LAN'
  return `${network} | ${endpoint.url}`
}

export type CompanionGatewaySession = {
  sessionId: string
  deviceName: string
  createdAtUtc: string
  expiresAtUtc: string
  lastSeenAtUtc: string
  remoteAddress: string
  executionAllowed: false
}

async function invokeNative<T>(command: string, args?: Record<string, unknown>): Promise<T> {
  if (typeof window === 'undefined' || !('__TAURI_INTERNALS__' in window)) {
    throw new Error('Companion gateway controls are available in the Windows app')
  }
  const { invoke } = await import('@tauri-apps/api/core')
  return invoke<T>(command, args)
}

function assertLocked(value: { executionAllowed: boolean }): void {
  if (value.executionAllowed) throw new Error('Companion gateway violated the execution lock')
}

export async function fetchCompanionGateway(): Promise<CompanionGatewayInfo> {
  const gateway = await invokeNative<CompanionGatewayInfo>('companion_gateway_info')
  if (gateway.contract !== COMPANION_GATEWAY_CONTRACT) {
    throw new Error(`Unsupported companion gateway contract: ${gateway.contract}`)
  }
  assertLocked(gateway)
  return gateway
}

export async function openCompanionPairing(): Promise<CompanionPairingWindow> {
  const pairing = await invokeNative<CompanionPairingWindow>('companion_start_pairing')
  if (pairing.contract !== COMPANION_GATEWAY_CONTRACT) {
    throw new Error(`Unsupported companion pairing contract: ${pairing.contract}`)
  }
  assertLocked(pairing)
  return pairing
}

export async function fetchCompanionSessions(): Promise<CompanionGatewaySession[]> {
  const sessions = await invokeNative<CompanionGatewaySession[]>('companion_gateway_sessions')
  sessions.forEach(assertLocked)
  return sessions
}

export async function revokeCompanionSession(sessionId: string): Promise<boolean> {
  return invokeNative<boolean>('companion_revoke_session', { sessionId })
}
