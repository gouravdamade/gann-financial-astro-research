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
import { BphsClassicalTimingPane } from './BphsClassicalTimingPane'
import {
  fieldsResearchWindowFor,
  isTimestampInsideResearchWindow,
  researchWindowPageForTimestamp,
} from '../fieldsResearchWindow'

const BODIES = ['SUN', 'MOON', 'MARS', 'MERCURY', 'JUPITER', 'VENUS', 'SATURN', 'RAHU', 'KETU'] as const
const CLASSICAL_TIMING_SESSION_KEY = 'gann-astro.fields.bphs-calendar.enabled.v1'

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

function istOffsetFromUtc(value: string): string {
  const date = new Date(value)
  return new Date(date.valueOf() + 19_800_000).toISOString().slice(0, 19) + '+05:30'
}

function isSupportedFxPair(symbol: string): boolean {
  return /^[A-Z]{6}$/.test(symbol) && symbol.slice(0, 3) === 'USD' && symbol.slice(3) === 'JPY'
}

function initialClassicalTimingEnabled(): boolean {
  try {
    return window.sessionStorage.getItem(CLASSICAL_TIMING_SESSION_KEY) === 'true'
  } catch {
    return false
  }
}

export function FieldsWorkspace({
  chart,
  priceChart,
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
  const [classicalTimingEnabled, setClassicalTimingEnabled] = useState(initialClassicalTimingEnabled)
  const [researchPageIndex, setResearchPageIndex] = useState(0)
  const requestSequence = useRef(0)
  const rangeCache = useRef(new Map<string, SynchronizedIndependentRange>())
  const isFxPair = isSupportedFxPair(chart.symbol)
  const datasetSignature = `${chart.symbol}:${chart.timeframe}:${chart.candles[0]?.time ?? ''}:${chart.candles.at(-1)?.time ?? ''}`
  const researchWindow = useMemo(
    () => fieldsResearchWindowFor(chart, researchPageIndex),
    [chart, researchPageIndex],
  )
  const crosshairPageIndex = researchWindowPageForTimestamp(chart, crosshairTimestampUtc)
  const crosshairOutsideResearchWindow = crosshairPageIndex !== null
    && !isTimestampInsideResearchWindow(researchWindow, crosshairTimestampUtc)
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
    if (!researchWindow) {
      setRange(null)
      setRangeError('Open Fields from a chart with at least two loaded timestamps.')
      return
    }
    if (!isFxPair) {
      setRange(null)
      setRangeError('The current synchronized side-field compiler supports the explicit FX USDJPY contract only. A stock does not receive an automatic FX relative field.')
      return
    }
    const sequence = requestSequence.current + 1
    requestSequence.current = sequence
    const cacheKey = `${researchWindow.rangeStartUtc}:${researchWindow.rangeEndUtc}:${vedhaProfileId}`
    const cached = rangeCache.current.get(cacheKey)
    if (cached) {
      setRange(cached)
      setRangeBusy(false)
      setRangeError('')
      return
    }
    setRangeBusy(true)
    setRangeError('')
    const boundaryRequest: ChakraLabRequest = {
      at: istOffsetFromUtc(researchWindow.rangeStartUtc),
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
        rangeStartUtc: researchWindow.rangeStartUtc,
        rangeEndUtc: researchWindow.rangeEndUtc,
        sideIdentities: ['USD', 'JPY'],
        aspectProfileId: 'ASPECT_STRENGTH_V0',
        sbcRange: {
          instrumentIdentity: `FX:${chart.symbol}`,
          boundaries: [{ reason: 'shared Fields research page start', request: boundaryRequest }],
        },
      })
      if (sequence === requestSequence.current) {
        rangeCache.current.set(cacheKey, result)
        setRange(result)
      }
    } catch (caught) {
      if (sequence === requestSequence.current) {
        setRange(null)
        setRangeError(caught instanceof Error ? caught.message : String(caught))
      }
    } finally {
      if (sequence === requestSequence.current) setRangeBusy(false)
    }
  }, [chart.symbol, defaultLatitude, defaultLongitude, isFxPair, researchWindow, vedhaProfileId])

  useEffect(() => {
    const timer = window.setTimeout(() => { void loadRange() }, 160)
    return () => window.clearTimeout(timer)
  }, [loadRange])

  useEffect(() => {
    void loadPilotStatus()
  }, [loadPilotStatus])

  useEffect(() => {
    setResearchPageIndex(0)
  }, [datasetSignature])

  useEffect(() => {
    try {
      window.sessionStorage.setItem(CLASSICAL_TIMING_SESSION_KEY, String(classicalTimingEnabled))
    } catch {
      // A private or restricted WebView can still use the pane for its current session.
    }
  }, [classicalTimingEnabled])

  return <section className="fields-workspace" aria-label="Fields workspace">
    <header className="fields-workspace-header">
      <div>
        <Layers3 size={18} />
        <div><strong>Fields</strong><span>{chart.symbol} {chart.timeframe} | synchronized descriptive research fields</span></div>
      </div>
      <div className="fields-workspace-controls">
        <div className="fields-research-window-controls" aria-label="Fields research window">
          <button type="button" onClick={() => setResearchPageIndex((page) => Math.max(0, page - 1))} disabled={!researchWindow || researchWindow.pageIndex === 0}>Previous 14 days</button>
          <span>{researchWindow ? `Research window ${researchWindow.pageIndex + 1}/${researchWindow.pageCount} | ${researchWindow.rangeStartUtc.slice(0, 10)} to ${researchWindow.rangeEndUtc.slice(0, 10)} | max 14 days` : 'Research window unavailable'}</span>
          <button type="button" onClick={() => setResearchPageIndex((page) => Math.min((researchWindow?.pageCount ?? 1) - 1, page + 1))} disabled={!researchWindow || researchWindow.isFinalPage}>Next 14 days</button>
          {crosshairOutsideResearchWindow ? <button type="button" className="fields-load-crosshair-window" onClick={() => {
            if (crosshairPageIndex !== null) setResearchPageIndex(crosshairPageIndex)
          }}>Load window containing crosshair</button> : null}
        </div>
        <button type="button" className="fields-founder-review-button" onClick={() => setFounderReviewOpen(true)} disabled={founderReviewOpen}><ClipboardCheck size={13} /> Founder Review</button>
        <label className="fields-classical-timing-toggle">
          <input
            type="checkbox"
            role="switch"
            checked={classicalTimingEnabled}
            onChange={(event) => setClassicalTimingEnabled(event.target.checked)}
          />
          <span><strong>BPHS Calendar</strong><small>1899 Research</small></span>
        </label>
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
      <div><b>Research range</b><span>{researchWindow ? 'Shared 14-day Fields page; price viewport remains visual only' : 'No usable loaded chart range'}</span></div>
    </section>

    <section className="fields-price-context" aria-label="Synchronized price chart">
      <header><Activity size={14} /><div><strong>Price and aspect context</strong><span>Shared crosshair, selected candle, and visible UTC range</span></div></header>
      <div className="fields-price-chart">{priceChart}</div>
    </section>

    <section className="fields-panes" aria-label="Synchronized independent fields">
      <IndependentFieldStack
        range={range}
        rangeSource={researchWindow ? 'shared 14-day Fields research window' : null}
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

    {classicalTimingEnabled && researchWindow ? <BphsClassicalTimingPane
      rangeStartUtc={researchWindow.rangeStartUtc}
      rangeEndUtc={researchWindow.rangeEndUtc}
      timezone="Asia/Kolkata"
      latitude={defaultLatitude}
      longitude={defaultLongitude}
      crosshairTimestampUtc={crosshairTimestampUtc}
      researchPageLabel={`page ${researchWindow.pageIndex + 1}/${researchWindow.pageCount}`}
    /> : null}

    <section className="fields-audit-details" aria-label="Field audit details">
      <div><ShieldCheck size={14} /><div><strong>Pair-relative field contract</strong><span>FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1 is a transparent modern research transform: USD side balance minus JPY side balance. It is not classical doctrine, a forecast, or SBC confirmation.</span></div></div>
      <div><RefreshCw size={14} /><div><strong>Independent SBC availability</strong><span>{vedhaProfileId === 'SBC_TRAILOKYA_1972_V1' ? 'GEOMETRY_ONLY_RANGE_NOT_IMPLEMENTED. No score, polarity, wave, or fallback.' : 'Atomic SBC availability remains independent from USD, JPY, and pair fields.'}</span></div></div>
      <div><Layers3 size={14} /><div><strong>Source gaps ({sourceGaps.length})</strong><span>{sourceGaps.length ? sourceGaps.map((gap) => gap.gapId).join(' | ') : 'No configured visualization-source gaps.'}</span></div></div>
    </section>
    </>}
  </section>
}
