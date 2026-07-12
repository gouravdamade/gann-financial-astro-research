import { BookOpen, BrainCircuit, CornerDownLeft, LoaderCircle, ShieldAlert } from 'lucide-react'
import { useEffect, useState } from 'react'
import { analyzeWithLocalJyotish, fetchLocalJyotishHealth } from '../api'
import type { ChartAnnotation, LocalJyotishDraft, LocalJyotishHealth } from '../types'

type LocalJyotishPanelProps = {
  eventId: string
  selectedAnnotation: ChartAnnotation | null
}

const DEFAULT_QUESTION = 'Explain the observed behavior using deterministic evidence and relevant classical Jyotish sources. List testable ML features and uncertainty.'

export function LocalJyotishPanel({ eventId, selectedAnnotation }: LocalJyotishPanelProps) {
  const [health, setHealth] = useState<LocalJyotishHealth | null>(null)
  const [question, setQuestion] = useState(DEFAULT_QUESTION)
  const [draft, setDraft] = useState<LocalJyotishDraft | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setDraft(null)
    setError('')
    fetchLocalJyotishHealth()
      .then(setHealth)
      .catch((reason) => setError(reason instanceof Error ? reason.message : String(reason)))
  }, [eventId])

  const submit = async () => {
    if (!question.trim() || busy || !health?.ready) return
    setBusy(true)
    setError('')
    try {
      setDraft(await analyzeWithLocalJyotish({
        eventId,
        annotationId: selectedAnnotation?.annotationId,
        question: question.trim(),
      }))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="local-jyotish-panel">
      <header className="local-jyotish-header">
        <div><BrainCircuit size={17} /><strong>Local Jyotish</strong></div>
        <span className={health?.ready ? 'bridge-ready' : 'bridge-offline'}>
          {health == null ? 'checking' : health.ready ? `${health.model} | ${health.corpusChunks.toLocaleString()} sources` : 'offline'}
        </span>
      </header>
      <div className="local-jyotish-boundary">
        <ShieldAlert size={14} /> Untrusted RAG draft. Deterministic evidence and reviewed notes remain authoritative.
      </div>
      {!health?.ready && health && (
        <div className="local-jyotish-unavailable">
          <strong>{health.runtimeReady ? 'Classical corpus unavailable' : 'Local Ollama runtime unavailable'}</strong>
          <span>{health.error || `Expected model ${health.model}`}</span>
        </div>
      )}
      <div className="local-jyotish-composer">
        <textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={busy}
          aria-label="Local Jyotish question"
        />
        <button type="button" onClick={submit} disabled={!health?.ready || !question.trim() || busy} title="Draft with local Jyotish model">
          {busy ? <LoaderCircle className="is-spinning" size={16} /> : <CornerDownLeft size={16} />}
        </button>
      </div>
      {error && <div className="local-jyotish-error">{error}</div>}
      {busy && <div className="local-jyotish-thinking"><LoaderCircle className="is-spinning" size={15} /> Retrieving doctrine and checking deterministic evidence...</div>}
      {draft && (
        <div className="local-jyotish-draft">
          <header>
            <strong>Draft analysis</strong>
            <span className={draft.verifier.status === 'pass' ? 'positive' : 'negative'}>
              {draft.verifier.status.replaceAll('_', ' ')} | {draft.model}
            </span>
          </header>
          {draft.verifier.issues.length > 0 && (
            <div className="local-jyotish-verifier">
              {draft.verifier.issues.map((issue) => <span key={issue}>{issue}</span>)}
            </div>
          )}
          <p>{draft.text}</p>
          <div className="local-jyotish-citations">
            <strong><BookOpen size={13} /> Retrieved citations</strong>
            {draft.citations.map((citation) => (
              <span key={citation.chunkId} title={`retrieval score ${citation.score}`}>
                [{citation.chunkId}] {citation.title} | {citation.layer.replace('_', ' ')}
              </span>
            ))}
            {!draft.citations.length && <span>No matching classical passage was found.</span>}
          </div>
          <small>{draft.disclaimer}</small>
        </div>
      )}
    </section>
  )
}
