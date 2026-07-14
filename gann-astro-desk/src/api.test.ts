// @vitest-environment jsdom

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { invokeMock } = vi.hoisted(() => ({ invokeMock: vi.fn() }))

vi.mock('@tauri-apps/api/core', () => ({ invoke: invokeMock }))

describe('Tauri backend transport', () => {
  beforeEach(() => {
    vi.resetModules()
    invokeMock.mockReset()
    Object.defineProperty(window, '__TAURI_INTERNALS__', {
      value: {},
      configurable: true,
    })
  })

  afterEach(() => {
    Reflect.deleteProperty(window, '__TAURI_INTERNALS__')
    vi.unstubAllGlobals()
  })

  it('routes API requests to the managed private loopback sidecar', async () => {
    invokeMock.mockResolvedValue({
      contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
      baseUrl: 'http://127.0.0.1:53123',
      port: 53123,
      pid: 44,
      status: 'ready',
      executionAllowed: false,
    })
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ ok: true, schema: { symbolOptions: ['USDJPY'] } }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const { fetchParameterSchema } = await import('./api')
    await fetchParameterSchema()

    expect(invokeMock).toHaveBeenCalledWith('backend_runtime')
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:53123/api/parameters/schema',
      expect.any(Object),
    )
  })

  it('refuses a runtime that claims execution permission', async () => {
    invokeMock.mockResolvedValue({
      contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
      baseUrl: 'http://127.0.0.1:53123',
      port: 53123,
      pid: 44,
      status: 'ready',
      executionAllowed: true,
    })
    vi.stubGlobal('fetch', vi.fn())

    const { fetchParameterSchema } = await import('./api')
    await expect(fetchParameterSchema()).rejects.toThrow('read-only execution lock')
  })
})
