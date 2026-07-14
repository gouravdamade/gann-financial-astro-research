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

  it('rediscovers the runtime after a network failure so Rust can recover the sidecar', async () => {
    vi.useFakeTimers()
    invokeMock.mockResolvedValue({
      contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
      baseUrl: 'http://127.0.0.1:53123',
      port: 53123,
      pid: 44,
      status: 'ready',
      executionAllowed: false,
      restartCount: 1,
      recoveryState: 'recovered',
      startedAtUnixMs: 1,
      spawnElapsedMs: 2,
      lastExit: 'exit code: 1',
    })
    const fetchMock = vi.fn()
      .mockRejectedValueOnce(new TypeError('connection reset'))
      .mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({ ok: true, schema: { symbolOptions: ['USDJPY'] } }),
      })
    vi.stubGlobal('fetch', fetchMock)

    const { fetchParameterSchema } = await import('./api')
    const pending = fetchParameterSchema()
    await vi.advanceTimersByTimeAsync(1000)
    await pending

    expect(invokeMock).toHaveBeenCalledTimes(2)
    expect(fetchMock).toHaveBeenCalledTimes(2)
    vi.useRealTimers()
  })

  it('refreshes supervisor state on every diagnostics poll', async () => {
    invokeMock
      .mockResolvedValueOnce({
        contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
        baseUrl: 'http://127.0.0.1:53123',
        port: 53123,
        pid: 44,
        status: 'starting',
        executionAllowed: false,
        restartCount: 1,
        recoveryState: 'recovering',
      })
      .mockResolvedValueOnce({
        contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
        baseUrl: 'http://127.0.0.1:53123',
        port: 53123,
        pid: 45,
        status: 'ready',
        executionAllowed: false,
        restartCount: 1,
        recoveryState: 'recovered',
      })
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        ok: true,
        diagnostics: {
          contract: 'GANN_RUNTIME_DIAGNOSTICS_V1',
          guardrails: { executionAllowed: false },
        },
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const { fetchRuntimeDiagnostics } = await import('./api')
    const first = await fetchRuntimeDiagnostics()
    const second = await fetchRuntimeDiagnostics()

    expect(first.runtime?.recoveryState).toBe('recovering')
    expect(second.runtime?.recoveryState).toBe('recovered')
    expect(invokeMock).toHaveBeenCalledTimes(2)
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })
})
