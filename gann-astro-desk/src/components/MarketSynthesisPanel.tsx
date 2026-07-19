import { LoaderCircle, Send, Workflow } from 'lucide-react'
import { useEffect, useState } from 'react'
import { analyzeWithMarketSynthesis, fetchMarketSynthesisHealth } from '../api'
import type {
  ChartAnnotation,
  MarketSynthesisDraft,
  MarketSynthesisHealth,
  RsiPaneSettings,
} from '../types'

type MarketSynthesisPanelProps = {
  eventId: string
  selectedAnnotation: ChartAnnotation | null
  rsiSettings: RsiPaneSettings
}

const DEFAULT_QUESTION = 'Compare the timestamp-safe astrology, candlestick, and RSI evidence. Return a provisional bullish, bearish, or abstain hypothesis, then define the closed-bar conditions that would be needed before considering an entry.'

export function MarketSynthesisPanel({
  eventId,
  selectedAnnotation,
  rsiSettings,
}: MarketSynthesisPanelProps) {
  const [health, setHealth] = useState<MarketSynthesisHealth | null>(null)
  const [draft, setDraft] = useState<MarketSynthesisDraft | null>(null)
  const [question, setQuestion] = useState(DEFAULT_QUESTION)
  const [inputs, setInputs] = useState({ astrology: true, candlesticks: true, rsi: true })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setDraft(null)
    setError('')
  }, [eventId, selectedAnnotation?.annotationId])

  useEffect(() => {
    fetchMarketSynthesisHealth()
      .then(setHealth)
      .catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
  }, [])

  const run = async () => {
    if (!question.trim() || !Object.values(inputs).some(Boolean)) return
    setBusy(true)
    setError('')
    try {
      setDraft(await analyzeWithMarketSynthesis({
        eventId,
        annotationId: selectedAnnotation?.annotationId,
        question: question.trim(),
        period: rsiSettings.period,
        levels: rsiSettings.levels,
        inputs,
      }))
    } catch (reason) {
      setDraft(null)
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="local-jyotish-panel market-synthesis-panel">
      <header className="local-jyotish-header">
        <div><Workflow size={16} /><strong>Market synthesis</strong></div>
        <span>{health?.model ?? 'checking local runtime'}</span>
      </header>
      <div className="local-jyotish-boundary">
        Coordinator draft only. The astrology specialist remains separate; this agent cannot place orders or unlock live execution.
      </div>
      <div className="synthesis-inputs" aria-label="Specialist inputs">
        <label><input type="checkbox" checked={inputs.astrology} onChange={(event) => setInputs({ ...inputs, astrology: event.target.checked })} /> Astrology evidence</label>
        <label><input type="checkbox" checked={inputs.candlesticks} onChange={(event) => setInputs({ ...inputs, candlesticks: event.target.checked })} /> Candle geometry</label>
        <label><input type="checkbox" checked={inputs.rsi} onChange={(event) => setInputs({ ...inputs, rsi: event.target.checked })} /> RSI {rsiSettings.period}</label>
      </div>
      {!health?.runtimeReady && health && (
        <div className="local-jyotish-unavailable"><strong>Local runtime unavailable</strong><span>{health.error || 'Start Ollama to create a synthesis draft.'}</span></div>
      )}
      <div className="local-jyotish-composer">
        <textarea value={question} onChange={(event) => setQuestion(event.target.value)} maxLength={3000} />
        <button onClick={() => void run()} disabled={busy || !health?.runtimeReady || !question.trim() || !Object.values(inputs).some(Boolean)} title="Create market synthesis draft">
          {busy ? <LoaderCircle className="is-spinning" size={15} /> : <Send size={15} />}
        </button>
      </div>
      {error && <div className="local-jyotish-error">{error}</div>}
      {busy && <div className="local-jyotish-thinking"><LoaderCircle className="is-spinning" size={15} /> Comparing isolated deterministic packets...</div>}
      {draft && (
        <div className="local-jyotish-draft">
          <header><strong>{draft.model}</strong><span>{draft.verifier.status.replaceAll('_', ' ')}</span></header>
          <p>{draft.text}</p>
          <div className="synthesis-packet-audit">
            <span>Cutoff {new Date(draft.packet.analysisCutoff).toLocaleString()}</span>
            <span>Outcome excluded</span>
            <span>Hindsight excluded</span>
            <span>Execution locked</span>
          </div>
          {draft.verifier.issues.length > 0 && (
            <div className="local-jyotish-verifier">
              <strong>Verifier review required</strong>
              {draft.verifier.issues.map((issue) => <span key={issue}>{issue}</span>)}
            </div>
          )}
          <small>{draft.disclaimer}</small>
        </div>
      )}
    </section>
  )
}
