// @vitest-environment jsdom

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type {
  ChakraAuditPackageRequest,
  ChakraLabAuditRequest,
  ChakraLabRequest,
} from './types'

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
      apiToken: 'private-test-token',
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
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-Gann-Astro-Token': 'private-test-token',
        }),
      }),
    )
  })

  it('refuses a runtime that claims execution permission', async () => {
    invokeMock.mockResolvedValue({
      contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
      baseUrl: 'http://127.0.0.1:53123',
      apiToken: 'private-test-token',
      port: 53123,
      pid: 44,
      status: 'ready',
      executionAllowed: true,
    })
    vi.stubGlobal('fetch', vi.fn())

    const { fetchParameterSchema } = await import('./api')
    await expect(fetchParameterSchema()).rejects.toThrow('read-only execution lock')
  })

  it('uses native IPC for Chakra Lab without exposing the private backend port', async () => {
    invokeMock.mockResolvedValue({
      ok: true,
      snapshot: {
        guardrails: {
          execution_allowed: false,
        },
      },
    })
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    const request: ChakraLabRequest = {
      at: '2026-07-17T12:00:00+05:30',
      timezone: 'Asia/Kolkata',
      latitude: 18.5204,
      longitude: 73.8567,
      altitudeM: 0,
      bodies: ['SUN'],
      actors: [{ body: 'SUN', dignity: 'ORDINARY' }],
      foundationProfileId: 'sbc_raman_foundation_v1',
      gridProfileId: 'sbc_81_rotation_normalized_partial_v1',
      vedhaProfileId: 'phaladeepika_editor_vedha_guidance_v1',
      vowels: [],
      nameInitials: [],
    }

    const { fetchChakraLabSnapshot } = await import('./api')
    const snapshot = await fetchChakraLabSnapshot(request)

    expect(invokeMock).toHaveBeenCalledWith('chakra_lab_snapshot', { request })
    expect(fetchMock).not.toHaveBeenCalled()
    expect(snapshot.guardrails.execution_allowed).toBe(false)
  })

  it('uses native IPC for the linked Chakra audit and preserves its locks', async () => {
    invokeMock.mockResolvedValue({
      ok: true,
      audit: {
        guardrails: {
          execution_allowed: false,
        },
      },
    })
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    const request: ChakraLabAuditRequest = {
      instrumentIdentity: 'FX:USDJPY',
      terminalEnd: '2026-07-17T13:00:00+05:30',
      boundaries: [{
        reason: 'review start',
        request: {
          at: '2026-07-17T12:00:00+05:30',
          timezone: 'Asia/Kolkata',
          latitude: 18.5204,
          longitude: 73.8567,
          altitudeM: 0,
          bodies: ['SUN'],
          actors: [{ body: 'SUN', dignity: 'ORDINARY' }],
          foundationProfileId: 'sbc_raman_foundation_v1',
          gridProfileId: 'sbc_81_rotation_normalized_partial_v1',
          vedhaProfileId: 'phaladeepika_editor_vedha_guidance_v1',
          vowels: [],
          nameInitials: [],
        },
      }],
    }

    const { fetchChakraLabAudit } = await import('./api')
    const audit = await fetchChakraLabAudit(request)

    expect(invokeMock).toHaveBeenCalledWith('chakra_lab_audit', { request })
    expect(fetchMock).not.toHaveBeenCalled()
    expect(audit.guardrails.execution_allowed).toBe(false)
  })

  it('uses native IPC for sealed audit packages and replay verification', async () => {
    const sealedPackage = {
      package_id: 'package-test',
      guardrails: {
        execution_allowed: false,
      },
    }
    invokeMock
      .mockResolvedValueOnce({
        ok: true,
        package: sealedPackage,
        htmlReport: '<!doctype html>',
      })
      .mockResolvedValueOnce({
        ok: true,
        verification: {
          contract: 'SBC_AUDIT_PACKAGE_VERIFICATION_V1',
          state: 'PASS',
          package_id: 'package-test',
          source_audit_id: 'audit-test',
          structural_hash_match: true,
          source_projection_match: true,
          replay_recipe_match: true,
          replay_audit_match: true,
          replay_package_match: true,
          errors: [],
        },
      })
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    const request = {
      auditRequest: {
        instrumentIdentity: 'FX:USDJPY',
        terminalEnd: '2026-07-17T13:00:00+05:30',
        boundaries: [],
      },
      baselineIntervalId: 'baseline',
      comparisonIntervalIds: ['comparison'],
      bookmarks: [],
      sealedAt: '2026-07-17T13:30:00+05:30',
    } as ChakraAuditPackageRequest

    const {
      buildChakraLabAuditPackage,
      verifyChakraLabAuditPackage,
    } = await import('./api')
    const built = await buildChakraLabAuditPackage(request)
    const verification = await verifyChakraLabAuditPackage(built.package)

    expect(invokeMock).toHaveBeenNthCalledWith(
      1,
      'chakra_lab_audit_package',
      { request },
    )
    expect(invokeMock).toHaveBeenNthCalledWith(
      2,
      'chakra_lab_verify_audit_package',
      { request: { package: sealedPackage } },
    )
    expect(fetchMock).not.toHaveBeenCalled()
    expect(verification.state).toBe('PASS')
  })

  it('rediscovers the runtime after a network failure so Rust can recover the sidecar', async () => {
    vi.useFakeTimers()
    invokeMock.mockResolvedValue({
      contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
      baseUrl: 'http://127.0.0.1:53123',
      apiToken: 'private-test-token',
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
        apiToken: 'private-test-token',
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
        apiToken: 'private-test-token',
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
