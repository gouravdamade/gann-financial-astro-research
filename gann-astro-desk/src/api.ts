import type {
  AnnotationDraft,
  AspectFamily,
  ChartAnnotation,
  ChartPayload,
  EventDetail,
  Mt5Status,
} from './types'

type ApiEnvelope<T> = { ok: boolean; error?: string } & T

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
  })
  const payload = (await response.json()) as ApiEnvelope<T>
  if (!response.ok || !payload.ok) {
    throw new Error(payload.error || `Request failed: ${response.status}`)
  }
  return payload
}

export async function fetchChart(
  start = '2025-05-25T00:00:00+05:30',
  end = '2025-05-31T23:59:59+05:30',
): Promise<ChartPayload> {
  const query = new URLSearchParams({ start, end, symbol: 'USDJPY', timeframe: 'H1' })
  const payload = await request<{ chart: ChartPayload }>(`/api/chart?${query}`)
  return payload.chart
}

export async function fetchMt5Status(): Promise<Mt5Status> {
  const payload = await request<{ mt5: Mt5Status }>('/api/mt5/status')
  return payload.mt5
}

export async function fetchFamily(familyKey: string, eventId?: string): Promise<AspectFamily> {
  const query = eventId ? `?eventId=${encodeURIComponent(eventId)}` : ''
  const payload = await request<{ family: AspectFamily }>(
    `/api/families/${encodeURIComponent(familyKey)}${query}`,
  )
  return payload.family
}

export async function fetchEventDetail(eventId: string): Promise<EventDetail> {
  const payload = await request<{ detail: EventDetail }>(`/api/events/${encodeURIComponent(eventId)}`)
  return payload.detail
}

export async function saveReviewStatus(
  eventId: string,
  status: 'pending' | 'reviewed',
): Promise<EventDetail['event']> {
  const payload = await request<{ event: EventDetail['event'] }>(
    `/api/events/${encodeURIComponent(eventId)}/review`,
    { method: 'POST', body: JSON.stringify({ status }) },
  )
  return payload.event
}

export async function saveAnnotation(draft: AnnotationDraft | ChartAnnotation): Promise<ChartAnnotation> {
  const payload = await request<{ annotation: ChartAnnotation }>('/api/annotations', {
    method: 'POST',
    body: JSON.stringify(draft),
  })
  return payload.annotation
}

export async function deleteAnnotation(annotationId: string): Promise<void> {
  await request<Record<string, never>>(`/api/annotations/${encodeURIComponent(annotationId)}`, {
    method: 'DELETE',
  })
}

export async function saveSnapshot(dataUrl: string): Promise<string> {
  const payload = await request<{ path: string }>('/api/snapshots', {
    method: 'POST',
    body: JSON.stringify({ dataUrl }),
  })
  return payload.path
}

export async function fetchCodexContext(eventId: string, annotationId?: string | null) {
  const query = new URLSearchParams({ eventId })
  if (annotationId) query.set('annotationId', annotationId)
  const payload = await request<{ context: Record<string, unknown> }>(`/api/codex/context?${query}`)
  return payload.context
}

export async function fetchCodexThread(scopeKey: string): Promise<string | null> {
  const query = new URLSearchParams({ scopeKey })
  const payload = await request<{ threadId: string | null }>(`/api/codex/thread?${query}`)
  return payload.threadId
}

export async function saveCodexThread(scopeKey: string, threadId: string): Promise<void> {
  await request<Record<string, never>>('/api/codex/thread', {
    method: 'POST',
    body: JSON.stringify({ scopeKey, threadId }),
  })
}

export async function sendCodexMessage(input: {
  threadId: string | null
  message: string
  context: Record<string, unknown>
  imagePath?: string | null
}): Promise<{ threadId: string; response: string }> {
  const payload = await request<{ threadId: string; response: string }>('/codex-api/chat', {
    method: 'POST',
    body: JSON.stringify(input),
  })
  return payload
}

export async function codexBridgeHealth(): Promise<boolean> {
  try {
    await request<{ bridge: string }>('/codex-api/health')
    return true
  } catch {
    return false
  }
}
