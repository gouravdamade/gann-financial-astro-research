import {
  Eye,
  EyeOff,
  Fan,
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
  return <Minus size={15} />
}

function localDateTimeValue(iso: string): string {
  const value = new Date(iso)
  if (!Number.isFinite(value.getTime())) return ''
  return new Date(value.getTime() - value.getTimezoneOffset() * 60_000).toISOString().slice(0, 16)
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
  const chartDrawings = useMemo(
    () => drawings.filter((item) => item.type !== 'square_of_nine'),
    [drawings],
  )
  const selected = chartDrawings.find((item) => item.drawingId === selectedDrawingId) ?? null
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

  const updateAnchor = (index: number, update: Partial<ChartDrawing['anchors'][number]>) => {
    if (!selected || selected.locked) return
    const anchors = selected.anchors.map((anchor, anchorIndex) => anchorIndex === index
      ? { ...anchor, ...update }
      : anchor)
    onUpdate(selected.drawingId, { anchors })
  }

  return (
    <aside className="drawing-object-panel" aria-label="Drawing object tree">
      <header>
        <div><strong>Objects</strong><span>{chartDrawings.length} research drawings</span></div>
        <button className="icon-button" onClick={onClose} title="Close object tree"><X size={16} /></button>
      </header>
      <div className="drawing-object-list">
        {chartDrawings.length === 0 && <p className="drawing-empty">Place a line or Gann fan to add it here.</p>}
        {chartDrawings.slice().sort((a, b) => b.zIndex - a.zIndex).map((drawing) => (
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

          <div className="drawing-anchor-properties">
            <div className="property-heading"><strong>Anchors</strong><span>{selected.locked ? 'Locked' : 'Drag on chart or edit'}</span></div>
            {selected.anchors.map((anchor, index) => (
              <div className="drawing-anchor-fields" key={`${selected.drawingId}-${index}`}>
                <strong>{selected.type === 'gann_fan' ? (index === 0 ? 'Origin' : 'Slope') : 'Position'}</strong>
                {selected.type !== 'horizontal_line' && <label>Time<input type="datetime-local" value={localDateTimeValue(anchor.timeUtc)} disabled={selected.locked} onChange={(event) => {
                  const date = new Date(event.target.value)
                  if (Number.isFinite(date.getTime())) updateAnchor(index, { timeUtc: date.toISOString() })
                }} /></label>}
                {selected.type !== 'vertical_line' && <label>Price<input type="number" step="any" value={anchor.price} disabled={selected.locked} onChange={(event) => updateAnchor(index, { price: Number(event.target.value) })} /></label>}
              </div>
            ))}
          </div>

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
          <button className="drawing-delete-command" onClick={() => onDelete(selected.drawingId)} disabled={selected.locked}><Trash2 size={14} /> Delete drawing</button>
        </div>
      )}
    </aside>
  )
}
