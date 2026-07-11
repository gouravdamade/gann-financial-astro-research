import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Bot, CalendarDays, ChevronDown, PanelBottom, Search, Settings2, SlidersHorizontal } from 'lucide-react'
import {
  fetchChart,
  fetchEventDetail,
  fetchMt5Status,
  saveAnnotation,
} from '../api'
import { openAnalyzeAspect } from '../desktop'
import { ConnectionBadge } from '../components/ConnectionBadge'
import { EventTable } from '../components/EventTable'
import { InspectorPanel } from '../components/InspectorPanel'
import { MarketChart, type MarketChartHandle } from '../components/MarketChart'
import { ToolRail } from '../components/ToolRail'
import type {
  AnnotationDraft,
  AspectWindow,
  ChartAnnotation,
  ChartPayload,
  ChartTool,
  EventDetail,
  Mt5Status,
} from '../types'

export function MainWorkspace() {
  const [chart, setChart] = useState<ChartPayload | null>(null)
  const [status, setStatus] = useState<Mt5Status | null>(null)
  const [selected, setSelected] = useState<AspectWindow | null>(null)
  const [detail, setDetail] = useState<EventDetail | null>(null)
  const [selectedAnnotation, setSelectedAnnotation] = useState<ChartAnnotation | null>(null)
  const [activeTool, setActiveTool] = useState<ChartTool>('select')
  const [bottomTab, setBottomTab] = useState<'events' | 'positions' | 'logs'>('events')
  const [error, setError] = useState('')
  const chartRef = useRef<MarketChartHandle>(null)

  useEffect(() => {
    fetchChart()
      .then((payload) => {
        setChart(payload)
        const preferred = payload.aspects.find((item) => item.familyKey === 'TN::MOON->MERCURY::square')
        setSelected(preferred ?? payload.aspects[0] ?? null)
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
  }, [])

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
  if (!chart) {
    return <main className="loading-state"><span className="loading-bar" /><strong>Starting Gann Astro Desk</strong></main>
  }

  return (
    <main className="desk-shell">
      <header className="top-command-bar">
        <div className="product-mark">
          <span className="product-glyph">GA</span>
          <div><strong>Gann Astro Desk</strong><span>Research workspace</span></div>
        </div>
        <button className="symbol-control"><Search size={15} /><strong>{chart.symbol}</strong><ChevronDown size={14} /></button>
        <div className="segmented-control" aria-label="Timeframe">
          {['M30', 'H1', 'H4', 'D1'].map((timeframe) => <button key={timeframe} className={timeframe === chart.timeframe ? 'is-active' : ''}>{timeframe}</button>)}
        </div>
        <button className="date-control"><CalendarDays size={15} /> May 25-31, 2025</button>
        <div className="segmented-control mode-control"><button>TT</button><button className="is-active">TN</button></div>
        <div className="topbar-spacer" />
        <ConnectionBadge status={status} />
        <button className="icon-button" title="Astrology parameters"><SlidersHorizontal size={18} /></button>
        <button className="icon-button" title="Application settings"><Settings2 size={18} /></button>
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
            <span>Tokyo IPO hypothesis</span>
            <span>{chart.aspects.length} visible aspects</span>
            {selected && <strong style={{ color: selected.color }}>{selected.transitBody} to {selected.natalBody} {selected.aspectLabel}</strong>}
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
          <button className={bottomTab === 'positions' ? 'is-active' : ''} onClick={() => setBottomTab('positions')}>MT5 positions</button>
          <button className={bottomTab === 'logs' ? 'is-active' : ''} onClick={() => setBottomTab('logs')}>Connection log</button>
          <div className="bottom-tabs-spacer" />
          <span><Bot size={14} /> Codex analysis available inside Analyze Aspect</span>
        </div>
        {bottomTab === 'events' && <EventTable events={sortedAspects} selectedId={selected?.eventId} onSelect={selectAspect} />}
        {bottomTab === 'positions' && <div className="dock-empty">Order execution is disabled. The MT5 gateway is market-data only.</div>}
        {bottomTab === 'logs' && <div className="dock-empty">{status?.lastError || `Heartbeat current: ${status?.updatedAt ?? 'starting'}`}</div>}
      </section>
    </main>
  )
}
