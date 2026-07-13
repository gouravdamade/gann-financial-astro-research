import {
  AlertTriangle,
  CopyPlus,
  Download,
  FolderTree,
  Save,
  Trash2,
  Upload,
  X,
} from 'lucide-react'
import { useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import type { ChartLayout } from '../types'
import type { LayoutSaveStatus } from '../useChartLayouts'

type LayoutToolbarProps = {
  layouts: ChartLayout[]
  activeLayout: ChartLayout | null
  saveStatus: LayoutSaveStatus
  error: string | null
  objectsOpen: boolean
  onSelect: (layoutId: string) => void
  onSave: () => Promise<boolean>
  onSaveAs: (name: string) => Promise<boolean>
  onDelete: (layoutId: string) => Promise<void>
  onToggleObjects: () => void
  onExport: () => void
  onImport: (contents: string) => Promise<boolean>
}

export function LayoutToolbar({
  layouts,
  activeLayout,
  saveStatus,
  error,
  objectsOpen,
  onSelect,
  onSave,
  onSaveAs,
  onDelete,
  onToggleObjects,
  onExport,
  onImport,
}: LayoutToolbarProps) {
  const [saveAsOpen, setSaveAsOpen] = useState(false)
  const [saveAsName, setSaveAsName] = useState('')
  const [deleteOpen, setDeleteOpen] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const submitSaveAs = async (event: FormEvent) => {
    event.preventDefault()
    if (await onSaveAs(saveAsName)) {
      setSaveAsOpen(false)
      setSaveAsName('')
    }
  }

  const importFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return
    await onImport(await file.text())
  }

  const statusLabel = saveStatus === 'saved'
    ? 'Saved'
    : saveStatus === 'saving'
      ? 'Saving'
      : saveStatus === 'loading'
        ? 'Loading'
        : saveStatus === 'conflict'
          ? 'Conflict'
          : 'Save error'

  return (
    <div className="layout-toolbar" aria-label="Chart layout controls">
      <select
        value={activeLayout?.layoutId ?? ''}
        onChange={(event) => void onSelect(event.target.value)}
        disabled={!activeLayout || saveStatus === 'loading'}
        title="Named chart layout"
        aria-label="Named chart layout"
      >
        {layouts.map((layout) => (
          <option key={layout.layoutId} value={layout.layoutId}>
            {layout.name}{layout.isDefault ? ' (default)' : ''}
          </option>
        ))}
      </select>
      <span className={`layout-save-state is-${saveStatus}`} title={error ?? statusLabel}>
        {saveStatus === 'conflict' || saveStatus === 'error' ? <AlertTriangle size={12} /> : <i />}
        {statusLabel}
      </span>
      <button className="icon-button" onClick={() => void onSave()} title="Save layout now" aria-label="Save layout now"><Save size={15} /></button>
      <button
        className="icon-button"
        onClick={() => {
          setSaveAsName(`${activeLayout?.name ?? 'Chart layout'} copy`)
          setSaveAsOpen(true)
        }}
        title="Save layout as"
        aria-label="Save layout as"
      ><CopyPlus size={15} /></button>
      <button className={`icon-button ${objectsOpen ? 'is-active' : ''}`} onClick={onToggleObjects} title="Drawing object tree" aria-label="Drawing object tree"><FolderTree size={15} /></button>
      <button className="icon-button" onClick={onExport} disabled={!activeLayout} title="Export layout JSON" aria-label="Export layout JSON"><Download size={15} /></button>
      <button className="icon-button" onClick={() => fileRef.current?.click()} title="Import layout JSON" aria-label="Import layout JSON"><Upload size={15} /></button>
      <button className="icon-button" onClick={() => setDeleteOpen(true)} disabled={!activeLayout} title="Delete layout" aria-label="Delete layout"><Trash2 size={15} /></button>
      <input ref={fileRef} type="file" accept="application/json,.json" hidden onChange={(event) => void importFile(event)} />

      {saveAsOpen && (
        <div className="compact-dialog-backdrop" role="presentation">
          <form className="compact-dialog" role="dialog" aria-modal="true" aria-label="Save chart layout as" onSubmit={(event) => void submitSaveAs(event)}>
            <header><strong>Save layout as</strong><button type="button" className="icon-button" onClick={() => setSaveAsOpen(false)} title="Close"><X size={15} /></button></header>
            <label>Layout name<input autoFocus value={saveAsName} maxLength={80} onChange={(event) => setSaveAsName(event.target.value)} /></label>
            <footer><button type="button" onClick={() => setSaveAsOpen(false)}>Cancel</button><button type="submit" className="primary-command" disabled={!saveAsName.trim()}>Save copy</button></footer>
          </form>
        </div>
      )}

      {deleteOpen && activeLayout && (
        <div className="compact-dialog-backdrop" role="presentation">
          <section className="compact-dialog" role="alertdialog" aria-modal="true" aria-label="Delete chart layout">
            <header><strong>Delete layout</strong><button className="icon-button" onClick={() => setDeleteOpen(false)} title="Close"><X size={15} /></button></header>
            <p>Delete <strong>{activeLayout.name}</strong>? Its persisted drawings will be removed with it.</p>
            <footer><button onClick={() => setDeleteOpen(false)}>Cancel</button><button className="danger-command" onClick={() => { setDeleteOpen(false); void onDelete(activeLayout.layoutId) }}>Delete</button></footer>
          </section>
        </div>
      )}
    </div>
  )
}
