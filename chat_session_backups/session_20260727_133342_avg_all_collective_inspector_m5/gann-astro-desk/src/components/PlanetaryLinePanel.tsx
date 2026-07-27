import { Activity, Copy, Orbit, RefreshCw, RotateCcw, ShieldCheck, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import {
  PLANETARY_LINE_MAX_LINES,
  PLANETARY_LINE_PLANETS,
  parsePlanetaryLineValues,
  planetaryLineCount,
  planetaryLineGroupCount,
} from '../planetaryLines'
import type { PlanetaryLineOverlayStatus } from '../usePlanetaryLineOverlay'
import type {
  PlanetaryCollectiveField,
  PlanetaryLineGroup,
  PlanetaryLineOverlaySettings,
} from '../types'

type PlanetaryLinePanelProps = {
  settings: PlanetaryLineOverlaySettings
  status: PlanetaryLineOverlayStatus
  error: string
  plottedLineCount: number
  sampledTimestampCount: number
  generatedAtUtc: string
  collectiveField: PlanetaryCollectiveField | null
  collectiveInspectorOpen: boolean
  onOpenCollectiveInspector: () => void
  onChange: (settings: PlanetaryLineOverlaySettings) => void
  onRecalculate: () => void
  onReset: () => void
  onClose: () => void
}

type ListField = 'nValues' | 'fValues' | 'degrees'

function draftKey(planet: string, field: ListField): string {
  return `${planet}:${field}`
}

function listText(values: number[]): string {
  return values.join(', ')
}

function ratioText(value: number | null): string {
  return value == null ? 'n/a' : value.toFixed(3)
}

export function PlanetaryLinePanel({
  settings,
  status,
  error,
  plottedLineCount,
  sampledTimestampCount,
  generatedAtUtc,
  collectiveField,
  collectiveInspectorOpen,
  onOpenCollectiveInspector,
  onChange,
  onRecalculate,
  onReset,
  onClose,
}: PlanetaryLinePanelProps) {
  const [drafts, setDrafts] = useState<Record<string, string>>({})
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [focusedKey, setFocusedKey] = useState('')
  const requestedLineCount = planetaryLineCount(settings)
  const overLimit = requestedLineCount > PLANETARY_LINE_MAX_LINES
  const planetLabels = useMemo(
    () => new Map<string, string>(PLANETARY_LINE_PLANETS.map((item) => [item.planet, item.label])),
    [],
  )

  useEffect(() => {
    const normalized = Object.fromEntries(settings.groups.flatMap((group) => [
      [draftKey(group.planet, 'nValues'), listText(group.nValues)],
      [draftKey(group.planet, 'fValues'), listText(group.fValues)],
      [draftKey(group.planet, 'degrees'), listText(group.degrees)],
    ]))
    setDrafts((current) => Object.fromEntries(
      Object.entries(normalized).map(([key, value]) => [
        key,
        key === focusedKey && current[key] != null ? current[key] : value,
      ]),
    ))
  }, [focusedKey, settings.groups])

  const updateGroup = (planet: string, update: Partial<PlanetaryLineGroup>) => {
    onChange({
      ...settings,
      groups: settings.groups.map((group) => (
        group.planet === planet ? { ...group, ...update } : group
      )),
    })
  }

  const updateList = (
    planet: string,
    field: ListField,
    text: string,
    minimum: number,
    maximum: number,
  ) => {
    const key = draftKey(planet, field)
    setDrafts((current) => ({ ...current, [key]: text }))
    try {
      const values = parsePlanetaryLineValues(text, field, minimum, maximum)
      setFieldErrors((current) => ({ ...current, [key]: '' }))
      updateGroup(planet, { [field]: values })
    } catch (reason) {
      setFieldErrors((current) => ({
        ...current,
        [key]: reason instanceof Error ? reason.message : String(reason),
      }))
    }
  }

  const restoreList = (group: PlanetaryLineGroup, field: ListField) => {
    const key = draftKey(group.planet, field)
    if (!fieldErrors[key]) return
    setDrafts((current) => ({ ...current, [key]: listText(group[field]) }))
    setFieldErrors((current) => ({ ...current, [key]: '' }))
  }

  const copyParametersToAll = (source: PlanetaryLineGroup) => {
    onChange({
      ...settings,
      groups: settings.groups.map((group) => ({
        ...group,
        mode: source.mode,
        nValues: [...source.nValues],
        fValues: [...source.fValues],
        degrees: [...source.degrees],
      })),
    })
  }

  return (
    <aside className="planetary-line-panel" aria-label="Live support and resistance line laboratory">
      <header>
        <span className="planetary-line-heading-icon"><Orbit size={17} /></span>
        <div>
          <strong>Live SR Lab</strong>
          <span>Per-planet live line calculations</span>
        </div>
        <button
          className="icon-button"
          onClick={onRecalculate}
          disabled={status === 'calculating'}
          title="Recalculate live support and resistance lines"
          aria-label="Recalculate live support and resistance lines"
        >
          <RefreshCw size={14} />
        </button>
        <button className="icon-button" onClick={onReset} title="Reset planetary line settings" aria-label="Reset planetary line settings"><RotateCcw size={14} /></button>
        <button className="icon-button" onClick={onClose} title="Close Live SR Lab" aria-label="Close Live SR Lab"><X size={15} /></button>
      </header>

      <section className="planetary-line-master-row">
        <label className="planetary-line-master-toggle">
          <input
            type="checkbox"
            checked={settings.visible}
            onChange={(event) => onChange({ ...settings, visible: event.target.checked })}
          />
          <span>Show calculated lines</span>
        </label>
        <span className={`planetary-line-count ${overLimit ? 'is-error' : ''}`}>
          {requestedLineCount}/{PLANETARY_LINE_MAX_LINES}
        </span>
        <label className="planetary-line-sample-control">
          Samples
          <select
            value={settings.sampleLimit}
            onChange={(event) => onChange({ ...settings, sampleLimit: Number(event.target.value) })}
          >
            {[300, 600, 900, 1200].map((value) => <option key={value} value={value}>{value}</option>)}
          </select>
        </label>
      </section>

      <section className={`planetary-line-runtime is-${status}`} aria-live="polite">
        <i />
        <span>
          {status === 'calculating' && `Calculating ${requestedLineCount} lines`}
          {status === 'ready' && `${plottedLineCount} lines across ${sampledTimestampCount} bar times${generatedAtUtc ? ` | updated ${new Date(generatedAtUtc).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}` : ''}`}
          {status === 'idle' && (settings.visible ? 'Enable at least one planet' : 'Overlay hidden')}
          {status === 'error' && (error || 'Planetary line calculation failed')}
        </span>
      </section>

      {collectiveField && (
        <section
          className={`collective-field-summary is-${collectiveField.latest.reliability.toLowerCase()}`}
          aria-label="AVG collective geometry"
        >
          <div className="collective-field-summary-heading">
            <strong>AVG collective geometry</strong>
            <span>{collectiveField.latest.state.replaceAll('_', ' ')}</span>
          </div>
          <div className="collective-field-metrics">
            <span title="R1 measures concentration of the ten-body circular field">
              R1 <strong>{ratioText(collectiveField.latest.coherenceR1)}</strong>
            </span>
            <span title="R2 measures two-pole or opposition-like geometry">
              R2 <strong>{ratioText(collectiveField.latest.polarisationR2)}</strong>
            </span>
            <span title="Whether the collective longitude has enough concentration to be treated as stable">
              <strong>{collectiveField.latest.reliability.replaceAll('_', ' ')}</strong>
            </span>
          </div>
          <small>
            {collectiveField.summary.reliabilityCounts.RELIABLE ?? 0} reliable of{' '}
            {collectiveField.summary.sampleCount} samples | legacy lines unchanged
          </small>
          <button
            className={collectiveInspectorOpen ? 'collective-field-open-command is-active' : 'collective-field-open-command'}
            onClick={onOpenCollectiveInspector}
            aria-label="Open planetary collective field inspector"
          >
            <Activity size={12} /> Collective inspector
          </button>
        </section>
      )}

      <div className="planetary-line-groups">
        {settings.groups.map((group) => {
          const groupCount = planetaryLineGroupCount(group)
          return (
            <details className={`planetary-line-group ${group.enabled ? 'is-enabled' : ''}`} key={group.planet}>
              <summary>
                <input
                  type="checkbox"
                  checked={group.enabled}
                  onClick={(event) => event.stopPropagation()}
                  onChange={(event) => updateGroup(group.planet, { enabled: event.target.checked })}
                  aria-label={`Enable ${planetLabels.get(group.planet) ?? group.planet}`}
                />
                <i style={{ background: group.color }} />
                <strong>{planetLabels.get(group.planet) ?? group.planet}</strong>
                <span>{group.mode}</span>
                <small>{groupCount} lines</small>
              </summary>
              <div className="planetary-line-group-fields">
                <div className="planetary-line-mode-row" aria-label={`${group.planet} calculation mode`}>
                  {(['direct', 'mirror', 'both'] as const).map((mode) => (
                    <button
                      key={mode}
                      className={group.mode === mode ? 'is-active' : ''}
                      onClick={() => updateGroup(group.planet, { mode })}
                    >
                      {mode}
                    </button>
                  ))}
                  <input
                    className="planetary-line-color"
                    type="color"
                    value={group.color}
                    onChange={(event) => updateGroup(group.planet, { color: event.target.value })}
                    title={`${group.planet} line color`}
                    aria-label={`${group.planet} line color`}
                  />
                </div>
                <label>
                  <span>n values</span>
                  <input
                    value={drafts[draftKey(group.planet, 'nValues')] ?? listText(group.nValues)}
                    onChange={(event) => updateList(group.planet, 'nValues', event.target.value, 0.000001, 100_000)}
                    onFocus={() => setFocusedKey(draftKey(group.planet, 'nValues'))}
                    onBlur={() => { setFocusedKey(''); restoreList(group, 'nValues') }}
                    spellCheck={false}
                  />
                  {fieldErrors[draftKey(group.planet, 'nValues')] && <small>{fieldErrors[draftKey(group.planet, 'nValues')]}</small>}
                </label>
                <label>
                  <span>f values</span>
                  <input
                    value={drafts[draftKey(group.planet, 'fValues')] ?? listText(group.fValues)}
                    onChange={(event) => updateList(group.planet, 'fValues', event.target.value, 0.000001, 1_000)}
                    onFocus={() => setFocusedKey(draftKey(group.planet, 'fValues'))}
                    onBlur={() => { setFocusedKey(''); restoreList(group, 'fValues') }}
                    spellCheck={false}
                  />
                  {fieldErrors[draftKey(group.planet, 'fValues')] && <small>{fieldErrors[draftKey(group.planet, 'fValues')]}</small>}
                </label>
                <label>
                  <span>Degree values</span>
                  <input
                    value={drafts[draftKey(group.planet, 'degrees')] ?? listText(group.degrees)}
                    onChange={(event) => updateList(group.planet, 'degrees', event.target.value, 0.000001, 360)}
                    onFocus={() => setFocusedKey(draftKey(group.planet, 'degrees'))}
                    onBlur={() => { setFocusedKey(''); restoreList(group, 'degrees') }}
                    spellCheck={false}
                  />
                  {fieldErrors[draftKey(group.planet, 'degrees')] && <small>{fieldErrors[draftKey(group.planet, 'degrees')]}</small>}
                </label>
                <button
                  className="planetary-line-copy-command"
                  onClick={() => copyParametersToAll(group)}
                  title={`Copy ${group.planet} mode and values to every planet`}
                >
                  <Copy size={12} /> Use values for all planets
                </button>
              </div>
            </details>
          )
        })}
      </div>

      <footer>
        <ShieldCheck size={13} />
        <span>Research-only overlay</span>
        <small>Excluded from Auto Suggest, validation, and execution</small>
      </footer>
    </aside>
  )
}
