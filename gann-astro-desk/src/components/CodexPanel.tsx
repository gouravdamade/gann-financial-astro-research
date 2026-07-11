import { Bot, Camera, CornerDownLeft, Link2, LoaderCircle, ShieldCheck } from 'lucide-react'
import { useEffect, useRef, useState, type RefObject } from 'react'
import {
  codexBridgeHealth,
  fetchCodexContext,
  fetchCodexThread,
  saveCodexThread,
  saveSnapshot,
  sendCodexMessage,
} from '../api'
import type { MarketChartHandle } from './MarketChart'
import type { ChartAnnotation, CodexMessage } from '../types'

type CodexPanelProps = {
  familyKey: string
  eventId: string
  selectedAnnotation: ChartAnnotation | null
  chartRef: RefObject<MarketChartHandle | null>
}

export function CodexPanel({ familyKey, eventId, selectedAnnotation, chartRef }: CodexPanelProps) {
  const [bridgeReady, setBridgeReady] = useState<boolean | null>(null)
  const [threadId, setThreadId] = useState<string | null>(null)
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [messages, setMessages] = useState<CodexMessage[]>([
    {
      id: 'welcome',
      role: 'system',
      text: 'This is a persistent, read-only Codex family thread. Selected annotations and the visible chart are attached to each question.',
    },
  ])
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    codexBridgeHealth().then(setBridgeReady)
    fetchCodexThread(familyKey).then(setThreadId).catch(() => undefined)
  }, [familyKey])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, sending])

  const submit = async () => {
    const text = message.trim()
    if (!text || sending || !bridgeReady) return
    const userMessage: CodexMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text,
      annotationId: selectedAnnotation?.annotationId,
    }
    setMessages((items) => [...items, userMessage])
    setMessage('')
    setSending(true)
    try {
      const [context, dataUrl] = await Promise.all([
        fetchCodexContext(eventId, selectedAnnotation?.annotationId),
        chartRef.current?.capture(),
      ])
      const imagePath = dataUrl ? await saveSnapshot(dataUrl) : null
      const result = await sendCodexMessage({ threadId, message: text, context, imagePath })
      if (result.threadId && result.threadId !== threadId) {
        setThreadId(result.threadId)
        await saveCodexThread(familyKey, result.threadId)
      }
      setMessages((items) => [
        ...items,
        { id: crypto.randomUUID(), role: 'assistant', text: result.response },
      ])
    } catch (error) {
      setMessages((items) => [
        ...items,
        {
          id: crypto.randomUUID(),
          role: 'system',
          text: `Codex bridge error: ${error instanceof Error ? error.message : String(error)}`,
        },
      ])
    } finally {
      setSending(false)
    }
  }

  return (
    <section className="codex-panel">
      <header className="codex-panel-header">
        <div><Bot size={18} /><strong>Codex</strong></div>
        <span className={bridgeReady ? 'bridge-ready' : 'bridge-offline'}>
          {bridgeReady == null ? 'checking' : bridgeReady ? 'read-only connected' : 'bridge offline'}
        </span>
      </header>
      <div className="codex-guardrail">
        <ShieldCheck size={14} /> Analysis only. No MT5 order capability.
      </div>
      {selectedAnnotation && (
        <div className="context-chip">
          <Link2 size={13} />
          Annotation at {new Date(selectedAnnotation.anchorTimeUtc).toLocaleString()} @ {selectedAnnotation.anchorPrice?.toFixed(3)}
        </div>
      )}
      <div className="codex-messages" ref={scrollRef}>
        {messages.map((item) => (
          <article key={item.id} className={`codex-message ${item.role}`}>
            <span>{item.role === 'assistant' ? 'Codex' : item.role === 'user' ? 'You' : 'System'}</span>
            <p>{item.text}</p>
          </article>
        ))}
        {sending && <div className="codex-thinking"><LoaderCircle className="is-spinning" size={15} /> Reading chart and deterministic evidence...</div>}
      </div>
      <div className="codex-composer">
        <textarea
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              submit()
            }
          }}
          placeholder={selectedAnnotation ? 'Ask about the selected annotation...' : 'Ask about this occurrence...'}
          disabled={!bridgeReady || sending}
        />
        <div className="composer-actions">
          <span><Camera size={13} /> chart attached</span>
          <button onClick={submit} disabled={!message.trim() || !bridgeReady || sending} title="Send to Codex">
            <CornerDownLeft size={16} />
          </button>
        </div>
      </div>
    </section>
  )
}
