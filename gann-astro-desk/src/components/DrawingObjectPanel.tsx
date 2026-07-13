import {
  Eye,
  EyeOff,
  Fan,
  Grid3X3,
  Lock,
  Minus,
  Save,
  SeparatorVertical,
  Trash2,
  Unlock,
  X,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import type {
  ChartDrawing,
  DrawingTemplate,
  SquareOfNineSettings,
} from '../types'

type DrawingObjectPanelProps = {
  drawings: ChartDrawing[]
  templates: DrawingTemplate[]
  selectedDrawingId: string | null
  onSelect: (drawingId: string | null) => void
  onUpdate: (drawingId: string, update: Partial<ChartDrawing>) => void
  onDelete: (drawingId: string) => void
  onCreateTemplate: (name: string, drawing: ChartDrawing) => Promise<DrawingTemplate>
  onRemoveTemplate: (templateId: string) => Promise<void>
  onClose: () => void
}

function DrawingIcon({ drawing }: { drawing: ChartDrawing }) {
  if (drawing.type === 'vertical_line') return <SeparatorVertical size={15} />
  if (drawing.type === 'gann_fan') return <Fan size={15} />
  if (drawing.type === 'square_of_nine') return <Grid3X3 size={15} />
  return <Minus size={15} />
}

function numberSetting(
  drawing: ChartDrawing,
  key: keyof SquareOfNineSettings,
  fallback: number,
): number {
  const value = drawing.settings[key]
  return typeof value === 'number' && Number.isFinite(value) ? value : fallback
}

export function DrawingObjectPanel({
  drawings,
  templates,
  selectedDrawingId,
  onSelect,
  onUpdate,
  onDelete,
  onCreateTemplate,
  onRemoveTemplate,
  onClose,
}: DrawingObjectPanelProps) {
  const selected = drawings.find((item) => item.drawingId === selectedDrawingId) ?? null
  const matchingTemplates = useMemo(
    () => templates.filter((item) => item.drawingType === selected?.type),
    [selected?.type, templates],
  )
  const [templateId, setTemplateId] = useState('')
  const [templateName, setTemplateName] = useState('')

  useEffect(() => {
    setTemplateId('')
    setTemplateName('')
  }, [selectedDrawingId])

  const updateStyle = (update: Partial<ChartDrawing['style']>) => {
    if (selected) onUpdate(selected.drawingId, { style: { ...selected.style, ...update } })
  }

  const updateSettings = (update: Record<string, unknown>) => {
    if (selected) onUpdate(selected.drawingId, { settings: { ...selected.settings, ...update } })
  }

  return (
    <aside className="drawing-object-panel" aria-label="Drawing object tree">
      <header>
        <div><strong>Objects</strong><span>{drawings.length} research drawings</span></div>
        <button className="icon-button" onClick={onClose} title="Close object tree"><X size={16} /></button>
      </header>
      <div className="drawing-object-list">
        {drawings.length === 0 && <p className="drawing-empty">Place a line, fan, or Square of Nine to add it here.</p>}
        {drawings.slice().sort((a, b) => b.zIndex - a.zIndex).map((drawing) => (
          <div className={`drawing-object-row ${drawing.drawingId === selectedDrawingId ? 'is-selected' : ''}`} key={drawing.drawingId}>
            <button className="drawing-object-name" onClick={() => onSelect(drawing.drawingId)} title={`Select ${drawing.name}`}>
              <DrawingIcon drawing={drawing} />
              <span><strong>{drawing.name}</strong><small>Research only</small></span>
            </button>
            <button className="icon-button" onClick={() => onUpdate(drawing.drawingId, { visible: !drawing.visible })} title={drawing.visible ? 'Hide drawing' : 'Show drawing'}>{drawing.visible ? <Eye size={14} /> : <EyeOff size={14} />}</button>
            <button className="icon-button" onClick={() => onUpdate(drawing.drawingId, { locked: !drawing.locked })} title={drawing.locked ? 'Unlock drawing' : 'Lock drawing'}>{drawing.locked ? <Lock size={14} /> : <Unlock size={14} />}</button>
            <button className="icon-button" onClick={() => onDelete(drawing.drawingId)} disabled={drawing.locked} title="Delete drawing"><Trash2 size={14} /></button>
          </div>
        ))}
      </div>

      {selected && (
        <div className="drawing-properties">
          <div className="property-heading"><strong>Properties</strong><span>{selected.type.replaceAll('_', ' ')}</span></div>
          <label>Name<input value={selected.name} maxLength={80} onChange={(event) => onUpdate(selected.drawingId, { name: event.target.value })} /></label>
          <div className="property-grid">
            <label>Color<input className="color-swatch-input" type="color" value={selected.style.color} onChange={(event) => updateStyle({ color: event.target.value })} /></label>
            <label>Width<select value={selected.style.lineWidth} onChange={(event) => updateStyle({ lineWidth: Number(event.target.value) })}><option value={1}>1 px</option><option value={2}>2 px</option><option value={3}>3 px</option><option value={4}>4 px</option></select></label>
            <label>Line<select value={selected.style.lineStyle} onChange={(event) => updateStyle({ lineStyle: event.target.value as ChartDrawing['style']['lineStyle'] })}><option value="solid">Solid</option><option value="dashed">Dashed</option><option value="dotted">Dotted</option></select></label>
            <label>Opacity<input type="number" min={0.1} max={1} step={0.1} value={selected.style.opacity} onChange={(event) => updateStyle({ opacity: Number(event.target.value) })} /></label>
          </div>

          {selected.type === 'square_of_nine' && (
            <div className="square9-properties">
              <div className="property-heading"><strong>Square of Nine</strong><span>Provisional geometry</span></div>
              <div className="property-grid">
                <label>Center<input type="number" step="0.001" value={numberSetting(selected, 'centerValue', selected.anchors[0]?.price ?? 1)} onChange={(event) => updateSettings({ centerValue: Number(event.target.value) })} /></label>
                <label>Increment<input type="number" min="0.00001" step="0.001" value={numberSetting(selected, 'increment', 0.01)} onChange={(event) => updateSettings({ increment: Number(event.target.value) })} /></label>
                <label>Rings<input type="number" min={1} max={12} step={1} value={numberSetting(selected, 'rings', 3)} onChange={(event) => updateSettings({ rings: Number(event.target.value) })} /></label>
                <label>Angle offset<input type="number" min={-360} max={360} step={1} value={numberSetting(selected, 'angleOffsetDeg', 0)} onChange={(event) => updateSettings({ angleOffsetDeg: Number(event.target.value) })} /></label>
                <label>Numbers<select value={String(selected.settings.numberRotation ?? 'clockwise')} onChange={(event) => updateSettings({ numberRotation: event.target.value })}><option value="clockwise">Clockwise</option><option value="counterclockwise">Counterclockwise</option></select></label>
                <label>Angles<select value={String(selected.settings.angleRotation ?? 'clockwise')} onChange={(event) => updateSettings({ angleRotation: event.target.value })}><option value="clockwise">Clockwise</option><option value="counterclockwise">Counterclockwise</option></select></label>
              </div>
              <div className="property-toggles">
                <label><input type="checkbox" checked={Boolean(selected.settings.showCardinals ?? true)} onChange={(event) => updateSettings({ showCardinals: event.target.checked })} /> Cardinals</label>
                <label><input type="checkbox" checked={Boolean(selected.settings.showDiagonals ?? true)} onChange={(event) => updateSettings({ showDiagonals: event.target.checked })} /> Diagonals</label>
                <label><input type="checkbox" checked={Boolean(selected.settings.showLabels ?? true)} onChange={(event) => updateSettings({ showLabels: event.target.checked })} /> Labels</label>
                <label><input type="checkbox" checked={Boolean(selected.settings.showPriceProjections ?? false)} onChange={(event) => updateSettings({ showPriceProjections: event.target.checked })} /> Price levels</label>
                <label><input type="checkbox" checked={Boolean(selected.settings.showTimeProjections ?? false)} onChange={(event) => updateSettings({ showTimeProjections: event.target.checked })} /> Time spokes</label>
              </div>
            </div>
          )}

          <div className="drawing-template-controls">
            <div className="property-heading"><strong>Template</strong><span>Style and settings</span></div>
            <div className="template-apply-row">
              <select value={templateId} onChange={(event) => setTemplateId(event.target.value)}><option value="">Choose template</option>{matchingTemplates.map((template) => <option key={template.templateId} value={template.templateId}>{template.name}</option>)}</select>
              <button onClick={() => {
                const template = matchingTemplates.find((item) => item.templateId === templateId)
                if (template) onUpdate(selected.drawingId, { style: template.style, settings: { ...selected.settings, ...template.settings } })
              }} disabled={!templateId}>Apply</button>
              <button className="icon-button" onClick={() => templateId && void onRemoveTemplate(templateId)} disabled={!templateId} title="Delete template"><Trash2 size={14} /></button>
            </div>
            <div className="template-save-row">
              <input value={templateName} maxLength={80} placeholder="New template name" onChange={(event) => setTemplateName(event.target.value)} />
              <button onClick={() => void onCreateTemplate(templateName, selected).then(() => setTemplateName(''))} disabled={!templateName.trim()}><Save size={14} /> Save</button>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
