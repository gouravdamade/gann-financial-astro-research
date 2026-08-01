import {
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  LineSeries,
  LineStyle,
  createChart,
  type IChartApi,
  type IPaneApi,
  type IPriceLine,
  type ISeriesApi,
  type MouseEventParams,
  type Time,
  type UTCTimestamp,
} from 'lightweight-charts'
import { toPng } from 'html-to-image'
import {
  Activity,
  ChevronLeft,
  ChevronRight,
  Eye,
  EyeOff,
  Info,
  Lock,
  Microscope,
  Minus,
  Plus,
  SlidersHorizontal,
  Trash2,
  Unlock,
  X,
} from 'lucide-react'
import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
  type MouseEvent as ReactMouseEvent,
  type PointerEvent as ReactPointerEvent,
} from 'react'
import {
  activeAspectCountsAtPeak,
  aspectsAtTime,
  formatAspectRange,
  nextAspectAtTime,
} from '../aspectPresentation'
import { createChartDrawing, defaultRsiPaneSettings } from '../chartLayouts'
import { chooseMagnetCandidate, type MagnetCandidate } from '../drawingMagnet'
import {
  isChartNavigationProximity,
  MIN_CHART_BAR_SPACING,
  navigateChartLogicalRange,
  type ChartNavigationAction,
} from '../chartViewport'
import { closedCandlesAt, normalizeRsiLevels, normalizeRsiPeriod, wilderRsiPoints } from '../rsi'
import type {
  AnnotationDraft,
  AspectWindow,
  Candle,
  ChartAnnotation,
  ChartDrawing,
  ChartDrawingAnchor,
  DrawingPreferences,
  ChartLayoutState,
  ChartPayload,
  ChartTool,
  PlanetaryLineSeries,
} from '../types'

type BandPosition = { event: AspectWindow; left: number; width: number }
type Point = { time: number; price: number }
type PendingDrawing = { type: 'gann_fan' | 'fibonacci_retracement'; point: Point }
type DragPreview = { drawingId: string; anchors: ChartDrawingAnchor[] }
type DragSession = DragPreview & { anchorIndex: number }
type OverlapPickerState = {
  time: number
  left: number
  top: number
  eventIds: string[]
}
type PaneBounds = { top: number; height: number }

export type MarketChartHandle = {
  capture: () => Promise<string>
  resetView: () => void
  clearDrawings: () => void
  undoDrawing: () => void
  setCrosshairTime: (time: number | null) => void
}

type MarketChartProps = {
  payload: ChartPayload
  selectedAspectId?: string | null
  selectedAnnotationId?: string | null
  activeTool: ChartTool
  toolActivationNonce?: number
  annotations?: ChartAnnotation[]
  onSelectAspect?: (aspect: AspectWindow) => void
  onShowAspectDetails?: (aspect: AspectWindow) => void
  onReviewAspect?: (aspect: AspectWindow) => void
  onSelectAnnotation?: (annotation: ChartAnnotation) => void
  onCreateAnnotation?: (draft: AnnotationDraft) => void
  onReplayCutoffSelect?: (candleOpenTime: number) => void
  onCrosshairTimeChange?: (candleOpenTime: number | null) => void
  onPinTime?: (candleOpenTime: number) => void
  onToolComplete?: () => void
  showAspects?: boolean
  showSrLines?: boolean
  planetaryLines?: PlanetaryLineSeries[]
  compact?: boolean
  drawings?: ChartDrawing[]
  selectedDrawingId?: string | null
  layoutKey?: string | null
  viewState?: ChartLayoutState
  onDrawingsChange?: (drawings: ChartDrawing[]) => void
  onSelectDrawing?: (drawingId: string | null) => void
  onViewStateChange?: (state: Partial<ChartLayoutState>) => void
  onUndo?: () => void
  drawingPreferences?: DrawingPreferences
}

function nearestTime(times: number[], value: number): number {
  if (!times.length) return value
  let low = 0
  let high = times.length - 1
  while (low < high) {
    const middle = Math.floor((low + high) / 2)
    if (times[middle] < value) low = middle + 1
    else high = middle
  }
  if (low === 0) return times[0]
  const before = times[low - 1]
  const after = times[low]
  return Math.abs(value - before) <= Math.abs(after - value) ? before : after
}

function annotationLabel(index: number): string {
  return `A${index + 1}`
}

export const MarketChart = forwardRef<MarketChartHandle, MarketChartProps>(function MarketChart(
  {
    payload,
    selectedAspectId,
    selectedAnnotationId,
    activeTool,
    toolActivationNonce = 0,
    annotations = [],
    onSelectAspect,
    onShowAspectDetails,
    onReviewAspect,
    onSelectAnnotation,
    onCreateAnnotation,
    onReplayCutoffSelect,
    onCrosshairTimeChange,
    onPinTime,
    onToolComplete,
    showAspects = true,
    showSrLines = true,
    planetaryLines = [],
    compact = false,
    drawings = [],
    selectedDrawingId,
    layoutKey,
    viewState,
    onDrawingsChange,
    onSelectDrawing,
    onViewStateChange,
    onUndo,
    drawingPreferences = {
      favoriteTools: ['horizontal', 'gann', 'fibonacci'],
      magnetMode: 'weak',
      keepDrawing: false,
    },
  },
  forwardedRef,
) {
  const rsiSettings = {
    ...defaultRsiPaneSettings(),
    ...(viewState?.rsi ?? {}),
  }
  const rsiPeriod = normalizeRsiPeriod(rsiSettings.period)
  const rsiLevels = normalizeRsiLevels(rsiSettings.levels)
  const rsiLevelsKey = rsiLevels.join(',')
  const rsiVisible = rsiSettings.visible
  const rootRef = useRef<HTMLDivElement>(null)
  const hostRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const rsiSeriesRef = useRef<ISeriesApi<'Line'> | null>(null)
  const planetarySeriesRef = useRef<Map<string, ISeriesApi<'Line'>>>(new Map())
  const rsiPaneRef = useRef<IPaneApi<Time> | null>(null)
  const priceLinesRef = useRef<IPriceLine[]>([])
  const rsiPriceLinesRef = useRef<IPriceLine[]>([])
  const toolRef = useRef(activeTool)
  const selectedAspectIdRef = useRef(selectedAspectId)
  const selectAspectRef = useRef(onSelectAspect)
  const showAspectDetailsRef = useRef(onShowAspectDetails)
  const reviewAspectRef = useRef(onReviewAspect)
  const showAspectsRef = useRef(showAspects)
  const payloadRef = useRef(payload)
  const createAnnotationRef = useRef(onCreateAnnotation)
  const replayCutoffSelectRef = useRef(onReplayCutoffSelect)
  const crosshairTimeChangeRef = useRef(onCrosshairTimeChange)
  const pinTimeRef = useRef(onPinTime)
  const toolCompleteRef = useRef(onToolComplete)
  const drawingPreferencesRef = useRef(drawingPreferences)
  const drawingsRef = useRef(drawings)
  const drawingsChangeRef = useRef(onDrawingsChange)
  const selectDrawingRef = useRef(onSelectDrawing)
  const selectedDrawingIdRef = useRef(selectedDrawingId)
  const viewStateChangeRef = useRef(onViewStateChange)
  const undoRef = useRef(onUndo)
  const viewKeyRef = useRef('')
  const appliedLayoutViewRef = useRef('')
  const applyingViewRef = useRef(false)
  const notifiedViewRef = useRef('')
  const renderedCandlesRef = useRef<Candle[]>([])
  const renderedSeriesKeyRef = useRef('')
  const srLinesSignatureRef = useRef('')
  const crosshairFrameRef = useRef<number | null>(null)
  const overlayFrameRef = useRef<number | null>(null)
  const overlayTimerRef = useRef<number | null>(null)
  const lastOverlayRefreshAtRef = useRef(0)
  const viewStateDebounceRef = useRef<number | null>(null)
  const pendingViewStateRef = useRef<Pick<ChartLayoutState, 'visibleStartUtc' | 'visibleEndUtc'> | null>(null)
  const pendingLegendRef = useRef<Candle | null>(null)
  const [bands, setBands] = useState<BandPosition[]>([])
  const [hoveredAspectId, setHoveredAspectId] = useState<string | null>(null)
  const [overlapPicker, setOverlapPicker] = useState<OverlapPickerState | null>(null)
  const hoverCloseTimerRef = useRef<number | null>(null)
  const [pendingDrawing, setPendingDrawing] = useState<PendingDrawing | null>(null)
  const pendingDrawingRef = useRef<PendingDrawing | null>(null)
  const [dragPreview, setDragPreview] = useState<DragPreview | null>(null)
  const dragSessionRef = useRef<DragSession | null>(null)
  const [legendCandle, setLegendCandle] = useState<Candle | null>(payload.candles[payload.candles.length - 1] ?? null)
  const [navigationVisible, setNavigationVisible] = useState(false)
  const [overlayRevision, setOverlayRevision] = useState(0)
  const [rsiPaneBounds, setRsiPaneBounds] = useState<PaneBounds | null>(null)
  const [rsiLegendValue, setRsiLegendValue] = useState<number | null>(null)
  const [rsiSettingsOpen, setRsiSettingsOpen] = useState(false)
  const [rsiLevelsInput, setRsiLevelsInput] = useState(rsiLevels.join(', '))
  const candleTimes = useMemo(() => payload.candles.map((item) => item.time), [payload.candles])
  const rsiPoints = useMemo(() => {
    const cutoff = payload.replay?.cutoffUtc ?? payload.generatedAt
    return wilderRsiPoints(
      closedCandlesAt(payload.candles, payload.timeframe, cutoff),
      rsiPeriod,
    )
  }, [payload.candles, payload.generatedAt, payload.replay?.cutoffUtc, payload.timeframe, rsiPeriod])
  const rsiPointsRef = useRef(rsiPoints)
  const activeCounts = useMemo(
    () => activeAspectCountsAtPeak(payload.aspects),
    [payload.aspects],
  )

  useEffect(() => {
    setRsiLevelsInput(rsiLevelsKey.split(',').join(', '))
  }, [rsiLevelsKey])

  useEffect(() => {
    rsiPointsRef.current = rsiPoints
  }, [rsiPoints])

  useEffect(() => {
    toolRef.current = activeTool
    pendingDrawingRef.current = null
    setPendingDrawing(null)
    setOverlapPicker(null)
  }, [activeTool, toolActivationNonce])

  useEffect(() => {
    selectedAspectIdRef.current = selectedAspectId
  }, [selectedAspectId])

  useEffect(() => {
    selectAspectRef.current = onSelectAspect
    showAspectDetailsRef.current = onShowAspectDetails
    reviewAspectRef.current = onReviewAspect
    showAspectsRef.current = showAspects
  }, [onReviewAspect, onSelectAspect, onShowAspectDetails, showAspects])

  useEffect(() => {
    payloadRef.current = payload
    createAnnotationRef.current = onCreateAnnotation
    replayCutoffSelectRef.current = onReplayCutoffSelect
    crosshairTimeChangeRef.current = onCrosshairTimeChange
    pinTimeRef.current = onPinTime
    toolCompleteRef.current = onToolComplete
    drawingPreferencesRef.current = drawingPreferences
  }, [
    drawingPreferences,
    onCreateAnnotation,
    onCrosshairTimeChange,
    onPinTime,
    onReplayCutoffSelect,
    onToolComplete,
    payload,
  ])

  useEffect(() => {
    drawingsRef.current = drawings
    drawingsChangeRef.current = onDrawingsChange
    selectDrawingRef.current = onSelectDrawing
    selectedDrawingIdRef.current = selectedDrawingId
    viewStateChangeRef.current = onViewStateChange
    undoRef.current = onUndo
    setOverlayRevision((value) => value + 1)
  }, [drawings, onDrawingsChange, onSelectDrawing, onUndo, onViewStateChange, selectedDrawingId])

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null
      if (target?.matches('input, textarea, select, [contenteditable="true"]')) return
      if (event.key === 'Escape') {
        setOverlapPicker(null)
        selectDrawingRef.current?.(null)
        return
      }
      if (event.key !== 'Delete' && event.key !== 'Backspace') return
      const drawingId = selectedDrawingIdRef.current
      const selected = drawingsRef.current.find((drawing) => drawing.drawingId === drawingId)
      if (!selected || selected.locked) return
      event.preventDefault()
      drawingsChangeRef.current?.(drawingsRef.current.filter((drawing) => drawing.drawingId !== drawingId))
      selectDrawingRef.current?.(null)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  useImperativeHandle(forwardedRef, () => ({
    capture: async () => {
      if (!rootRef.current) throw new Error('chart is not mounted')
      return toPng(rootRef.current, {
        backgroundColor: '#101722',
        cacheBust: true,
        pixelRatio: 1.25,
      })
    },
    resetView: () => {
      chartRef.current?.timeScale().fitContent()
      setOverlayRevision((value) => value + 1)
    },
    clearDrawings: () => {
      drawingsChangeRef.current?.([])
      pendingDrawingRef.current = null
      setPendingDrawing(null)
    },
    undoDrawing: () => {
      if (pendingDrawingRef.current) {
        pendingDrawingRef.current = null
        setPendingDrawing(null)
        return
      }
      undoRef.current?.()
    },
    setCrosshairTime: (time) => {
      const chart = chartRef.current
      const series = seriesRef.current
      if (!chart || !series) return
      const candles = payloadRef.current.candles
      if (time == null) {
        chart.clearCrosshairPosition()
        setLegendCandle(candles.at(-1) ?? null)
        setRsiLegendValue(rsiPointsRef.current.at(-1)?.value ?? null)
        return
      }
      const targetTime = nearestTime(candles.map((item) => item.time), time)
      const candle = candles.find((item) => item.time === targetTime)
      if (!candle) return
      const rsiPoint = rsiPointsRef.current.find((item) => item.time === targetTime)
      setLegendCandle(candle)
      setRsiLegendValue(rsiPoint?.value ?? null)
      chart.setCrosshairPosition(
        candle.close,
        targetTime as UTCTimestamp,
        series,
      )
    },
  }), [])

  const magnetizePoint = (
    rawTime: number,
    rawPrice: number,
    screenX: number,
    screenY: number,
  ): Point => {
    const chart = chartRef.current
    const series = seriesRef.current
    const candles = payloadRef.current.candles
    const mode = drawingPreferencesRef.current.magnetMode
    if (!chart || !series || !candles.length || mode === 'off') {
      return { time: nearestTime(candles.map((item) => item.time), rawTime), price: rawPrice }
    }
    const candleTime = nearestTime(candles.map((item) => item.time), rawTime)
    const candle = candles.find((item) => item.time === candleTime)
    const candleX = chart.timeScale().timeToCoordinate(candleTime as UTCTimestamp)
    if (!candle || candleX == null) return { time: candleTime, price: rawPrice }
    const candidates = (['open', 'high', 'low', 'close'] as const).flatMap((field) => {
      const candidateY = series.priceToCoordinate(candle[field])
      if (candidateY == null) return []
      return [{
        time: candleTime,
        price: candle[field],
        field,
        distancePx: Math.hypot(Number(candleX) - screenX, Number(candidateY) - screenY),
      } satisfies MagnetCandidate]
    })
    const snapped = chooseMagnetCandidate(candidates, mode)
    return snapped
      ? { time: snapped.time, price: snapped.price }
      : { time: candleTime, price: rawPrice }
  }

  useEffect(() => {
    if (!hostRef.current) return
    const planetarySeries = planetarySeriesRef.current
    const chart = createChart(hostRef.current, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: '#0f1621' },
        textColor: '#94a3b5',
        attributionLogo: false,
        fontFamily: 'Inter, Segoe UI, sans-serif',
        fontSize: 12,
      },
      grid: {
        vertLines: { color: '#1c2734', style: LineStyle.Solid },
        horzLines: { color: '#1c2734', style: LineStyle.Solid },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: '#73859a', labelBackgroundColor: '#33465a', width: 1 },
        horzLine: { color: '#73859a', labelBackgroundColor: '#33465a', width: 1 },
      },
      rightPriceScale: {
        borderColor: '#2a3747',
        scaleMargins: { top: 0.16, bottom: 0.08 },
      },
      timeScale: {
        borderColor: '#2a3747',
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 5,
        barSpacing: compact ? 8 : 11,
        minBarSpacing: MIN_CHART_BAR_SPACING,
      },
      handleScroll: true,
      handleScale: true,
    })
    const series = chart.addSeries(CandlestickSeries, {
      upColor: '#3cc7a0',
      downColor: '#f07178',
      borderUpColor: '#3cc7a0',
      borderDownColor: '#f07178',
      wickUpColor: '#78d7bd',
      wickDownColor: '#f49a9f',
      priceLineVisible: false,
      lastValueVisible: true,
    })
    const rsiSeries = rsiVisible
      ? chart.addSeries(LineSeries, {
          color: '#d6a84b',
          lineWidth: 2,
          priceLineVisible: false,
          lastValueVisible: true,
          crosshairMarkerVisible: true,
          priceFormat: {
            type: 'custom',
            minMove: 0.1,
            formatter: (value: number) => value.toFixed(1),
          },
          autoscaleInfoProvider: () => ({
            priceRange: { minValue: 0, maxValue: 100 },
          }),
        }, 1)
      : null
    const panes = chart.panes()
    if (rsiSeries && panes[1]) {
      panes[0].setStretchFactor(3)
      panes[1].setStretchFactor(1)
    }
    chartRef.current = chart
    seriesRef.current = series
    rsiSeriesRef.current = rsiSeries
    rsiPaneRef.current = rsiSeries?.getPane() ?? null

    const refreshPaneBounds = () => {
      const root = rootRef.current
      const paneElement = rsiPaneRef.current?.getHTMLElement()
      if (!root || !paneElement) {
        setRsiPaneBounds(null)
        return
      }
      const rootBounds = root.getBoundingClientRect()
      const paneBounds = paneElement.getBoundingClientRect()
      const next = {
        top: paneBounds.top - rootBounds.top,
        height: paneBounds.height,
      }
      setRsiPaneBounds((current) => (
        current?.top === next.top && current?.height === next.height ? current : next
      ))
    }

    const flushSavedView = () => {
      viewStateDebounceRef.current = null
      const next = pendingViewStateRef.current
      pendingViewStateRef.current = null
      if (next) viewStateChangeRef.current?.(next)
    }
    const queueSavedView = (next: Pick<ChartLayoutState, 'visibleStartUtc' | 'visibleEndUtc'>) => {
      const signature = `${next.visibleStartUtc}:${next.visibleEndUtc}`
      if (signature === notifiedViewRef.current) return
      notifiedViewRef.current = signature
      pendingViewStateRef.current = next
      if (viewStateDebounceRef.current != null) window.clearTimeout(viewStateDebounceRef.current)
      // Scaling can emit dozens of logical-range changes per wheel gesture.
      // Persist only the settled range, rather than causing a full parent render per tick.
      viewStateDebounceRef.current = window.setTimeout(flushSavedView, 180)
    }
    const refreshOverlays = () => {
      if (overlayFrameRef.current != null || overlayTimerRef.current != null) return
      const run = () => {
        overlayFrameRef.current = null
        overlayTimerRef.current = null
        lastOverlayRefreshAtRef.current = performance.now()
        setOverlayRevision((value) => value + 1)
        refreshPaneBounds()
        if (applyingViewRef.current) return
        const visible = chart.timeScale().getVisibleRange()
        if (!visible || typeof visible.from !== 'number' || typeof visible.to !== 'number') return
        queueSavedView({
          visibleStartUtc: new Date(Number(visible.from) * 1000).toISOString(),
          visibleEndUtc: new Date(Number(visible.to) * 1000).toISOString(),
        })
      }
      // Keep the native chart itself fully responsive while coalescing expensive
      // aspect-band and drawing overlays to a stable presentation cadence.
      const delay = Math.max(0, 48 - (performance.now() - lastOverlayRefreshAtRef.current))
      if (delay > 0) {
        overlayTimerRef.current = window.setTimeout(() => {
          overlayTimerRef.current = null
          overlayFrameRef.current = window.requestAnimationFrame(run)
        }, delay)
      } else {
        overlayFrameRef.current = window.requestAnimationFrame(run)
      }
    }
    chart.timeScale().subscribeVisibleLogicalRangeChange(refreshOverlays)
    const resizeObserver = new ResizeObserver(refreshOverlays)
    resizeObserver.observe(hostRef.current)
    window.requestAnimationFrame(refreshPaneBounds)

    const commitDrawing = (drawing: ChartDrawing) => {
      drawingsChangeRef.current?.([...drawingsRef.current, drawing])
      selectDrawingRef.current?.(drawing.drawingId)
    }

    const clickHandler = (params: MouseEventParams<Time>) => {
      if (!params.point || params.time == null) return
      const time = Number(params.time)
      const rsiPaneClicked = Boolean(rsiSeries && params.paneIndex === 1)
      const rawValue = rsiPaneClicked
        ? rsiSeries?.coordinateToPrice(params.point.y)
        : series.coordinateToPrice(params.point.y)
      if (rawValue == null) return
      const point = rsiPaneClicked
        ? {
            time: nearestTime(payloadRef.current.candles.map((item) => item.time), time),
            price: Math.max(0, Math.min(100, Number(rawValue))),
          }
        : magnetizePoint(
            time,
            Number(rawValue),
            params.point.x,
            params.point.y,
          )
      const tool = toolRef.current
      if (tool === 'replay') {
        replayCutoffSelectRef.current?.(time)
      } else if (tool === 'horizontal') {
        const drawing = createChartDrawing(
          'horizontal_line',
          [{ timeUtc: new Date(time * 1000).toISOString(), price: point.price }],
          drawingsRef.current.length,
          undefined,
          rsiPaneClicked ? 'rsi' : 'price',
        )
        commitDrawing(drawing)
        if (!drawingPreferencesRef.current.keepDrawing) toolCompleteRef.current?.()
      } else if (tool === 'vertical') {
        const drawing = createChartDrawing(
          'vertical_line',
          [{ timeUtc: new Date(time * 1000).toISOString(), price: point.price }],
          drawingsRef.current.length,
          undefined,
          rsiPaneClicked ? 'rsi' : 'price',
        )
        commitDrawing(drawing)
        if (!drawingPreferencesRef.current.keepDrawing) toolCompleteRef.current?.()
      } else if (tool === 'gann' || tool === 'fibonacci') {
        if (rsiPaneClicked) return
        const drawingType = tool === 'gann' ? 'gann_fan' : 'fibonacci_retracement'
        const pending = pendingDrawingRef.current
        if (!pending || pending.type !== drawingType) {
          const nextPending: PendingDrawing = { type: drawingType, point }
          pendingDrawingRef.current = nextPending
          setPendingDrawing(nextPending)
          return
        }
        const sameTime = pending.point.time === point.time
        const priceTolerance = Math.max(Math.abs(pending.point.price) * 1e-10, 1e-8)
        const samePrice = Math.abs(pending.point.price - point.price) <= priceTolerance
        if (sameTime || samePrice) return
        const anchors: ChartDrawingAnchor[] = [pending.point, point].map((anchor) => ({
          timeUtc: new Date(anchor.time * 1000).toISOString(),
          price: anchor.price,
        }))
        const drawing = createChartDrawing(
          drawingType,
          anchors,
          drawingsRef.current.length,
        )
        pendingDrawingRef.current = null
        setPendingDrawing(null)
        commitDrawing(drawing)
        if (!drawingPreferencesRef.current.keepDrawing) toolCompleteRef.current?.()
      } else if (tool === 'annotation' && createAnnotationRef.current) {
        if (rsiPaneClicked) return
        const currentPayload = payloadRef.current
        const selected = currentPayload.aspects.find((item) => item.eventId === selectedAspectIdRef.current)
        if (!selected) return
        createAnnotationRef.current({
          eventId: selected.eventId,
          familyKey: selected.familyKey,
          annotationType: 'point',
          anchorTimeUtc: new Date(time * 1000).toISOString(),
          anchorPrice: Number(Number(rawValue).toFixed(5)),
          targetType: 'chart_point',
          targetId: '',
          note: 'Review this location',
          color: '#4bb7e5',
          chartState: { timeframe: currentPayload.timeframe, visibleStart: currentPayload.start, visibleEnd: currentPayload.end },
        })
      } else if (tool === 'select') {
        pinTimeRef.current?.(
          nearestTime(payloadRef.current.candles.map((item) => item.time), time),
        )
        const active = showAspectsRef.current && !rsiPaneClicked
          ? aspectsAtTime(payloadRef.current.aspects, time)
          : []
        const aspect = active.length
          ? nextAspectAtTime(active, time, selectedAspectIdRef.current)
          : null
        if (aspect) {
          selectAspectRef.current?.(aspect)
          if (active.length > 1) {
            const rootWidth = rootRef.current?.clientWidth ?? 900
            const rootHeight = rootRef.current?.clientHeight ?? 600
            setHoveredAspectId(null)
            setOverlapPicker({
              time,
              left: Math.max(8, Math.min(params.point.x + 12, rootWidth - 352)),
              top: Math.max(40, Math.min(params.point.y + 12, rootHeight - 330)),
              eventIds: active.map((item) => item.eventId),
            })
          } else {
            setOverlapPicker(null)
          }
          return
        }
        setOverlapPicker(null)
        selectDrawingRef.current?.(null)
      }
    }
    chart.subscribeClick(clickHandler)
    const scheduleLegendUpdate = (candle: Candle | null) => {
      pendingLegendRef.current = candle
      if (crosshairFrameRef.current != null) return
      crosshairFrameRef.current = window.requestAnimationFrame(() => {
        crosshairFrameRef.current = null
        setLegendCandle(pendingLegendRef.current)
      })
    }
    chart.subscribeCrosshairMove((params) => {
      if (!params.point || params.time == null) {
        crosshairTimeChangeRef.current?.(null)
        scheduleLegendUpdate(payloadRef.current.candles[payloadRef.current.candles.length - 1] ?? null)
        setRsiLegendValue(rsiPointsRef.current.at(-1)?.value ?? null)
        return
      }
      crosshairTimeChangeRef.current?.(Number(params.time))
      const candle = params.seriesData.get(series)
      if (!candle || !('close' in candle)) return
      scheduleLegendUpdate({
        time: Number(params.time),
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
        volume: 0,
      })
      const rsiPoint = rsiSeries ? params.seriesData.get(rsiSeries) : null
      setRsiLegendValue(rsiPoint && 'value' in rsiPoint ? Number(rsiPoint.value) : null)
    })

    return () => {
      resizeObserver.disconnect()
      chart.timeScale().unsubscribeVisibleLogicalRangeChange(refreshOverlays)
      chart.unsubscribeClick(clickHandler)
      if (overlayFrameRef.current != null) {
        window.cancelAnimationFrame(overlayFrameRef.current)
        overlayFrameRef.current = null
      }
      if (overlayTimerRef.current != null) {
        window.clearTimeout(overlayTimerRef.current)
        overlayTimerRef.current = null
      }
      if (viewStateDebounceRef.current != null) {
        window.clearTimeout(viewStateDebounceRef.current)
        viewStateDebounceRef.current = null
      }
      flushSavedView()
      if (crosshairFrameRef.current != null) {
        window.cancelAnimationFrame(crosshairFrameRef.current)
        crosshairFrameRef.current = null
      }
      chart.remove()
      chartRef.current = null
      seriesRef.current = null
      rsiSeriesRef.current = null
      planetarySeries.clear()
      rsiPaneRef.current = null
      priceLinesRef.current = []
      rsiPriceLinesRef.current = []
      renderedCandlesRef.current = []
      renderedSeriesKeyRef.current = ''
      srLinesSignatureRef.current = ''
      appliedLayoutViewRef.current = ''
      setRsiPaneBounds(null)
    }
  }, [compact, rsiVisible])

  useEffect(() => {
    const chart = chartRef.current
    if (!chart) return
    const desiredIds = new Set(planetaryLines.map((line) => line.id))
    for (const [lineId, lineSeries] of planetarySeriesRef.current) {
      if (desiredIds.has(lineId)) continue
      chart.removeSeries(lineSeries)
      planetarySeriesRef.current.delete(lineId)
    }
    for (const line of planetaryLines) {
      let lineSeries = planetarySeriesRef.current.get(line.id)
      const options = {
        color: line.color,
        lineWidth: 1 as const,
        lineStyle: line.mode === 'mirror' ? LineStyle.Dashed : LineStyle.Solid,
        priceLineVisible: false,
        lastValueVisible: false,
        crosshairMarkerVisible: true,
        title: line.label,
        autoscaleInfoProvider: () => null,
      }
      if (!lineSeries) {
        lineSeries = chart.addSeries(LineSeries, options)
        planetarySeriesRef.current.set(line.id, lineSeries)
      } else {
        lineSeries.applyOptions(options)
      }
      lineSeries.setData(line.points.map((point) => ({
        time: point.time as UTCTimestamp,
        value: point.value,
      })))
    }
  }, [planetaryLines, rsiVisible])

  useEffect(() => {
    const chart = chartRef.current
    const series = seriesRef.current
    if (!chart || !series) return
    const nextSeriesData = payload.candles.map((candle) => ({
        time: candle.time as UTCTimestamp,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }))
    const previousCandles = renderedCandlesRef.current
    const seriesKey = `${payload.symbol}:${payload.timeframe}:${payload.dataSource}`
    const lastCandle = payload.candles[payload.candles.length - 1]
    const previousLast = previousCandles[previousCandles.length - 1]
    const previousPenultimate = previousCandles[previousCandles.length - 2]
    const nextPenultimate = payload.candles[payload.candles.length - 2]
    const sameLiveWindow = payload.dataSource === 'mt5_live'
      && renderedSeriesKeyRef.current === seriesKey
      && previousCandles.length === payload.candles.length
      && previousCandles[0]?.time === payload.candles[0]?.time
      && previousPenultimate?.time === nextPenultimate?.time
      && previousLast?.time === lastCandle?.time
    const appendedLiveBar = payload.dataSource === 'mt5_live'
      && renderedSeriesKeyRef.current === seriesKey
      && payload.candles.length === previousCandles.length + 1
      && previousLast?.time === nextPenultimate?.time
    if ((sameLiveWindow || appendedLiveBar) && lastCandle) {
      series.update(nextSeriesData[nextSeriesData.length - 1])
    } else {
      series.setData(nextSeriesData)
    }
    renderedCandlesRef.current = payload.candles
    renderedSeriesKeyRef.current = seriesKey

    const rsiSeries = rsiSeriesRef.current
    if (rsiSeries) {
      rsiSeries.setData(rsiPoints.map((point) => ({
        time: point.time as UTCTimestamp,
        value: point.value,
      })))
      rsiPriceLinesRef.current.forEach((line) => rsiSeries.removePriceLine(line))
      rsiPriceLinesRef.current = rsiLevelsKey.split(',').map(Number).map((level) => rsiSeries.createPriceLine({
        price: level,
        color: level === 50 ? '#587086' : '#795f42',
        lineWidth: 1,
        lineStyle: level === 50 ? LineStyle.Dashed : LineStyle.Dotted,
        axisLabelVisible: true,
        title: String(level),
      }))
      setRsiLegendValue(rsiPoints.at(-1)?.value ?? null)
    } else {
      setRsiLegendValue(null)
    }

    const visibleSrLines = showSrLines ? payload.srLines : []
    const srLinesSignature = JSON.stringify(
      visibleSrLines.map((line) => [line.price, line.color, line.label]),
    )
    if (srLinesSignatureRef.current !== srLinesSignature) {
      priceLinesRef.current.forEach((line) => series.removePriceLine(line))
      priceLinesRef.current = visibleSrLines.map((line) => series.createPriceLine({
        price: line.price,
        color: line.color,
        lineWidth: 1,
        lineStyle: LineStyle.Solid,
        axisLabelVisible: true,
        title: line.label,
      }))
      srLinesSignatureRef.current = srLinesSignature
    }
    const viewKey = payload.dataSource === 'mt5_live'
      ? `${payload.symbol}:${payload.timeframe}:live`
      : `${payload.symbol}:${payload.timeframe}:${payload.start}:${payload.end}`
    const layoutViewKey = `${viewKey}:${layoutKey ?? 'unmanaged'}`
    if (appliedLayoutViewRef.current !== layoutViewKey) {
      applyingViewRef.current = true
      const visibleStart = viewState?.visibleStartUtc
      const visibleEnd = viewState?.visibleEndUtc
      if (visibleStart && visibleEnd) {
        chart.timeScale().setVisibleRange({
          from: Math.floor(new Date(visibleStart).getTime() / 1000) as UTCTimestamp,
          to: Math.floor(new Date(visibleEnd).getTime() / 1000) as UTCTimestamp,
        })
      } else {
        chart.timeScale().fitContent()
      }
      appliedLayoutViewRef.current = layoutViewKey
      window.setTimeout(() => {
        applyingViewRef.current = false
      }, 0)
    }
    viewKeyRef.current = viewKey
    setOverlayRevision((value) => value + 1)
    setLegendCandle((current) => {
      const latest = payload.candles[payload.candles.length - 1] ?? null
      return current?.time === latest?.time
        && current?.open === latest?.open
        && current?.high === latest?.high
        && current?.low === latest?.low
        && current?.close === latest?.close
        ? current
        : latest
    })
  }, [compact, layoutKey, payload, rsiLevelsKey, rsiPoints, rsiVisible, showSrLines, viewState?.visibleEndUtc, viewState?.visibleStartUtc])

  useEffect(() => {
    const chart = chartRef.current
    if (!chart || !hostRef.current) return
    const width = hostRef.current.clientWidth
    const positions = (showAspects ? payload.aspects : [])
      .map((event) => {
        const start = nearestTime(candleTimes, event.start)
        const end = nearestTime(candleTimes, event.end)
        const startX = chart.timeScale().timeToCoordinate(start as UTCTimestamp)
        const endX = chart.timeScale().timeToCoordinate(end as UTCTimestamp)
        if (startX == null || endX == null) return null
        const left = Math.max(0, Math.min(startX, endX))
        const right = Math.min(width, Math.max(startX, endX))
        if (right < 0 || left > width) return null
        return { event, left, width: Math.max(5, right - left) }
      })
      .filter((item): item is BandPosition => item !== null)
    setBands(positions)
  }, [candleTimes, overlayRevision, payload.aspects, showAspects])

  useEffect(() => () => {
    if (hoverCloseTimerRef.current != null) {
      window.clearTimeout(hoverCloseTimerRef.current)
    }
  }, [])

  const showAspectHover = (eventId: string) => {
    if (hoverCloseTimerRef.current != null) {
      window.clearTimeout(hoverCloseTimerRef.current)
      hoverCloseTimerRef.current = null
    }
    setHoveredAspectId(eventId)
  }

  const hideAspectHover = () => {
    if (hoverCloseTimerRef.current != null) {
      window.clearTimeout(hoverCloseTimerRef.current)
    }
    hoverCloseTimerRef.current = window.setTimeout(() => {
      setHoveredAspectId(null)
      hoverCloseTimerRef.current = null
    }, 140)
  }

  const legendValues = useMemo(() => {
    if (!legendCandle) return null
    const index = payload.candles.findIndex((item) => item.time === legendCandle.time)
    const previous = index > 0 ? payload.candles[index - 1].close : legendCandle.open
    const change = legendCandle.close - previous
    const percent = previous ? (change / previous) * 100 : 0
    return { change, percent, positive: change >= 0 }
  }, [legendCandle, payload.candles])

  const paneBounds = (pane: ChartDrawing['pane']): PaneBounds => {
    const root = rootRef.current
    const chart = chartRef.current
    const paneIndex = pane === 'rsi' ? 1 : 0
    const paneElement = chart?.panes()[paneIndex]?.getHTMLElement()
    if (!root || !paneElement) {
      return { top: 0, height: root?.clientHeight ?? 0 }
    }
    const rootBounds = root.getBoundingClientRect()
    const bounds = paneElement.getBoundingClientRect()
    return { top: bounds.top - rootBounds.top, height: bounds.height }
  }

  const drawingPane = (drawing: ChartDrawing): ChartDrawing['pane'] => {
    if (drawing.pane) return drawing.pane
    return drawing.type === 'vertical_line' ? 'global' : 'price'
  }

  const toScreen = (
    point: Point | ChartDrawingAnchor,
    pane: ChartDrawing['pane'] = 'price',
  ) => {
    const chart = chartRef.current
    const series = pane === 'rsi' ? rsiSeriesRef.current : seriesRef.current
    if (!chart || !series) return null
    const pointTime = 'timeUtc' in point
      ? Math.floor(new Date(point.timeUtc).getTime() / 1000)
      : point.time
    const time = nearestTime(candleTimes, pointTime)
    const x = chart.timeScale().timeToCoordinate(time as UTCTimestamp)
    const localY = series.priceToCoordinate(point.price)
    const bounds = paneBounds(pane)
    return x == null || localY == null ? null : { x, y: bounds.top + Number(localY) }
  }

  const startAnchorDrag = (
    event: ReactPointerEvent<SVGCircleElement>,
    drawing: ChartDrawing,
    anchorIndex: number,
  ) => {
    if (drawing.locked || activeTool !== 'select') return
    event.preventDefault()
    event.stopPropagation()
    const session = {
      drawingId: drawing.drawingId,
      anchorIndex,
      anchors: drawing.anchors.map((anchor) => ({ ...anchor })),
    }
    dragSessionRef.current = session
    setDragPreview({ drawingId: session.drawingId, anchors: session.anchors })
    onSelectDrawing?.(drawing.drawingId)
  }

  const moveAnchorDrag = (clientX: number, clientY: number) => {
    const session = dragSessionRef.current
    const chart = chartRef.current
    const root = rootRef.current
    const drawing = drawingsRef.current.find((item) => item.drawingId === session?.drawingId)
    const pane = drawing ? drawingPane(drawing) : 'price'
    const series = pane === 'rsi' ? rsiSeriesRef.current : seriesRef.current
    if (!session || !chart || !series || !root) return
    const bounds = root.getBoundingClientRect()
    const x = Math.max(0, Math.min(bounds.width, clientX - bounds.left))
    const activePaneBounds = paneBounds(pane)
    const y = Math.max(0, Math.min(activePaneBounds.height, clientY - bounds.top - activePaneBounds.top))
    const rawTime = chart.timeScale().coordinateToTime(x)
    const price = series.coordinateToPrice(y)
    if (rawTime == null || price == null || typeof rawTime !== 'number') return
    const snapped = pane === 'rsi'
      ? {
          time: nearestTime(payloadRef.current.candles.map((item) => item.time), Number(rawTime)),
          price: Math.max(0, Math.min(100, Number(price))),
        }
      : magnetizePoint(Number(rawTime), Number(price), x, y)
    const anchors = session.anchors.map((anchor, index) => index === session.anchorIndex
      ? { timeUtc: new Date(snapped.time * 1000).toISOString(), price: snapped.price }
      : anchor)
    const nextSession = { ...session, anchors }
    dragSessionRef.current = nextSession
    setDragPreview({ drawingId: session.drawingId, anchors })
  }
  const moveAnchorDragRef = useRef(moveAnchorDrag)
  moveAnchorDragRef.current = moveAnchorDrag

  const finishAnchorDrag = () => {
    const session = dragSessionRef.current
    if (!session) return
    dragSessionRef.current = null
    setDragPreview(null)
    drawingsChangeRef.current?.(drawingsRef.current.map((drawing) => drawing.drawingId === session.drawingId
      ? { ...drawing, anchors: session.anchors }
      : drawing))
  }

  const cancelAnchorDrag = () => {
    dragSessionRef.current = null
    setDragPreview(null)
  }

  useEffect(() => {
    const movePointer = (event: PointerEvent) => {
      if (!dragSessionRef.current) return
      event.preventDefault()
      moveAnchorDragRef.current(event.clientX, event.clientY)
    }
    const moveMouse = (event: MouseEvent) => {
      if (!dragSessionRef.current) return
      event.preventDefault()
      moveAnchorDragRef.current(event.clientX, event.clientY)
    }
    const finish = () => finishAnchorDrag()
    const cancel = () => cancelAnchorDrag()
    window.addEventListener('pointermove', movePointer, { passive: false })
    window.addEventListener('pointerup', finish)
    window.addEventListener('pointercancel', cancel)
    window.addEventListener('mousemove', moveMouse, { passive: false })
    window.addEventListener('mouseup', finish)
    return () => {
      window.removeEventListener('pointermove', movePointer)
      window.removeEventListener('pointerup', finish)
      window.removeEventListener('pointercancel', cancel)
      window.removeEventListener('mousemove', moveMouse)
      window.removeEventListener('mouseup', finish)
    }
  }, [])

  const renderAnchorHandle = (
    drawing: ChartDrawing,
    anchorIndex: number,
    position: { x: number; y: number },
    label: string,
  ) => (
    <g className="drawing-anchor-control" key={`${drawing.drawingId}-anchor-${anchorIndex}`}>
      <circle
        className="drawing-anchor-handle"
        cx={position.x}
        cy={position.y}
        r={6}
        onPointerDown={(event) => startAnchorDrag(event, drawing, anchorIndex)}
      />
      <text className="drawing-anchor-label" x={position.x + 9} y={position.y - 9}>{label}</text>
    </g>
  )

  const renderDrawing = (inputDrawing: ChartDrawing) => {
    if (inputDrawing.type === 'square_of_nine') return null
    const drawing = dragPreview?.drawingId === inputDrawing.drawingId
      ? { ...inputDrawing, anchors: dragPreview.anchors }
      : inputDrawing
    if (!drawing.visible) return null
    const pane = drawingPane(drawing)
    if (pane === 'rsi' && !rsiVisible) return null
    const coordinatePane = pane === 'global' ? 'price' : pane
    const start = drawing.anchors[0] ? toScreen(drawing.anchors[0], coordinatePane) : null
    if (!start) return null
    const selected = drawing.drawingId === selectedDrawingId
    const dash = drawing.style.lineStyle === 'dashed'
      ? '6 4'
      : drawing.style.lineStyle === 'dotted'
        ? '2 4'
        : undefined
    const strokeStyle = {
      stroke: drawing.style.color,
      strokeWidth: drawing.style.lineWidth,
      strokeDasharray: dash,
      opacity: drawing.style.opacity,
    }
    const selectDrawing = (event: ReactMouseEvent<SVGGElement>) => {
      if (activeTool !== 'select') return
      event.stopPropagation()
      onSelectDrawing?.(drawing.drawingId)
    }
    if (drawing.type === 'horizontal_line') {
      const handlePosition = {
        x: Math.max(18, Math.min((rootRef.current?.clientWidth ?? start.x) - 18, start.x)),
        y: start.y,
      }
      return (
        <g key={drawing.drawingId} className={`chart-drawing ${selected ? 'is-selected' : ''}`} onClick={selectDrawing}>
          <line x1={0} y1={start.y} x2="100%" y2={start.y} style={strokeStyle} />
          <line x1={0} y1={start.y} x2="100%" y2={start.y} className="drawing-hit-target" />
          {selected && !drawing.locked && renderAnchorHandle(drawing, 0, handlePosition, pane === 'rsi' ? 'RSI' : 'Price')}
        </g>
      )
    }
    if (drawing.type === 'vertical_line') {
      const bounds = pane === 'global'
        ? { top: 0, height: rootRef.current?.clientHeight ?? 0 }
        : paneBounds(pane)
      const handlePosition = {
        x: start.x,
        y: bounds.top + Math.max(18, Math.min(bounds.height - 18, start.y - bounds.top)),
      }
      return (
        <g key={drawing.drawingId} className={`chart-drawing ${selected ? 'is-selected' : ''}`} onClick={selectDrawing}>
          <line x1={start.x} y1={bounds.top} x2={start.x} y2={bounds.top + bounds.height} style={strokeStyle} />
          <line x1={start.x} y1={bounds.top} x2={start.x} y2={bounds.top + bounds.height} className="drawing-hit-target" />
          {selected && !drawing.locked && renderAnchorHandle(drawing, 0, handlePosition, 'Time')}
        </g>
      )
    }
    const end = drawing.anchors[1] ? toScreen(drawing.anchors[1], coordinatePane) : null
    if (!end) return null
    if (drawing.type === 'gann_fan') {
      const rawRatios = Array.isArray(drawing.settings.ratios)
        ? drawing.settings.ratios.filter((value): value is number => typeof value === 'number')
        : [0.25, 0.5, 1, 2, 4]
      const ratios = rawRatios.length ? rawRatios : [1]
      const dx = end.x - start.x
      const scale = dx === 0 ? 1 : Math.max(1, (rootRef.current?.clientWidth ?? end.x) / Math.abs(dx))
      return (
        <g key={drawing.drawingId} className={`chart-drawing gann-drawing ${selected ? 'is-selected' : ''}`} onClick={selectDrawing}>
          {ratios.map((ratio) => {
            const targetY = start.y + (end.y - start.y) * ratio * scale
            return <line key={ratio} x1={start.x} y1={start.y} x2={start.x + dx * scale} y2={targetY} style={{ ...strokeStyle, strokeWidth: ratio === 1 ? drawing.style.lineWidth + 1 : drawing.style.lineWidth }} />
          })}
          <line x1={start.x} y1={start.y} x2={start.x + dx * scale} y2={start.y + (end.y - start.y) * scale} className="drawing-hit-target" />
          <circle cx={start.x} cy={start.y} r={selected ? 5 : 3} fill={drawing.style.color} opacity={drawing.style.opacity} />
          {selected && !drawing.locked && renderAnchorHandle(drawing, 0, start, 'Origin')}
          {selected && !drawing.locked && renderAnchorHandle(drawing, 1, end, 'Slope')}
        </g>
      )
    }
    if (drawing.type === 'fibonacci_retracement') {
      const rawLevels = Array.isArray(drawing.settings.levels)
        ? drawing.settings.levels.filter((value): value is number => (
            typeof value === 'number' && Number.isFinite(value) && value >= -5 && value <= 5
          ))
        : [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1]
      const levels = [...new Set(rawLevels)].slice(0, 24)
      const series = seriesRef.current
      if (!series || levels.length < 2) return null
      const rootWidth = rootRef.current?.clientWidth ?? Math.max(start.x, end.x)
      const x1 = drawing.settings.extendLines ? 0 : Math.min(start.x, end.x)
      const x2 = drawing.settings.extendLines ? rootWidth : Math.max(start.x, end.x)
      const levelRows = levels.flatMap((level) => {
        const price = drawing.anchors[0].price
          + (drawing.anchors[1].price - drawing.anchors[0].price) * level
        const y = series.priceToCoordinate(price)
        return y == null ? [] : [{ level, price, y: Number(y) }]
      })
      if (levelRows.length < 2) return null
      const yValues = levelRows.map((row) => row.y)
      const y1 = Math.min(...yValues)
      const y2 = Math.max(...yValues)
      const showLabels = drawing.settings.showLabels !== false
      const showPrices = drawing.settings.showPrices !== false
      return (
        <g key={drawing.drawingId} className={`chart-drawing fibonacci-drawing ${selected ? 'is-selected' : ''}`} onClick={selectDrawing}>
          <rect
            className="drawing-hit-target fibonacci-hit-target"
            x={x1}
            y={y1 - 6}
            width={Math.max(12, x2 - x1)}
            height={Math.max(12, y2 - y1 + 12)}
          />
          {levelRows.map(({ level, price, y }) => (
            <g key={level} className="fibonacci-level">
              <line className="fibonacci-level-line" x1={x1} y1={y} x2={x2} y2={y} style={strokeStyle} />
              {showLabels && (
                <text className="fibonacci-level-label" x={Math.max(x1 + 54, x2 - 4)} y={y - 3} fill={drawing.style.color}>
                  {(level * 100).toFixed(level === 0 || level === 1 ? 0 : 1)}%{showPrices ? `  ${price.toFixed(3)}` : ''}
                </text>
              )}
            </g>
          ))}
          {selected && !drawing.locked && renderAnchorHandle(drawing, 0, start, 'Start')}
          {selected && !drawing.locked && renderAnchorHandle(drawing, 1, end, 'End')}
        </g>
      )
    }

    return null
  }

  const selectedDrawing = drawings.find((drawing) => drawing.drawingId === selectedDrawingId) ?? null
  const updateRsiSettings = (update: Partial<typeof rsiSettings>) => {
    onViewStateChange?.({
      rsi: {
        ...defaultRsiPaneSettings(),
        ...rsiSettings,
        ...update,
      },
    })
  }
  const commitRsiLevels = () => {
    const levels = normalizeRsiLevels(
      rsiLevelsInput.split(/[\s,;]+/).map(Number),
    )
    setRsiLevelsInput(levels.join(', '))
    updateRsiSettings({ levels })
  }
  const updateSelectedDrawing = (update: Partial<ChartDrawing>) => {
    if (!selectedDrawing) return
    onDrawingsChange?.(drawings.map((drawing) => drawing.drawingId === selectedDrawing.drawingId
      ? { ...drawing, ...update, guardrails: drawing.guardrails }
      : drawing))
  }

  const navigateChart = (action: ChartNavigationAction) => {
    const chart = chartRef.current
    if (!chart) return
    const visibleRange = chart.timeScale().getVisibleLogicalRange()
    if (!visibleRange) return
    const nextRange = navigateChartLogicalRange(
      { from: Number(visibleRange.from), to: Number(visibleRange.to) },
      action,
      payloadRef.current.candles.length,
    )
    if (!nextRange) return
    chart.timeScale().setVisibleLogicalRange(nextRange)
    setOverlayRevision((value) => value + 1)
  }

  const handleNavigationClick = (
    event: ReactMouseEvent<HTMLButtonElement>,
    action: ChartNavigationAction,
  ) => {
    navigateChart(action)
    if (event.detail > 0) event.currentTarget.blur()
  }

  const handleChartPointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    const bounds = event.currentTarget.getBoundingClientRect()
    const nearNavigation = isChartNavigationProximity(
      event.clientX - bounds.left,
      event.clientY - bounds.top,
      bounds.width,
      bounds.height,
    )
    setNavigationVisible((current) => current === nearNavigation ? current : nearNavigation)
  }

  const hoveredBand = hoveredAspectId
    ? bands.find(({ event }) => event.eventId === hoveredAspectId) ?? null
    : null
  const hoverCardWidth = 318
  const hoverCardLeft = hoveredBand
    ? Math.max(
        8,
        Math.min(
          hoveredBand.left,
          (rootRef.current?.clientWidth ?? hoveredBand.left + hoverCardWidth) - hoverCardWidth - 8,
        ),
      )
    : 8
  const hoverCardTop = hoveredBand
    ? Math.min(
        39 + (hoveredBand.event.lane ?? 0) * 19 + 21,
        Math.max(176, (rootRef.current?.clientHeight ?? 360) - 176),
      )
    : 60
  const overlapAspects = overlapPicker
    ? overlapPicker.eventIds.flatMap((eventId) => {
        const aspect = payload.aspects.find((item) => item.eventId === eventId)
        return aspect ? [aspect] : []
      })
    : []

  return (
    <div
      className={`market-chart ${activeTool !== 'select' ? 'is-drawing' : ''}`}
      ref={rootRef}
      onPointerMove={handleChartPointerMove}
      onPointerLeave={() => setNavigationVisible(false)}
    >
      <div className="market-chart-host" ref={hostRef} />
      <div className="rsi-indicator-control" role="toolbar" aria-label="RSI indicator controls">
        <button
          type="button"
          className={rsiVisible ? 'is-active' : ''}
          onClick={() => updateRsiSettings({ visible: !rsiVisible })}
          title={rsiVisible ? 'Hide RSI pane' : 'Show RSI pane'}
        >
          <Activity size={14} /> RSI {rsiPeriod}
        </button>
        {rsiVisible && (
          <button
            type="button"
            className="icon-button"
            onClick={() => setRsiSettingsOpen((value) => !value)}
            title="RSI settings"
            aria-label="RSI settings"
          ><SlidersHorizontal size={14} /></button>
        )}
      </div>
      {rsiSettingsOpen && rsiVisible && (
        <aside className="rsi-settings-popover" aria-label="RSI settings panel">
          <header><div><strong>Relative Strength Index</strong><span>Wilder close</span></div><button className="icon-button" onClick={() => setRsiSettingsOpen(false)} title="Close RSI settings"><X size={14} /></button></header>
          <label>Period<input type="number" min={2} max={200} value={rsiPeriod} onChange={(event) => updateRsiSettings({ period: normalizeRsiPeriod(Number(event.target.value)) })} /></label>
          <label>Levels<input value={rsiLevelsInput} onChange={(event) => setRsiLevelsInput(event.target.value)} onBlur={commitRsiLevels} onKeyDown={(event) => { if (event.key === 'Enter') commitRsiLevels() }} /></label>
          <small>Follows {payload.timeframe}. Closed bars only; a level touch is evidence, not proof of reversal.</small>
        </aside>
      )}
      {legendCandle && legendValues && (
        <div className="chart-ohlc-legend">
          <strong>{payload.symbol}</strong>
          <span>{payload.timeframe}</span>
          <small>{new Date(legendCandle.time * 1000).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</small>
          <dl>
            <div><dt>O</dt><dd>{legendCandle.open.toFixed(3)}</dd></div>
            <div><dt>H</dt><dd>{legendCandle.high.toFixed(3)}</dd></div>
            <div><dt>L</dt><dd>{legendCandle.low.toFixed(3)}</dd></div>
            <div><dt>C</dt><dd>{legendCandle.close.toFixed(3)}</dd></div>
          </dl>
          <em className={legendValues.positive ? 'positive' : 'negative'}>
            {legendValues.change >= 0 ? '+' : ''}{legendValues.change.toFixed(3)} ({legendValues.percent >= 0 ? '+' : ''}{legendValues.percent.toFixed(2)}%)
          </em>
        </div>
      )}
      {rsiVisible && rsiPaneBounds && (
        <div className="rsi-pane-legend" style={{ top: rsiPaneBounds.top + 5 }}>
          <strong>RSI {rsiPeriod}</strong>
          <span>{payload.timeframe}</span>
          <em className={rsiLegendValue != null && rsiLegendValue >= 70 ? 'is-high' : rsiLegendValue != null && rsiLegendValue <= 30 ? 'is-low' : ''}>
            {rsiLegendValue == null ? 'warming up' : rsiLegendValue.toFixed(2)}
          </em>
        </div>
      )}
      <div className="aspect-window-layer" aria-hidden="true">
        {bands.map(({ event, left, width }) => {
          const selected = event.eventId === selectedAspectId
          return (
            <div
              className={`aspect-window-shade ${selected ? 'is-selected' : ''}`}
              key={`window-${event.eventId}`}
              style={{
                left,
                width,
                bottom: rsiPaneBounds ? Math.max(24, (rootRef.current?.clientHeight ?? 0) - rsiPaneBounds.top) : 24,
                borderColor: `${event.color}${selected ? 'e6' : '73'}`,
                backgroundColor: `${event.color}${selected ? '22' : '12'}`,
              }}
            />
          )
        })}
      </div>
      <div className="aspect-band-layer" aria-label="Astrological aspect windows">
        {bands.map(({ event, left, width }) => (
          <button
            className={`aspect-band ${event.eventId === selectedAspectId ? 'is-selected' : ''}`}
            key={event.eventId}
            style={{
              left,
              width,
              top: 39 + (event.lane ?? 0) * 19,
              borderColor: event.color,
              backgroundColor: `${event.color}33`,
            }}
            title={`${event.transitBody} to natal ${event.natalBody} ${event.aspectLabel}\n${event.knownPriorCount} known prior occurrences`}
            onMouseEnter={() => showAspectHover(event.eventId)}
            onMouseLeave={hideAspectHover}
            onFocus={() => showAspectHover(event.eventId)}
            onBlur={hideAspectHover}
            onClick={(eventClick) => {
              eventClick.stopPropagation()
              const rootBounds = rootRef.current?.getBoundingClientRect()
              const rawClickTime = rootBounds
                ? chartRef.current?.timeScale().coordinateToTime(eventClick.clientX - rootBounds.left)
                : null
              const clickTime = typeof rawClickTime === 'number'
                ? Number(rawClickTime)
                : event.peak
              const active = aspectsAtTime(payload.aspects, clickTime)
              onSelectAspect?.(event)
              if (active.length > 1 && rootBounds) {
                setHoveredAspectId(null)
                setOverlapPicker({
                  time: clickTime,
                  left: Math.max(8, Math.min(eventClick.clientX - rootBounds.left + 10, rootBounds.width - 352)),
                  top: Math.max(40, Math.min(eventClick.clientY - rootBounds.top + 10, rootBounds.height - 330)),
                  eventIds: active.map((item) => item.eventId),
                })
              } else {
                setOverlapPicker(null)
              }
            }}
          >
            <span>{event.transitBody} to {event.natalBody}</span>
          </button>
        ))}
      </div>
      {hoveredBand && !overlapPicker && (
        <aside
          className="aspect-hover-card"
          style={{ left: hoverCardLeft, top: hoverCardTop }}
          onMouseEnter={() => showAspectHover(hoveredBand.event.eventId)}
          onMouseLeave={hideAspectHover}
          aria-label="Aspect summary"
        >
          <header style={{ borderColor: hoveredBand.event.color }}>
            <div>
              <strong>{hoveredBand.event.transitBody} to {hoveredBand.event.natalBody}</strong>
              <span>{hoveredBand.event.aspectLabel}</span>
            </div>
            <em>{activeCounts.get(hoveredBand.event.eventId) ?? 1} active</em>
          </header>
          <dl>
            <div><dt>Range</dt><dd>{formatAspectRange(hoveredBand.event)}</dd></div>
            <div><dt>Duration</dt><dd>{Math.round(hoveredBand.event.durationMinutes)} min</dd></div>
            <div><dt>Peak orb</dt><dd>{hoveredBand.event.peakOrbDeg.toFixed(3)} / {hoveredBand.event.orbLimitDeg.toFixed(3)} deg</dd></div>
            <div><dt>Known history</dt><dd>{hoveredBand.event.knownPriorCount} prior / {hoveredBand.event.knownOccurrenceCount} total</dd></div>
          </dl>
          <footer>
            <button
              type="button"
              onClick={() => showAspectDetailsRef.current?.(hoveredBand.event)}
            >
              <Info size={13} /> Details
            </button>
            <button
              type="button"
              className="is-primary"
              onClick={() => reviewAspectRef.current?.(hoveredBand.event)}
            >
              <Microscope size={13} /> Review
            </button>
          </footer>
          {(activeCounts.get(hoveredBand.event.eventId) ?? 1) > 1 && (
            <small>Repeated chart clicks cycle aspects active at the same time.</small>
          )}
        </aside>
      )}
      {overlapPicker && overlapAspects.length > 1 && (
        <aside
          className="aspect-overlap-picker"
          style={{ left: overlapPicker.left, top: overlapPicker.top }}
          aria-label="Overlapping aspects"
        >
          <header>
            <div>
              <strong>{overlapAspects.length} overlapping aspects</strong>
              <span>{new Date(overlapPicker.time * 1000).toLocaleString()}</span>
            </div>
            <button className="icon-button" onClick={() => setOverlapPicker(null)} title="Close overlap picker" aria-label="Close overlap picker">
              <X size={14} />
            </button>
          </header>
          <div className="aspect-overlap-list">
            {overlapAspects.map((aspect) => (
              <div className={`aspect-overlap-item ${aspect.eventId === selectedAspectId ? 'is-selected' : ''}`} key={aspect.eventId}>
                <button
                  className="aspect-overlap-select"
                  onClick={() => onSelectAspect?.(aspect)}
                  title={`Select ${aspect.transitBody} to ${aspect.natalBody} ${aspect.aspectLabel}`}
                >
                  <i style={{ backgroundColor: aspect.color }} />
                  <span>
                    <strong>{aspect.transitBody} to {aspect.natalBody}</strong>
                    <small>{aspect.aspectLabel} | {formatAspectRange(aspect)}</small>
                    <em>orb {aspect.peakOrbDeg.toFixed(3)} deg | {aspect.knownPriorCount} prior</em>
                  </span>
                </button>
                <div>
                  <button onClick={() => {
                    onSelectAspect?.(aspect)
                    setOverlapPicker(null)
                    showAspectDetailsRef.current?.(aspect)
                  }} title="Show deterministic details" aria-label={`Details for ${aspect.transitBody} to ${aspect.natalBody}`}><Info size={12} /></button>
                  <button onClick={() => {
                    onSelectAspect?.(aspect)
                    setOverlapPicker(null)
                    reviewAspectRef.current?.(aspect)
                  }} title="Review recurrence family" aria-label={`Review ${aspect.transitBody} to ${aspect.natalBody}`}><Microscope size={12} /></button>
                </div>
              </div>
            ))}
          </div>
          <footer>Choose the exact event; chart clicks still cycle this same active set.</footer>
        </aside>
      )}
      <svg className="drawing-layer" aria-label="Persisted research drawings">
        {drawings.slice().sort((a, b) => a.zIndex - b.zIndex).map(renderDrawing)}
      </svg>
      {selectedDrawing && (
        <div className="selected-drawing-toolbar" role="toolbar" aria-label={`${selectedDrawing.name} drawing controls`}>
          <button className="selected-drawing-name" onClick={() => onSelectDrawing?.(selectedDrawing.drawingId)} title="Open drawing properties">
            <strong>{selectedDrawing.name}</strong>
            <span>Edit</span>
          </button>
          <button className="icon-button" onClick={() => onSelectDrawing?.(selectedDrawing.drawingId)} title="Edit drawing properties" aria-label="Edit drawing properties"><SlidersHorizontal size={14} /></button>
          <button className="icon-button" onClick={() => updateSelectedDrawing({ visible: !selectedDrawing.visible })} title={selectedDrawing.visible ? 'Hide drawing' : 'Show drawing'} aria-label={selectedDrawing.visible ? 'Hide drawing' : 'Show drawing'}>{selectedDrawing.visible ? <Eye size={14} /> : <EyeOff size={14} />}</button>
          <button className="icon-button" onClick={() => updateSelectedDrawing({ locked: !selectedDrawing.locked })} title={selectedDrawing.locked ? 'Unlock drawing' : 'Lock drawing'} aria-label={selectedDrawing.locked ? 'Unlock drawing' : 'Lock drawing'}>{selectedDrawing.locked ? <Lock size={14} /> : <Unlock size={14} />}</button>
          <button
            className="icon-button danger"
            onClick={() => {
              if (selectedDrawing.locked) return
              onDrawingsChange?.(drawings.filter((drawing) => drawing.drawingId !== selectedDrawing.drawingId))
              onSelectDrawing?.(null)
            }}
            disabled={selectedDrawing.locked}
            title={selectedDrawing.locked ? 'Unlock drawing before deleting' : 'Delete drawing'}
            aria-label="Delete drawing"
          ><Trash2 size={14} /></button>
        </div>
      )}
      <div className="annotation-layer" aria-label="Chart annotations">
        {annotations.map((annotation, index) => {
          if (annotation.anchorPrice == null) return null
          const position = toScreen({
            time: Math.floor(new Date(annotation.anchorTimeUtc).getTime() / 1000),
            price: annotation.anchorPrice,
          })
          if (!position) return null
          return (
            <button
              key={annotation.annotationId}
              className={`annotation-pin ${annotation.annotationId === selectedAnnotationId ? 'is-selected' : ''}`}
              style={{ left: position.x, top: position.y, borderColor: annotation.color }}
              onClick={() => onSelectAnnotation?.(annotation)}
              title={`${annotationLabel(index)}: ${annotation.note}`}
            >
              {annotationLabel(index)}
            </button>
          )
        })}
      </div>
      <div
        className={`chart-navigation-controls ${navigationVisible ? 'is-visible' : ''}`}
        role="toolbar"
        aria-label="Chart navigation controls"
      >
        <button type="button" className="icon-button" onClick={(event) => handleNavigationClick(event, 'backward')} title="Move chart backward" aria-label="Move chart backward"><ChevronLeft size={16} /></button>
        <button type="button" className="icon-button" onClick={(event) => handleNavigationClick(event, 'zoom_out')} title="Zoom out" aria-label="Zoom out"><Minus size={16} /></button>
        <button type="button" className="icon-button" onClick={(event) => handleNavigationClick(event, 'zoom_in')} title="Zoom in" aria-label="Zoom in"><Plus size={16} /></button>
        <button type="button" className="icon-button" onClick={(event) => handleNavigationClick(event, 'forward')} title="Move chart forward" aria-label="Move chart forward"><ChevronRight size={16} /></button>
      </div>
      {pendingDrawing && <div className="drawing-status">Place the second time/price anchor</div>}
    </div>
  )
})
