import { normalizeCollectiveAuditSnapshots } from './collectiveAudit'
import type {
  ChakraLabRequest,
  ChakraLabSnapshot,
  ChartDrawing,
  PlanetaryCollectiveAuditSnapshot,
  PlanetaryCollectiveVisualStudyDossier,
} from './types'

const STUDY_GUARDRAILS = {
  researchOnly: true,
  countsAsIndependentVote: false,
  directionalContribution: 0,
  consumedByLiveInference: false,
  consumedByAutoSuggest: false,
  consumedByShadowLedger: false,
  consumedByOfficialMlNotes: false,
  executionAllowed: false,
} as const

const SBC_BODIES = [
  'SUN',
  'MOON',
  'MARS',
  'MERCURY',
  'JUPITER',
  'VENUS',
  'SATURN',
  'RAHU',
  'KETU',
] as const

const FIXED_BODY_ACTORS = ['SUN', 'MOON', 'RAHU', 'KETU'] as const
const MAX_GANN_FANS_PER_DOSSIER = 32

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T
}

function canonicalize(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(canonicalize)
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value)
        .filter(([, item]) => item !== undefined)
        .sort(([left], [right]) => left.localeCompare(right))
        .map(([key, item]) => [key, canonicalize(item)]),
    )
  }
  return value
}

async function sha256Hex(value: unknown): Promise<string> {
  const bytes = new TextEncoder().encode(JSON.stringify(canonicalize(value)))
  const digest = await crypto.subtle.digest('SHA-256', bytes)
  return [...new Uint8Array(digest)]
    .map((item) => item.toString(16).padStart(2, '0'))
    .join('')
    .toUpperCase()
}

function istTimestamp(unixSeconds: number): string {
  const istOffsetSeconds = 5.5 * 60 * 60
  return `${new Date((unixSeconds + istOffsetSeconds) * 1000)
    .toISOString()
    .slice(0, 19)}+05:30`
}

export function createCollectiveStudySbcRequest(input: {
  selectedTimeUnix: number
  latitude: number
  longitude: number
  altitudeM?: number
}): ChakraLabRequest {
  if (
    !Number.isFinite(input.selectedTimeUnix)
    || !Number.isFinite(input.latitude)
    || !Number.isFinite(input.longitude)
    || Math.abs(input.latitude) > 90
    || Math.abs(input.longitude) > 180
  ) {
    throw new Error('M7 SBC study requires a valid timestamp and location')
  }
  return {
    at: istTimestamp(input.selectedTimeUnix),
    timezone: 'Asia/Kolkata',
    latitude: input.latitude,
    longitude: input.longitude,
    altitudeM: input.altitudeM ?? 0,
    bodies: [...SBC_BODIES],
    actors: FIXED_BODY_ACTORS.map((body) => ({ body })),
    foundationProfileId: 'sbc_raman_foundation_v1',
    gridProfileId: 'sbc_81_rotation_normalized_partial_v1',
    vedhaProfileId: 'phaladeepika_editor_vedha_guidance_v1',
    vowels: [],
    nameInitials: [],
  }
}

function assertTimestampSafeSbc(
  snapshot: ChakraLabSnapshot,
  selectedTimeUnix: number,
): void {
  const asOfUnix = Date.parse(snapshot.as_of_utc) / 1000
  const cutoffUnix = Date.parse(snapshot.evidence_cutoff_utc) / 1000
  if (
    snapshot.contract !== 'SBC_CHAKRA_LAB_SNAPSHOT_V1'
    || snapshot.schema_version !== 1
    || snapshot.guardrails?.read_only !== true
    || snapshot.guardrails?.timestamp_safe !== true
    || snapshot.guardrails?.no_lookahead !== true
    || snapshot.guardrails?.execution_allowed !== false
    || snapshot.guardrails?.market_data_included !== false
    || snapshot.guardrails?.financially_validated !== false
    || snapshot.guardrails?.guidance_only !== true
    || snapshot.grid?.rows !== 9
    || snapshot.grid?.columns !== 9
    || !Number.isFinite(asOfUnix)
    || !Number.isFinite(cutoffUnix)
    || Math.abs(asOfUnix - selectedTimeUnix) > 1
    || cutoffUnix > selectedTimeUnix + 1
    || (
      snapshot.guidance != null
      && (
        snapshot.guidance.guidance_only !== true
        || snapshot.guidance.financial_validation_status !== 'NOT_VALIDATED'
      )
    )
  ) {
    throw new Error('M7 SBC study response violated timestamp or research guardrails')
  }
}

function visibleGannFans(drawings: ChartDrawing[]) {
  const candidates = drawings.filter((drawing) => (
    drawing.type === 'gann_fan' && drawing.visible
  ))
  if (candidates.length > MAX_GANN_FANS_PER_DOSSIER) {
    throw new Error(`M7 visual study supports at most ${MAX_GANN_FANS_PER_DOSSIER} visible Gann fans`)
  }
  return candidates.map((drawing) => {
    const ratios = Array.isArray(drawing.settings.ratios)
      ? drawing.settings.ratios.filter((ratio): ratio is number => (
          typeof ratio === 'number' && Number.isFinite(ratio) && ratio > 0
        ))
      : []
    if (
      drawing.contract !== 'GANN_RESEARCH_CHART_DRAWING_V1'
      || drawing.schemaVersion !== 1
      || drawing.anchors.length < 1
      || drawing.anchors.some((anchor) => (
        !Number.isFinite(Date.parse(anchor.timeUtc))
        || !Number.isFinite(anchor.price)
      ))
      || ratios.length === 0
      || drawing.guardrails?.researchOnly !== true
      || drawing.guardrails?.consumedByLiveInference !== false
      || drawing.guardrails?.consumedByShadowLedger !== false
      || drawing.guardrails?.executionAllowed !== false
    ) {
      throw new Error('M7 visual study rejected an unsafe Gann drawing')
    }
    return {
      drawingId: drawing.drawingId,
      name: drawing.name,
      anchors: clone(drawing.anchors),
      style: clone(drawing.style),
      ratios: [...ratios],
    }
  })
}

export async function createCollectiveVisualStudyDossier(input: {
  audit: PlanetaryCollectiveAuditSnapshot
  drawings: ChartDrawing[]
  sbcSnapshot: ChakraLabSnapshot
  createdAtUtc?: string
}): Promise<PlanetaryCollectiveVisualStudyDossier> {
  const audit = normalizeCollectiveAuditSnapshots([input.audit])[0]
  if (!audit) throw new Error('M7 visual study requires a valid immutable AVG audit')
  assertTimestampSafeSbc(input.sbcSnapshot, audit.selectedTimeUnix)
  const createdAtUtc = input.createdAtUtc ?? new Date().toISOString()
  if (!Number.isFinite(Date.parse(createdAtUtc))) {
    throw new Error('M7 visual study creation time is invalid')
  }
  const gannStudy: PlanetaryCollectiveVisualStudyDossier['gannStudy'] = {
    contract: 'GANN_AVG_ALL_GANN_VISUAL_STUDY_V1',
    mode: 'VISIBLE_USER_AUTHORED_FANS',
    fanCount: 0,
    fans: visibleGannFans(input.drawings),
    guardrails: {
      geometryOnly: true,
      directionalInterpretation: false,
      outcomeLabelsIncluded: false,
    },
  }
  gannStudy.fanCount = gannStudy.fans.length
  const sbcStudy: PlanetaryCollectiveVisualStudyDossier['sbcStudy'] = {
    contract: 'GANN_AVG_ALL_SBC_VISUAL_STUDY_V1',
    mode: 'TIMESTAMP_MATCHED_FIXED_BODY_CONTEXT',
    actorScope: 'SUN_MOON_RAHU_KETU_ONLY',
    snapshot: clone(input.sbcSnapshot),
    guardrails: {
      avgAllCastsVedha: false,
      guidanceOnly: true,
      financiallyValidated: false,
      outcomeLabelsIncluded: false,
    },
  }
  const prospectiveFreeze: PlanetaryCollectiveVisualStudyDossier['prospectiveFreeze'] = {
    contract: 'GANN_AVG_ALL_PROSPECTIVE_FREEZE_CANDIDATE_V1',
    policyVersion: 'avg_all_visual_observer_v1',
    status: 'EXPORT_ONLY_NOT_REGISTERED',
    packetFrozen: true,
    trialRegistered: false,
    evidenceCutoffUtc: input.sbcSnapshot.evidence_cutoff_utc,
    outcomeLabelsIncluded: false,
    existingShadowTrialModified: false,
    requirementsBeforeRegistration: [
      'predeclare outcomes, horizons, exclusions, and pass/fail thresholds',
      'register a separate immutable manifest and untouched future start time',
      'keep this observer separate from the existing frozen shadow cohort',
      'collect enough future cases before examining outcome labels',
    ],
  }
  const fingerprintInput = {
    contract: 'GANN_AVG_ALL_VISUAL_STUDY_DOSSIER_V1',
    schemaVersion: 1,
    createdAtUtc,
    audit,
    gannStudy,
    sbcStudy,
    prospectiveFreeze,
    guardrails: STUDY_GUARDRAILS,
  }
  const studyFingerprintSha256 = await sha256Hex(fingerprintInput)
  return {
    ...fingerprintInput,
    contract: 'GANN_AVG_ALL_VISUAL_STUDY_DOSSIER_V1',
    schemaVersion: 1,
    dossierId: `avg-all-study-${studyFingerprintSha256.slice(0, 24).toLowerCase()}`,
    studyFingerprintSha256,
  }
}

export function collectiveVisualStudyFileName(
  dossier: PlanetaryCollectiveVisualStudyDossier,
): string {
  const timestamp = new Date(dossier.audit.selectedTimeUnix * 1000)
    .toISOString()
    .replaceAll(':', '')
    .replace('.000Z', 'Z')
  return [
    dossier.audit.symbol,
    dossier.audit.timeframe,
    'avg_all_m7_visual_study',
    timestamp,
  ].join('_') + '.json'
}

export function downloadCollectiveVisualStudyDossier(
  dossier: PlanetaryCollectiveVisualStudyDossier,
): void {
  const blob = new Blob(
    [JSON.stringify(dossier, null, 2)],
    { type: 'application/json' },
  )
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = collectiveVisualStudyFileName(dossier)
  link.click()
  URL.revokeObjectURL(url)
}
