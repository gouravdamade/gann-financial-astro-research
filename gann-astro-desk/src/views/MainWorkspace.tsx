import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Bot, CalendarDays, ChevronDown, PanelBottom, Search, ShieldCheck, SlidersHorizontal, X } from 'lucide-react'
import {
  fetchChart,
  fetchDataArtifacts,
  fetchEventDetail,
  fetchMt5Status,
  fetchParameterProfiles,
  fetchParameterSchema,
  fetchShadowLedger,
  saveAnnotation,
  scanShadowLedger,
} from '../api'
import { openAnalyzeAspect } from '../desktop'
import { ConnectionBadge } from '../components/ConnectionBadge'
import { EventTable } from '../components/EventTable'
import { InspectorPanel } from '../components/InspectorPanel'
import { MarketChart, type MarketChartHandle } from '../components/MarketChart'
import { ParameterDrawer } from '../components/ParameterDrawer'
import { ShadowLedgerPanel } from '../components/ShadowLedgerPanel'
import { ToolRail } from '../components/ToolRail'
import type {
  AnnotationDraft,
  AspectWindow,
  ChartAnnotation,
  ChartPayload,
  ChartParameters,
  ChartTool,
  DataArtifact,
  EventDetail,
  Mt5Status,
  ParameterSchema,
  SavedParameterProfile,
  ShadowLedgerSnapshot,
} from '../types'

function dateRangeLabel(parameters: ChartParameters | null): string {
  if (!parameters) return 'Date range'
  if (parameters.dataSource === 'live') return `Live ${parameters.liveBarCount} bars`
  const start = new Date(parameters.start)
  const end = new Date(parameters.end)
  return `${start.toLocaleDateString([], { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}`
}

export function MainWorkspace() {
  const [chart, setChart] = useState<ChartPayload | null>(null)
  const [schema, setSchema] = useState<ParameterSchema | null>(null)
  const [parameters, setParameters] = useState<ChartParameters | null>(null)
  const [profiles, setProfiles] = useState<SavedParameterProfile[]>([])
  const [status, setStatus] = useState<Mt5Status | null>(null)
  const [shadow, setShadow] = useState<ShadowLedgerSnapshot | null>(null)
  const [shadowBusy, setShadowBusy] = useState(false)
  const [shadowError, setShadowError] = useState('')
  const [selected, setSelected] = useState<AspectWindow | null>(null)
  const [detail, setDetail] = useState<EventDetail | null>(null)
  const [selectedAnnotation, setSelectedAnnotation] = useState<ChartAnnotation | null>(null)
  const [activeTool, setActiveTool] = useState<ChartTool>('select')
  const [bottomTab, setBottomTab] = useState<'events' | 'shadow' | 'positions' | 'logs'>('events')
  const [error, setError] = useState('')
  const [parameterError, setParameterError] = useState('')
  const [parametersOpen, setParametersOpen] = useState(false)
  const [chartLoading, setChartLoading] = useState(false)
  const chartRef = useRef<MarketChartHandle>(null)
  const artifactActivationRef = useRef('')

  useEffect(() => {
    Promise.all([fetchParameterSchema(), fetchParameterProfiles()])
      .then(async ([parameterSchema, savedProfiles]) => {
        const preferredProfile = savedProfiles.find((item) => item.isDefault)
        const initialParameters = preferredProfile && parameterSchema.generation.activeArtifactId === 'baseline'
          ? {
              ...parameterSchema.defaults,
              ...preferredProfile.parameters,
              reference: {
                ...parameterSchema.defaults.reference,
                ...preferredProfile.parameters.reference,
              },
            }
          : parameterSchema.defaults
        setSchema(parameterSchema)
        setProfiles(savedProfiles)
        setParameters(initialParameters)
        const payload = await fetchChart(initialParameters)
        setChart(payload)
        const preferred = payload.aspects.find((item) => item.familyKey === 'TN::MOON->MERCURY::square')
        setSelected(preferred ?? payload.aspects[0] ?? null)
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
  }, [])

  useEffect(() => {
    let disposed = false
    const refresh = () => fetchShadowLedger()
      .then((value) => {
        if (!disposed) {
          setShadow(value)
          setShadowError('')
        }
      })
      .catch((reason) => !disposed && setShadowError(reason instanceof Error ? reason.message : String(reason)))
    refresh()
    const timer = window.setInterval(refresh, 10000)
    return () => {
      disposed = true
      window.clearInterval(timer)
    }
  }, [])

  const runShadowScan = useCallback(async () => {
    setShadowBusy(true)
    setShadowError('')
    try {
      setShadow(await scanShadowLedger())
    } catch (reason) {
      setShadowError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setShadowBusy(false)
    }
  }, [])

  const applyParameters = useCallback(async (nextParameters: ChartParameters) => {
    setChartLoading(true)
    setParameterError('')
    try {
      const payload = await fetchChart(nextParameters)
      setChart(payload)
      setParameters(nextParameters)
      setSelected((current) => payload.aspects.find((item) => item.eventId === current?.eventId) ?? payload.aspects[0] ?? null)
      setSelectedAnnotation(null)
      setParametersOpen(false)
    } catch (reason) {
      setParameterError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setChartLoading(false)
    }
  }, [])

  const handleArtifactActivated = useCallback(async (artifact: DataArtifact) => {
    if (artifactActivationRef.current === artifact.artifactId) return
    artifactActivationRef.current = artifact.artifactId
    setChartLoading(true)
    setParameterError('')
    try {
      const nextSchema = await fetchParameterSchema()
      const nextParameters: ChartParameters = {
        ...nextSchema.defaults,
        ...artifact.parameters,
        reference: {
          ...nextSchema.defaults.reference,
          ...(artifact.parameters?.reference ?? {}),
        },
        dataSource: 'research',
      }
      const payload = await fetchChart(nextParameters)
      setSchema(nextSchema)
      setParameters(nextParameters)
      setChart(payload)
      setSelected(payload.aspects[0] ?? null)
      setSelectedAnnotation(null)
    } catch (reason) {
      setParameterError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      artifactActivationRef.current = ''
      setChartLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!parameters || !chart || parameters.dataSource !== 'research') return
    let disposed = false
    const refresh = () => fetchDataArtifacts()
      .then((artifacts) => {
        if (disposed) return
        const active = artifacts.find((artifact) => artifact.isActive)
        if (active && active.artifactId !== chart?.artifact.artifactId) {
          void handleArtifactActivated(active)
        }
      })
      .catch(() => undefined)
    refresh()
    const timer = window.setInterval(refresh, 3000)
    return () => {
      disposed = true
      window.clearInterval(timer)
    }
  }, [chart, handleArtifactActivated, parameters])

  useEffect(() => {
    if (!parameters || parameters.dataSource !== 'live') return
    const timer = window.setInterval(() => {
      fetchChart(parameters)
        .then((payload) => setChart(payload))
        .catch((reason) => setParameterError(reason instanceof Error ? reason.message : String(reason)))
    }, 5000)
    return () => window.clearInterval(timer)
  }, [parameters])

  useEffect(() => {
    let disposed = false
    const refresh = () => fetchMt5Status().then((value) => !disposed && setStatus(value)).catch(() => undefined)
    refresh()
    const timer = window.setInterval(refresh, 2500)
    return () => {
      disposed = true
      window.clearInterval(timer)
    }
  }, [])

  useEffect(() => {
    if (!selected) {
      setDetail(null)
      return
    }
    fetchEventDetail(selected.eventId)
      .then((value) => {
        setDetail(value)
        setSelectedAnnotation(null)
      })
      .catch(() => setDetail(null))
  }, [selected])

  const annotations = detail?.annotations ?? []
  const selectAspect = useCallback((aspect: AspectWindow) => {
    setSelected(aspect)
    setActiveTool('select')
  }, [])

  const createAnnotation = useCallback(async (draft: AnnotationDraft) => {
    const saved = await saveAnnotation(draft)
    setDetail((current) => current ? { ...current, annotations: [...current.annotations, saved] } : current)
    setSelectedAnnotation(saved)
    setActiveTool('select')
  }, [])

  const saveSelectedAnnotation = useCallback(async () => {
    if (!selectedAnnotation) return
    const saved = await saveAnnotation(selectedAnnotation)
    setSelectedAnnotation(saved)
    setDetail((current) => current
      ? { ...current, annotations: current.annotations.map((item) => item.annotationId === saved.annotationId ? saved : item) }
      : current)
  }, [selectedAnnotation])

  const sortedAspects = useMemo(
    () => chart?.aspects.slice().sort((a, b) => a.start - b.start) ?? [],
    [chart],
  )

  if (error) {
    return <main className="fatal-state"><strong>Gann Astro Desk could not load</strong><span>{error}</span></main>
  }
  if (!chart || !schema || !parameters) {
    return <main className="loading-state"><span className="loading-bar" /><strong>Starting Gann Astro Desk</strong></main>
  }

  return (
    <main className="desk-shell">
      <header className="top-command-bar">
        <div className="product-mark">
          <span className="product-glyph">GA</span>
          <div><strong>Gann Astro Desk</strong><span>Research workspace</span></div>
        </div>
        <button className="symbol-control" onClick={() => setParametersOpen(true)}><Search size={15} /><strong>{chart.symbol}</strong><ChevronDown size={14} /></button>
        <div className="segmented-control" aria-label="Timeframe">
          {schema.options.timeframes.map((timeframe) => <button key={timeframe} className={timeframe === chart.timeframe ? 'is-active' : ''} disabled={chartLoading} onClick={() => applyParameters({ ...parameters, timeframe })}>{timeframe}</button>)}
        </div>
        <button className="date-control" onClick={() => setParametersOpen(true)}><CalendarDays size={15} /> {dateRangeLabel(parameters)}</button>
        <div className="segmented-control mode-control"><button disabled title="Corrected TT generator pending">TT</button><button className="is-active">TN</button></div>
        <div className="topbar-spacer" />
        <ConnectionBadge status={status} />
        <button className="icon-button" onClick={() => setParametersOpen(true)} title="Astrology parameters"><SlidersHorizontal size={18} /></button>
      </header>
      <section className="workspace-grid">
        <ToolRail
          activeTool={activeTool}
          onToolChange={setActiveTool}
          onReset={() => chartRef.current?.resetView()}
          onClear={() => chartRef.current?.clearDrawings()}
        />
        <section className="chart-workspace">
          <div className="chart-context-strip">
            <span>Raman sidereal</span>
            <span>{parameters.reference.label}</span>
            <span>{chart.artifact.label}</span>
            <span>{chart.aspects.length} visible aspects</span>
            <span>{chart.dataSource === 'mt5_live' ? 'MT5 live bars' : chart.timeframe + ' archive'}</span>
            {selected && <strong style={{ color: selected.color }}>{selected.transitBody} to {selected.natalBody} {selected.aspectLabel}</strong>}
            {chartLoading && <strong className="chart-loading-label">Updating chart</strong>}
          </div>
          <MarketChart
            ref={chartRef}
            payload={chart}
            selectedAspectId={selected?.eventId}
            selectedAnnotationId={selectedAnnotation?.annotationId}
            activeTool={activeTool}
            annotations={annotations}
            onSelectAspect={selectAspect}
            onSelectAnnotation={setSelectedAnnotation}
            onCreateAnnotation={createAnnotation}
          />
        </section>
        <InspectorPanel
          selected={selected}
          detail={detail}
          annotation={selectedAnnotation}
          onAnalyze={() => selected && openAnalyzeAspect(selected)}
          onAnnotationNoteChange={(note) => setSelectedAnnotation((value) => value ? { ...value, note } : value)}
          onSaveAnnotation={saveSelectedAnnotation}
        />
      </section>
      <section className="bottom-dock">
        <div className="bottom-tabs">
          <button className={bottomTab === 'events' ? 'is-active' : ''} onClick={() => setBottomTab('events')}><PanelBottom size={14} /> Events</button>
          <button className={bottomTab === 'shadow' ? 'is-active' : ''} onClick={() => setBottomTab('shadow')}><ShieldCheck size={14} /> Shadow validation</button>
          <button className={bottomTab === 'positions' ? 'is-active' : ''} onClick={() => setBottomTab('positions')}>MT5 positions</button>
          <button className={bottomTab === 'logs' ? 'is-active' : ''} onClick={() => setBottomTab('logs')}>Connection log</button>
          <div className="bottom-tabs-spacer" />
          <span><Bot size={14} /> Codex analysis available inside Analyze Aspect</span>
        </div>
        {bottomTab === 'events' && <EventTable events={sortedAspects} selectedId={selected?.eventId} onSelect={selectAspect} />}
        {bottomTab === 'shadow' && <ShadowLedgerPanel snapshot={shadow} busy={shadowBusy} error={shadowError} onScan={runShadowScan} />}
        {bottomTab === 'positions' && <div className="dock-empty">Order execution is disabled. The MT5 gateway is market-data only.</div>}
        {bottomTab === 'logs' && <div className="dock-empty">{status?.lastError || `Heartbeat current: ${status?.updatedAt ?? 'starting'}`}</div>}
      </section>
      {parameterError && <div className="parameter-error" role="alert">{parameterError}<button onClick={() => setParameterError('')} title="Dismiss"><X size={14} /></button></div>}
      <ParameterDrawer
        open={parametersOpen}
        busy={chartLoading}
        schema={schema}
        parameters={parameters}
        profiles={profiles}
        activeArtifactId={chart.artifact.artifactId}
        onClose={() => setParametersOpen(false)}
        onApply={applyParameters}
        onArtifactActivated={handleArtifactActivated}
        onProfilesChange={setProfiles}
      />
    </main>
  )
}
