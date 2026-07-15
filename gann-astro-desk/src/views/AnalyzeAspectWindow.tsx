import {
  ArrowLeft,
  ArrowRight,
  Bot,
  BrainCircuit,
  CandlestickChart,
  Check,
  ChevronLeft,
  Filter,
  LoaderCircle,
  MessageSquareText,
  Microscope,
  RefreshCw,
  Save,
  ShieldCheck,
  SlidersHorizontal,
  Trash2,
  X,
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  deleteAnnotation,
  fetchEventDetail,
  fetchFamily,
  fetchLiveDecision,
  saveAnnotation,
  saveReviewStatus,
} from '../api'
import { downloadLayoutJson } from '../chartLayouts'
import { CodexPanel } from '../components/CodexPanel'
import { CandlestickPanel } from '../components/CandlestickPanel'
import { DrawingObjectPanel } from '../components/DrawingObjectPanel'
import { LayoutToolbar } from '../components/LayoutToolbar'
import { LocalJyotishPanel } from '../components/LocalJyotishPanel'
import { MarketChart, type MarketChartHandle } from '../components/MarketChart'
import { ToolRail } from '../components/ToolRail'
import { canToggleReview, nextReviewStatus, reviewButtonLabel } from '../reviewProgress'
import { useChartLayouts } from '../useChartLayouts'
import type {
  AnnotationDraft,
  AspectFamily,
  AspectWindow,
  ChartAnnotation,
  ChartTool,
  DecisionPacket,
  EventDetail,
} from '../types'

type AnalyzeAspectWindowProps = {
  familyKey: string
  initialEventId?: string | null
}

type InspectorTab = 'evidence' | 'annotations' | 'candles' | 'jyotish' | 'codex'
type OccurrenceFilter = 'all' | 'reviewed' | 'pending' | 'bullish' | 'bearish'

function resultLabel(occurrence: AspectWindow): string {
  if (occurrence.returnPct == null) return 'No outcome'
  return `${occurrence.returnPct > 0 ? '+' : ''}${occurrence.returnPct.toFixed(2)}%`
}

function evidenceCutoff(detail: EventDetail): string {
  const eventStart = new Date(detail.event.startIso).getTime()
  const eventEnd = new Date(detail.event.endIso).getTime()
  const touchValue = detail.context.touch_time_local
  const touchTime = typeof touchValue === 'string' ? new Date(touchValue).getTime() : Number.NaN
  const timeframe = String(detail.chart.artifact.sourceTimeframe || detail.chart.timeframe).toUpperCase()
  const durationMinutes = timeframe === 'M30' ? 30 : timeframe === 'H4' ? 240 : timeframe === 'D1' ? 1440 : 60
  if (!Number.isFinite(touchTime)) return new Date(eventEnd).toISOString()
  const touchClose = touchTime + durationMinutes * 60_000
  return new Date(Math.max(eventStart, touchClose)).toISOString()
}

export function AnalyzeAspectWindow({ familyKey, initialEventId }: AnalyzeAspectWindowProps) {
  const [family, setFamily] = useState<AspectFamily | null>(null)
  const [selectedEventId, setSelectedEventId] = useState(initialEventId ?? '')
  const [detail, setDetail] = useState<EventDetail | null>(null)
  const [activeTool, setActiveTool] = useState<ChartTool>('select')
  const [toolActivationNonce, setToolActivationNonce] = useState(0)
  const [tab, setTab] = useState<InspectorTab>('evidence')
  const [filter, setFilter] = useState<OccurrenceFilter>('all')
  const [selectedAnnotation, setSelectedAnnotation] = useState<ChartAnnotation | null>(null)
  const [reviewSaving, setReviewSaving] = useState(false)
  const [decisionPacket, setDecisionPacket] = useState<DecisionPacket | null>(null)
  const [decisionLoading, setDecisionLoading] = useState(false)
  const [decisionError, setDecisionError] = useState('')
  const [error, setError] = useState('')
  const [objectsOpen, setObjectsOpen] = useState(false)
  const chartRef = useRef<MarketChartHandle>(null)
  const chartLayouts = useChartLayouts({
    enabled: Boolean(detail),
    scope: {
      workspaceKind: 'analysis',
      symbol: detail?.chart.symbol ?? 'USDJPY',
      timeframe: detail?.chart.timeframe ?? 'H1',
      familyKey,
    },
    initialChartState: { showAspects: true, showSrLines: true },
  })

  useEffect(() => {
    fetchFamily(familyKey, initialEventId ?? undefined)
      .then((value) => {
        setFamily(value)
        setSelectedEventId((current) => current || value.selectedEventId)
      })
      .catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
  }, [familyKey, initialEventId])

  useEffect(() => {
    if (!selectedEventId) return
    setDetail(null)
    setSelectedAnnotation(null)
    setDecisionPacket(null)
    setDecisionError('')
    fetchEventDetail(selectedEventId)
      .then(setDetail)
      .catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
  }, [selectedEventId])

  const runCutoffDecision = useCallback(async (eventId: string, decisionTime: string) => {
    setDecisionLoading(true)
    setDecisionError('')
    try {
      setDecisionPacket(await fetchLiveDecision(eventId, decisionTime))
    } catch (reason) {
      setDecisionPacket(null)
      setDecisionError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setDecisionLoading(false)
    }
  }, [])

  useEffect(() => {
    if (!detail) return
    void runCutoffDecision(detail.event.eventId, evidenceCutoff(detail))
  }, [detail, runCutoffDecision])

  const selectedOccurrence = useMemo(
    () => family?.occurrences.find((item) => item.eventId === selectedEventId) ?? null,
    [family, selectedEventId],
  )
  const filteredOccurrences = useMemo(() => {
    if (!family) return []
    if (filter === 'all') return family.occurrences
    if (filter === 'reviewed') return family.occurrences.filter((item) => item.reviewed)
    if (filter === 'pending') return family.occurrences.filter((item) => !item.reviewed)
    if (filter === 'bullish') return family.occurrences.filter((item) => item.outcome === 'UP')
    return family.occurrences.filter((item) => item.outcome === 'DOWN')
  }, [family, filter])

  const selectedIndex = family?.occurrences.findIndex((item) => item.eventId === selectedEventId) ?? -1
  const navigate = (direction: -1 | 1) => {
    if (!family || selectedIndex < 0) return
    const next = Math.max(0, Math.min(family.occurrences.length - 1, selectedIndex + direction))
    setSelectedEventId(family.occurrences[next].eventId)
  }

  const createAnnotation = useCallback(async (draft: AnnotationDraft) => {
    const saved = await saveAnnotation(draft)
    setDetail((current) => current ? { ...current, annotations: [...current.annotations, saved] } : current)
    setSelectedAnnotation(saved)
    setTab('annotations')
    setActiveTool('select')
  }, [])

  const updateSelectedAnnotation = async () => {
    if (!selectedAnnotation) return
    const saved = await saveAnnotation(selectedAnnotation)
    setSelectedAnnotation(saved)
    setDetail((current) => current
      ? { ...current, annotations: current.annotations.map((item) => item.annotationId === saved.annotationId ? saved : item) }
      : current)
  }

  const removeSelectedAnnotation = async () => {
    if (!selectedAnnotation) return
    await deleteAnnotation(selectedAnnotation.annotationId)
    const id = selectedAnnotation.annotationId
    setSelectedAnnotation(null)
    setDetail((current) => current
      ? { ...current, annotations: current.annotations.filter((item) => item.annotationId !== id) }
      : current)
  }

  const toggleReviewStatus = async () => {
    if (!selectedOccurrence || reviewSaving || !canToggleReview(selectedOccurrence)) return
    setReviewSaving(true)
    try {
      const nextStatus = nextReviewStatus(selectedOccurrence)
      await saveReviewStatus(selectedOccurrence.eventId, nextStatus)
      const [nextFamily, nextDetail] = await Promise.all([
        fetchFamily(familyKey, selectedOccurrence.eventId),
        fetchEventDetail(selectedOccurrence.eventId),
      ])
      setFamily(nextFamily)
      setDetail(nextDetail)
    } finally {
      setReviewSaving(false)
    }
  }

  if (error) return <main className="fatal-state"><strong>Analyze Aspect could not open</strong><span>{error}</span></main>
  if (!family || !detail || !selectedOccurrence) {
    return <main className="loading-state"><span className="loading-bar" /><strong>Loading aspect family</strong></main>
  }

  return (
    <main className="analyze-shell">
      <header className="analyze-topbar">
        <button className="icon-button" onClick={() => window.close()} title="Close Analyze Aspect"><ChevronLeft size={19} /></button>
        <div className="analyze-title">
          <span className="eyebrow">Analyze Aspect</span>
          <h1>{family.transitBody} to {family.natalBody} <span>{selectedOccurrence.aspectLabel}</span></h1>
        </div>
        <span className="family-key-label">{family.familyKey}</span>
        <div className="analyze-topbar-spacer" />
        <button className="secondary-command"><SlidersHorizontal size={15} /> Family parameters</button>
        <button
          className={`secondary-command ${selectedOccurrence.reviewed ? 'is-complete' : ''}`}
          onClick={toggleReviewStatus}
          disabled={reviewSaving || !canToggleReview(selectedOccurrence)}
          title={selectedOccurrence.reviewSource === 'legacy_completed_review' ? 'Completed in the legacy review database' : 'Update this occurrence review status'}
        >
          <Check size={15} />
          {reviewButtonLabel(selectedOccurrence, reviewSaving)}
        </button>
        <button className="icon-button" onClick={() => window.close()} title="Close"><X size={18} /></button>
      </header>
      <section className="analyze-layout">
        <aside className="occurrence-sidebar">
          <header>
            <div><strong>Occurrences</strong><span>{family.summary.total} total</span></div>
            <Filter size={15} />
          </header>
          <div className="occurrence-filter">
            {(['all', 'pending', 'reviewed', 'bullish', 'bearish'] as OccurrenceFilter[]).map((item) => (
              <button key={item} className={filter === item ? 'is-active' : ''} onClick={() => setFilter(item)}>{item}</button>
            ))}
          </div>
          <div className="occurrence-list">
            {filteredOccurrences.map((occurrence) => (
              <button
                key={occurrence.eventId}
                className={`occurrence-item ${occurrence.eventId === selectedEventId ? 'is-selected' : ''}`}
                onClick={() => setSelectedEventId(occurrence.eventId)}
              >
                <span className="occurrence-number">{String(occurrence.occurrenceIndex).padStart(2, '0')}</span>
                <div>
                  <strong>{new Date(occurrence.start * 1000).toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' })}</strong>
                  <span>{new Date(occurrence.start * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <div className={`occurrence-result ${occurrence.outcome === 'UP' ? 'positive' : occurrence.outcome === 'DOWN' ? 'negative' : ''}`}>
                  {resultLabel(occurrence)}
                  <span>{occurrence.reviewed ? 'reviewed' : 'pending'}</span>
                </div>
              </button>
            ))}
          </div>
        </aside>
        <section className="analyze-chart-column">
          <div className="occurrence-nav">
            <button onClick={() => navigate(-1)} disabled={selectedIndex <= 0}><ArrowLeft size={15} /> Previous</button>
            <div>
              <strong>Occurrence {selectedIndex + 1} of {family.summary.total}</strong>
              <span>{new Date(selectedOccurrence.start * 1000).toLocaleString()} | case {selectedOccurrence.caseId ?? 'not touched'}</span>
            </div>
            <button onClick={() => navigate(1)} disabled={selectedIndex >= family.summary.total - 1}>Next <ArrowRight size={15} /></button>
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
          </div>
          <div className="analyze-chart-row">
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
            <MarketChart
              ref={chartRef}
              payload={detail.chart}
              selectedAspectId={selectedEventId}
              selectedAnnotationId={selectedAnnotation?.annotationId}
              activeTool={activeTool}
              toolActivationNonce={toolActivationNonce}
              annotations={detail.annotations}
              onSelectAspect={(aspect) => {
                if (aspect.familyKey === family.familyKey) setSelectedEventId(aspect.eventId)
              }}
              onSelectAnnotation={(annotation) => {
                setSelectedAnnotation(annotation)
                setTab('annotations')
              }}
              onCreateAnnotation={createAnnotation}
              showAspects={chartLayouts.chartState.showAspects}
              showSrLines={chartLayouts.chartState.showSrLines}
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
            )}
          </div>
          <footer className="family-summary-strip">
            <span><strong>{family.summary.bullish}</strong> bullish</span>
            <span><strong>{family.summary.bearish}</strong> bearish</span>
            <span><strong>{family.summary.unknown}</strong> unknown</span>
            <span><strong>{family.summary.reviewed}/{family.summary.total}</strong> reviewed</span>
            <span><strong>{family.summary.averageReturnPct == null ? '-' : `${family.summary.averageReturnPct > 0 ? '+' : ''}${family.summary.averageReturnPct}%`}</strong> average 72h</span>
          </footer>
        </section>
        <aside className="analysis-inspector">
          <div className="analysis-tabs">
            <button className={tab === 'evidence' ? 'is-active' : ''} onClick={() => setTab('evidence')}><Microscope size={15} /> Evidence</button>
            <button className={tab === 'annotations' ? 'is-active' : ''} onClick={() => setTab('annotations')} title="Chart annotations"><MessageSquareText size={15} /> Notes</button>
            <button className={tab === 'candles' ? 'is-active' : ''} onClick={() => setTab('candles')}><CandlestickChart size={15} /> Candles</button>
            <button className={tab === 'jyotish' ? 'is-active' : ''} onClick={() => setTab('jyotish')}><BrainCircuit size={15} /> Local Jyotish</button>
            <button className={tab === 'codex' ? 'is-active' : ''} onClick={() => setTab('codex')}><Bot size={15} /> Codex</button>
          </div>
          {tab === 'evidence' && (
            <div className="analysis-tab-body">
              <section className="evidence-summary">
                <span className="eyebrow">Observed outcome</span>
                <strong className={selectedOccurrence.outcome === 'UP' ? 'positive' : selectedOccurrence.outcome === 'DOWN' ? 'negative' : ''}>
                  {selectedOccurrence.outcome ?? 'Pending'} {selectedOccurrence.returnPct == null ? '' : `${selectedOccurrence.returnPct > 0 ? '+' : ''}${selectedOccurrence.returnPct.toFixed(2)}%`}
                </strong>
                <p>Observed outcome is a retrospective label and is not available to live inference.</p>
              </section>
              <section className={`live-decision ${decisionPacket?.status ?? 'loading'}`}>
                <header>
                  <div><ShieldCheck size={16} /><strong>Timestamp-safe inference</strong></div>
                  <button
                    className="icon-button"
                    onClick={() => runCutoffDecision(selectedEventId, evidenceCutoff(detail))}
                    disabled={decisionLoading}
                    title="Recalculate when the selected touch candle is closed"
                  >
                    {decisionLoading ? <LoaderCircle size={15} /> : <RefreshCw size={15} />}
                  </button>
                </header>
                {decisionPacket ? (
                  <>
                    <div className="live-decision-result">
                      <strong>{decisionPacket.decision.action.replace('_', ' ')}</strong>
                      <span>{decisionPacket.status}</span>
                    </div>
                    <p>{decisionPacket.decision.reason}</p>
                    <dl>
                      <div><dt>Decision cutoff</dt><dd>{new Date(decisionPacket.times.decisionTime).toLocaleString()}</dd></div>
                      <div><dt>Signal available</dt><dd>{decisionPacket.times.signalTime ? new Date(decisionPacket.times.signalTime).toLocaleString() : 'no closed touch'}</dd></div>
                      <div><dt>Closed evidence through</dt><dd>{decisionPacket.times.sourceDataMaxTime ? new Date(decisionPacket.times.sourceDataMaxTime).toLocaleString() : 'none'}</dd></div>
                      <div><dt>Direction source</dt><dd>{decisionPacket.decision.directionSource.replaceAll('_', ' ')}</dd></div>
                      <div><dt>Packet</dt><dd>{decisionPacket.packetId.slice(0, 12)}</dd></div>
                    </dl>
                    <div className="decision-guards">
                      <span className={decisionPacket.guardrails.timestampSafe ? 'is-safe' : ''}>timestamp safe</span>
                      <span className={decisionPacket.guardrails.noLookahead ? 'is-safe' : ''}>no lookahead</span>
                      <span>outcome excluded</span>
                      <span>execution locked</span>
                    </div>
                    {decisionPacket.policyLocks && (
                      <div className="decision-validation-lock">
                        <strong>Historical gate failed</strong>
                        <span>54.26% hit rate; 95% interval crossed 50%. Research watch only.</span>
                      </div>
                    )}
                    {decisionPacket.evidence && Object.keys(decisionPacket.evidence).length > 0 && (
                      <div className="decision-evidence">
                        {Object.entries(decisionPacket.evidence).slice(0, 6).map(([key, value]) => (
                          <div key={key}><span>{key.replaceAll('_', ' ')}</span><strong>{String(value)}</strong></div>
                        ))}
                      </div>
                    )}
                  </>
                ) : (
                  <p>{decisionError || 'Calculating from evidence available at the event cutoff.'}</p>
                )}
              </section>
              <div className="evidence-list">
                {detail.astroEvidence.map((item) => (
                  <div className="evidence-item" key={item.key}>
                    <div><span>{item.label}</span><small>{item.certification}</small></div>
                    <strong>{typeof item.value === 'number' ? item.value.toFixed(3) : item.value}<small>{item.unit === 'text' ? '' : ` ${item.unit}`}</small></strong>
                  </div>
                ))}
              </div>
              <div className="doctrine-note">
                <strong>Interpretation boundary</strong>
                <p>{String(detail.context.event_strict_shadbala_decision_notes ?? 'Astrology evidence is provisional until external validation is complete.')}</p>
              </div>
            </div>
          )}
          {tab === 'annotations' && (
            <div className="analysis-tab-body annotation-tab">
              <header><strong>{detail.annotations.length} annotations</strong><span>Chart-linked research notes</span></header>
              <div className="annotation-list">
                {detail.annotations.map((annotation, index) => (
                  <button
                    key={annotation.annotationId}
                    className={annotation.annotationId === selectedAnnotation?.annotationId ? 'is-selected' : ''}
                    onClick={() => setSelectedAnnotation(annotation)}
                  >
                    <span style={{ borderColor: annotation.color }}>A{index + 1}</span>
                    <div><strong>{annotation.note || 'Untitled annotation'}</strong><small>{new Date(annotation.anchorTimeUtc).toLocaleString()} @ {annotation.anchorPrice?.toFixed(3)}</small></div>
                  </button>
                ))}
                {!detail.annotations.length && <div className="empty-inline">No annotations yet.</div>}
              </div>
              {selectedAnnotation && (
                <div className="annotation-detail-editor">
                  <label htmlFor="annotation-note">Notes for Codex and ML review</label>
                  <textarea
                    id="annotation-note"
                    value={selectedAnnotation.note}
                    onChange={(event) => setSelectedAnnotation({ ...selectedAnnotation, note: event.target.value })}
                  />
                  <div>
                    <button className="secondary-command danger" onClick={removeSelectedAnnotation}><Trash2 size={14} /> Delete</button>
                    <button className="primary-command" onClick={updateSelectedAnnotation}><Save size={14} /> Save</button>
                  </div>
                </div>
              )}
            </div>
          )}
          {tab === 'codex' && (
            <CodexPanel
              familyKey={family.familyKey}
              eventId={selectedEventId}
              selectedAnnotation={selectedAnnotation}
              chartRef={chartRef}
            />
          )}
          {tab === 'jyotish' && (
            <LocalJyotishPanel
              eventId={selectedEventId}
              selectedAnnotation={selectedAnnotation}
            />
          )}
          {tab === 'candles' && (
            <CandlestickPanel
              eventId={selectedEventId}
              selectedAnnotation={selectedAnnotation}
            />
          )}
        </aside>
      </section>
    </main>
  )
}
