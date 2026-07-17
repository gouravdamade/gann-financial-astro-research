import { lazy, Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  Activity,
  Bot,
  CalendarDays,
  Camera,
  ChevronDown,
  ChevronUp,
  CircleDot,
  Eye,
  EyeOff,
  Grid3X3,
  LockKeyhole,
  Maximize2,
  Minimize2,
  PanelBottom,
  PanelRightClose,
  PanelRightOpen,
  Search,
  ShieldCheck,
  Waves,
  X,
} from 'lucide-react'
import {
  fetchChart,
  fetchCandlestickShadow,
  fetchDataArtifacts,
  fetchEventDetail,
  fetchMt5Status,
  fetchParameterProfiles,
  fetchParameterSchema,
  fetchRuntimeDiagnostics,
  fetchShadowLedger,
  fetchWorkspacePreferences,
  requestProspectiveRefresh,
  recordFrontendDiagnostic,
  saveAnnotation,
  saveWorkspacePreferences,
  scanShadowLedger,
  scanCandlestickShadow,
} from '../api'
import { downloadLayoutJson } from '../chartLayouts'
import { effectiveAspectMinDurationMinutes, formatAspectDuration } from '../aspectTimeframePolicy'
import { openAnalyzeAspect } from '../desktop'
import { ConnectionBadge } from '../components/ConnectionBadge'
import { CandlestickShadowPanel } from '../components/CandlestickShadowPanel'
import { EventTable } from '../components/EventTable'
import { InspectorPanel } from '../components/InspectorPanel'
import { LayoutToolbar } from '../components/LayoutToolbar'
import { MarketChart, type MarketChartHandle } from '../components/MarketChart'
import { RefreshStatusChip } from '../components/RefreshStatusChip'
import { RuntimeDiagnosticsPanel } from '../components/RuntimeDiagnosticsPanel'
import { ShadowLedgerPanel } from '../components/ShadowLedgerPanel'
import { ToolRail } from '../components/ToolRail'
import { useChartLayouts } from '../useChartLayouts'
import { useVisibilityPolling } from '../useVisibilityPolling'
import type {
  AnnotationDraft,
  AspectWindow,
  ChartAnnotation,
  ChartPayload,
  ChartParameters,
  ChartTool,
  CandlestickShadowSnapshot,
  DataArtifact,
  EventDetail,
  Mt5Status,
  ParameterSchema,
  RuntimeDiagnosticsBundle,
  SavedParameterProfile,
  ShadowLedgerSnapshot,
  WorkspacePreferences,
} from '../types'

const DrawingObjectPanel = lazy(() => import('../components/DrawingObjectPanel').then((module) => ({
  default: module.DrawingObjectPanel,
})))
const ParameterDrawer = lazy(() => import('../components/ParameterDrawer').then((module) => ({
  default: module.ParameterDrawer,
})))
const SquareOfNineWorkspace = lazy(() => import('./SquareOfNineWorkspace').then((module) => ({
  default: module.SquareOfNineWorkspace,
})))
const ChakraLabWorkspace = lazy(() => import('./ChakraLabWorkspace').then((module) => ({
  default: module.ChakraLabWorkspace,
})))

function dateRangeLabel(parameters: ChartParameters | null): string {
  if (!parameters) return 'Date range'
  if (parameters.dataSource === 'live') return `Live ${parameters.liveBarCount} bars`
  const start = new Date(parameters.start)
  const end = new Date(parameters.end)
  return `${start.toLocaleDateString([], { month: 'short', day: 'numeric' })} - ${end.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}`
}

const WORKSPACE_PREFERENCES_KEY = 'gann-astro-desk.workspace.v1'
const APP_BOOTSTRAP_STARTED_AT = performance.now()

function recordAfterPaint(
  name: 'app_bootstrap' | 'chart_initial_render',
  startedAt: number,
): void {
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => {
      void recordFrontendDiagnostic(name, performance.now() - startedAt).catch(() => undefined)
    })
  })
}

function initialWorkspacePreferences(): WorkspacePreferences {
  const defaults: WorkspacePreferences = {
    inspectorOpen: true,
    bottomOpen: true,
    showAspects: true,
    showSrLines: true,
  }
  try {
    const saved = JSON.parse(window.localStorage.getItem(WORKSPACE_PREFERENCES_KEY) ?? '{}') as Partial<WorkspacePreferences>
    return { ...defaults, ...saved }
  } catch {
    return defaults
  }
}

function StatusClock() {
  const [clock, setClock] = useState(() => new Date())
  useEffect(() => {
    const timer = window.setInterval(() => setClock(new Date()), 1000)
    return () => window.clearInterval(timer)
  }, [])
  return <time>{clock.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })} IST</time>
}

export function MainWorkspace() {
  const [chart, setChart] = useState<ChartPayload | null>(null)
  const [schema, setSchema] = useState<ParameterSchema | null>(null)
  const [parameters, setParameters] = useState<ChartParameters | null>(null)
  const [profiles, setProfiles] = useState<SavedParameterProfile[]>([])
  const [status, setStatus] = useState<Mt5Status | null>(null)
  const [runtimeDiagnostics, setRuntimeDiagnostics] = useState<RuntimeDiagnosticsBundle | null>(null)
  const [runtimeDiagnosticsError, setRuntimeDiagnosticsError] = useState('')
  const [shadow, setShadow] = useState<ShadowLedgerSnapshot | null>(null)
  const [shadowBusy, setShadowBusy] = useState(false)
  const [refreshBusy, setRefreshBusy] = useState(false)
  const [shadowError, setShadowError] = useState('')
  const [candleShadow, setCandleShadow] = useState<CandlestickShadowSnapshot | null>(null)
  const [candleShadowBusy, setCandleShadowBusy] = useState(false)
  const [candleShadowError, setCandleShadowError] = useState('')
  const [selected, setSelected] = useState<AspectWindow | null>(null)
  const [detail, setDetail] = useState<EventDetail | null>(null)
  const [selectedAnnotation, setSelectedAnnotation] = useState<ChartAnnotation | null>(null)
  const [activeSurface, setActiveSurface] = useState<'chart' | 'square9' | 'chakra'>('chart')
  const [activeTool, setActiveTool] = useState<ChartTool>('select')
  const [toolActivationNonce, setToolActivationNonce] = useState(0)
  const [bottomTab, setBottomTab] = useState<'events' | 'shadow' | 'candle-shadow' | 'positions' | 'diagnostics'>('events')
  const [error, setError] = useState('')
  const [parameterError, setParameterError] = useState('')
  const [parametersOpen, setParametersOpen] = useState(false)
  const [chartLoading, setChartLoading] = useState(false)
  const [workspace, setWorkspace] = useState<WorkspacePreferences>(initialWorkspacePreferences)
  const [workspaceHydrated, setWorkspaceHydrated] = useState(false)
  const [focusMode, setFocusMode] = useState(false)
  const [objectsOpen, setObjectsOpen] = useState(false)
  const chartRef = useRef<MarketChartHandle>(null)
  const artifactActivationRef = useRef('')
  const inspectorVisible = activeSurface === 'chart' && workspace.inspectorOpen && !focusMode
  const bottomVisible = activeSurface === 'chart' && workspace.bottomOpen && !focusMode
  const restoreLayoutState = useCallback((state: { showAspects: boolean; showSrLines: boolean }) => {
    setWorkspace((current) => ({
      ...current,
      showAspects: state.showAspects,
      showSrLines: state.showSrLines,
    }))
  }, [])
  const chartLayouts = useChartLayouts({
    enabled: Boolean(chart),
    scope: {
      workspaceKind: 'main',
      symbol: chart?.symbol ?? parameters?.symbol ?? 'USDJPY',
      timeframe: chart?.timeframe ?? parameters?.timeframe ?? 'H1',
      familyKey: '',
    },
    initialChartState: {
      showAspects: workspace.showAspects,
      showSrLines: workspace.showSrLines,
    },
    onRestoreChartState: restoreLayoutState,
  })
  const activeChartLayout = chartLayouts.activeLayout
  const updateLayoutChartState = chartLayouts.updateChartState

  useEffect(() => {
    if (!activeChartLayout) return
    updateLayoutChartState({
      showAspects: workspace.showAspects,
      showSrLines: workspace.showSrLines,
    })
  }, [activeChartLayout, updateLayoutChartState, workspace.showAspects, workspace.showSrLines])

  useEffect(() => {
    let disposed = false
    fetchWorkspacePreferences()
      .then((preferences) => {
        if (!disposed) setWorkspace(preferences)
      })
      .catch(() => undefined)
      .finally(() => {
        if (!disposed) setWorkspaceHydrated(true)
      })
    return () => { disposed = true }
  }, [])

  const refreshCandlestickShadow = useCallback(async () => {
    try {
      setCandleShadow(await fetchCandlestickShadow())
      setCandleShadowError('')
    } catch (reason) {
      setCandleShadowError(reason instanceof Error ? reason.message : String(reason))
    }
  }, [])
  useVisibilityPolling(refreshCandlestickShadow, {
    enabled: bottomVisible && bottomTab === 'candle-shadow',
    intervalMs: 10000,
  })

  const runCandleShadowScan = useCallback(async () => {
    setCandleShadowBusy(true)
    setCandleShadowError('')
    try {
      setCandleShadow(await scanCandlestickShadow())
    } catch (reason) {
      setCandleShadowError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setCandleShadowBusy(false)
    }
  }, [])

  useEffect(() => {
    if (!workspaceHydrated) return
    window.localStorage.setItem(WORKSPACE_PREFERENCES_KEY, JSON.stringify(workspace))
    const timer = window.setTimeout(() => {
      void saveWorkspacePreferences(workspace).catch(() => undefined)
    }, 250)
    return () => window.clearTimeout(timer)
  }, [workspace, workspaceHydrated])

  useEffect(() => {
    const chartStartedAt = performance.now()
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
        recordAfterPaint('chart_initial_render', chartStartedAt)
        recordAfterPaint('app_bootstrap', APP_BOOTSTRAP_STARTED_AT)
        const preferred = payload.aspects.find((item) => item.familyKey === 'TN::MOON->MERCURY::square')
        setSelected(preferred ?? payload.aspects[0] ?? null)
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
  }, [])

  const refreshShadowLedger = useCallback(async () => {
    try {
      setShadow(await fetchShadowLedger())
      setShadowError('')
    } catch (reason) {
      setShadowError(reason instanceof Error ? reason.message : String(reason))
    }
  }, [])
  useVisibilityPolling(refreshShadowLedger, {
    intervalMs: bottomVisible && bottomTab === 'shadow' ? 10000 : 30000,
  })

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

  const runProspectiveRefresh = useCallback(async () => {
    setRefreshBusy(true)
    setShadowError('')
    try {
      const refresh = await requestProspectiveRefresh()
      setShadow((current) => current ? { ...current, refresh } : current)
    } catch (reason) {
      setShadowError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      window.setTimeout(() => setRefreshBusy(false), 1200)
    }
  }, [])

  const applyParameters = useCallback(async (nextParameters: ChartParameters) => {
    const startedAt = performance.now()
    let succeeded = false
    setChartLoading(true)
    setParameterError('')
    try {
      const payload = await fetchChart(nextParameters)
      setChart(payload)
      setParameters(nextParameters)
      setSelected((current) => payload.aspects.find((item) => item.eventId === current?.eventId) ?? payload.aspects[0] ?? null)
      setSelectedAnnotation(null)
      setParametersOpen(false)
      succeeded = true
    } catch (reason) {
      setParameterError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setChartLoading(false)
      void recordFrontendDiagnostic('chart_apply', performance.now() - startedAt, succeeded).catch(() => undefined)
    }
  }, [])

  const handleArtifactActivated = useCallback(async (artifact: DataArtifact) => {
    if (artifactActivationRef.current === artifact.artifactId) return
    artifactActivationRef.current = artifact.artifactId
    const startedAt = performance.now()
    let succeeded = false
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
      succeeded = true
    } catch (reason) {
      setParameterError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      artifactActivationRef.current = ''
      setChartLoading(false)
      void recordFrontendDiagnostic('artifact_activation', performance.now() - startedAt, succeeded).catch(() => undefined)
    }
  }, [])

  const refreshActiveArtifact = useCallback(async () => {
    if (!parameters || !chart || parameters.dataSource !== 'research') return
    try {
      const artifacts = await fetchDataArtifacts()
      const active = artifacts.find((artifact) => artifact.isActive)
      if (active && active.artifactId !== chart.artifact.artifactId) {
        await handleArtifactActivated(active)
      }
    } catch {
      // The parameter drawer exposes generation errors when the user is working there.
    }
  }, [chart, handleArtifactActivated, parameters])
  useVisibilityPolling(refreshActiveArtifact, {
    enabled: Boolean(parameters && chart && parameters.dataSource === 'research' && !parametersOpen),
    intervalMs: 10000,
  })

  const refreshLiveChart = useCallback(async () => {
    if (!parameters || parameters.dataSource !== 'live') return
    const startedAt = performance.now()
    try {
      setChart(await fetchChart(parameters))
      void recordFrontendDiagnostic('chart_live_refresh', performance.now() - startedAt).catch(() => undefined)
    } catch (reason) {
      void recordFrontendDiagnostic('chart_live_refresh', performance.now() - startedAt, false).catch(() => undefined)
      setParameterError(reason instanceof Error ? reason.message : String(reason))
    }
  }, [parameters])
  useVisibilityPolling(refreshLiveChart, {
    enabled: parameters?.dataSource === 'live',
    intervalMs: 5000,
  })

  const refreshMt5Status = useCallback(async () => {
    try {
      setStatus(await fetchMt5Status())
    } catch {
      // The last known state remains visible until the reconnect supervisor responds.
    }
  }, [])
  useVisibilityPolling(refreshMt5Status, { intervalMs: 5000 })

  const refreshRuntimeDiagnostics = useCallback(async () => {
    try {
      setRuntimeDiagnostics(await fetchRuntimeDiagnostics())
      setRuntimeDiagnosticsError('')
    } catch (reason) {
      setRuntimeDiagnosticsError(reason instanceof Error ? reason.message : String(reason))
    }
  }, [])
  useVisibilityPolling(refreshRuntimeDiagnostics, {
    enabled: bottomVisible && bottomTab === 'diagnostics',
    intervalMs: 10000,
  })

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
  const appliedAspectMinimum = Number(
    chart?.parametersApplied.effectiveMinDurationMinutes
    ?? (parameters ? effectiveAspectMinDurationMinutes(parameters) : 0),
  )
  const appliedAspectMinimumLabel = formatAspectDuration(appliedAspectMinimum)

  const selectBottomTab = useCallback((tab: 'events' | 'shadow' | 'candle-shadow' | 'positions' | 'diagnostics') => {
    setBottomTab(tab)
    setFocusMode(false)
    setWorkspace((current) => ({ ...current, bottomOpen: true }))
  }, [])
  const captureChart = useCallback(async () => {
    const dataUrl = await chartRef.current?.capture()
    if (!dataUrl) return
    const link = document.createElement('a')
    link.href = dataUrl
    link.download = `${chart?.symbol ?? 'chart'}_${chart?.timeframe ?? 'view'}_${new Date().toISOString().replaceAll(':', '-')}.png`
    link.click()
  }, [chart?.symbol, chart?.timeframe])

  if (error) {
    return <main className="fatal-state"><strong>Gann Astro Desk could not load</strong><span>{error}</span></main>
  }
  if (!chart || !schema || !parameters) {
    return <main className="loading-state"><span className="loading-bar" /><strong>Starting Gann Astro Desk</strong></main>
  }

  return (
    <main className={`desk-shell ${activeSurface === 'square9' ? 'square9-mode' : ''} ${activeSurface === 'chakra' ? 'chakra-mode' : ''} ${inspectorVisible ? '' : 'inspector-collapsed'} ${bottomVisible ? '' : 'bottom-collapsed'} ${focusMode ? 'focus-mode' : ''}`}>
      <header className="top-command-bar">
        <div className="product-mark">
          <span className="product-glyph">GA</span>
          <div><strong>Gann Astro Desk</strong><span>Market research terminal</span></div>
        </div>
        <div className="segmented-control workspace-surface-tabs" aria-label="Research workspace">
          <button className={activeSurface === 'chart' ? 'is-active' : ''} onClick={() => setActiveSurface('chart')}><Activity size={13} /> Chart</button>
          <button className={activeSurface === 'square9' ? 'is-active' : ''} onClick={() => { setActiveSurface('square9'); setFocusMode(false); setObjectsOpen(false) }}><Grid3X3 size={13} /> Square of Nine</button>
          <button className={activeSurface === 'chakra' ? 'is-active' : ''} onClick={() => { setActiveSurface('chakra'); setFocusMode(false); setObjectsOpen(false) }}><CircleDot size={13} /> Chakra</button>
        </div>
        <button className="symbol-control" onClick={() => setParametersOpen(true)}><Search size={15} /><strong>{chart.symbol}</strong><ChevronDown size={14} /></button>
        {activeSurface === 'chart' && <>
          <div className="segmented-control" aria-label="Timeframe">
            {schema.options.timeframes.map((timeframe) => <button key={timeframe} className={timeframe === chart.timeframe ? 'is-active' : ''} disabled={chartLoading} onClick={() => applyParameters({ ...parameters, timeframe })}>{timeframe}</button>)}
          </div>
          <button className="date-control" onClick={() => setParametersOpen(true)}><CalendarDays size={15} /> {dateRangeLabel(parameters)}</button>
          <div className="segmented-control mode-control"><button disabled title="Corrected TT generator pending">TT</button><button className="is-active">TN</button></div>
          <button className="secondary-command astro-command" onClick={() => setParametersOpen(true)} title="Configure planets, aspects, harmonics, reference chart, and data source"><Activity size={15} /> Astro layers</button>
        </>}
        <div className="topbar-spacer" />
        <RefreshStatusChip status={shadow?.refresh} busy={refreshBusy} onRefresh={runProspectiveRefresh} />
        <ConnectionBadge status={status} />
        {activeSurface === 'chart' && <>
          <button className="icon-button" onClick={() => void captureChart()} title="Download chart snapshot" aria-label="Download chart snapshot"><Camera size={18} /></button>
          <button className="icon-button" onClick={() => setFocusMode((value) => !value)} title={focusMode ? 'Restore panels' : 'Focus chart'} aria-label={focusMode ? 'Restore panels' : 'Focus chart'}>
            {focusMode ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
          </button>
          <button
            className={`icon-button ${workspace.inspectorOpen ? 'is-active' : ''}`}
            onClick={() => {
              setFocusMode(false)
              setWorkspace((current) => ({ ...current, inspectorOpen: !current.inspectorOpen }))
            }}
            title={workspace.inspectorOpen ? 'Hide aspect inspector' : 'Show aspect inspector'}
            aria-label={workspace.inspectorOpen ? 'Hide aspect inspector' : 'Show aspect inspector'}
          >
            {workspace.inspectorOpen ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
          </button>
        </>}
      </header>
      {activeSurface === 'chart' && <section className="workspace-grid">
        <ToolRail
          activeTool={activeTool}
          onToolChange={(tool) => {
            setActiveTool(tool)
            setToolActivationNonce((value) => value + 1)
          }}
          onUndo={chartLayouts.undo}
          onReset={() => chartRef.current?.resetView()}
          onClear={chartLayouts.clearDrawings}
        />
        <section className="chart-workspace">
          <div className="chart-context-strip">
            <div className="chart-context-primary">
              <strong>{chart.symbol}</strong>
              <span>{chart.timeframe}</span>
              <span>Raman sidereal</span>
              <span>{parameters.reference.label}</span>
              {selected && <em style={{ color: selected.color }}>{selected.transitBody} to {selected.natalBody} {selected.aspectLabel}</em>}
            </div>
            <div className="chart-context-spacer" />
            <LayoutToolbar
              layouts={chartLayouts.layouts}
              activeLayout={chartLayouts.activeLayout}
              saveStatus={chartLayouts.saveStatus}
              error={chartLayouts.error}
              objectsOpen={objectsOpen}
              objectCount={chartLayouts.drawings.length}
              onSelect={chartLayouts.switchLayout}
              onSave={chartLayouts.saveNow}
              onSaveAs={chartLayouts.saveAs}
              onDelete={chartLayouts.removeLayout}
              onToggleObjects={() => setObjectsOpen((value) => !value)}
              onExport={() => chartLayouts.activeLayout && downloadLayoutJson({
                ...chartLayouts.activeLayout,
                chartState: chartLayouts.chartState,
                drawings: chartLayouts.drawings,
              })}
              onImport={chartLayouts.importLayout}
            />
            <button
              className={workspace.showAspects ? 'is-active' : ''}
              onClick={() => setWorkspace((current) => ({ ...current, showAspects: !current.showAspects }))}
              title={`Show or hide aspects lasting at least ${appliedAspectMinimumLabel} on ${chart.timeframe}`}
            >
              {workspace.showAspects ? <Eye size={13} /> : <EyeOff size={13} />} Aspects {chart.aspects.length} · ≥{appliedAspectMinimumLabel}
            </button>
            <button
              className={workspace.showSrLines ? 'is-active' : ''}
              onClick={() => setWorkspace((current) => ({ ...current, showSrLines: !current.showSrLines }))}
              title="Show or hide planetary support and resistance lines"
            >
              <Waves size={13} /> SR {chart.srLines.length}
            </button>
            {chartLoading && <strong className="chart-loading-label">Updating chart</strong>}
          </div>
          <MarketChart
            ref={chartRef}
            payload={chart}
            selectedAspectId={selected?.eventId}
            selectedAnnotationId={selectedAnnotation?.annotationId}
            activeTool={activeTool}
            toolActivationNonce={toolActivationNonce}
            annotations={annotations}
            onSelectAspect={selectAspect}
            onSelectAnnotation={setSelectedAnnotation}
            onCreateAnnotation={createAnnotation}
            showAspects={workspace.showAspects}
            showSrLines={workspace.showSrLines}
            drawings={chartLayouts.drawings}
            selectedDrawingId={chartLayouts.selectedDrawingId}
            layoutKey={chartLayouts.activeLayout?.layoutId}
            viewState={chartLayouts.chartState}
            onDrawingsChange={chartLayouts.replaceDrawings}
            onSelectDrawing={(drawingId) => {
              chartLayouts.setSelectedDrawingId(drawingId)
              if (drawingId) {
                setActiveTool('select')
                setObjectsOpen(true)
              }
            }}
            onViewStateChange={chartLayouts.updateChartState}
            onUndo={chartLayouts.undo}
          />
          {objectsOpen && (
            <Suspense fallback={null}>
              <DrawingObjectPanel
                drawings={chartLayouts.drawings}
                templates={chartLayouts.templates}
                selectedDrawingId={chartLayouts.selectedDrawingId}
                onSelect={chartLayouts.setSelectedDrawingId}
                onUpdate={chartLayouts.updateDrawing}
                onDelete={chartLayouts.deleteDrawing}
                onCreateTemplate={chartLayouts.createTemplate}
                onRemoveTemplate={chartLayouts.removeTemplate}
                onClose={() => setObjectsOpen(false)}
              />
            </Suspense>
          )}
        </section>
        {inspectorVisible && (
          <InspectorPanel
            selected={selected}
            detail={detail}
            annotation={selectedAnnotation}
            onAnalyze={() => selected && openAnalyzeAspect(selected)}
            onAnnotationNoteChange={(note) => setSelectedAnnotation((value) => value ? { ...value, note } : value)}
            onSaveAnnotation={saveSelectedAnnotation}
          />
        )}
      </section>}
      {activeSurface === 'square9' && (
        <Suspense fallback={<div className="loading-state"><strong>Opening Square of Nine</strong></div>}>
          <SquareOfNineWorkspace
            symbol={chart.symbol}
            timeframe={chart.timeframe}
            latestPrice={chart.candles.at(-1)?.close ?? 1}
            state={chartLayouts.chartState.squareOfNine}
            onChange={(squareOfNine) => chartLayouts.updateChartState({ squareOfNine })}
            layoutToolbar={(
              <LayoutToolbar
                layouts={chartLayouts.layouts}
                activeLayout={chartLayouts.activeLayout}
                saveStatus={chartLayouts.saveStatus}
                error={chartLayouts.error}
                showObjects={false}
                onSelect={chartLayouts.switchLayout}
                onSave={chartLayouts.saveNow}
                onSaveAs={chartLayouts.saveAs}
                onDelete={chartLayouts.removeLayout}
                onExport={() => chartLayouts.activeLayout && downloadLayoutJson({
                  ...chartLayouts.activeLayout,
                  chartState: chartLayouts.chartState,
                  drawings: chartLayouts.drawings,
                })}
                onImport={chartLayouts.importLayout}
              />
            )}
          />
        </Suspense>
      )}
      {activeSurface === 'chakra' && (
        <Suspense fallback={<div className="loading-state"><strong>Opening Chakra Lab</strong></div>}>
          <ChakraLabWorkspace
            defaultLatitude={parameters.reference.latitude}
            defaultLongitude={parameters.reference.longitude}
          />
        </Suspense>
      )}
      {activeSurface === 'chart' && <section className={`bottom-dock ${bottomVisible ? '' : 'is-collapsed'}`}>
        <div className="bottom-tabs">
          <button className={bottomTab === 'events' && bottomVisible ? 'is-active' : ''} onClick={() => selectBottomTab('events')}><PanelBottom size={14} /> Events</button>
          <button className={bottomTab === 'shadow' && bottomVisible ? 'is-active' : ''} onClick={() => selectBottomTab('shadow')}><ShieldCheck size={14} /> Shadow validation</button>
          <button className={bottomTab === 'candle-shadow' && bottomVisible ? 'is-active' : ''} onClick={() => selectBottomTab('candle-shadow')}><Activity size={14} /> Candle shadow</button>
          <button className={bottomTab === 'positions' && bottomVisible ? 'is-active' : ''} onClick={() => selectBottomTab('positions')}>MT5 positions</button>
          <button className={bottomTab === 'diagnostics' && bottomVisible ? 'is-active' : ''} onClick={() => selectBottomTab('diagnostics')}>Diagnostics</button>
          <div className="bottom-tabs-spacer" />
          <span><Bot size={14} /> Codex + local Jyotish</span>
          <button
            className="bottom-collapse-button"
            onClick={() => {
              setFocusMode(false)
              setWorkspace((current) => ({ ...current, bottomOpen: !current.bottomOpen }))
            }}
            title={bottomVisible ? 'Collapse bottom panel' : 'Expand bottom panel'}
            aria-label={bottomVisible ? 'Collapse bottom panel' : 'Expand bottom panel'}
          >
            {bottomVisible ? <ChevronDown size={15} /> : <ChevronUp size={15} />}
          </button>
        </div>
        {bottomVisible && (
          <div className="bottom-dock-body">
            {bottomTab === 'events' && <EventTable events={sortedAspects} selectedId={selected?.eventId} onSelect={selectAspect} />}
            {bottomTab === 'shadow' && (
              <ShadowLedgerPanel
                snapshot={shadow}
                busy={shadowBusy}
                refreshBusy={refreshBusy}
                error={shadowError}
                onScan={runShadowScan}
                onRefresh={runProspectiveRefresh}
              />
            )}
            {bottomTab === 'candle-shadow' && (
              <CandlestickShadowPanel
                snapshot={candleShadow}
                busy={candleShadowBusy}
                error={candleShadowError}
                onScan={runCandleShadowScan}
              />
            )}
            {bottomTab === 'positions' && <div className="dock-empty">Order execution is disabled. The MT5 gateway is market-data only.</div>}
            {bottomTab === 'diagnostics' && (
              <RuntimeDiagnosticsPanel bundle={runtimeDiagnostics} error={runtimeDiagnosticsError || status?.lastError || ''} />
            )}
          </div>
        )}
      </section>}
      <footer className="workstation-status-bar">
        <span className={status?.connected ? 'is-live' : 'is-waiting'}><i /> {status?.connected ? 'Market data live' : 'Market data waiting'}</span>
        <span>{chart.candles.length} bars</span>
        <span>{chart.artifact.label}</span>
        <span className="status-spacer" />
        <span>{shadow?.refresh?.state === 'up_to_date' ? 'Artifact current' : shadow?.refresh?.state?.replaceAll('_', ' ') ?? 'Refresh checking'}</span>
        <span className="execution-locked"><LockKeyhole size={12} /> Read-only</span>
        <StatusClock />
      </footer>
      {parameterError && <div className="parameter-error" role="alert">{parameterError}<button onClick={() => setParameterError('')} title="Dismiss"><X size={14} /></button></div>}
      {parametersOpen && (
        <Suspense fallback={null}>
          <ParameterDrawer
            open
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
        </Suspense>
      )}
    </main>
  )
}
