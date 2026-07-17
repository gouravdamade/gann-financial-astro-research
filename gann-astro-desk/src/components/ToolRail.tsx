import {
  Crosshair,
  Fan,
  ListFilter,
  Magnet,
  MessageSquarePlus,
  Minus,
  MousePointer2,
  Pin,
  RotateCcw,
  SeparatorVertical,
  Star,
  Trash2,
  Undo2,
} from 'lucide-react'
import type { ChartTool } from '../types'
import type { DrawingPreferences } from '../types'

const tools: Array<{ id: ChartTool; label: string; icon: typeof MousePointer2 }> = [
  { id: 'select', label: 'Select aspect or drawing', icon: MousePointer2 },
  { id: 'crosshair', label: 'Crosshair', icon: Crosshair },
  { id: 'annotation', label: 'Add annotation', icon: MessageSquarePlus },
  { id: 'horizontal', label: 'Horizontal line', icon: Minus },
  { id: 'vertical', label: 'Vertical line', icon: SeparatorVertical },
  { id: 'gann', label: 'Gann fan', icon: Fan },
  { id: 'fibonacci', label: 'Fibonacci retracement', icon: ListFilter },
]

type ToolRailProps = {
  activeTool: ChartTool
  onToolChange: (tool: ChartTool) => void
  onClear?: () => void
  onReset?: () => void
  onUndo?: () => void
  preferences?: DrawingPreferences
  onPreferencesChange?: (update: Partial<DrawingPreferences>) => void
}

const favoriteEligible = new Set<ChartTool>(['horizontal', 'vertical', 'gann', 'fibonacci', 'annotation'])

export function ToolRail({
  activeTool,
  onToolChange,
  onClear,
  onReset,
  onUndo,
  preferences,
  onPreferencesChange,
}: ToolRailProps) {
  const favorites = preferences?.favoriteTools ?? []
  const orderedTools = tools.slice().sort((left, right) => {
    const leftFavorite = favorites.includes(left.id) ? 0 : 1
    const rightFavorite = favorites.includes(right.id) ? 0 : 1
    return leftFavorite - rightFavorite
  })
  const toggleFavorite = () => {
    if (!favoriteEligible.has(activeTool)) return
    onPreferencesChange?.({
      favoriteTools: favorites.includes(activeTool)
        ? favorites.filter((tool) => tool !== activeTool)
        : [...favorites, activeTool],
    })
  }
  const cycleMagnet = () => {
    const current = preferences?.magnetMode ?? 'weak'
    onPreferencesChange?.({
      magnetMode: current === 'off' ? 'weak' : current === 'weak' ? 'strong' : 'off',
    })
  }
  return (
    <nav className="tool-rail" aria-label="Chart drawing tools">
      {orderedTools.map((tool, index) => {
        const Icon = tool.icon
        return (
          <div className={`tool-rail-item ${favorites.includes(tool.id) ? 'is-favorite' : ''}`} key={tool.id}>
            {index === 2 && <span className="tool-rail-divider" />}
            <button
              className={`icon-button ${activeTool === tool.id ? 'is-active' : ''}`}
              onClick={() => onToolChange(tool.id)}
              title={tool.label}
              aria-label={tool.label}
            >
              <Icon size={18} strokeWidth={1.8} />
              {favorites.includes(tool.id) && <span className="tool-favorite-dot" />}
            </button>
          </div>
        )
      })}
      <div className="tool-rail-spacer" />
      <button
        className={`icon-button ${favoriteEligible.has(activeTool) && favorites.includes(activeTool) ? 'is-active' : ''}`}
        onClick={toggleFavorite}
        disabled={!favoriteEligible.has(activeTool)}
        title="Add or remove the active tool from favorites"
        aria-label="Toggle active drawing tool favorite"
      >
        <Star size={17} strokeWidth={1.8} />
      </button>
      <button
        className={`icon-button magnet-${preferences?.magnetMode ?? 'weak'}`}
        onClick={cycleMagnet}
        title={`OHLC magnet: ${preferences?.magnetMode ?? 'weak'}`}
        aria-label={`OHLC magnet ${preferences?.magnetMode ?? 'weak'}`}
      >
        <Magnet size={17} strokeWidth={1.8} />
      </button>
      <button
        className={`icon-button ${preferences?.keepDrawing ? 'is-active' : ''}`}
        onClick={() => onPreferencesChange?.({ keepDrawing: !preferences?.keepDrawing })}
        title={preferences?.keepDrawing ? 'Keep drawing is on' : 'Keep drawing is off'}
        aria-label="Toggle keep drawing"
      >
        <Pin size={17} strokeWidth={1.8} />
      </button>
      <button className="icon-button" onClick={onUndo} title="Undo last drawing" aria-label="Undo last drawing">
        <Undo2 size={18} strokeWidth={1.8} />
      </button>
      <button className="icon-button" onClick={onReset} title="Reset chart view" aria-label="Reset chart view">
        <RotateCcw size={18} strokeWidth={1.8} />
      </button>
      <button className="icon-button danger" onClick={onClear} title="Clear manual drawings" aria-label="Clear manual drawings">
        <Trash2 size={18} strokeWidth={1.8} />
      </button>
    </nav>
  )
}
