import {
  AlertTriangle,
  ArrowLeftRight,
  CalendarDays,
  Clock,
  DollarSign,
  Download,
  Grid3X3,
  MousePointer2,
  RotateCcw,
  Search,
  Sparkles,
  Trash2,
  TrendingDown,
  TrendingUp,
  ZoomIn,
  ZoomOut,
} from 'lucide-react'
import { toPng } from 'html-to-image'
import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from 'react'
import {
  buildSquareOfNineCells,
  normalizeSquareOfNineWorkspaceState,
  SQUARE_OF_NINE_MAX_SIZE,
  SQUARE_OF_NINE_MAX_ZOOM,
  SQUARE_OF_NINE_MIN_SIZE,
  SQUARE_OF_NINE_MIN_ZOOM,
} from '../squareOfNineWorkspace'
import type {
  SquareOfNineDataType,
  SquareOfNineIncrementUnit,
  SquareOfNineMark,
  SquareOfNineWorkspaceState,
} from '../types'

type SquareOfNineWorkspaceProps = {
  symbol: string
  timeframe: string
  latestPrice: number
  state?: SquareOfNineWorkspaceState
  layoutToolbar: ReactNode
  onChange: (state: SquareOfNineWorkspaceState) => void
}

const DATA_MODES: Array<{ id: SquareOfNineDataType; label: string; icon: typeof DollarSign }> = [
  { id: 'price', label: 'Price', icon: DollarSign },
  { id: 'time', label: 'Time', icon: Clock },
  { id: 'date', label: 'Date', icon: CalendarDays },
  { id: 'datetime', label: 'Date + time', icon: CalendarDays },
]

const MARK_MODES: Array<{
  id: SquareOfNineWorkspaceState['activeMarkMode']
  label: string
  icon: typeof MousePointer2
}> = [
  { id: 'select', label: 'Select', icon: MousePointer2 },
  { id: 'high', label: 'High', icon: TrendingUp },
  { id: 'low', label: 'Low', icon: TrendingDown },
  { id: 'forecast', label: 'Forecast', icon: Sparkles },
  { id: 'error', label: 'Error', icon: AlertTriangle },
]

const UNIT_LABELS: Record<SquareOfNineIncrementUnit, string> = {
  minute: 'Minutes',
  hour: 'Hours',
  day: 'Days',
  week: 'Weeks',
  month: 'Months',
  trading_day: 'Trading days',
}

function allowedUnits(dataType: SquareOfNineDataType): SquareOfNineIncrementUnit[] {
  if (dataType === 'time') return ['minute', 'hour']
  if (dataType === 'date') return ['day', 'week', 'month', 'trading_day']
  if (dataType === 'datetime') return ['minute', 'hour', 'day', 'week', 'month', 'trading_day']
  return []
}

function cellClass(
  mark: SquareOfNineMark | undefined,
  selected: boolean,
  axis: boolean,
  diagonal: boolean,
): string {
  return [
    'square9-cell',
    mark ? `is-${mark.kind}` : '',
    selected ? 'is-current' : '',
    axis ? 'is-axis' : '',
    diagonal ? 'is-diagonal' : '',
  ].filter(Boolean).join(' ')
}

export function SquareOfNineWorkspace({
  symbol,
  timeframe,
  latestPrice,
  state,
  layoutToolbar,
  onChange,
}: SquareOfNineWorkspaceProps) {
  const normalized = useMemo(
    () => normalizeSquareOfNineWorkspaceState(state, latestPrice),
    [latestPrice, state],
  )
  const cells = useMemo(() => buildSquareOfNineCells(normalized), [normalized])
  const gridRef = useRef<HTMLDivElement>(null)
  const [findValue, setFindValue] = useState('')
  const [findStatus, setFindStatus] = useState('')
  const dimension = normalized.size * 2 - 1
  const selectedCell = cells.find((cell) => cell.ordinal === normalized.selectedCellOrdinal) ?? cells[0]
  const selectedMark = normalized.marks[String(selectedCell.ordinal)]
  const temporalUnits = allowedUnits(normalized.dataType)

  const update = (patch: Partial<SquareOfNineWorkspaceState>) => {
    onChange(normalizeSquareOfNineWorkspaceState({ ...normalized, ...patch }, latestPrice))
  }

  const selectCell = (ordinal: number) => {
    const marks = { ...normalized.marks }
    if (normalized.activeMarkMode !== 'select') {
      marks[String(ordinal)] = {
        kind: normalized.activeMarkMode,
        note: marks[String(ordinal)]?.note ?? '',
      }
    }
    update({ selectedCellOrdinal: ordinal, marks })
  }

  const clearCellMark = (ordinal: number) => {
    const marks = { ...normalized.marks }
    delete marks[String(ordinal)]
    update({ selectedCellOrdinal: ordinal, marks })
  }

  const updateSelectedNote = (note: string) => {
    update({
      marks: {
        ...normalized.marks,
        [String(selectedCell.ordinal)]: {
          kind: selectedMark?.kind ?? 'selected',
          note,
        },
      },
    })
  }

  const revealOrdinal = (ordinal: number) => {
    update({ selectedCellOrdinal: ordinal })
    window.requestAnimationFrame(() => {
      gridRef.current?.querySelector<HTMLElement>(`[data-square9-ordinal="${ordinal}"]`)
        ?.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' })
    })
  }

  const findCell = () => {
    const query = findValue.trim().toLowerCase()
    if (!query) return
    let found = cells.find((cell) => cell.displayValue.toLowerCase() === query)
    const ordinalQuery = query.startsWith('#') ? Number(query.slice(1)) : Number.NaN
    if (!found && Number.isInteger(ordinalQuery)) {
      found = cells.find((cell) => cell.ordinal === ordinalQuery)
    }
    if (!found && normalized.dataType === 'price' && Number.isFinite(Number(query))) {
      const numericQuery = Number(query)
      found = cells.reduce((nearest, cell) => {
        if (cell.numericValue == null) return nearest
        if (!nearest || nearest.numericValue == null) return cell
        return Math.abs(cell.numericValue - numericQuery) < Math.abs(nearest.numericValue - numericQuery)
          ? cell
          : nearest
      }, cells[0])
    }
    if (!found) {
      found = cells.find((cell) => cell.displayValue.toLowerCase().includes(query))
    }
    if (!found) {
      setFindStatus('No matching cell')
      return
    }
    setFindStatus(`Cell ${found.ordinal}`)
    revealOrdinal(found.ordinal)
  }

  const captureSquare = async () => {
    const node = gridRef.current
    if (!node) return
    const dataUrl = await toPng(node, {
      backgroundColor: '#11161c',
      cacheBust: true,
      pixelRatio: 1.25,
      width: node.scrollWidth,
      height: node.scrollHeight,
    })
    const link = document.createElement('a')
    link.href = dataUrl
    link.download = `${symbol}_square_of_nine_${new Date().toISOString().replaceAll(':', '-')}.png`
    link.click()
  }

  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if (event.key !== 'F8') return
      event.preventDefault()
      update({ marks: {} })
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  })

  const width = normalized.dataType === 'datetime'
    ? 132
    : normalized.dataType === 'date'
      ? 94
      : 76
  const cellWidth = Math.round(width * normalized.zoomPercent / 100)
  const cellHeight = Math.round(58 * normalized.zoomPercent / 100)
  const gridStyle = {
    '--square9-dimension': dimension,
    '--square9-cell-width': `${cellWidth}px`,
    '--square9-cell-height': `${cellHeight}px`,
  } as CSSProperties

  return (
    <section className="square9-workspace" aria-label="Square of Nine workspace">
      <header className="square9-command-strip">
        <div className="square9-title-block">
          <Grid3X3 size={17} />
          <div><strong>Square of Nine</strong><span>{symbol} {timeframe} | Research only</span></div>
        </div>
        <div className="square9-layout-slot">{layoutToolbar}</div>
        <button className="icon-button" onClick={() => void captureSquare()} title="Download Square of Nine as PNG" aria-label="Download Square of Nine as PNG"><Download size={16} /></button>
      </header>

      <div className="square9-body">
        <aside className="square9-settings-panel">
          <section>
            <div className="square9-section-heading"><strong>Values</strong><span>{dimension} x {dimension}</span></div>
            <div className="square9-mode-grid" role="group" aria-label="Square data type">
              {DATA_MODES.map((mode) => {
                const Icon = mode.icon
                return <button key={mode.id} className={normalized.dataType === mode.id ? 'is-active' : ''} onClick={() => {
                  const units = allowedUnits(mode.id)
                  update({
                    dataType: mode.id,
                    incrementUnit: units.includes(normalized.incrementUnit) ? normalized.incrementUnit : (units[0] ?? normalized.incrementUnit),
                  })
                }}><Icon size={14} /> {mode.label}</button>
              })}
            </div>

            {normalized.dataType === 'price' && (
              <label>First price
                <div className="square9-inline-input"><input type="number" step="any" value={normalized.firstPrice} onChange={(event) => update({ firstPrice: Number(event.target.value) })} /><button onClick={() => update({ firstPrice: latestPrice })} title="Use latest market close">Live</button></div>
              </label>
            )}
            {(normalized.dataType === 'date' || normalized.dataType === 'datetime') && <label>First date<input type="date" value={normalized.firstDate} onChange={(event) => update({ firstDate: event.target.value })} /></label>}
            {(normalized.dataType === 'time' || normalized.dataType === 'datetime') && <label>First time (IST)<input type="time" step={1} value={normalized.firstTime} onChange={(event) => update({ firstTime: event.target.value })} /></label>}
            <div className="square9-value-row">
              <label>Increment<input type="number" step="any" value={normalized.increment} onChange={(event) => update({ increment: Number(event.target.value) })} /></label>
              {normalized.dataType !== 'price' && <label>Unit<select value={normalized.incrementUnit} onChange={(event) => update({ incrementUnit: event.target.value as SquareOfNineIncrementUnit })}>{temporalUnits.map((unit) => <option key={unit} value={unit}>{UNIT_LABELS[unit]}</option>)}</select></label>}
              <button className="icon-button square9-invert-button" onClick={() => update({ increment: normalized.increment === 0 ? -1 : -normalized.increment })} title="Reverse increment direction" aria-label="Reverse increment direction"><ArrowLeftRight size={15} /></button>
            </div>
          </section>

          <section>
            <div className="square9-section-heading"><strong>Grid</strong><span>Center + rings</span></div>
            <label>Size
              <div className="square9-stepper">
                <button onClick={() => update({ size: normalized.size - 1 })} disabled={normalized.size <= SQUARE_OF_NINE_MIN_SIZE}>-</button>
                <input type="number" min={SQUARE_OF_NINE_MIN_SIZE} max={SQUARE_OF_NINE_MAX_SIZE} value={normalized.size} onChange={(event) => update({ size: Number(event.target.value) })} />
                <button onClick={() => update({ size: normalized.size + 1 })} disabled={normalized.size >= SQUARE_OF_NINE_MAX_SIZE}>+</button>
              </div>
            </label>
            <label>Number direction<select value={normalized.numberRotation} onChange={(event) => update({ numberRotation: event.target.value as SquareOfNineWorkspaceState['numberRotation'] })}><option value="clockwise">Clockwise</option><option value="counterclockwise">Counterclockwise</option></select></label>
            <div className="square9-value-row">
              <label>Angle direction<select value={normalized.angleRotation} onChange={(event) => update({ angleRotation: event.target.value as SquareOfNineWorkspaceState['angleRotation'] })}><option value="clockwise">Clockwise</option><option value="counterclockwise">Counterclockwise</option></select></label>
              <label>Offset<input type="number" step={1} value={normalized.angleOffsetDeg} onChange={(event) => update({ angleOffsetDeg: Number(event.target.value) })} /></label>
            </div>
            <div className="square9-toggle-row">
              <label><input type="checkbox" checked={normalized.showOrdinals} onChange={(event) => update({ showOrdinals: event.target.checked })} /> Cell number</label>
              <label><input type="checkbox" checked={normalized.showAngles} onChange={(event) => update({ showAngles: event.target.checked })} /> Angle</label>
            </div>
          </section>

          <section>
            <div className="square9-section-heading"><strong>View</strong><span>{normalized.zoomPercent}%</span></div>
            <div className="square9-zoom-row">
              <button className="icon-button" onClick={() => update({ zoomPercent: normalized.zoomPercent - 10 })} disabled={normalized.zoomPercent <= SQUARE_OF_NINE_MIN_ZOOM} title="Zoom out"><ZoomOut size={15} /></button>
              <input type="range" min={SQUARE_OF_NINE_MIN_ZOOM} max={SQUARE_OF_NINE_MAX_ZOOM} step={10} value={normalized.zoomPercent} onChange={(event) => update({ zoomPercent: Number(event.target.value) })} />
              <button className="icon-button" onClick={() => update({ zoomPercent: normalized.zoomPercent + 10 })} disabled={normalized.zoomPercent >= SQUARE_OF_NINE_MAX_ZOOM} title="Zoom in"><ZoomIn size={15} /></button>
              <button className="icon-button" onClick={() => update({ zoomPercent: 100 })} title="Reset zoom"><RotateCcw size={14} /></button>
            </div>
            <label>Find value or #cell
              <div className="square9-inline-input"><input value={findValue} onChange={(event) => setFindValue(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter') findCell() }} /><button onClick={findCell} title="Find"><Search size={14} /></button></div>
            </label>
            {findStatus && <output className="square9-find-status">{findStatus}</output>}
          </section>
        </aside>

        <div className="square9-grid-viewport">
          <div className="square9-grid" ref={gridRef} style={gridStyle}>
            {cells.map((cell) => {
              const mark = normalized.marks[String(cell.ordinal)]
              return (
                <button
                  key={cell.ordinal}
                  data-square9-ordinal={cell.ordinal}
                  className={cellClass(mark, cell.ordinal === selectedCell.ordinal, cell.x === 0 || cell.y === 0, Math.abs(cell.x) === Math.abs(cell.y))}
                  style={{ gridColumn: cell.column, gridRow: cell.row }}
                  onClick={() => selectCell(cell.ordinal)}
                  onContextMenu={(event) => { event.preventDefault(); clearCellMark(cell.ordinal) }}
                  title={`Cell ${cell.ordinal} | Ring ${cell.ring} | ${cell.angleDeg.toFixed(1)} degrees`}
                >
                  {normalized.showOrdinals && <small>#{cell.ordinal}</small>}
                  <strong>{cell.displayValue}</strong>
                  {normalized.showAngles && <em>{cell.angleDeg.toFixed(1)} deg</em>}
                </button>
              )
            })}
          </div>
        </div>

        <aside className="square9-selection-panel">
          <section>
            <div className="square9-section-heading"><strong>Mark mode</strong><span>{Object.keys(normalized.marks).length} marked</span></div>
            <div className="square9-mark-modes">
              {MARK_MODES.map((mode) => {
                const Icon = mode.icon
                return <button key={mode.id} className={normalized.activeMarkMode === mode.id ? 'is-active' : ''} onClick={() => update({ activeMarkMode: mode.id })} title={mode.label}><Icon size={14} /><span>{mode.label}</span></button>
              })}
            </div>
          </section>
          <section className="square9-cell-inspector">
            <div className="square9-section-heading"><strong>Cell {selectedCell.ordinal}</strong><span>Ring {selectedCell.ring}</span></div>
            <dl>
              <div><dt>Value</dt><dd>{selectedCell.displayValue}</dd></div>
              <div><dt>Angle</dt><dd>{selectedCell.angleDeg.toFixed(2)} deg</dd></div>
              <div><dt>Position</dt><dd>{selectedCell.x}, {selectedCell.y}</dd></div>
              <div><dt>Mark</dt><dd>{selectedMark?.kind ?? 'none'}</dd></div>
            </dl>
            <label>Note<textarea value={selectedMark?.note ?? ''} onChange={(event) => updateSelectedNote(event.target.value)} placeholder="Research note" /></label>
            <button className="secondary-command danger" onClick={() => clearCellMark(selectedCell.ordinal)} disabled={!selectedMark}><Trash2 size={14} /> Clear cell mark</button>
          </section>
          <button className="square9-clear-all" onClick={() => update({ marks: {} })} disabled={Object.keys(normalized.marks).length === 0}><Trash2 size={14} /> Clear all marks <kbd>F8</kbd></button>
        </aside>
      </div>
    </section>
  )
}
