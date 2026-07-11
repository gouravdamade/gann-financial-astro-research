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
} from 'react'
import type {
  AnnotationDraft,
  AspectWindow,
  ChartAnnotation,
  ChartPayload,
  ChartTool,
} from '../types'

type BandPosition = { event: AspectWindow; left: number; width: number }
type Point = { time: number; price: number }
type Drawing = Point & {
  id: string
  type: 'horizontal' | 'vertical' | 'gann'
  endTime?: number
  endPrice?: number
}

export type MarketChartHandle = {
  capture: () => Promise<string>
  resetView: () => void
  clearDrawings: () => void
}

type MarketChartProps = {
  payload: ChartPayload
  selectedAspectId?: string | null
  selectedAnnotationId?: string | null
  activeTool: ChartTool
  annotations?: ChartAnnotation[]
  onSelectAspect?: (aspect: AspectWindow) => void
  onSelectAnnotation?: (annotation: ChartAnnotation) => void
  onCreateAnnotation?: (draft: AnnotationDraft) => void
  compact?: boolean
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
    annotations = [],
    onSelectAspect,
    onSelectAnnotation,
    onCreateAnnotation,
    compact = false,
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
  const viewKeyRef = useRef('')
  const [bands, setBands] = useState<BandPosition[]>([])
  const [drawings, setDrawings] = useState<Drawing[]>([])
  const [pendingGann, setPendingGann] = useState<Point | null>(null)
  const [tooltip, setTooltip] = useState<{ x: number; y: number; text: string } | null>(null)
  const [overlayRevision, setOverlayRevision] = useState(0)
  const candleTimes = useMemo(() => payload.candles.map((item) => item.time), [payload.candles])

  useEffect(() => {
    toolRef.current = activeTool
    if (activeTool !== 'gann') setPendingGann(null)
  }, [activeTool])

  useEffect(() => {
    selectedAspectIdRef.current = selectedAspectId
  }, [selectedAspectId])

  useEffect(() => {
    payloadRef.current = payload
    createAnnotationRef.current = onCreateAnnotation
  }, [onCreateAnnotation, payload])

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
      setDrawings([])
      setPendingGann(null)
    },
  }))

  useEffect(() => {
    if (!hostRef.current) return
    const chart = createChart(hostRef.current, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: '#101722' },
        textColor: '#aebdce',
        attributionLogo: false,
        fontFamily: 'Inter, Segoe UI, sans-serif',
        fontSize: 12,
      },
      grid: {
        vertLines: { color: '#202c3a', style: LineStyle.Solid },
        horzLines: { color: '#202c3a', style: LineStyle.Solid },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: '#73859a', labelBackgroundColor: '#33465a', width: 1 },
        horzLine: { color: '#73859a', labelBackgroundColor: '#33465a', width: 1 },
      },
      rightPriceScale: {
        borderColor: '#344357',
        scaleMargins: { top: 0.12, bottom: 0.08 },
      },
      timeScale: {
        borderColor: '#344357',
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

    const refreshOverlays = () => setOverlayRevision((value) => value + 1)
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
        setDrawings((items) => [...items, { ...point, id: crypto.randomUUID(), type: 'horizontal' }])
      } else if (tool === 'vertical') {
        setDrawings((items) => [...items, { ...point, id: crypto.randomUUID(), type: 'vertical' }])
      } else if (tool === 'gann') {
        setPendingGann((first) => {
          if (!first) return point
          setDrawings((items) => [
            ...items,
            {
              ...first,
              id: crypto.randomUUID(),
              type: 'gann',
              endTime: point.time,
              endPrice: point.price,
            },
          ])
          return null
        })
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
      }
    }
    chart.subscribeClick(clickHandler)
    chart.subscribeCrosshairMove((params) => {
      if (!params.point || params.time == null) {
        setTooltip(null)
        return
      }
      const candle = params.seriesData.get(series)
      if (!candle || !('close' in candle)) return
      setTooltip({
        x: params.point.x,
        y: params.point.y,
        text: `${new Date(Number(params.time) * 1000).toLocaleString()}  O ${candle.open.toFixed(3)}  H ${candle.high.toFixed(3)}  L ${candle.low.toFixed(3)}  C ${candle.close.toFixed(3)}`,
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
    priceLinesRef.current = payload.srLines.map((line) => series.createPriceLine({
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
    if (viewKeyRef.current !== viewKey) {
      chart.timeScale().fitContent()
      viewKeyRef.current = viewKey
    }
    setOverlayRevision((value) => value + 1)
  }, [payload])

  useEffect(() => {
    const chart = chartRef.current
    if (!chart || !hostRef.current) return
    const width = hostRef.current.clientWidth
    const positions = payload.aspects
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
  }, [candleTimes, overlayRevision, payload.aspects])

  const toScreen = (point: Point) => {
    const chart = chartRef.current
    const series = seriesRef.current
    if (!chart || !series) return null
    const time = nearestTime(candleTimes, point.time)
    const x = chart.timeScale().timeToCoordinate(time as UTCTimestamp)
    const y = series.priceToCoordinate(point.price)
    return x == null || y == null ? null : { x, y }
  }

  return (
    <div className={`market-chart ${activeTool !== 'select' ? 'is-drawing' : ''}`} ref={rootRef}>
      <div className="market-chart-host" ref={hostRef} />
      <div className="aspect-band-layer" aria-label="Astrological aspect windows">
        {bands.map(({ event, left, width }) => (
          <button
            className={`aspect-band ${event.eventId === selectedAspectId ? 'is-selected' : ''}`}
            key={event.eventId}
            style={{
              left,
              width,
              top: 8 + (event.lane ?? 0) * 19,
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
      {bands
        .filter(({ event }) => event.eventId === selectedAspectId)
        .map(({ event, left, width }) => (
          <div
            className="selected-aspect-shade"
            key={`shade-${event.eventId}`}
            style={{ left, width, borderColor: event.color, backgroundColor: `${event.color}12` }}
          />
        ))}
      <svg className="drawing-layer" aria-hidden="true">
        {drawings.flatMap((drawing) => {
          const start = toScreen(drawing)
          if (!start) return []
          if (drawing.type === 'horizontal') {
            return [<line key={drawing.id} x1={0} y1={start.y} x2="100%" y2={start.y} className="manual-line horizontal" />]
          }
          if (drawing.type === 'vertical') {
            return [<line key={drawing.id} x1={start.x} y1={0} x2={start.x} y2="100%" className="manual-line vertical" />]
          }
          const end = drawing.endTime && drawing.endPrice != null
            ? toScreen({ time: drawing.endTime, price: drawing.endPrice })
            : null
          if (!end) return []
          const ratios = [0.25, 0.5, 1, 2, 4]
          return ratios.map((ratio) => {
            const dx = end.x - start.x
            const dy = (end.y - start.y) * ratio
            const scale = dx === 0 ? 1 : Math.max(1, (rootRef.current?.clientWidth ?? end.x) / Math.abs(dx))
            return (
              <line
                key={`${drawing.id}-${ratio}`}
                x1={start.x}
                y1={start.y}
                x2={start.x + dx * scale}
                y2={start.y + dy * scale}
                className={ratio === 1 ? 'gann-line primary' : 'gann-line'}
              />
            )
          })
        })}
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
      {tooltip && (
        <div
          className="chart-tooltip"
          style={{ left: Math.min(tooltip.x + 16, (rootRef.current?.clientWidth ?? 500) - 390), top: Math.max(tooltip.y - 42, 8) }}
        >
          {tooltip.text}
        </div>
      )}
      {activeTool === 'gann' && pendingGann && <div className="drawing-status">Second anchor pending</div>}
    </div>
  )
})
