import { describe, expect, it } from 'vitest'
import {
  companionEndpointLabel,
  companionEndpoints,
  type CompanionGatewayEndpoint,
} from './desktopCompanion'

const lan: CompanionGatewayEndpoint = {
  url: 'https://192.168.1.2:9443',
  address: '192.168.1.2',
  interfaceName: 'Wi-Fi',
  network: 'lan',
  recommended: false,
  remoteAccess: false,
}

const tailscale: CompanionGatewayEndpoint = {
  url: 'https://100.94.12.7:9443',
  address: '100.94.12.7',
  interfaceName: 'Tailscale',
  network: 'tailscale',
  recommended: true,
  remoteAccess: true,
}

describe('desktop companion endpoints', () => {
  it('places the recommended Tailscale endpoint first', () => {
    const endpoints = companionEndpoints({ endpoints: [lan, tailscale], urls: [] })
    expect(endpoints.map((endpoint) => endpoint.network)).toEqual(['tailscale', 'lan'])
    expect(companionEndpointLabel(endpoints[0])).toContain('Tailscale remote')
  })

  it('keeps the original URL contract as a LAN fallback', () => {
    const endpoints = companionEndpoints({
      urls: ['https://192.168.1.2:9443'],
    })
    expect(endpoints).toHaveLength(1)
    expect(endpoints[0]).toMatchObject({ network: 'lan', recommended: true })
  })
})
