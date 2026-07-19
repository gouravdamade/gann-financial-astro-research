import { Activity, LoaderCircle, RefreshCw } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { fetchRsiEvidence } from '../api'
import { normalizeRsiLevels, normalizeRsiPeriod } from '../rsi'
import type { ChartAnnotation, RsiEvidence, RsiPaneSettings } from '../types'

type RsiPanelProps = {
  eventId: string
  selectedAnnotation: ChartAnnotation | null
  settings: RsiPaneSettings
  onSettingsChange: (update: Partial<RsiPaneSettings>) => void
}

function valueLabel(value: number | null): string {
  return value == null ? '-' : value.toFixed(2)
}

export function RsiPanel({
  eventId,
  selectedAnnotation,
  settings,
  onSettingsChange,
}: RsiPanelProps) {
  const [evidence, setEvidence] = useState<RsiEvidence | null>(null)
  const [levelsInput, setLevelsInput] = useState(settings.levels.join(', '))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => setLevelsInput(settings.levels.join(', ')), [settings.levels])

  const load = useCallback(async () => {
    setBusy(true)
    setError('')
    try {
      setEvidence(await fetchRsiEvidence({
        eventId,
        annotationId: selectedAnnotation?.annotationId,
        period: settings.period,
        levels: settings.levels,
      }))
    } catch (reason) {
      setEvidence(null)
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }, [eventId, selectedAnnotation?.annotationId, settings.levels, settings.period])

  useEffect(() => { void load() }, [load])

  const commitLevels = () => {
    const levels = normalizeRsiLevels(levelsInput.split(/[\s,;]+/).map(Number))
    setLevelsInput(levels.join(', '))
    onSettingsChange({ levels })
  }

  return (
    <section className="local-jyotish-panel rsi-analysis-panel">
      <header className="local-jyotish-header">
        <div><Activity size={16} /><strong>RSI evidence</strong></div>
        <button className="icon-button" onClick={() => void load()} disabled={busy} title="Refresh RSI evidence">
          {busy ? <LoaderCircle className="is-spinning" size={15} /> : <RefreshCw size={15} />}
        </button>
      </header>
      <div className="local-jyotish-boundary">
        Wilder close RSI from fully closed {evidence?.timeframe ?? 'chart'} bars. Level contact alone does not prove reversal.
      </div>
      <div className="rsi-analysis-controls">
        <label>Period<input type="number" min={2} max={200} value={settings.period} onChange={(event) => onSettingsChange({ period: normalizeRsiPeriod(Number(event.target.value)) })} /></label>
        <label>Levels<input value={levelsInput} onChange={(event) => setLevelsInput(event.target.value)} onBlur={commitLevels} onKeyDown={(event) => { if (event.key === 'Enter') commitLevels() }} /></label>
        <label className="rsi-pane-toggle"><input type="checkbox" checked={settings.visible} onChange={(event) => onSettingsChange({ visible: event.target.checked })} /> Show below chart</label>
      </div>
      {error && <div className="local-jyotish-error">{error}</div>}
      {busy && !evidence && <div className="local-jyotish-thinking"><LoaderCircle className="is-spinning" size={15} /> Calculating closed-bar RSI...</div>}
      {evidence && (
        <div className="rsi-evidence-body">
          <section className="rsi-focus-value">
            <span>At analysis cutoff</span>
            <strong>{evidence.focus ? evidence.focus.value.toFixed(2) : 'Warm-up incomplete'}</strong>
            <em>{evidence.focus?.zone.replaceAll('_', ' ') ?? `${evidence.closedBarCountAtCutoff}/${evidence.warmupBarsRequired} bars`}</em>
            <small>{new Date(evidence.analysisCutoff).toLocaleString()} | {evidence.closedBarCountAtCutoff} closed bars</small>
          </section>
          <dl className="rsi-evidence-grid">
            <div><dt>Window start</dt><dd>{valueLabel(evidence.eventWindow.startValue)}</dd></div>
            <div><dt>Window end</dt><dd>{valueLabel(evidence.eventWindow.endValue)}</dd></div>
            <div><dt>Minimum</dt><dd>{valueLabel(evidence.eventWindow.minimum)}</dd></div>
            <div><dt>Maximum</dt><dd>{valueLabel(evidence.eventWindow.maximum)}</dd></div>
            <div><dt>Change</dt><dd>{valueLabel(evidence.eventWindow.change)}</dd></div>
            <div><dt>Samples</dt><dd>{evidence.eventWindow.sampleCount}</dd></div>
          </dl>
          <section className="rsi-crossing-list">
            <header><strong>Level crossings inside event</strong><span>{evidence.eventWindow.crossings.length}</span></header>
            {evidence.eventWindow.crossings.map((crossing, index) => (
              <div key={`${crossing.time}-${crossing.level}-${index}`}>
                <strong>{crossing.direction === 'up' ? 'Crossed above' : 'Crossed below'} {crossing.level}</strong>
                <span>{crossing.from.toFixed(2)} to {crossing.to.toFixed(2)}</span>
                <small>{new Date(crossing.time).toLocaleString()}</small>
              </div>
            ))}
            {!evidence.eventWindow.crossings.length && <p>No configured level crossing occurred in the timestamp-safe event window.</p>}
          </section>
          <footer>Contract {evidence.contract} | research-only | excluded from live inference until prospective validation.</footer>
        </div>
      )}
    </section>
  )
}
