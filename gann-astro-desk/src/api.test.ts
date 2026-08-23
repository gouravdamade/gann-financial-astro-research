// @vitest-environment jsdom

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type {
  ChakraAuditPackageRequest,
  ChakraLabAuditRequest,
  ChakraLabRequest,
  MultiOscillatorActivityRangeRequest,
  SynchronizedIndependentRangeRequest,
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

  it('uses the managed packaged base for every XE3 startup request', async () => {
    invokeMock.mockResolvedValue({
      contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
      baseUrl: 'http://127.0.0.1:55214',
      apiToken: 'private-test-token',
      port: 55214,
      pid: 44,
      status: 'ready',
      executionAllowed: false,
    })
    const guardrails = {
      executionAllowed: false,
      priceDataRead: false,
      priceOutcomeRead: false,
    }
    const fetchMock = vi.fn().mockImplementation(async (url: string) => {
      const payload = url.endsWith('/workbench')
        ? { ok: true, workbench: { guardrails } }
        : url.endsWith('/signed-ledger')
          ? { ok: true, ledger: { guardrails } }
          : url.endsWith('/transform-preview')
            ? { ok: true, comparison: { guardrails } }
            : { ok: true, preregistration: { guardrails } }
      return {
        ok: true,
        status: 200,
        headers: { get: () => 'application/json' },
        text: async () => JSON.stringify(payload),
      }
    })
    vi.stubGlobal('fetch', fetchMock)

    const {
      fetchXe3OutcomeBlindWorkbench,
      fetchXe3Preregistration,
      fetchXe3SignedLedger,
      fetchXe3TransformPreview,
    } = await import('./api')
    await Promise.all([
      fetchXe3OutcomeBlindWorkbench(),
      fetchXe3SignedLedger(),
      fetchXe3TransformPreview(),
      fetchXe3Preregistration(),
    ])

    const urls = fetchMock.mock.calls.map(([url]) => url)
    expect(urls).toEqual(expect.arrayContaining([
      'http://127.0.0.1:55214/api/experiments/xe3/workbench',
      'http://127.0.0.1:55214/api/experiments/xe3/signed-ledger',
      'http://127.0.0.1:55214/api/experiments/xe3/transform-preview',
      'http://127.0.0.1:55214/api/experiments/xe3/preregistration',
    ]))
    for (const [, init] of fetchMock.mock.calls) {
      expect(init.headers).toEqual(expect.objectContaining({ 'X-Gann-Astro-Token': 'private-test-token' }))
    }
  })

  it('reports response metadata when an API returns HTML instead of JSON', async () => {
    invokeMock.mockResolvedValue({
      contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
      baseUrl: 'http://127.0.0.1:55214',
      apiToken: 'private-test-token',
      port: 55214,
      pid: 44,
      status: 'ready',
      executionAllowed: false,
    })
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      status: 500,
      headers: { get: () => 'text/html; charset=utf-8' },
      text: async () => '<!doctype html><html><title>500 Internal Server Error</title></html>',
    }))

    const { fetchXe3SignedLedger } = await import('./api')
    await expect(fetchXe3SignedLedger()).rejects.toThrow(
      'API returned non-JSON response: HTTP 500, text/html; charset=utf-8',
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

  it('refuses a runtime that omits the execution lock', async () => {
    invokeMock.mockResolvedValue({
      contract: 'GANN_ASTRO_TAURI_PYTHON_SIDECAR_V1',
      baseUrl: 'http://127.0.0.1:53123',
      apiToken: 'private-test-token',
      port: 53123,
      pid: 44,
      status: 'ready',
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

  it('uses native IPC for synchronized independent fields', async () => {
    invokeMock.mockResolvedValue({
      ok: true,
      range: {
        guardrails: {
          executionAllowed: false,
          fieldsFused: false,
          marketDirectionInferred: false,
        },
      },
    })
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    const request = {
      rangeStartUtc: '2026-07-17T06:30:00Z',
      rangeEndUtc: '2026-07-17T08:30:00Z',
      sideIdentities: ['USD', 'JPY'],
      aspectProfileId: 'ASPECT_STRENGTH_V0',
      sbcRange: { instrumentIdentity: 'FX:USDJPY', boundaries: [] },
    } as unknown as SynchronizedIndependentRangeRequest

    const { fetchSynchronizedIndependentRange } = await import('./api')
    await fetchSynchronizedIndependentRange(request)

    expect(invokeMock).toHaveBeenCalledWith(
      'synchronized_independent_range',
      { request },
    )
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('uses native IPC for unsigned multi-oscillator activity and preserves every lock', async () => {
    invokeMock.mockResolvedValue({
      ok: true,
      activity: {
        evidenceMode: 'EXPLORATORY_UNSIGNED',
        contributionContract: 'MO_ACTIVITY_CONTRIBUTION_V1',
        guardrails: {
          readOnly: true,
          unsigned: true,
          nonPredictive: true,
          polarityAssigned: false,
          magnitudeAssigned: false,
          priceDataRead: false,
          priceOutcomeRead: false,
          sbcRead: false,
          llmRead: false,
          executionAllowed: false,
          pairDifferenceComputed: false,
          normalizationUsed: false,
          smoothingUsed: false,
        },
      },
    })
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    const request = {
      rangeStartUtc: '2026-07-17T06:30:00Z',
      rangeEndUtc: '2026-07-17T08:30:00Z',
      sideIdentities: ['USD', 'JPY'],
      aspectProfileId: 'ASPECT_STRENGTH_V0',
    } as MultiOscillatorActivityRangeRequest

    const { fetchMultiOscillatorActivityRange } = await import('./api')
    await fetchMultiOscillatorActivityRange(request)

    expect(invokeMock).toHaveBeenCalledWith('multi_oscillator_activity_range', { request })
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('uses native IPC for the read-only FX side pilot status', async () => {
    invokeMock.mockResolvedValue({
      ok: true,
      status: {
        guardrails: {
          executionAllowed: false,
          createsCatalogueEntry: false,
          marketDirectionInferred: false,
          fieldsFused: false,
        },
      },
    })
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    const { fetchFxSidePilotStatus } = await import('./api')
    await fetchFxSidePilotStatus()

    expect(invokeMock).toHaveBeenCalledWith('fx_side_pilot_status', { request: {} })
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('refuses FX pilot status when any research-only guardrail is absent', async () => {
    invokeMock.mockResolvedValue({
      ok: true,
      status: {
        guardrails: {
          executionAllowed: false,
          createsCatalogueEntry: false,
          marketDirectionInferred: false,
        },
      },
    })
    vi.stubGlobal('fetch', vi.fn())

    const { fetchFxSidePilotStatus } = await import('./api')
    await expect(fetchFxSidePilotStatus()).rejects.toThrow('research-only guardrails')
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

  it('uses native IPC for signed audit catalogs and full replay verification', async () => {
    const sealedPackage = {
      package_id: 'package-test',
      guardrails: { execution_allowed: false },
    }
    const bundle = {
      contract: 'SBC_SIGNED_AUDIT_CATALOG_BUNDLE_V1',
      catalog: {
        catalog_id: 'catalog-test',
        guardrails: { execution_allowed: false },
      },
      signature: { key_id: 'key-test' },
    }
    const verification = {
      contract: 'SBC_AUDIT_CATALOG_VERIFICATION_V1',
      state: 'PASS',
      catalog_id: 'catalog-test',
      key_id: 'key-test',
      catalog_hash_match: true,
      signature_valid: true,
      embedded_packages_valid: true,
      semantic_replay_state: 'PASS',
      entry_count: 1,
      entry_verifications: [],
      errors: [],
    }
    invokeMock
      .mockResolvedValueOnce({
        ok: true,
        bundle,
        verification,
        signingIdentity: {
          algorithm: 'ED25519',
          keyId: 'key-test',
          storage: 'WINDOWS_DPAPI_APP_DATA',
          claim: 'Integrity only.',
        },
      })
      .mockResolvedValueOnce({
        ok: true,
        verification,
      })
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    const {
      buildChakraLabAuditCatalog,
      verifyChakraLabAuditCatalog,
    } = await import('./api')
    const request = {
      packages: [sealedPackage],
      createdAt: '2026-07-17T17:00:00+05:30',
      signedAt: '2026-07-17T17:01:00+05:30',
    }
    const result = await buildChakraLabAuditCatalog(request as never)
    const replayed = await verifyChakraLabAuditCatalog(
      result.bundle,
      true,
    )

    expect(invokeMock).toHaveBeenNthCalledWith(
      1,
      'chakra_lab_audit_catalog',
      { request },
    )
    expect(invokeMock).toHaveBeenNthCalledWith(
      2,
      'chakra_lab_verify_audit_catalog',
      { request: { bundle, fullReplay: true } },
    )
    expect(fetchMock).not.toHaveBeenCalled()
    expect(replayed.semantic_replay_state).toBe('PASS')
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
