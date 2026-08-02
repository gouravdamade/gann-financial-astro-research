import {
  AlertTriangle,
  CircleDot,
  Download,
  Grid3X3,
  Network,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react'
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
} from 'react'
import {
  fetchChartConditionedPolarityLookup,
  fetchChakraLabFixedPhasor,
  fetchChakraLabSnapshot,
  fetchSynchronizedIndependentRange,
} from '../api'
import type {
  ChakraDignityState,
  ChakraFixedPhasorSeries,
  ChakraGridCell,
  ChakraLabRequest,
  ChakraLabSnapshot,
  ChartConditionedPolarityLookup,
  AspectWindow,
  ChakraMotionClass,
  ChartPayload,
  CurrencyPairEvidence,
  SynchronizedIndependentRange,
} from '../types'
import type { InstrumentKeyCandidate } from '../instrumentKeyConverter'
import { InstrumentKeyConverter } from './InstrumentKeyConverter'
import { SbcLinkedAuditWorkspace } from './SbcLinkedAuditWorkspace'
import { ProductFirstSbcWorkspace } from './ProductFirstSbcWorkspace'
import { VISUALIZATION_ENGINE_MODES, visualizationModePolicy, type VisualizationEngineMode } from '../visualizationModes'
import { sourceGapsForVisualizationMode } from '../visualizationSourceGaps'


const BODIES = [
  'SUN',
  'MOON',
  'MARS',
  'MERCURY',
  'JUPITER',
  'VENUS',
  'SATURN',
  'RAHU',
  'KETU',
] as const
const FIXED_BODIES = new Set(['SUN', 'MOON', 'RAHU', 'KETU'])

type Body = (typeof BODIES)[number]
type ActorState = {
  selected: boolean
  motionClass: '' | ChakraMotionClass
  dignity: ChakraDignityState
}

function initialActors(): Record<Body, ActorState> {
  return Object.fromEntries(
    BODIES.map((body) => [
      body,
      {
        selected: true,
        motionClass: '',
        dignity: 'ORDINARY',
      },
    ]),
  ) as Record<Body, ActorState>
}

function currentIstInput(): string {
  return new Date(Date.now() + 330 * 60 * 1000).toISOString().slice(0, 16)
}

function offsetIst(localValue: string): string {
  const seconds = localValue.length === 16 ? ':00' : ''
  return `${localValue}${seconds}+05:30`
}

function oneHourAfter(value: string): string {
  return new Date(Date.parse(value) + 60 * 60 * 1000).toISOString()
}

function istOffsetFromUtc(value: string): string {
  const date = new Date(value)
  return new Date(date.valueOf() + 19_800_000).toISOString().slice(0, 19) + '+05:30'
}

function splitValues(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean)
}

function mergeValue(value: string, token: string): string {
  return [...new Set([...splitValues(value), token])].join(', ')
}

function displayToken(value: string): string {
  return value.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function cellKey(cell: ChakraGridCell): string {
  return `${cell.row}:${cell.column}`
}

type Props = {
  defaultLatitude: number
  defaultLongitude: number
  chart?: ChartPayload | null
  currencyPairEvidence?: CurrencyPairEvidence | null
  selectedAspectLabel?: string | null
  selectedAspect?: AspectWindow | null
}

export function ChakraLabWorkspace({
  defaultLatitude,
  defaultLongitude,
  chart = null,
  currencyPairEvidence = null,
  selectedAspectLabel = null,
  selectedAspect = null,
}: Props) {
  const [atLocal, setAtLocal] = useState(currentIstInput)
  const [latitude, setLatitude] = useState(defaultLatitude)
  const [longitude, setLongitude] = useState(defaultLongitude)
  const [altitudeM, setAltitudeM] = useState(0)
  const [vowels, setVowels] = useState('')
  const [nameInitials, setNameInitials] = useState('')
  const [actors, setActors] = useState(initialActors)
  const [snapshot, setSnapshot] = useState<ChakraLabSnapshot | null>(null)
  const [fixedPhasor, setFixedPhasor] = useState<ChakraFixedPhasorSeries | null>(null)
  const [synchronizedRange, setSynchronizedRange] = useState<SynchronizedIndependentRange | null>(null)
  const [fxSidePolarities, setFxSidePolarities] = useState<Record<'USD' | 'JPY', ChartConditionedPolarityLookup> | null>(null)
  const [selectedCell, setSelectedCell] = useState('5:5')
  const [workspaceMode, setWorkspaceMode] = useState<'WORKSPACE' | 'BOARD' | 'AUDIT'>('WORKSPACE')
  const [visualizationMode, setVisualizationMode] = useState<VisualizationEngineMode>(() => {
    const stored = localStorage.getItem('gann-astro.visualization-mode')
    return VISUALIZATION_ENGINE_MODES.includes(stored as VisualizationEngineMode)
      ? stored as VisualizationEngineMode
      : 'SOURCE_ONLY_BASELINE'
  })
  const [busy, setBusy] = useState(false)
  const [phasorBusy, setPhasorBusy] = useState(false)
  const [phasorError, setPhasorError] = useState('')
  const [synchronizedBusy, setSynchronizedBusy] = useState(false)
  const [synchronizedError, setSynchronizedError] = useState('')
  const [error, setError] = useState('')
  const initialRun = useRef(false)
  const request = useMemo<ChakraLabRequest>(() => ({
    at: offsetIst(atLocal),
    timezone: 'Asia/Kolkata',
    latitude,
    longitude,
    altitudeM,
    bodies: [...BODIES],
    actors: BODIES
      .filter((body) => actors[body].selected)
      .map((body) => ({
        body,
        ...(actors[body].motionClass
          ? { motionClass: actors[body].motionClass as ChakraMotionClass }
          : {}),
        dignity: actors[body].dignity,
      })),
    foundationProfileId: 'sbc_raman_foundation_v1',
    gridProfileId: 'sbc_81_rotation_normalized_partial_v1',
    vedhaProfileId: 'phaladeepika_editor_vedha_guidance_v1',
    vowels: splitValues(vowels),
    nameInitials: splitValues(nameInitials),
  }), [
    actors,
    altitudeM,
    atLocal,
    latitude,
    longitude,
    nameInitials,
    vowels,
  ])

  const loadSnapshot = useCallback(async (atOverride?: string) => {
    setBusy(true)
    setError('')
    try {
      setSnapshot(await fetchChakraLabSnapshot(
        atOverride ? { ...request, at: offsetIst(atOverride) } : request,
      ))
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }, [request])

  const selectMoment = useCallback((at: string) => {
    setAtLocal(at)
    setFixedPhasor(null)
    setPhasorError('')
    void loadSnapshot(at)
  }, [loadSnapshot])

  const loadFixedPhasor = useCallback(async () => {
    setPhasorBusy(true)
    setPhasorError('')
    try {
      const at = request.at
      const result = await fetchChakraLabFixedPhasor({
        instrumentIdentity: `FX:${chart?.symbol ?? 'USDJPY'}`,
        terminalEnd: oneHourAfter(at),
        boundaries: [{
          reason: 'selected product moment',
          request: structuredClone(request),
        }],
      })
      setFixedPhasor(result)
    } catch (caught) {
      setPhasorError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setPhasorBusy(false)
    }
  }, [chart?.symbol, request])

  const loadSynchronizedFields = useCallback(async () => {
    const candles = chart?.candles.slice(-110) ?? []
    if (!candles.length) {
      setSynchronizedRange(null)
      setSynchronizedError('Open this workspace from a loaded chart before loading its visible range.')
      return
    }
    const rangeStartUtc = new Date(candles[0].time * 1000).toISOString()
    const rangeEndUtc = new Date(candles.at(-1)!.time * 1000).toISOString()
    if (Date.parse(rangeEndUtc) <= Date.parse(rangeStartUtc)) {
      setSynchronizedRange(null)
      setSynchronizedError('The rendered chart range must contain at least two distinct timestamps.')
      return
    }
    setSynchronizedBusy(true)
    setSynchronizedError('')
    try {
      const boundaryRequest = {
        ...structuredClone(request),
        at: istOffsetFromUtc(rangeStartUtc),
      }
      const result = await fetchSynchronizedIndependentRange({
        rangeStartUtc,
        rangeEndUtc,
        aspectRanges: [
          {
            sideIdentity: 'USD',
            instrumentIdentity: 'FX_CURRENCY:USD',
            chartId: 'UNCONFIGURED_USD_SIDE_CHART',
            chartHypothesisId: 'PENDING_FOUNDER_REVIEW',
            events: [],
          },
          {
            sideIdentity: 'JPY',
            instrumentIdentity: 'FX_CURRENCY:JPY',
            chartId: 'UNCONFIGURED_JPY_SIDE_CHART',
            chartHypothesisId: 'PENDING_FOUNDER_REVIEW',
            events: [],
          },
        ],
        sbcRange: {
          instrumentIdentity: `FX:${chart?.symbol ?? 'USDJPY'}`,
          boundaries: [{
            reason: 'rendered chart range start',
            request: boundaryRequest,
          }],
        },
      })
      setSynchronizedRange(result)
    } catch (caught) {
      setSynchronizedRange(null)
      setSynchronizedError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setSynchronizedBusy(false)
    }
  }, [chart?.candles, chart?.symbol, request])

  useEffect(() => {
    if (initialRun.current) return
    initialRun.current = true
    void loadSnapshot()
  }, [loadSnapshot])

  useEffect(() => {
    setSynchronizedRange(null)
    setSynchronizedError('')
  }, [chart?.candles, request])

  useEffect(() => {
    let active = true
    void (async () => {
      try {
        const [usd, jpy] = await Promise.all([
          fetchChartConditionedPolarityLookup({ instrumentIdentity: 'FX_CURRENCY:USD' }),
          fetchChartConditionedPolarityLookup({ instrumentIdentity: 'FX_CURRENCY:JPY' }),
        ])
        if (active) setFxSidePolarities({ USD: usd, JPY: jpy })
      } catch (caught) {
        if (active) {
          setFxSidePolarities(null)
          setError(caught instanceof Error ? caught.message : String(caught))
        }
      }
    })()
    return () => { active = false }
  }, [])

  useEffect(() => {
    localStorage.setItem('gann-astro.visualization-mode', visualizationMode)
  }, [visualizationMode])

  const contextKeys = useMemo(() => new Set(
    snapshot?.target_context.flatMap((layer) => (
      layer.values.map((value) => `${layer.layer}:${value}`)
    )) ?? [],
  ), [snapshot])
  const targetCoordinates = useMemo(() => new Set(
    snapshot?.guidance?.actor_resolutions.flatMap((actor) => (
      actor.targets.map((target) => `${target.row}:${target.column}`)
    )) ?? [],
  ), [snapshot])
  const hitCoordinates = useMemo(() => new Set(
    snapshot?.guidance?.contributions.map((item) => (
      `${item.target.row}:${item.target.column}`
    )) ?? [],
  ), [snapshot])
  const selected = snapshot?.grid.cells.find((cell) => cellKey(cell) === selectedCell)
  const guidance = snapshot?.guidance
  const visualizationPolicy = visualizationModePolicy(visualizationMode)
  const visualizationSourceGaps = sourceGapsForVisualizationMode(visualizationMode)
  const resolvedByBody = new Map(
    guidance?.actor_resolutions.map((actor) => [actor.body, actor]) ?? [],
  )

  const updateActor = (body: Body, patch: Partial<ActorState>) => {
    setActors((current) => ({
      ...current,
      [body]: { ...current[body], ...patch },
    }))
  }

  const applyInstrumentKey = (candidate: InstrumentKeyCandidate) => {
    if (candidate.layer === 'VOWEL') {
      setVowels((current) => mergeValue(current, candidate.key))
      return
    }
    setNameInitials((current) => mergeValue(current, candidate.key))
  }

  const exportVisualizationManifest = () => {
    const payload = {
      export_type: 'GANN_ASTRO_VISUALIZATION_STATE_V1',
      generated_at_utc: new Date().toISOString(),
      visualization_mode: visualizationPolicy.mode,
      evidence_status: visualizationPolicy.evidenceStatus,
      approval_state: visualizationPolicy.approvalState,
      classical_completeness_claim: visualizationPolicy.classicalCompletenessClaim,
      calculation_version: 'PFR_C2_VISUALIZATION_STATE_V1',
      profile: visualizationPolicy.calibrationProfile,
      source_gaps: visualizationSourceGaps,
      snapshot_id: snapshot?.snapshot_id ?? null,
      as_of_utc: snapshot?.as_of_utc ?? null,
      evidence_cutoff_utc: snapshot?.evidence_cutoff_utc ?? null,
      request,
      guardrails: visualizationPolicy.guardrails,
      note: 'Experimental visualization state only. Not financially validated. No execution or automatic order placement is permitted.',
    }
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `gann-astro-${visualizationPolicy.mode.toLowerCase()}-${new Date().toISOString().replaceAll(':', '-')}.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <section className="chakra-lab-workspace">
      <div className="chakra-command-strip">
        <div className="chakra-title-block">
          <CircleDot size={17} />
          <div>
            <strong>Sarvatobhadra Chakra</strong>
            <span>Raman sidereal · current-moment context</span>
          </div>
        </div>
        <div className="chakra-mode-switch" role="tablist" aria-label="Chakra workspace mode">
          <button
            role="tab"
            aria-selected={workspaceMode === 'WORKSPACE'}
            className={workspaceMode === 'WORKSPACE' ? 'is-active' : ''}
            onClick={() => setWorkspaceMode('WORKSPACE')}
            title="Integrated SBC analysis workspace"
          >
            <Network size={12} />
            Workspace
          </button>
          <button
            role="tab"
            aria-selected={workspaceMode === 'BOARD'}
            className={workspaceMode === 'BOARD' ? 'is-active' : ''}
            onClick={() => setWorkspaceMode('BOARD')}
            title="Single-moment Chakra board"
          >
            <Grid3X3 size={12} />
            Board
          </button>
          <button
            role="tab"
            aria-selected={workspaceMode === 'AUDIT'}
            className={workspaceMode === 'AUDIT' ? 'is-active' : ''}
            onClick={() => setWorkspaceMode('AUDIT')}
            title="Linked timestamp-safe audit"
          >
            <Network size={12} />
            Audit
          </button>
        </div>
        <div className="visualization-mode-switch" role="tablist" aria-label="Visualization calculation mode">
          {VISUALIZATION_ENGINE_MODES.map((mode) => {
            const policy = visualizationModePolicy(mode)
            return <button
              key={mode}
              role="tab"
              aria-selected={visualizationMode === mode}
              className={visualizationMode === mode ? 'is-active' : ''}
              onClick={() => setVisualizationMode(mode)}
              title={policy.explanation}
            >{policy.shortLabel}</button>
          })}
        </div>
        <span className="visualization-mode-id" title={visualizationPolicy.explanation}>{visualizationPolicy.mode}</span>
        {visualizationPolicy.approvalState === 'FOUNDER_APPROVAL_PENDING' && <span className="visualization-mode-id is-pending">Founder approval pending</span>}
        <span className="chakra-contract-chip"><ShieldCheck size={12} /> Read only</span>
        <span className="chakra-contract-chip">No lookahead</span>
        <span className="chakra-contract-chip is-warning">Not financially validated</span>
        <div className="chakra-command-spacer" />
        {snapshot && (
          <span className="chakra-snapshot-id" title={snapshot.snapshot_id}>
            {snapshot.snapshot_id.slice(0, 12)}
          </span>
        )}
        <button
          className="secondary-command chakra-run-button"
          onClick={() => void loadSnapshot()}
          disabled={busy}
        >
          <RefreshCw size={14} className={busy ? 'is-spinning' : ''} />
          {busy ? 'Calculating' : 'Refresh snapshot'}
        </button>
        <button
          className="secondary-command chakra-run-button"
          onClick={exportVisualizationManifest}
          title="Export this visualization mode, source gaps, timestamp, and safety locks"
        >
          <Download size={14} /> Export state
        </button>
      </div>

      <section className="visualization-mode-status" aria-label="Visualization mode status">
        <div>
          <strong>{visualizationPolicy.label}</strong>
          <span>{visualizationPolicy.explanation}</span>
        </div>
        <div>
          <b>Profile</b>
          <span>{visualizationPolicy.calibrationProfile.profileId}</span>
          <small>{visualizationPolicy.calibrationProfile.status} · {visualizationPolicy.approvalState} · {visualizationPolicy.calibrationProfile.parameterCount} fitted parameters</small>
        </div>
        {visualizationSourceGaps.length > 0 && <details>
          <summary>Source gaps ({visualizationSourceGaps.length})</summary>
          {visualizationSourceGaps.map((gap) => <p key={gap.gapId}><b>{gap.status}</b> · {gap.title}: {gap.explanation}</p>)}
        </details>}
      </section>

      {workspaceMode === 'WORKSPACE' ? (
        <ProductFirstSbcWorkspace
          chart={chart}
          snapshot={snapshot}
          selectedCell={selectedCell}
          onSelectCell={setSelectedCell}
          onSelectMoment={selectMoment}
          currencyPairEvidence={currencyPairEvidence}
            fxSidePolarities={fxSidePolarities}
          selectedAspectLabel={selectedAspectLabel}
          selectedAspect={selectedAspect}
          fixedPhasorInterval={fixedPhasor?.intervals[0] ?? null}
          visualizationPolicy={visualizationPolicy}
          phasorBusy={phasorBusy}
          phasorError={phasorError}
          onLoadFixedPhasor={() => void loadFixedPhasor()}
          synchronizedRange={synchronizedRange}
          synchronizedBusy={synchronizedBusy}
          synchronizedError={synchronizedError}
          onLoadSynchronizedFields={() => void loadSynchronizedFields()}
        />
      ) : workspaceMode === 'BOARD' ? (
      <div className="chakra-lab-body">
        <aside className="chakra-settings-panel">
          <section>
            <div className="chakra-section-heading">
              <strong>Moment</strong>
              <span>IST</span>
            </div>
            <label>
              Timestamp
              <input
                type="datetime-local"
                value={atLocal}
                onChange={(event) => setAtLocal(event.target.value)}
              />
            </label>
            <div className="chakra-coordinate-grid">
              <label>
                Latitude
                <input
                  type="number"
                  step="0.0001"
                  value={latitude}
                  onChange={(event) => setLatitude(Number(event.target.value))}
                />
              </label>
              <label>
                Longitude
                <input
                  type="number"
                  step="0.0001"
                  value={longitude}
                  onChange={(event) => setLongitude(Number(event.target.value))}
                />
              </label>
            </div>
            <label>
              Altitude (m)
              <input
                type="number"
                step="1"
                value={altitudeM}
                onChange={(event) => setAltitudeM(Number(event.target.value))}
              />
            </label>
          </section>

          <section>
            <div className="chakra-section-heading">
              <strong>Context</strong>
              <span>Optional</span>
            </div>
            <label>
              Vowel keys
              <input
                value={vowels}
                placeholder="A, AA"
                onChange={(event) => setVowels(event.target.value)}
              />
            </label>
            <label>
              Name-initial keys
              <input
                value={nameInitials}
                placeholder="KA, RA"
                onChange={(event) => setNameInitials(event.target.value)}
              />
            </label>
            <InstrumentKeyConverter onApply={applyInstrumentKey} />
          </section>

          <section className="chakra-actors-section">
            <div className="chakra-section-heading">
              <strong>Vedha actors</strong>
              <span>Explicit motion</span>
            </div>
            <div className="chakra-actor-header">
              <span />
              <span>Body</span>
              <span>Motion</span>
              <span>Dignity</span>
            </div>
            {BODIES.map((body) => (
              <div className="chakra-actor-row" key={body}>
                <input
                  type="checkbox"
                  checked={actors[body].selected}
                  onChange={(event) => updateActor(body, { selected: event.target.checked })}
                  aria-label={`Include ${body}`}
                />
                <strong>{body}</strong>
                {FIXED_BODIES.has(body) ? (
                  <span className="chakra-fixed-motion">Fixed</span>
                ) : (
                  <select
                    value={actors[body].motionClass}
                    onChange={(event) => updateActor(body, {
                      motionClass: event.target.value as ActorState['motionClass'],
                    })}
                    aria-label={`${body} motion`}
                  >
                    <option value="">Required</option>
                    <option value="DIRECT_SWIFT">Direct / swift</option>
                    <option value="MEAN">Mean</option>
                    <option value="RETROGRADE">Retrograde</option>
                  </select>
                )}
                <select
                  value={actors[body].dignity}
                  onChange={(event) => updateActor(body, {
                    dignity: event.target.value as ChakraDignityState,
                  })}
                  aria-label={`${body} dignity`}
                >
                  <option value="ORDINARY">Ordinary</option>
                  <option value="EXALTED">Exalted</option>
                  <option value="DEBILITATED">Debilitated</option>
                </select>
              </div>
            ))}
          </section>
        </aside>

        <section className="chakra-board-panel">
          {error && (
            <div className="chakra-error-band">
              <AlertTriangle size={14} />
              <span>{error}</span>
            </div>
          )}
          {snapshot ? (
            <>
              <div className="chakra-board-context">
                <div>
                  <strong>{new Date(snapshot.requested_at_local).toLocaleString()}</strong>
                  <span>{snapshot.foundation_snapshot.astronomy_contract}</span>
                </div>
                <div>
                  <strong>{snapshot.foundation_snapshot.panchanga.tithi_name}</strong>
                  <span>
                    {snapshot.foundation_snapshot.panchanga.paksha} · {snapshot.foundation_snapshot.panchanga.vara.weekday}
                  </span>
                </div>
                <div className="chakra-legend">
                  <span><i className="is-context" /> Context</span>
                  <span><i className="is-target" /> Ray</span>
                  <span><i className="is-hit" /> Matched</span>
                </div>
              </div>
              <div className="chakra-grid-viewport">
                <div className="chakra-grid" style={{
                  '--chakra-columns': snapshot.grid.columns,
                  '--chakra-rows': snapshot.grid.rows,
                } as CSSProperties}>
                  {snapshot.grid.cells.map((cell) => {
                    const key = cellKey(cell)
                    const isContext = cell.entries.some((entry) => (
                      contextKeys.has(`${entry.layer}:${entry.value}`)
                    ))
                    const primary = cell.entries.find((entry) => entry.layer === 'NAKSHATRA')
                      ?? cell.entries.find((entry) => entry.layer === 'RASHI')
                      ?? cell.entries[0]
                    return (
                      <button
                        key={key}
                        className={[
                          'chakra-cell',
                          isContext ? 'is-context' : '',
                          targetCoordinates.has(key) ? 'is-target' : '',
                          hitCoordinates.has(key) ? 'is-hit' : '',
                          selectedCell === key ? 'is-selected' : '',
                        ].filter(Boolean).join(' ')}
                        onClick={() => setSelectedCell(key)}
                        title={cell.entries.map((entry) => `${entry.layer}: ${entry.value}`).join('\n')}
                      >
                        <small>{cell.row},{cell.column}</small>
                        {primary ? <strong>{displayToken(primary.value)}</strong> : <strong>·</strong>}
                        <em>{cell.entries.map((entry) => entry.layer.slice(0, 3)).join(' · ')}</em>
                      </button>
                    )
                  })}
                </div>
              </div>
            </>
          ) : (
            <div className="chakra-empty-state">
              <CircleDot size={24} />
              <strong>{busy ? 'Calculating snapshot' : 'Snapshot unavailable'}</strong>
            </div>
          )}
        </section>

        <aside className="chakra-evidence-panel">
          <section className="chakra-score-section">
            <div className="chakra-section-heading">
              <strong>Guidance ledger</strong>
              <span>{guidance?.financial_validation_status ?? 'PENDING'}</span>
            </div>
            {visualizationPolicy.scoringVisible ? <>
            <div className="chakra-score-line">
              <strong>
                {guidance ? `${(guidance.normalized_guidance_score * 100).toFixed(1)}%` : '—'}
              </strong>
              <span>{guidance ? displayToken(guidance.guidance_band) : 'No resolved actors'}</span>
            </div>
            <div className="chakra-score-metrics">
              <div><span>Favorable</span><strong>{guidance?.favorable_guidance_units.toFixed(1) ?? '—'}</strong></div>
              <div><span>Adverse</span><strong>{guidance?.adverse_guidance_units.toFixed(1) ?? '—'}</strong></div>
              <div><span>Net</span><strong>{guidance?.net_guidance_units.toFixed(1) ?? '—'}</strong></div>
              <div><span>Coverage</span><strong>{guidance ? `${(guidance.scoring_coverage_ratio * 100).toFixed(0)}%` : '—'}</strong></div>
            </div>
            </> : <div className="chakra-mode-suppressed-score">
              <strong>{visualizationPolicy.evidenceStatus}</strong>
              <span>{visualizationPolicy.explanation}</span>
              <small>Scores, directions, and execution remain unavailable in this mode.</small>
            </div>}
          </section>

          <section>
            <div className="chakra-section-heading">
              <strong>Actor evidence</strong>
              <span>{snapshot?.actor_readiness.filter((item) => item.status === 'READY').length ?? 0} ready</span>
            </div>
            <div className="chakra-evidence-list">
              {snapshot?.actor_readiness.filter((item) => item.requested).map((item) => {
                const resolution = resolvedByBody.get(item.body)
                return (
                  <div className={`chakra-evidence-row is-${item.status.toLowerCase()}`} key={item.body}>
                    <strong>{item.body}</strong>
                    <span>{displayToken(item.source_nakshatra)}</span>
                    <span>{visualizationPolicy.scoringVisible ? (resolution?.direction ?? displayToken(item.status)) : displayToken(item.status)}</span>
                    <em>{resolution?.nature ?? item.motion_class ?? '—'}</em>
                  </div>
                )
              })}
            </div>
          </section>

          <section>
            <div className="chakra-section-heading">
              <strong>Matched cells</strong>
              <span>{guidance?.matched_target_count ?? 0}</span>
            </div>
            <div className="chakra-contribution-list">
              {guidance?.contributions.length ? guidance.contributions.map((item, index) => (
                <button
                  key={`${item.body}-${item.target.row}-${item.target.column}-${index}`}
                  onClick={() => setSelectedCell(`${item.target.row}:${item.target.column}`)}
                >
                  <strong>{item.body}</strong>
                  <span>{item.target.layer}: {displayToken(item.target.value)}</span>
                  <em>{visualizationPolicy.scoringVisible ? (item.signed_guidance_units?.toFixed(1) ?? 'Unresolved') : displayToken(item.status)}</em>
                </button>
              )) : <span className="chakra-muted-row">No matched target cells</span>}
            </div>
          </section>

          <section>
            <div className="chakra-section-heading">
              <strong>Cell inspector</strong>
              <span>{selectedCell}</span>
            </div>
            <div className="chakra-cell-evidence">
              {selected?.entries.length ? selected.entries.map((entry) => (
                <div key={`${entry.layer}-${entry.value}`}>
                  <span>{displayToken(entry.layer)}</span>
                  <strong>{displayToken(entry.value)}</strong>
                </div>
              )) : <span className="chakra-muted-row">No certified layer in this cell</span>}
            </div>
          </section>
        </aside>
      </div>
      ) : (
        <SbcLinkedAuditWorkspace currentRequest={request} visualizationPolicy={visualizationPolicy} />
      )}
      <footer className="visualization-export-footer">
        <span>{visualizationPolicy.mode}</span>
        <span>{visualizationPolicy.evidenceStatus}</span>
        <span>{visualizationPolicy.approvalState}</span>
        <span>Experimental · not financially validated · execution locked</span>
      </footer>
    </section>
  )
}
