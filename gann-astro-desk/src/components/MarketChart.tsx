import {
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  LineStyle,
  createChart,
  type IChartApi,
  type IPriceLine,
  type ISeriesApi,
  type MouseEventParams,
  type Time,
  type UTCTimestamp,
} from 'lightweight-charts'
import { toPng } from 'html-to-image'
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
import { createChartDrawing } from '../chartLayouts'
import type {
  AnnotationDraft,
  AspectWindow,
  Candle,
  ChartAnnotation,
  ChartDrawing,
  ChartDrawingAnchor,
  ChartLayoutState,
  ChartPayload,
  ChartTool,
} from '../types'

type BandPosition = { event: AspectWindow; left: number; width: number }
type Point = { time: number; price: number }
type PendingDrawing = { type: 'gann_fan'; point: Point }
type DragPreview = { drawingId: string; anchors: ChartDrawingAnchor[] }
type DragSession = DragPreview & { anchorIndex: number }

export type MarketChartHandle = {
  capture: () => Promise<string>
  resetView: () => void
  clearDrawings: () => void
  undoDrawing: () => void
}

type MarketChartProps = {
  payload: ChartPayload
  selectedAspectId?: string | null
  selectedAnnotationId?: string | null
  activeTool: ChartTool
  toolActivationNonce?: number
  annotations?: ChartAnnotation[]
  onSelectAspect?: (aspect: AspectWindow) => void
  onSelectAnnotation?: (annotation: ChartAnnotation) => void
  onCreateAnnotation?: (draft: AnnotationDraft) => void
  showAspects?: boolean
  showSrLines?: boolean
  compact?: boolean
  drawings?: ChartDrawing[]
  selectedDrawingId?: string | null
  layoutKey?: string | null
  viewState?: ChartLayoutState
  onDrawingsChange?: (drawings: ChartDrawing[]) => void
  onSelectDrawing?: (drawingId: string | null) => void
  onViewStateChange?: (state: Partial<ChartLayoutState>) => void
  onUndo?: () => void
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
    onSelectAnnotation,
    onCreateAnnotation,
    showAspects = true,
    showSrLines = true,
    compact = false,
    drawings = [],
    selectedDrawingId,
    layoutKey,
    viewState,
    onDrawingsChange,
    onSelectDrawing,
    onViewStateChange,
    onUndo,
  },
  forwardedRef,
) {
  const rootRef = useRef<HTMLDivElement>(null)
  const hostRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const priceLinesRef = useRef<IPriceLine[]>([])
  const toolRef = useRef(activeTool)
  const selectedAspectIdRef = useRef(selectedAspectId)
  const payloadRef = useRef(payload)
  const createAnnotationRef = useRef(onCreateAnnotation)
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
  const [bands, setBands] = useState<BandPosition[]>([])
  const [pendingDrawing, setPendingDrawing] = useState<PendingDrawing | null>(null)
  const pendingDrawingRef = useRef<PendingDrawing | null>(null)
  const [dragPreview, setDragPreview] = useState<DragPreview | null>(null)
  const dragSessionRef = useRef<DragSession | null>(null)
  const [legendCandle, setLegendCandle] = useState<Candle | null>(payload.candles[payload.candles.length - 1] ?? null)
  const [overlayRevision, setOverlayRevision] = useState(0)
  const candleTimes = useMemo(() => payload.candles.map((item) => item.time), [payload.candles])

  useEffect(() => {
    toolRef.current = activeTool
    pendingDrawingRef.current = null
    setPendingDrawing(null)
  }, [activeTool, toolActivationNonce])

  useEffect(() => {
    selectedAspectIdRef.current = selectedAspectId
  }, [selectedAspectId])

  useEffect(() => {
    payloadRef.current = payload
    createAnnotationRef.current = onCreateAnnotation
  }, [onCreateAnnotation, payload])

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
  }), [])

  useEffect(() => {
    if (!hostRef.current) return
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
        minBarSpacing: 3,
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
    chartRef.current = chart
    seriesRef.current = series

    const refreshOverlays = () => {
      setOverlayRevision((value) => value + 1)
      if (applyingViewRef.current) return
      const visible = chart.timeScale().getVisibleRange()
      if (!visible || typeof visible.from !== 'number' || typeof visible.to !== 'number') return
      const next = {
        visibleStartUtc: new Date(Number(visible.from) * 1000).toISOString(),
        visibleEndUtc: new Date(Number(visible.to) * 1000).toISOString(),
      }
      const signature = `${next.visibleStartUtc}:${next.visibleEndUtc}`
      if (signature === notifiedViewRef.current) return
      notifiedViewRef.current = signature
      viewStateChangeRef.current?.(next)
    }
    chart.timeScale().subscribeVisibleLogicalRangeChange(refreshOverlays)
    const resizeObserver = new ResizeObserver(refreshOverlays)
    resizeObserver.observe(hostRef.current)

    const clickHandler = (params: MouseEventParams<Time>) => {
      if (!params.point || params.time == null) return
      const time = Number(params.time)
      const priceValue = series.coordinateToPrice(params.point.y)
      if (priceValue == null) return
      const point = { time, price: Number(priceValue) }
      const tool = toolRef.current
      if (tool === 'horizontal') {
        const drawing = createChartDrawing(
          'horizontal_line',
          [{ timeUtc: new Date(time * 1000).toISOString(), price: point.price }],
          drawingsRef.current.length,
        )
        drawingsChangeRef.current?.([...drawingsRef.current, drawing])
      } else if (tool === 'vertical') {
        const drawing = createChartDrawing(
          'vertical_line',
          [{ timeUtc: new Date(time * 1000).toISOString(), price: point.price }],
          drawingsRef.current.length,
        )
        drawingsChangeRef.current?.([...drawingsRef.current, drawing])
      } else if (tool === 'gann') {
        const drawingType = 'gann_fan'
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
        drawingsChangeRef.current?.([...drawingsRef.current, drawing])
      } else if (tool === 'annotation' && createAnnotationRef.current) {
        const currentPayload = payloadRef.current
        const selected = currentPayload.aspects.find((item) => item.eventId === selectedAspectIdRef.current)
        if (!selected) return
        createAnnotationRef.current({
          eventId: selected.eventId,
          familyKey: selected.familyKey,
          annotationType: 'point',
          anchorTimeUtc: new Date(time * 1000).toISOString(),
          anchorPrice: Number(priceValue.toFixed(5)),
          targetType: 'chart_point',
          targetId: '',
          note: 'Review this location',
          color: '#4bb7e5',
          chartState: { timeframe: currentPayload.timeframe, visibleStart: currentPayload.start, visibleEnd: currentPayload.end },
        })
      } else if (tool === 'select') {
        selectDrawingRef.current?.(null)
      }
    }
    chart.subscribeClick(clickHandler)
    chart.subscribeCrosshairMove((params) => {
      if (!params.point || params.time == null) {
        setLegendCandle(payloadRef.current.candles[payloadRef.current.candles.length - 1] ?? null)
        return
      }
      const candle = params.seriesData.get(series)
      if (!candle || !('close' in candle)) return
      setLegendCandle({
        time: Number(params.time),
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
        volume: 0,
      })
    })

    return () => {
      resizeObserver.disconnect()
      chart.timeScale().unsubscribeVisibleLogicalRangeChange(refreshOverlays)
      chart.unsubscribeClick(clickHandler)
      chart.remove()
      chartRef.current = null
      seriesRef.current = null
      priceLinesRef.current = []
    }
  }, [compact])

  useEffect(() => {
    const chart = chartRef.current
    const series = seriesRef.current
    if (!chart || !series) return
    series.setData(
      payload.candles.map((candle) => ({
        time: candle.time as UTCTimestamp,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      })),
    )
    priceLinesRef.current.forEach((line) => series.removePriceLine(line))
    priceLinesRef.current = (showSrLines ? payload.srLines : []).map((line) => series.createPriceLine({
      price: line.price,
      color: line.color,
      lineWidth: 1,
      lineStyle: LineStyle.Solid,
      axisLabelVisible: true,
      title: line.label,
    }))
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
    setLegendCandle(payload.candles[payload.candles.length - 1] ?? null)
  }, [layoutKey, payload, showSrLines, viewState?.visibleEndUtc, viewState?.visibleStartUtc])

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

  const legendValues = useMemo(() => {
    if (!legendCandle) return null
    const index = payload.candles.findIndex((item) => item.time === legendCandle.time)
    const previous = index > 0 ? payload.candles[index - 1].close : legendCandle.open
    const change = legendCandle.close - previous
    const percent = previous ? (change / previous) * 100 : 0
    return { change, percent, positive: change >= 0 }
  }, [legendCandle, payload.candles])

  const toScreen = (point: Point | ChartDrawingAnchor) => {
    const chart = chartRef.current
    const series = seriesRef.current
    if (!chart || !series) return null
    const pointTime = 'timeUtc' in point
      ? Math.floor(new Date(point.timeUtc).getTime() / 1000)
      : point.time
    const time = nearestTime(candleTimes, pointTime)
    const x = chart.timeScale().timeToCoordinate(time as UTCTimestamp)
    const y = series.priceToCoordinate(point.price)
    return x == null || y == null ? null : { x, y }
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
    const series = seriesRef.current
    const root = rootRef.current
    if (!session || !chart || !series || !root) return
    const bounds = root.getBoundingClientRect()
    const x = Math.max(0, Math.min(bounds.width, clientX - bounds.left))
    const y = Math.max(0, Math.min(bounds.height, clientY - bounds.top))
    const rawTime = chart.timeScale().coordinateToTime(x)
    const price = series.coordinateToPrice(y)
    if (rawTime == null || price == null || typeof rawTime !== 'number') return
    const time = nearestTime(candleTimes, Number(rawTime))
    const anchors = session.anchors.map((anchor, index) => index === session.anchorIndex
      ? { timeUtc: new Date(time * 1000).toISOString(), price: Number(price) }
      : anchor)
    const nextSession = { ...session, anchors }
    dragSessionRef.current = nextSession
    setDragPreview({ drawingId: session.drawingId, anchors })
  }

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
      moveAnchorDrag(event.clientX, event.clientY)
    }
    const moveMouse = (event: MouseEvent) => {
      if (!dragSessionRef.current) return
      event.preventDefault()
      moveAnchorDrag(event.clientX, event.clientY)
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
  })

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
    const start = drawing.anchors[0] ? toScreen(drawing.anchors[0]) : null
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
          {selected && !drawing.locked && renderAnchorHandle(drawing, 0, handlePosition, 'Price')}
        </g>
      )
    }
    if (drawing.type === 'vertical_line') {
      const handlePosition = {
        x: start.x,
        y: Math.max(18, Math.min((rootRef.current?.clientHeight ?? start.y) - 18, start.y)),
      }
      return (
        <g key={drawing.drawingId} className={`chart-drawing ${selected ? 'is-selected' : ''}`} onClick={selectDrawing}>
          <line x1={start.x} y1={0} x2={start.x} y2="100%" style={strokeStyle} />
          <line x1={start.x} y1={0} x2={start.x} y2="100%" className="drawing-hit-target" />
          {selected && !drawing.locked && renderAnchorHandle(drawing, 0, handlePosition, 'Time')}
        </g>
      )
    }
    const end = drawing.anchors[1] ? toScreen(drawing.anchors[1]) : null
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

    return null
  }

  return (
    <div className={`market-chart ${activeTool !== 'select' ? 'is-drawing' : ''}`} ref={rootRef}>
      <div className="market-chart-host" ref={hostRef} />
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
            title={`${event.transitBody} to natal ${event.natalBody} ${event.aspectLabel}\n${event.occurrenceCount} occurrences`}
            onClick={(eventClick) => {
              eventClick.stopPropagation()
              onSelectAspect?.(event)
            }}
          >
            <span>{event.transitBody} to {event.natalBody}</span>
          </button>
        ))}
      </div>
      {showAspects && bands
        .filter(({ event }) => event.eventId === selectedAspectId)
        .map(({ event, left, width }) => (
          <div
            className="selected-aspect-shade"
            key={`shade-${event.eventId}`}
            style={{ left, width, borderColor: event.color, backgroundColor: `${event.color}12` }}
          />
        ))}
      <svg className="drawing-layer" aria-label="Persisted research drawings">
        {drawings.slice().sort((a, b) => a.zIndex - b.zIndex).map(renderDrawing)}
      </svg>
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
      {pendingDrawing && <div className="drawing-status">Place the second time/price anchor</div>}
    </div>
  )
})
