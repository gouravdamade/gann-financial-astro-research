import { Activity, ClipboardCheck, Layers3, RefreshCw, ShieldCheck } from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import {
  fetchFxSidePilotStatus,
  fetchSynchronizedIndependentRange,
} from '../api'
import type {
  ChakraLabRequest,
  ChartPayload,
  FxSidePilotStatus,
  ResearchFieldIntervalSelection,
  SynchronizedIndependentRange,
} from '../types'
import {
  VISUALIZATION_ENGINE_MODES,
  visualizationModePolicy,
  type VisualizationEngineMode,
} from '../visualizationModes'
import { sourceGapsForVisualizationMode } from '../visualizationSourceGaps'
import { IndependentFieldStack } from './IndependentFieldStack'
import { FounderReviewWorkbench } from './FounderReviewWorkbench'

const BODIES = ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN', 'RAHU', 'KETU'] as const

type Props = {
  chart: ChartPayload
  priceChart: ReactNode
  visibleRangeStartUtc: string | null
  visibleRangeEndUtc: string | null
  defaultLatitude: number
  defaultLongitude: number
  vedhaProfileId: ChakraLabRequest['vedhaProfileId']
  onVedhaProfileIdChange: (profileId: ChakraLabRequest['vedhaProfileId']) => void
  visualizationMode: VisualizationEngineMode
  onVisualizationModeChange: (mode: VisualizationEngineMode) => void
  crosshairTimestampUtc: string | null
  selectedFieldInterval: ResearchFieldIntervalSelection | null
  onSelectFieldInterval: (selection: ResearchFieldIntervalSelection) => void
}

type FieldRange = {
  rangeStartUtc: string
  rangeEndUtc: string
  signature: string
  source: 'live chart viewport' | 'loaded chart extent'
}

function fieldRangeFor(
  chart: ChartPayload,
  visibleRangeStartUtc: string | null,
  visibleRangeEndUtc: string | null,
): FieldRange | null {
  if (!chart.candles.length) return null
  const chartStart = chart.candles[0].time * 1000
  const chartEnd = chart.candles.at(-1)!.time * 1000
  const requestedStart = visibleRangeStartUtc ? Date.parse(visibleRangeStartUtc) : Number.NaN
  const requestedEnd = visibleRangeEndUtc ? Date.parse(visibleRangeEndUtc) : Number.NaN
  const start = Number.isFinite(requestedStart) ? Math.max(chartStart, requestedStart) : chartStart
  const end = Number.isFinite(requestedEnd) ? Math.min(chartEnd, requestedEnd) : chartEnd
  if (end <= start) return null
  const rangeStartUtc = new Date(start).toISOString()
  const rangeEndUtc = new Date(end).toISOString()
  return {
    rangeStartUtc,
    rangeEndUtc,
    signature: `${rangeStartUtc}:${rangeEndUtc}`,
    source: Number.isFinite(requestedStart) && Number.isFinite(requestedEnd)
      ? 'live chart viewport'
      : 'loaded chart extent',
  }
}

function istOffsetFromUtc(value: string): string {
  const date = new Date(value)
  return new Date(date.valueOf() + 19_800_000).toISOString().slice(0, 19) + '+05:30'
}

function isSupportedFxPair(symbol: string): boolean {
  return /^[A-Z]{6}$/.test(symbol) && symbol.slice(0, 3) === 'USD' && symbol.slice(3) === 'JPY'
}

export function FieldsWorkspace({
  chart,
  priceChart,
  visibleRangeStartUtc,
  visibleRangeEndUtc,
  defaultLatitude,
  defaultLongitude,
  vedhaProfileId,
  onVedhaProfileIdChange,
  visualizationMode,
  onVisualizationModeChange,
  crosshairTimestampUtc,
  selectedFieldInterval,
  onSelectFieldInterval,
}: Props) {
  const [range, setRange] = useState<SynchronizedIndependentRange | null>(null)
  const [rangeBusy, setRangeBusy] = useState(false)
  const [rangeError, setRangeError] = useState('')
  const [pilotStatus, setPilotStatus] = useState<FxSidePilotStatus | null>(null)
  const [pilotBusy, setPilotBusy] = useState(false)
  const [pilotError, setPilotError] = useState('')
  const [founderReviewOpen, setFounderReviewOpen] = useState(false)
  const requestSequence = useRef(0)
  const isFxPair = isSupportedFxPair(chart.symbol)
  const fieldRange = useMemo(
    () => fieldRangeFor(chart, visibleRangeStartUtc, visibleRangeEndUtc),
    [chart, visibleRangeEndUtc, visibleRangeStartUtc],
  )
  const visualizationPolicy = visualizationModePolicy(visualizationMode, vedhaProfileId)
  const sourceGaps = sourceGapsForVisualizationMode(visualizationMode, vedhaProfileId)

  const loadPilotStatus = useCallback(async () => {
    setPilotBusy(true)
    setPilotError('')
    try {
      setPilotStatus(await fetchFxSidePilotStatus())
    } catch (caught) {
      setPilotStatus(null)
      setPilotError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setPilotBusy(false)
    }
  }, [])

  const loadRange = useCallback(async () => {
    if (!fieldRange) {
      setRange(null)
      setRangeError('Open Fields from a chart with at least two visible timestamps.')
      return
    }
    if (!isFxPair) {
      setRange(null)
      setRangeError('The current synchronized side-field compiler supports the explicit FX USDJPY contract only. A stock does not receive an automatic FX relative field.')
      return
    }
    const sequence = requestSequence.current + 1
    requestSequence.current = sequence
    setRangeBusy(true)
    setRangeError('')
    const boundaryRequest: ChakraLabRequest = {
      at: istOffsetFromUtc(fieldRange.rangeStartUtc),
      timezone: 'Asia/Kolkata',
      latitude: defaultLatitude,
      longitude: defaultLongitude,
      altitudeM: 0,
      bodies: [...BODIES],
      actors: BODIES.map((body) => ({ body, dignity: 'ORDINARY' })),
      foundationProfileId: 'sbc_raman_foundation_v1',
      gridProfileId: 'sbc_81_rotation_normalized_partial_v1',
      vedhaProfileId,
      vowels: [],
      nameInitials: [],
    }
    try {
      const result = await fetchSynchronizedIndependentRange({
        rangeStartUtc: fieldRange.rangeStartUtc,
        rangeEndUtc: fieldRange.rangeEndUtc,
        sideIdentities: ['USD', 'JPY'],
        aspectProfileId: 'ASPECT_STRENGTH_V0',
        sbcRange: {
          instrumentIdentity: `FX:${chart.symbol}`,
          boundaries: [{ reason: 'rendered chart range start', request: boundaryRequest }],
        },
      })
      if (sequence === requestSequence.current) setRange(result)
    } catch (caught) {
      if (sequence === requestSequence.current) {
        setRange(null)
        setRangeError(caught instanceof Error ? caught.message : String(caught))
      }
    } finally {
      if (sequence === requestSequence.current) setRangeBusy(false)
    }
  }, [chart.symbol, defaultLatitude, defaultLongitude, fieldRange, isFxPair, vedhaProfileId])

  useEffect(() => {
    const timer = window.setTimeout(() => { void loadRange() }, 160)
    return () => window.clearTimeout(timer)
  }, [loadRange])

  useEffect(() => {
    void loadPilotStatus()
  }, [loadPilotStatus])

  return <section className="fields-workspace" aria-label="Fields workspace">
    <header className="fields-workspace-header">
      <div>
        <Layers3 size={18} />
        <div><strong>Fields</strong><span>{chart.symbol} {chart.timeframe} | synchronized descriptive research fields</span></div>
      </div>
      <div className="fields-workspace-controls">
        <button type="button" className="fields-founder-review-button" onClick={() => setFounderReviewOpen(true)} disabled={founderReviewOpen}><ClipboardCheck size={13} /> Founder Review</button>
        <label>Source profile
          <select value={vedhaProfileId} onChange={(event) => onVedhaProfileIdChange(event.target.value as ChakraLabRequest['vedhaProfileId'])}>
            <option value="phaladeepika_editor_vedha_guidance_v1">Phaladeepika editor profile</option>
            <option value="SBC_TRAILOKYA_1972_V1">Trailokya 1972 source-only geometry</option>
          </select>
        </label>
        <div className="fields-mode-switch" role="tablist" aria-label="Fields visualization mode">
          {VISUALIZATION_ENGINE_MODES.map((mode) => <button
            key={mode}
            role="tab"
            aria-selected={visualizationMode === mode}
            className={visualizationMode === mode ? 'is-active' : ''}
            title={visualizationModePolicy(mode, vedhaProfileId).explanation}
            onClick={() => onVisualizationModeChange(mode)}
          >{visualizationModePolicy(mode, vedhaProfileId).shortLabel}</button>)}
        </div>
      </div>
    </header>
    {founderReviewOpen ? <FounderReviewWorkbench onClose={() => setFounderReviewOpen(false)} /> : <>
    <section className="fields-context-card" aria-label="Field contract and context">
      <div><b>Instrument</b><span>{chart.symbol} {isFxPair ? 'FX base/quote' : 'single instrument'}</span></div>
      <div><b>Mode</b><span>{visualizationPolicy.label}</span></div>
      <div><b>Chart identities</b><span>{isFxPair ? 'USD and JPY founder-approved research hypotheses' : 'No FX side identity required'}</span></div>
      <div><b>Range</b><span>{fieldRange?.source ?? 'No usable range'}</span></div>
    </section>

    <section className="fields-price-context" aria-label="Synchronized price chart">
      <header><Activity size={14} /><div><strong>Price and aspect context</strong><span>Shared crosshair, selected candle, and visible UTC range</span></div></header>
      <div className="fields-price-chart">{priceChart}</div>
    </section>

    <section className="fields-panes" aria-label="Synchronized independent fields">
      <IndependentFieldStack
        range={range}
        rangeSource={fieldRange?.source ?? null}
        busy={rangeBusy}
        error={rangeError}
        onLoad={() => void loadRange()}
        pilotStatus={pilotStatus}
        pilotBusy={pilotBusy}
        pilotError={pilotError}
        onLoadPilot={() => void loadPilotStatus()}
        selectedInterval={selectedFieldInterval}
        onSelectInterval={onSelectFieldInterval}
        crosshairTimestampUtc={crosshairTimestampUtc}
        visualizationMode={visualizationMode}
        isFxPair={isFxPair}
      />
    </section>

    <section className="fields-audit-details" aria-label="Field audit details">
      <div><ShieldCheck size={14} /><div><strong>Pair-relative field contract</strong><span>FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1 is a transparent modern research transform: USD side balance minus JPY side balance. It is not classical doctrine, a forecast, or SBC confirmation.</span></div></div>
      <div><RefreshCw size={14} /><div><strong>Independent SBC availability</strong><span>{vedhaProfileId === 'SBC_TRAILOKYA_1972_V1' ? 'GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED. No score, polarity, wave, or fallback.' : 'Atomic SBC availability remains independent from USD, JPY, and pair fields.'}</span></div></div>
      <div><Layers3 size={14} /><div><strong>Source gaps ({sourceGaps.length})</strong><span>{sourceGaps.length ? sourceGaps.map((gap) => gap.gapId).join(' | ') : 'No configured visualization-source gaps.'}</span></div></div>
    </section>
    </>}
  </section>
}
