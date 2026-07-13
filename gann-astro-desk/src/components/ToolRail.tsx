import {
  Crosshair,
  Fan,
  MessageSquarePlus,
  Minus,
  MousePointer2,
  RotateCcw,
  SeparatorVertical,
  Trash2,
  Undo2,
} from 'lucide-react'
import type { ChartTool } from '../types'

const tools: Array<{ id: ChartTool; label: string; icon: typeof MousePointer2 }> = [
  { id: 'select', label: 'Select aspect or drawing', icon: MousePointer2 },
  { id: 'crosshair', label: 'Crosshair', icon: Crosshair },
  { id: 'annotation', label: 'Add annotation', icon: MessageSquarePlus },
  { id: 'horizontal', label: 'Horizontal line', icon: Minus },
  { id: 'vertical', label: 'Vertical line', icon: SeparatorVertical },
  { id: 'gann', label: 'Gann fan', icon: Fan },
]

type ToolRailProps = {
  activeTool: ChartTool
  onToolChange: (tool: ChartTool) => void
  onClear?: () => void
  onReset?: () => void
  onUndo?: () => void
}

export function ToolRail({ activeTool, onToolChange, onClear, onReset, onUndo }: ToolRailProps) {
  return (
    <nav className="tool-rail" aria-label="Chart drawing tools">
      {tools.map((tool, index) => {
        const Icon = tool.icon
        return (
          <div className="tool-rail-item" key={tool.id}>
            {index === 2 && <span className="tool-rail-divider" />}
            <button
              className={`icon-button ${activeTool === tool.id ? 'is-active' : ''}`}
              onClick={() => onToolChange(tool.id)}
              title={tool.label}
              aria-label={tool.label}
            >
              <Icon size={18} strokeWidth={1.8} />
            </button>
          </div>
        )
      })}
      <div className="tool-rail-spacer" />
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
