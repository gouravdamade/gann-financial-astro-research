import type {
  PlanetaryCollectiveAuditSnapshot,
  PlanetaryCollectiveEvent,
  PlanetaryCollectiveField,
  PlanetaryCollectiveSample,
} from './types'

export const MAX_COLLECTIVE_AUDIT_SNAPSHOTS = 24
export const MAX_COLLECTIVE_AUDIT_STORAGE_BYTES = 224 * 1024

const AUDIT_GUARDRAILS = {
  researchOnly: true,
  immutableEvidenceCopy: true,
  countsAsIndependentVote: false,
  directionalContribution: 0,
  consumedByLiveInference: false,
  consumedByAutoSuggest: false,
  consumedByShadowLedger: false,
  consumedByOfficialMlNotes: false,
  executionAllowed: false,
} as const

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

function validResearchEvent(value: unknown): value is PlanetaryCollectiveEvent {
  if (!value || typeof value !== 'object') return false
  const event = value as PlanetaryCollectiveEvent
  if (!event.timing || !event.guardrails || !event.sourceBracket) return false
  const refinement = event.refinement
  if (
    event.contract !== 'GANN_PLANETARY_COLLECTIVE_EVENT_V1'
    || !Number.isFinite(event.estimatedTimeUnix)
    || !Number.isFinite(event.sourceBracket?.startUnix)
    || !Number.isFinite(event.sourceBracket?.endUnix)
    || event.sourceBracket.startUnix > event.sourceBracket.endUnix
    || event.guardrails?.researchOnly !== true
    || event.guardrails?.visualMarkerOnly !== true
    || event.guardrails?.timestampSafe !== true
    || event.guardrails?.directionalContribution !== 0
    || event.guardrails?.castsSbcVedha !== false
    || event.guardrails?.consumedByLiveInference !== false
    || event.guardrails?.consumedByAutoSuggest !== false
    || event.guardrails?.consumedByShadowLedger !== false
    || event.guardrails?.consumedByOfficialMlNotes !== false
    || event.guardrails?.executionAllowed !== false
  ) return false
  if (!event.timing.exact) {
    return (
      event.refinedTimeUnix == null
      && event.guardrails.exactEventTime === false
      && (
        event.eventType === 'MEAN_RASHI_INGRESS'
          ? (
              refinement?.status === 'SAMPLED_FALLBACK'
              && refinement.refinedTimeUnix == null
            )
          : refinement == null
      )
    )
  }
  return (
    event.eventType === 'MEAN_RASHI_INGRESS'
    && event.guardrails.exactEventTime === true
    && event.timing.method === 'BRACKETED_BISECTION_OF_EPHEMERIS_MEAN'
    && event.refinedTimeUnix != null
    && Number.isFinite(event.refinedTimeUnix)
    && event.refinedTimeUnix >= event.sourceBracket.startUnix
    && event.refinedTimeUnix <= event.sourceBracket.endUnix
    && refinement?.contract === 'GANN_PLANETARY_COLLECTIVE_EVENT_REFINEMENT_V1'
    && refinement?.policyId === 'AVG_ALL_EPHEMERIS_ROOT_REFINEMENT_V1'
    && refinement.status === 'REFINED_BRACKETED_ROOT'
    && refinement.refinedTimeUnix === event.refinedTimeUnix
    && refinement.residualDeg != null
    && Number.isFinite(refinement.residualDeg)
    && Math.abs(refinement.residualDeg) <= refinement.residualToleranceDeg
    && refinement.guardrails?.researchOnly === true
    && refinement.guardrails?.countsAsIndependentVote === false
    && refinement.guardrails?.directionalContribution === 0
    && refinement.guardrails?.consumedByLiveInference === false
    && refinement.guardrails?.consumedByAutoSuggest === false
    && refinement.guardrails?.consumedByShadowLedger === false
    && refinement.guardrails?.consumedByOfficialMlNotes === false
    && refinement.guardrails?.executionAllowed === false
  )
}

function nearestSample(
  samples: PlanetaryCollectiveSample[],
  target: number,
): PlanetaryCollectiveSample {
  return samples.reduce((best, sample) => (
    Math.abs(sample.time - target) < Math.abs(best.time - target)
      ? sample
      : best
  ))
}

export function collectiveEventTime(event: PlanetaryCollectiveEvent): number {
  return event.refinedTimeUnix ?? event.estimatedTimeUnix
}

export function createCollectiveAuditSnapshot(input: {
  field: PlanetaryCollectiveField
  selectedTimeUnix: number
  symbol: string
  timeframe: string
  chartStartUtc: string
  chartEndUtc: string
  snapshotId?: string
  createdAtUtc?: string
}): PlanetaryCollectiveAuditSnapshot {
  if (!input.field.samples.length) {
    throw new Error('Collective audit requires at least one field sample')
  }
  const sample = nearestSample(input.field.samples, input.selectedTimeUnix)
  const nearbyEvents = [...input.field.events]
    .sort((left, right) => (
      Math.abs(collectiveEventTime(left) - sample.time)
      - Math.abs(collectiveEventTime(right) - sample.time)
    ))
    .slice(0, 4)
  return {
    contract: 'GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1',
    schemaVersion: 1,
    snapshotId: input.snapshotId ?? crypto.randomUUID(),
    createdAtUtc: input.createdAtUtc ?? new Date().toISOString(),
    symbol: input.symbol.trim().toUpperCase(),
    timeframe: input.timeframe.trim().toUpperCase(),
    chartRange: {
      startUtc: input.chartStartUtc,
      endUtc: input.chartEndUtc,
    },
    selectedTimeUnix: sample.time,
    fieldCalculationVersion: input.field.calculationVersion,
    profile: clone(input.field.profile),
    sample: clone(sample),
    nearbyEvents: clone(nearbyEvents),
    guardrails: { ...AUDIT_GUARDRAILS },
  }
}

function validSnapshot(
  value: unknown,
): value is PlanetaryCollectiveAuditSnapshot {
  if (!value || typeof value !== 'object') return false
  const snapshot = value as PlanetaryCollectiveAuditSnapshot
  return (
    snapshot.contract === 'GANN_PLANETARY_COLLECTIVE_AUDIT_SNAPSHOT_V1'
    && snapshot.schemaVersion === 1
    && typeof snapshot.snapshotId === 'string'
    && snapshot.snapshotId.length > 0
    && typeof snapshot.createdAtUtc === 'string'
    && Number.isFinite(Date.parse(snapshot.createdAtUtc))
    && typeof snapshot.symbol === 'string'
    && snapshot.symbol.length > 0
    && typeof snapshot.timeframe === 'string'
    && snapshot.timeframe.length > 0
    && typeof snapshot.chartRange?.startUtc === 'string'
    && Number.isFinite(Date.parse(snapshot.chartRange.startUtc))
    && typeof snapshot.chartRange?.endUtc === 'string'
    && Number.isFinite(Date.parse(snapshot.chartRange.endUtc))
    && Number.isFinite(snapshot.selectedTimeUnix)
    && snapshot.sample?.time === snapshot.selectedTimeUnix
    && Array.isArray(snapshot.sample?.memberAudit)
    && Array.isArray(snapshot.profile?.members)
    && Array.isArray(snapshot.profile?.weights)
    && snapshot.profile.members.length > 0
    && snapshot.profile.members.length === snapshot.profile.weights.length
    && new Set(snapshot.profile.members).size === snapshot.profile.members.length
    && snapshot.profile.weights.every((weight) => Number.isFinite(weight))
    && snapshot.sample.memberAudit.length === snapshot.profile.members.length
    && snapshot.sample.memberAudit.every((member) => (
      member != null
      && typeof member === 'object'
      && snapshot.profile.members.includes(member.body)
      && Number.isFinite(member.longitudeDeg)
      && Number.isFinite(member.weight)
    ))
    && typeof snapshot.profile?.memberSetHash === 'string'
    && Array.isArray(snapshot.nearbyEvents)
    && snapshot.nearbyEvents.length <= 4
    && snapshot.nearbyEvents.every(validResearchEvent)
    && snapshot.guardrails?.researchOnly === true
    && snapshot.guardrails?.immutableEvidenceCopy === true
    && snapshot.guardrails?.countsAsIndependentVote === false
    && snapshot.guardrails?.directionalContribution === 0
    && snapshot.guardrails?.consumedByLiveInference === false
    && snapshot.guardrails?.consumedByAutoSuggest === false
    && snapshot.guardrails?.consumedByShadowLedger === false
    && snapshot.guardrails?.consumedByOfficialMlNotes === false
    && snapshot.guardrails?.executionAllowed === false
  )
}

export function normalizeCollectiveAuditSnapshots(
  value: unknown,
): PlanetaryCollectiveAuditSnapshot[] {
  if (!Array.isArray(value)) return []
  const unique = new Map<string, {
    snapshot: PlanetaryCollectiveAuditSnapshot
    storageBytes: number
  }>()
  for (const candidate of value) {
    if (!validSnapshot(candidate)) continue
    const serialized = JSON.stringify(candidate)
    unique.set(candidate.snapshotId, {
      snapshot: JSON.parse(serialized) as PlanetaryCollectiveAuditSnapshot,
      storageBytes: new TextEncoder().encode(serialized).byteLength,
    })
  }
  const ordered = [...unique.values()]
    .sort((left, right) => (
      Date.parse(right.snapshot.createdAtUtc)
      - Date.parse(left.snapshot.createdAtUtc)
    ))
  const output: PlanetaryCollectiveAuditSnapshot[] = []
  let storageBytes = 0
  for (const item of ordered) {
    if (output.length >= MAX_COLLECTIVE_AUDIT_SNAPSHOTS) break
    if (
      storageBytes + item.storageBytes
      > MAX_COLLECTIVE_AUDIT_STORAGE_BYTES
    ) continue
    output.push(item.snapshot)
    storageBytes += item.storageBytes
  }
  return output
}

export function upsertCollectiveAuditSnapshot(
  current: PlanetaryCollectiveAuditSnapshot[],
  snapshot: PlanetaryCollectiveAuditSnapshot,
): PlanetaryCollectiveAuditSnapshot[] {
  const sameAudit = (item: PlanetaryCollectiveAuditSnapshot) => (
    item.symbol === snapshot.symbol
    && item.timeframe === snapshot.timeframe
    && item.selectedTimeUnix === snapshot.selectedTimeUnix
    && item.profile.memberSetHash === snapshot.profile.memberSetHash
  )
  return normalizeCollectiveAuditSnapshots([
    snapshot,
    ...current.filter((item) => !sameAudit(item)),
  ])
}

export function collectiveAuditFileName(
  snapshot: PlanetaryCollectiveAuditSnapshot,
): string {
  const timestamp = new Date(snapshot.selectedTimeUnix * 1000)
    .toISOString()
    .replaceAll(':', '')
    .replace('.000Z', 'Z')
  return [
    snapshot.symbol,
    snapshot.timeframe,
    'avg_all_audit',
    timestamp,
  ].join('_') + '.json'
}

export function downloadCollectiveAuditSnapshot(
  snapshot: PlanetaryCollectiveAuditSnapshot,
): void {
  const blob = new Blob(
    [JSON.stringify(snapshot, null, 2)],
    { type: 'application/json' },
  )
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = collectiveAuditFileName(snapshot)
  link.click()
  URL.revokeObjectURL(url)
}
