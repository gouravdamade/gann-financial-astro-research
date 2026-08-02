import { CalendarClock, ChevronLeft, ChevronRight, CircleHelp, Download, Grid3X3, Layers3, Orbit, ShieldCheck, SlidersHorizontal } from 'lucide-react'
import { useState, type CSSProperties } from 'react'
import type {
  ChakraFixedPhasorInterval,
  ChakraGridCell,
  ChakraLabSnapshot,
  AspectWindow,
  ChartConditionedPolarityLookup,
  ChartPayload,
  CurrencyPairEvidence,
} from '../types'
import { calculateProductFirstTimingPhase, PROJECT_CONVENTION_TIMING_PHASE_V1 } from '../productFirstTimingPhase'
import type { VisualizationModePolicy } from '../visualizationModes'

const TIMING_PHASE_EXPERIMENT_ENABLED = import.meta.env.VITE_ENABLE_TIMING_PHASE_EXPERIMENT === 'true'

type Props = {
  chart?: ChartPayload | null
  snapshot: ChakraLabSnapshot | null
  selectedCell: string
  onSelectCell: (cell: string) => void
  onSelectMoment: (value: string) => void
  currencyPairEvidence?: CurrencyPairEvidence | null
  fxSidePolarities?: Record<'USD' | 'JPY', ChartConditionedPolarityLookup> | null
  selectedAspectLabel?: string | null
  selectedAspect?: AspectWindow | null
  fixedPhasorInterval?: ChakraFixedPhasorInterval | null
  visualizationPolicy: VisualizationModePolicy
  phasorBusy: boolean
  phasorError: string
  onLoadFixedPhasor: () => void
}

function display(value: string | null | undefined): string {
  if (!value) return 'Unavailable'
  return value.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function cellKey(cell: ChakraGridCell): string {
  return `${cell.row}:${cell.column}`
}

function toIstInput(epochSeconds: number): string {
  return new Date((epochSeconds + 19_800) * 1000).toISOString().slice(0, 16)
}

function momentInput(snapshot: ChakraLabSnapshot | null): string {
  return snapshot?.requested_at_local.slice(0, 16) ?? ''
}

function compactUtc(value: string | null): string {
  if (!value) return 'Unknown'
  const date = new Date(value)
  return Number.isNaN(date.valueOf())
    ? value
    : new Intl.DateTimeFormat('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
      timeZone: 'UTC', timeZoneName: 'short',
    }).format(date)
}

function compactAspectLabel(value: string): string {
  return value.replace('AVG(ALL)', 'AVG').replaceAll('|', ' / ')
}

export function ProductFirstSbcWorkspace({
  chart,
  snapshot,
  selectedCell,
  onSelectCell,
  onSelectMoment,
  currencyPairEvidence = null,
  fxSidePolarities = null,
  selectedAspectLabel = null,
  selectedAspect = null,
  fixedPhasorInterval = null,
  visualizationPolicy,
  phasorBusy,
  phasorError,
  onLoadFixedPhasor,
}: Props) {
  const [sideView, setSideView] = useState<'TIME' | 'PROFILE' | null>(null)
  const [draftMoment, setDraftMoment] = useState('')
  const [wheelOpen, setWheelOpen] = useState(false)
  const [selectedVectorId, setSelectedVectorId] = useState('')
  const [timingOpen, setTimingOpen] = useState(false)
  const [comparisonOpen, setComparisonOpen] = useState(false)
  const guidance = snapshot?.guidance ?? null
  const candles = chart?.candles.slice(-110) ?? []
  const firstTime = candles[0]?.time ?? 0
  const lastTime = candles.at(-1)?.time ?? firstTime + 1
  const rangeSeconds = Math.max(1, lastTime - firstTime)
  const highs = candles.map((candle) => candle.high)
  const lows = candles.map((candle) => candle.low)
  const low = lows.length ? Math.min(...lows) : 0
  const high = highs.length ? Math.max(...highs) : 1
  const priceSpan = Math.max(0.000001, high - low)
  const chartWidth = 1000
  const chartHeight = 440
  const selectedEpoch = snapshot ? Date.parse(snapshot.as_of_utc) / 1000 : lastTime
  const xFor = (epoch: number) => 28 + ((epoch - firstTime) / rangeSeconds) * 944
  const yFor = (price: number) => 28 + ((high - price) / priceSpan) * 360
  const candleWidth = Math.max(2, Math.min(11, 820 / Math.max(candles.length, 1)))
  const visibleAspects = (chart?.aspects ?? []).filter((aspect) => (
    aspect.end >= firstTime && aspect.start <= lastTime
  ))
  const selected = snapshot?.grid.cells.find((cell) => cellKey(cell) === selectedCell)
  const targetCells = new Set(guidance?.contributions.map((item) => (
    `${item.target.row}:${item.target.column}`
  )) ?? [])
  const contextCells = new Set(snapshot?.target_context.flatMap((layer) => (
    layer.values.map((value) => `${layer.layer}:${value}`)
  )) ?? [])
  const readiness = snapshot?.actor_readiness.filter((item) => item.requested) ?? []
  const selectedCandleIndex = candles.length
    ? candles.reduce((closest, candle, index) => (
      Math.abs(candle.time - selectedEpoch) < Math.abs(candles[closest].time - selectedEpoch) ? index : closest
    ), 0)
    : -1
  const unknownCount = readiness.filter((item) => item.status !== 'READY').length
    + (guidance?.contributions.filter((item) => item.signed_guidance_units == null).length ?? 0)
  const supportive = Math.abs(guidance?.favorable_guidance_units ?? 0)
  const obstructive = Math.abs(guidance?.adverse_guidance_units ?? 0)
  const gross = supportive + obstructive
  const conflict = guidance && supportive > 0 && obstructive > 0
    ? 'Mixed support and obstruction'
    : guidance?.adverse_guidance_units
      ? 'Obstruction only'
      : guidance?.favorable_guidance_units
        ? 'Support only'
        : 'No resolved contribution'
  const baseScore = currencyPairEvidence?.base.netUnits ?? null
  const quoteScore = currencyPairEvidence?.quote.netUnits ?? null
  const pairScore = currencyPairEvidence?.pair.netDifferenceUnits ?? null
  const commonActivation = currencyPairEvidence?.pair.commonActivationUnits ?? null
  const jointNetStrength = currencyPairEvidence?.pair.jointNetStrengthUnits ?? null
  const pairConflict = currencyPairEvidence?.pair.conflictRatio ?? null
  const plottedVectors = fixedPhasorInterval?.vectors.filter((vector) => vector.projection_status === 'PLOTTED') ?? []
  const unknownVectors = fixedPhasorInterval?.vectors.filter((vector) => vector.projection_status === 'UNKNOWN_NOT_PLOTTED') ?? []
  const maxVectorMagnitude = Math.max(1, ...plottedVectors.map((vector) => vector.magnitude_units ?? 0))
  const selectedVector = plottedVectors.find((vector) => vector.vector_id === selectedVectorId) ?? plottedVectors[0] ?? null
  const fixedGrossRadius = 24 + Math.min(1, (fixedPhasorInterval?.vector_magnitude_sum_units ?? 0) / (maxVectorMagnitude * 4)) * 88
  const fixedResultantRadius = Math.min(112, Math.abs(fixedPhasorInterval?.vector_real_sum_units ?? 0) / maxVectorMagnitude * 88)
  const fixedResultantPositive = (fixedPhasorInterval?.vector_real_sum_units ?? 0) >= 0
  const fixedNearZero = Boolean(fixedPhasorInterval)
    && Math.abs(fixedPhasorInterval?.vector_real_sum_units ?? 0) <= Math.max(0.25, (fixedPhasorInterval?.vector_magnitude_sum_units ?? 0) * 0.15)
  const fixedZeroVectors = plottedVectors.filter((vector) => vector.fixed_angle === 'ZERO')
  const fixedPiVectors = plottedVectors.filter((vector) => vector.fixed_angle === 'PI')
  const timingExperiment = calculateProductFirstTimingPhase({
    enabled: TIMING_PHASE_EXPERIMENT_ENABLED && visualizationPolicy.allowTimingGeometry,
    snapshot,
    aspects: visibleAspects,
  })
  const unresolvedTiming = snapshot?.guidance?.contributions.filter((contribution) => contribution.signed_guidance_units == null) ?? []
  const formatScalar = (value: number | null | undefined, digits = 2): string => (
    visualizationPolicy.scoringVisible
      ? (value == null ? 'Unknown' : value.toFixed(digits))
      : 'Value suppressed'
  )
  const formatScalarPercent = (value: number | null | undefined, digits = 1): string => (
    visualizationPolicy.scoringVisible
      ? (value == null ? 'Unknown' : `${(value * 100).toFixed(digits)}%`)
      : 'Value suppressed'
  )
  const formatScoreText = (value: string): string => (
    visualizationPolicy.scoringVisible ? value : 'Value suppressed'
  )
  const stepLoadedCandle = (direction: -1 | 1) => {
    const nextIndex = selectedCandleIndex + direction
    if (nextIndex >= 0 && nextIndex < candles.length) onSelectMoment(toIstInput(candles[nextIndex].time))
  }
  const fixedVectorRadius = (magnitude: number): number => (
    visualizationPolicy.scoringVisible
      ? 24 + (magnitude / maxVectorMagnitude) * 88
      : 72
  )
  const downloadCandidateEvidencePacket = (side: 'USD' | 'JPY') => {
    if (!selectedAspect) return
    const safeToken = [side, chart?.symbol ?? 'INSTRUMENT', selectedAspect.transitBody, selectedAspect.natalBody, selectedAspect.aspect]
      .join('_')
      .replace(/[^A-Za-z0-9_]+/g, '_')
      .toUpperCase()
    const candidate = {
      contract: 'CHART_CONDITIONED_POLARITY_EVIDENCE_PACKET_CANDIDATE_V1',
      status: 'CANDIDATE_NOT_ADMISSIBLE',
      packetId: `CANDIDATE_${safeToken}`,
      instrumentId: `FX_CURRENCY:${side}`,
      sideIdentity: side,
      chartId: '',
      chartHypothesisId: '',
      transitBody: selectedAspect.transitBody,
      natalTarget: '',
      aspectType: selectedAspect.aspect,
      reviewedPolarity: '',
      evidenceStatus: 'PENDING_REVIEW',
      chartAcceptanceStatus: 'PENDING_FOUNDER_REVIEW',
      astronomyContract: selectedAspect.astronomyContract,
      profileHash: '',
      reviewedBy: '',
      reviewedAtUtc: '',
      sourceRefs: [],
      packetHash: '',
      reviewScope: {
        sourcePairSymbol: chart?.symbol ?? 'USDJPY',
        eventId: selectedAspect.eventId,
        familyKey: selectedAspect.familyKey,
        sourceGenerator: selectedAspect.sourceGenerator,
        selectedPairAspect: {
          transitBody: selectedAspect.transitBody,
          natalTarget: selectedAspect.natalBody,
          aspectType: selectedAspect.aspect,
        },
      },
      admissionNote: 'The pair event is review context only. Fill this side chart identity, accepted chart id, chart hypothesis id, natal target, reviewed state, evidence, and packet hash from reviewed source material. This candidate cannot be loaded as production evidence.',
    }
    const blob = new Blob([JSON.stringify(candidate, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const anchor = document.createElement('a')
    anchor.href = url
    anchor.download = `${safeToken.toLowerCase()}_polarity_evidence_candidate.json`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <section className={`product-first-sbc mode-${visualizationPolicy.mode.toLowerCase()}${sideView || currencyPairEvidence || wheelOpen || timingOpen || comparisonOpen ? ' has-product-first-panel' : ''}`} aria-label="Integrated Sarvatobhadra Chakra workspace">
      <header className="product-first-sbc-summary">
        <div className="product-first-summary-title">
          <Layers3 size={16} />
          <div>
            <strong>Integrated SBC workspace</strong>
            <span>{chart ? `${chart.symbol} ${chart.timeframe} market context` : 'No market context loaded'}</span>
          </div>
        </div>
        <span className="visualization-panel-mode">{visualizationPolicy.mode}</span>
        {visualizationPolicy.approvalState === 'FOUNDER_APPROVAL_PENDING' && <span className="visualization-panel-mode is-pending">Founder approval pending</span>}
        <div className="product-first-metric">
          <span>Supportive</span>
          <strong>{formatScalar(guidance ? supportive : null, 1)}</strong>
        </div>
        <div className="product-first-metric is-adverse">
          <span>Obstructive</span>
          <strong>{formatScalar(guidance ? obstructive : null, 1)}</strong>
        </div>
        <div className="product-first-metric">
          <span>Gross activity</span>
          <strong>{formatScalar(guidance ? gross : null, 1)}</strong>
        </div>
        <div className="product-first-metric">
          <span>Conflict</span>
          <strong>{formatScoreText(conflict)}</strong>
        </div>
        <div className="product-first-metric">
          <span>Coverage / unknown</span>
          <strong>{visualizationPolicy.scoringVisible && guidance ? `${Math.round(guidance.scoring_coverage_ratio * 100)}% / ${unknownCount}` : `Suppressed / ${unknownCount}`}</strong>
        </div>
        <span className="product-first-lock"><ShieldCheck size={12} /> Read-only experimental</span>
        <div className="product-first-view-controls" aria-label="Workspace view controls">
          <button aria-label="Previous loaded candle" title="Previous loaded candle" disabled={selectedCandleIndex <= 0} onClick={() => stepLoadedCandle(-1)}><ChevronLeft size={12} /></button>
          <button
            className={sideView === 'TIME' ? 'is-active' : ''}
            onClick={() => {
              setDraftMoment(momentInput(snapshot))
              setSideView((current) => current === 'TIME' ? null : 'TIME')
            }}
          >
            <CalendarClock size={12} /> Time
          </button>
          <button
            className={sideView === 'PROFILE' ? 'is-active' : ''}
            onClick={() => setSideView((current) => current === 'PROFILE' ? null : 'PROFILE')}
          >
            <SlidersHorizontal size={12} /> Profile
          </button>
          <button
            className={wheelOpen ? 'is-active' : ''}
            onClick={() => {
              setWheelOpen((current) => !current)
              if (!fixedPhasorInterval && !phasorBusy) onLoadFixedPhasor()
            }}
          >
            <Orbit size={12} /> Wheel
          </button>
          <button
            className={timingOpen ? 'is-active' : ''}
            disabled={!TIMING_PHASE_EXPERIMENT_ENABLED || !visualizationPolicy.allowTimingGeometry}
            onClick={() => setTimingOpen((current) => !current)}
          >
            <Orbit size={12} /> Phase lab
          </button>
          <button
            className={comparisonOpen ? 'is-active' : ''}
            onClick={() => {
              setComparisonOpen((current) => !current)
              if (!fixedPhasorInterval && !phasorBusy) onLoadFixedPhasor()
            }}
          >
            <Layers3 size={12} /> Compare
          </button>
          <button aria-label="Next loaded candle" title="Next loaded candle" disabled={selectedCandleIndex < 0 || selectedCandleIndex >= candles.length - 1} onClick={() => stepLoadedCandle(1)}><ChevronRight size={12} /></button>
        </div>
      </header>

      {sideView === 'TIME' && (
        <section className="product-first-time-profile" aria-label="Selected time view">
          <div>
            <CalendarClock size={15} />
            <div><strong>Selected time</strong><span>Changes the same timestamp used by price, event lanes, and the Chakra.</span></div>
          </div>
          <div className="product-first-time-actions">
            <button
              title="Previous loaded candle"
              disabled={selectedCandleIndex <= 0}
              onClick={() => stepLoadedCandle(-1)}
            ><ChevronLeft size={14} /> Previous candle</button>
            <input
              type="datetime-local"
              value={draftMoment}
              aria-label="Selected IST moment"
              onChange={(event) => setDraftMoment(event.target.value)}
            />
            <button
              className="is-primary"
              disabled={!draftMoment}
              onClick={() => onSelectMoment(draftMoment)}
            >Synchronize moment</button>
            <button
              title="Next loaded candle"
              disabled={selectedCandleIndex < 0 || selectedCandleIndex >= candles.length - 1}
              onClick={() => stepLoadedCandle(1)}
            >Next candle <ChevronRight size={14} /></button>
          </div>
          <div className="product-first-time-facts">
            <span><b>IST</b>{snapshot ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'full', timeStyle: 'medium', timeZone: 'Asia/Kolkata' }).format(new Date(snapshot.as_of_utc)) : 'Unavailable'}</span>
            <span><b>Location</b>{snapshot ? `${snapshot.location.latitude.toFixed(4)}, ${snapshot.location.longitude.toFixed(4)}` : 'Unavailable'}</span>
            <span><b>Chart candle</b>{selectedCandleIndex >= 0 ? `${selectedCandleIndex + 1} of ${candles.length}` : 'No chart candle'}</span>
          </div>
          {snapshot && <div className="product-first-panchanga-strip">
            <span>Tithi <b>{display(snapshot.foundation_snapshot.panchanga.tithi_name)}</b></span>
            <span>Paksha <b>{display(snapshot.foundation_snapshot.panchanga.paksha)}</b></span>
            <span>Yoga <b>{display(snapshot.foundation_snapshot.panchanga.yoga_name)}</b></span>
            <span>Karana <b>{display(snapshot.foundation_snapshot.panchanga.karana_name)}</b></span>
            <span>Weekday <b>{display(snapshot.foundation_snapshot.panchanga.vara.weekday)}</b></span>
          </div>}
        </section>
      )}

      {sideView === 'PROFILE' && (
        <section className="product-first-time-profile" aria-label="Current profile view">
          <div>
            <SlidersHorizontal size={15} />
            <div><strong>Current profile</strong><span>These are the existing read-only configurations behind the synchronized display.</span></div>
          </div>
          <div className="product-first-profile-facts">
            <span><b>Foundation</b>{snapshot ? display(snapshot.foundation_snapshot.profile_id) : 'Unavailable'}</span>
            <span><b>Chakra grid</b>{snapshot ? display(snapshot.grid.grid_profile_id) : 'Unavailable'}</span>
            <span><b>Vedha guidance</b>{snapshot?.guidance ? display(snapshot.guidance.vedha_profile_id) : 'No resolved guidance'}</span>
            <span><b>Active actors</b>{readiness.length ? readiness.map((item) => item.body).join(', ') : 'None selected'}</span>
            <span><b>Included layers</b>{snapshot?.grid.certified_layers.length ? snapshot.grid.certified_layers.map(display).join(', ') : 'Unavailable'}</span>
          </div>
          <p className="product-first-profile-note">This workspace reports the loaded profile context only. It does not alter a formula, create a market call, or unlock any execution path.</p>
        </section>
      )}

      {currencyPairEvidence && (
        <section className="product-first-fx-panel" aria-label="USDJPY relative context">
          <div>
            <Layers3 size={15} />
            <div>
              <strong>USDJPY relative context</strong>
              <span>{selectedAspectLabel ?? 'Selected aspect'} · existing provisional research arithmetic only</span>
            </div>
          </div>
          <dl>
            <div><dt>{currencyPairEvidence.base.label} mapping</dt><dd>{currencyPairEvidence.base.referenceLabel} · {display(currencyPairEvidence.base.state)}</dd></div>
            <div><dt>{currencyPairEvidence.quote.label} mapping</dt><dd>{currencyPairEvidence.quote.referenceLabel} · {display(currencyPairEvidence.quote.state)}</dd></div>
            <div><dt>{currencyPairEvidence.base.label}</dt><dd>{formatScalar(baseScore, 3)}</dd></div>
            <div><dt>{currencyPairEvidence.quote.label}</dt><dd>{formatScalar(quoteScore, 3)}</dd></div>
            <div><dt>Pair net difference</dt><dd>{formatScalar(pairScore, 3)}</dd></div>
            <div><dt>Common activation</dt><dd>{formatScalar(commonActivation, 3)}</dd></div>
            <div><dt>Joint net strength</dt><dd>{formatScalar(jointNetStrength, 3)}</dd></div>
            <div><dt>Conflict</dt><dd>{formatScalarPercent(pairConflict, 1)}</dd></div>
          </dl>
          <p>Evidence cutoff: {compactUtc(currencyPairEvidence.evidenceCutoffUtc)}. Gross activation is calculated before supportive and adverse activity can cancel. Both currencies remain visible; this is not a price prediction and cannot unlock an order or execution path.</p>
        </section>
      )}

      <section className="product-first-aspect-polarity-panel" aria-label="Chart-conditioned aspect pressure">
        <div>
          <Layers3 size={15} />
          <div>
            <strong>Chart-conditioned aspect pressure</strong>
            <span>Independent synchronized comparison field. It never confirms SBC or produces an order.</span>
          </div>
        </div>
        {(['USD', 'JPY'] as const).map((side) => {
          const lookup = fxSidePolarities?.[side] ?? null
          return lookup?.lookupState === 'READY' && lookup.entry ? (
            <dl key={side}>
              <div><dt>{side} state</dt><dd>{display(lookup.entry.precomputedPolarity)}</dd></div>
              <div><dt>{side} evidence</dt><dd>{display(lookup.entry.evidenceStatus)}</dd></div>
              <div><dt>{side} magnitude</dt><dd>{display(lookup.magnitudeState)}</dd></div>
            </dl>
          ) : (
            <p key={side}><b>{side}: {lookup ? display(lookup.lookupState) : 'Loading status'}</b> - {lookup?.reason ?? 'Checking the immutable side-chart polarity catalogue.'}</p>
          )
        })}
        <small>CATEGORICAL_POLARITY_STATE / MAGNITUDE_NOT_CONFIGURED. USDJPY is derived from two independently reviewed side-chart contexts; no sign is inferred from transit geometry, natural planet nature, or SBC.</small>
        {selectedAspect && <div className="product-first-polarity-candidate">
          <div>
            <strong>Side-chart evidence packet readiness</strong>
            <span>Pair review context: {selectedAspect.transitBody} to {selectedAspect.natalBody} {display(selectedAspect.aspect)} · {selectedAspect.astronomyContract}</span>
          </div>
          <p>Still required per side: accepted chart id, chart hypothesis id, natal target, reviewed categorical state, profile hash, reviewer, timestamp, source references, and packet hash. The selected pair target is not copied into either primary chart.</p>
          <div className="product-first-polarity-candidate-actions">
            <button onClick={() => downloadCandidateEvidencePacket('USD')}><Download size={12} /> USD candidate</button>
            <button onClick={() => downloadCandidateEvidencePacket('JPY')}><Download size={12} /> JPY candidate</button>
          </div>
        </div>}
      </section>

      {wheelOpen && (
        <section className="product-first-wheel" aria-label="Fixed phasor wheel">
          <div className="product-first-wheel-heading">
            <Orbit size={15} />
            <div><strong>Fixed real-axis phasor wheel</strong><span>Existing scalar display only: 0 at right, pi at left. It is not timing phase, a vote, or a price signal.</span></div>
          </div>
          {phasorBusy && <p className="product-first-wheel-state">Loading the read-only fixed-vector display for this selected timestamp.</p>}
          {phasorError && <p className="product-first-wheel-state is-error">{phasorError}</p>}
          {!phasorBusy && !phasorError && !fixedPhasorInterval && <p className="product-first-wheel-state">No fixed-vector display is available for this selected timestamp.</p>}
          {fixedPhasorInterval && <>
            <div className="product-first-wheel-layout">
              <svg viewBox="0 0 300 300" role="img" aria-label="Fixed zero and pi circular phasor display">
                <circle cx="150" cy="150" r="118" className="product-first-wheel-ring" />
                {visualizationPolicy.scoringVisible && <circle cx="150" cy="150" r={fixedGrossRadius} className="product-first-wheel-gross-ring" />}
                <line x1="24" y1="150" x2="276" y2="150" className="product-first-wheel-axis" />
                <text x="276" y="142" textAnchor="end" className={`product-first-wheel-label${visualizationPolicy.scoringVisible ? ' is-positive' : ''}`}>fixed 0</text>
                <text x="24" y="142" className={`product-first-wheel-label${visualizationPolicy.scoringVisible ? ' is-negative' : ''}`}>fixed pi</text>
                {plottedVectors.map((vector) => {
                  const magnitude = vector.magnitude_units ?? 0
                  const radius = fixedVectorRadius(magnitude)
                  const positive = vector.fixed_angle === 'ZERO'
                  const x = 150 + (positive ? radius : -radius)
                  return <g
                    key={vector.vector_id}
                    className={`product-first-wheel-vector${visualizationPolicy.scoringVisible ? (positive ? ' is-positive' : ' is-negative') : ' is-neutral'}${selectedVector?.vector_id === vector.vector_id ? ' is-selected' : ''}`}
                  >
                    <title>{`${vector.actor_identity ?? 'Unlabelled'}: ${positive ? '0/right' : 'pi/left'}${visualizationPolicy.scoringVisible ? ` (${magnitude.toFixed(2)} source units)` : ' (value suppressed)'}`}</title>
                    <line x1="150" y1="150" x2={x} y2="150" />
                  </g>
                })}
                {visualizationPolicy.scoringVisible && <line
                  x1="150"
                  y1="150"
                  x2={150 + (fixedResultantPositive ? fixedResultantRadius : -fixedResultantRadius)}
                  y2="150"
                  className="product-first-wheel-resultant"
                />}
                {visualizationPolicy.scoringVisible && fixedNearZero && <g className="product-first-wheel-near-zero"><circle cx="150" cy="150" r="10" /><line x1="142" y1="142" x2="158" y2="158" /><line x1="158" y1="142" x2="142" y2="158" /></g>}
                <circle cx="150" cy="150" r="5" className="product-first-wheel-origin" />
              </svg>
              <div className="product-first-wheel-detail">
                <span>Selected vector from visual-only group</span>
                {selectedVector ? <>
                  <strong>{selectedVector.actor_identity ?? 'Unlabelled contribution'}</strong>
                  <div><em>Fixed side</em><b>{selectedVector.fixed_angle === 'ZERO' ? '0 / right' : 'Pi / left'}</b></div>
                  <div><em>Scalar units</em><b>{formatScalar(selectedVector.real_component_units, 1)}</b></div>
                  <div><em>Target</em><b>{selectedVector.target_value ?? 'Unknown'}</b></div>
                </> : <p>No resolved vector was plotted.</p>}
              </div>
            </div>
            <div className="product-first-wheel-groups" aria-label="Visual-only vector groups">
              <div><span>0 / right ({fixedZeroVectors.length})</span>{fixedZeroVectors.map((vector) => <button key={vector.vector_id} aria-pressed={selectedVector?.vector_id === vector.vector_id} className={selectedVector?.vector_id === vector.vector_id ? 'is-selected' : ''} onClick={() => setSelectedVectorId(vector.vector_id)}>{vector.actor_identity ?? 'Unlabelled'} - {visualizationPolicy.scoringVisible ? `${(vector.magnitude_units ?? 0).toFixed(1)} units` : 'value suppressed'}</button>)}</div>
              <div><span>Pi / left ({fixedPiVectors.length})</span>{fixedPiVectors.map((vector) => <button key={vector.vector_id} aria-pressed={selectedVector?.vector_id === vector.vector_id} className={selectedVector?.vector_id === vector.vector_id ? 'is-selected' : ''} onClick={() => setSelectedVectorId(vector.vector_id)}>{vector.actor_identity ?? 'Unlabelled'} - {visualizationPolicy.scoringVisible ? `${(vector.magnitude_units ?? 0).toFixed(1)} units` : 'value suppressed'}</button>)}</div>
            </div>
            <div className="product-first-wheel-summary">
              <span>Real sum <b>{formatScalar(fixedPhasorInterval.vector_real_sum_units, 1)}</b></span>
              <span>Gross magnitude <b>{formatScalar(fixedPhasorInterval.vector_magnitude_sum_units, 1)}</b></span>
              <span>Imaginary sum <b>{formatScalar(fixedPhasorInterval.vector_imaginary_sum_units, 1)}</b></span>
              <span>Known coverage <b>{formatScalarPercent(fixedPhasorInterval.known_scored_coherence_ratio, 1)}</b></span>
            </div>
            <p className="product-first-wheel-interpretation">{visualizationPolicy.scoringVisible ? `Resultant: fixed real-axis sum only. Gross ring: total scalar magnitude. ${fixedNearZero ? 'Near-zero resultant marker shown using a visual threshold of max(0.25, 15% of gross).' : 'No near-zero resultant marker.'}` : 'Fixed side and actor identity remain visible; scalar magnitude, resultant, gross ring, and near-zero state are withheld.'} These are visual parity checks, not a timing or physical-wave claim.</p>
            {unknownVectors.length > 0 && <div className="product-first-wheel-unknown"><b>Unresolved tray</b><span>{unknownVectors.length} unknown vector{unknownVectors.length === 1 ? '' : 's'} remain unplotted and outside the fixed-axis geometry.</span></div>}
          </>}
        </section>
      )}

      {timingOpen && (
        <section className="product-first-timing-phase" aria-label="Experimental timing phase lab">
          <div className="product-first-wheel-heading">
            <Orbit size={15} />
            <div>
              <strong>Timing phase lab</strong>
              <span>{PROJECT_CONVENTION_TIMING_PHASE_V1.contract} - engineering test coordinate only</span>
            </div>
            <span className="product-first-phase-badge">Zero vote</span>
          </div>
          {!TIMING_PHASE_EXPERIMENT_ENABLED && <p className="product-first-wheel-state">This feature-flagged experiment is disabled.</p>}
          {TIMING_PHASE_EXPERIMENT_ENABLED && !timingExperiment.activeEvents.length && <p className="product-first-wheel-state">No aspect window is active at this selected timestamp. Phase geometry remains unknown and market direction stays ABSTAIN.</p>}
          {TIMING_PHASE_EXPERIMENT_ENABLED && timingExperiment.activeEvents.length > 0 && <>
            <div className="product-first-timing-meta">
              <span><b>Active events</b>{timingExperiment.activeEvents.length}</span>
              <span><b>Safe sector</b>{timingExperiment.safeSector ? 'Inside declared safe sector' : 'Outside declared safe sector'}</span>
              <span><b>State</b>{display(timingExperiment.state)}</span>
              <span><b>Aggregate</b>{timingExperiment.aggregateWithheld ? 'Withheld' : 'Unavailable'}</span>
            </div>
            <div className="product-first-timing-meta" aria-label="Per-event timing lifecycle">
              {timingExperiment.activeEvents.map((event) => (
                <span key={event.eventId}><b>{compactAspectLabel(event.label)}</b>{display(event.lifecycle)} - {event.timingPhaseRadians == null ? 'Unknown geometry' : `${event.timingPhaseRadians.toFixed(2)} rad`} - normalized {event.normalizedLifecycleProgress == null ? 'Unknown' : event.normalizedLifecycleProgress.toFixed(2)}</span>
              ))}
            </div>
            <p className="product-first-wheel-state">{timingExperiment.aggregateWithheldReason}</p>
            {unresolvedTiming.length > 0 && <div className="product-first-timing-unknown" aria-label="Unresolved timing evidence">
              <b>Unresolved timing evidence</b>
              <span>{unresolvedTiming.map((contribution) => `${contribution.body}: ${contribution.explanation || contribution.status}`).join('; ')}</span>
            </div>}
            <p className="product-first-phase-note">Each active event keeps its own lifecycle displacement; overlapping events are never collapsed into one nearest-event rotation. {timingExperiment.unlinkedResolvedContributionCount} resolved contribution{timingExperiment.unlinkedResolvedContributionCount === 1 ? '' : 's'} and {timingExperiment.unknownVectorCount} unresolved contribution{timingExperiment.unknownVectorCount === 1 ? '' : 's'} are not linked to events, so no aggregate interference is shown. This experiment never creates a market direction, confidence score, trade, or execution path.</p>
          </>}
        </section>
      )}

      {comparisonOpen && (
        <section className="product-first-comparison" aria-label="Scalar fixed timing comparison">
          <div className="product-first-wheel-heading">
            <Layers3 size={15} />
            <div>
              <strong>Three-model comparison</strong>
              <span>One synchronized moment; the scalar baseline stays visible and no model can issue a market call.</span>
            </div>
            <span className="product-first-phase-badge">Read-only</span>
          </div>
          <div className="product-first-comparison-grid">
            <article>
              <header><strong>Scalar SBC baseline</strong><span>Existing source guidance</span></header>
              <dl>
                <div><dt>Supportive</dt><dd>{formatScalar(guidance ? supportive : null)}</dd></div>
                <div><dt>Obstructive</dt><dd>{formatScalar(guidance ? obstructive : null)}</dd></div>
                <div><dt>Net</dt><dd>{formatScalar(guidance?.net_guidance_units ?? null)}</dd></div>
                <div><dt>Gross</dt><dd>{formatScalar(guidance ? gross : null)}</dd></div>
              </dl>
              <p>{visualizationPolicy.scoringVisible ? 'Original units and explicit unknowns; this remains the visible baseline.' : 'Scalar values remain deliberately withheld in this mode.'}</p>
            </article>
            <article>
              <header><strong>Fixed 0/pi wheel</strong><span>Existing scalar visualization</span></header>
              {fixedPhasorInterval ? <dl>
                <div><dt>Real</dt><dd>{formatScalar(fixedPhasorInterval.vector_real_sum_units)}</dd></div>
                <div><dt>Imaginary</dt><dd>{formatScalar(fixedPhasorInterval.vector_imaginary_sum_units)}</dd></div>
                <div><dt>Gross</dt><dd>{formatScalar(fixedPhasorInterval.vector_magnitude_sum_units)}</dd></div>
                <div><dt>Parity</dt><dd>{visualizationPolicy.scoringVisible ? (fixedPhasorInterval.real_matches_net ? 'Matches scalar' : 'Check required') : 'Value suppressed'}</dd></div>
              </dl> : <p className="product-first-comparison-unavailable">{phasorBusy ? 'Loading existing fixed-vector display.' : 'Fixed display unavailable for this timestamp.'}</p>}
              <p>Only re-expresses scalar polarity on the fixed real axis; it adds no independent vote.</p>
            </article>
            <article>
              <header><strong>Timing phase lab</strong><span>Feature-flagged engineering coordinate</span></header>
              <dl>
                <div><dt>Active events</dt><dd>{timingExperiment.activeEvents.length || 'Unknown'}</dd></div>
                <div><dt>Aggregate interference</dt><dd>{timingExperiment.aggregateWithheld ? 'Withheld: unlinked geometry' : 'Unavailable'}</dd></div>
                <div><dt>State</dt><dd>{display(timingExperiment.state)}</dd></div>
                <div><dt>Market result</dt><dd>ABSTAIN</dd></div>
              </dl>
              <p>{timingExperiment.aggregateWithheldReason ?? 'No active event lifecycle is available.'}</p>
            </article>
          </div>
          <div className="product-first-comparison-causes">
            <div><b>Why values differ</b><span>Fixed re-expresses the scalar ledger at 0/pi. Timing shows each event lifecycle independently, but aggregate interference is withheld until a contribution-event link profile exists.</span></div>
            <div><b>Pinned timestamp</b><span>{snapshot ? new Date(snapshot.as_of_utc).toISOString() : 'Unavailable'}</span></div>
            <div><b>Evidence cutoff</b><span>{snapshot?.evidence_cutoff_utc ?? 'Unavailable'} · no future market data is read by this comparison.</span></div>
          </div>
        </section>
      )}

      <div className="product-first-sbc-body">
        <section className="product-first-market-panel">
          <div className="product-first-panel-heading">
            <div>
              <strong>Price and aspect context</strong>
              <span>Click a candle to synchronize the SBC moment in IST</span>
            </div>
            <time>{snapshot ? new Intl.DateTimeFormat('en-IN', {
              dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Kolkata',
            }).format(new Date(snapshot.as_of_utc)) : 'Moment unavailable'}</time>
          </div>
          {candles.length ? (
            <div className="product-first-market-viewport">
              <svg
                viewBox={`0 0 ${chartWidth} ${chartHeight}`}
                role="img"
                tabIndex={0}
                aria-label="Price chart with aspect event lanes. Use Left and Right Arrow to move the selected timestamp by one loaded candle."
                onKeyDown={(event) => {
                  if (event.key === 'ArrowLeft') {
                    event.preventDefault()
                    stepLoadedCandle(-1)
                  }
                  if (event.key === 'ArrowRight') {
                    event.preventDefault()
                    stepLoadedCandle(1)
                  }
                }}
              >
                <rect x="0" y="0" width={chartWidth} height={chartHeight} className="product-first-chart-bg" />
                {[0, 1, 2, 3, 4].map((index) => {
                  const y = 28 + index * 90
                  const price = high - (priceSpan * index) / 4
                  return <g key={index}>
                    <line x1="28" y1={y} x2="972" y2={y} className="product-first-chart-grid" />
                    <text x="4" y={y + 3} className="product-first-chart-axis">{price.toFixed(3)}</text>
                  </g>
                })}
                {visibleAspects.map((aspect, index) => {
                  const x = Math.max(28, xFor(Math.max(firstTime, aspect.start)))
                  const end = Math.min(972, xFor(Math.min(lastTime, aspect.end)))
                  const lane = index % 4
                  const y = 4 + lane * 19
                  return <g key={aspect.eventId} className="product-first-aspect-lane">
                    <rect x={x} y={y} width={Math.max(2, end - x)} height="16" fill={aspect.color} />
                    {end - x > 74 && <text x={x + 4} y={y + 11}>{compactAspectLabel(aspect.aspectLabel)}</text>}
                  </g>
                })}
                {candles.map((candle) => {
                  const x = xFor(candle.time)
                  const up = candle.close >= candle.open
                  const bodyTop = yFor(Math.max(candle.open, candle.close))
                  const bodyBottom = yFor(Math.min(candle.open, candle.close))
                  return <g key={candle.time} className="product-first-candle" onClick={() => onSelectMoment(toIstInput(candle.time))}>
                    <line x1={x} y1={yFor(candle.high)} x2={x} y2={yFor(candle.low)} className={up ? 'is-up' : 'is-down'} />
                    <rect x={x - candleWidth / 2} y={bodyTop} width={candleWidth} height={Math.max(1.2, bodyBottom - bodyTop)} className={up ? 'is-up' : 'is-down'} />
                  </g>
                })}
                <line x1={xFor(selectedEpoch)} y1="24" x2={xFor(selectedEpoch)} y2="392" className="product-first-selected-moment" />
                <text x={Math.min(835, Math.max(32, xFor(selectedEpoch) + 5))} y="420" className="product-first-chart-axis">Selected moment</text>
              </svg>
            </div>
          ) : (
            <div className="product-first-empty"><CircleHelp size={20} /><span>Open this workspace from a loaded chart to see price and aspect context.</span></div>
          )}
          <div className="product-first-event-strip">
            <strong>Visible aspects</strong>
            {visibleAspects.slice(0, 12).map((aspect) => (
              <span key={aspect.eventId} style={{ borderColor: aspect.color }} title={`${aspect.startIso} to ${aspect.endIso}`}>
                {compactAspectLabel(aspect.aspectLabel)}
              </span>
            ))}
            {!visibleAspects.length && <em>No aspects in the loaded chart range</em>}
          </div>
        </section>

        <section className="product-first-chakra-panel">
          <div className="product-first-panel-heading">
            <div><strong>81-cell Chakra</strong><span>Selected cell follows evidence and manual clicks</span></div>
            <Grid3X3 size={15} />
          </div>
          {snapshot ? (
            <div className="product-first-chakra-grid" style={{
              '--chakra-columns': snapshot.grid.columns,
              '--chakra-rows': snapshot.grid.rows,
            } as CSSProperties}>
              {snapshot.grid.cells.map((cell) => {
                const key = cellKey(cell)
                const primary = cell.entries.find((entry) => entry.layer === 'NAKSHATRA') ?? cell.entries[0]
                const isContext = cell.entries.some((entry) => contextCells.has(`${entry.layer}:${entry.value}`))
                return <button
                  key={key}
                  className={[
                    'product-first-chakra-cell',
                    selectedCell === key ? 'is-selected' : '',
                    targetCells.has(key) ? 'is-hit' : '',
                    isContext ? 'is-context' : '',
                  ].filter(Boolean).join(' ')}
                  onClick={() => onSelectCell(key)}
                  title={cell.entries.map((entry) => `${entry.layer}: ${entry.value}`).join('\n')}
                >
                  <small>{cell.row},{cell.column}</small>
                  <strong>{primary ? display(primary.value) : '·'}</strong>
                </button>
              })}
            </div>
          ) : <div className="product-first-empty"><span>Calculating the Chakra snapshot.</span></div>}
        </section>

        <aside className="product-first-why-drawer">
          <div className="product-first-panel-heading">
            <div><strong>Why this state</strong><span>Evidence only, not a market call</span></div>
            <CircleHelp size={15} />
          </div>
          <section className="product-first-why-card">
            <span>Current state</span>
            <strong>{visualizationPolicy.scoringVisible ? (guidance ? display(guidance.guidance_band) : 'Unknown') : visualizationPolicy.evidenceStatus}</strong>
            <p>{visualizationPolicy.scoringVisible ? `${conflict}. Coverage is ${guidance ? `${Math.round(guidance.scoring_coverage_ratio * 100)}%` : 'unavailable'}; unresolved inputs remain explicit.` : 'This mode keeps source status and geometry visible while withholding directional and aggregate guidance.'}</p>
          </section>
        <section className="product-first-why-card">
          <span>Visualization evidence status</span>
          <div><em>{display(visualizationPolicy.evidenceStatus)}</em><strong>{display(visualizationPolicy.approvalState)}</strong></div>
          <p>{visualizationPolicy.classicalCompletenessClaim ? 'Classical completeness claim recorded.' : 'No founder-approved claim of classical completeness is made.'}</p>
        </section>
        <section className="product-first-why-card">
          <span>Selected Chakra cell</span>
            {selected?.entries.map((entry) => <div key={`${entry.layer}:${entry.value}`}><em>{display(entry.layer)}</em><strong>{display(entry.value)}</strong></div>)}
            {!selected?.entries.length && <p>No certified layer at this cell.</p>}
          </section>
          <section className="product-first-why-card">
            <span>Resolved Vedha evidence</span>
            {(guidance?.contributions ?? []).slice(0, 9).map((item, index) => (
              <button key={`${item.body}-${index}`} onClick={() => onSelectCell(`${item.target.row}:${item.target.column}`)}>
                <strong>{item.body}</strong><em>{visualizationPolicy.scoringVisible ? `${display(item.direction)} → ${display(item.target.value)}` : display(item.status)}</em><b>{visualizationPolicy.scoringVisible ? (item.signed_guidance_units == null ? 'Unknown' : item.signed_guidance_units.toFixed(1)) : visualizationPolicy.evidenceStatus}</b>
              </button>
            ))}
            {!guidance?.contributions.length && <p>No resolved Vedha contribution for this moment.</p>}
          </section>
          <section className="product-first-why-card">
            <span>Actor readiness</span>
            {readiness.map((item) => <div key={item.body}><em>{item.body}</em><strong>{display(item.status)}</strong></div>)}
          </section>
        </aside>
      </div>
    </section>
  )
}
