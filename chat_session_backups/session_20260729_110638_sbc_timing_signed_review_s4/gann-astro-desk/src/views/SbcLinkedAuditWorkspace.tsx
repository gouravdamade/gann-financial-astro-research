import {
  Archive,
  BadgeCheck,
  BookmarkPlus,
  Clock3,
  Columns3,
  Download,
  FileCheck2,
  FileSearch,
  FileSignature,
  GitBranch,
  ListChecks,
  Orbit,
  PackageCheck,
  Plus,
  Radar,
  RefreshCw,
  ShieldAlert,
  Table2,
  Trash2,
  Upload,
} from 'lucide-react'
import { useMemo, useRef, useState } from 'react'
import {
  buildChakraLabAuditCatalog,
  buildChakraLabAuditPackage,
  fetchChakraLabAudit,
  fetchChakraLabFixedPhasor,
  fetchChakraTimingProfileAdmission,
  fetchChakraTimingExternalReview,
  fetchChakraTimingSignedReview,
  fetchChakraTimingSourcePacketReadiness,
  fetchChakraTimingSourceVerification,
  verifyChakraLabAuditCatalog,
  verifyChakraLabAuditPackage,
} from '../api'
import type {
  ChakraAuditCatalogBuild,
  ChakraAuditCatalogVerification,
  ChakraAuditBookmarkInput,
  ChakraAuditBookmarkTarget,
  ChakraAuditInterval,
  ChakraAuditLedgerCell,
  ChakraAuditPackageBuild,
  ChakraAuditPackageVerification,
  ChakraAuditRay,
  ChakraFixedPhasorSeries,
  ChakraLabAuditBoundaryInput,
  ChakraLabAuditRequest,
  ChakraLabRequest,
  ChakraLinkedAuditView,
  ChakraReproducibleAuditPackage,
  ChakraSignedAuditCatalogBundle,
  ChakraTimingProfileAdmissionReport,
  ChakraTimingProfileExternalReviewReport,
  ChakraTimingProfileSignedReviewReport,
  ChakraTimingProfileSourceReadinessReport,
  ChakraTimingProfileSourceVerificationReport,
} from '../types'


type AuditTab =
  | 'TIMELINE'
  | 'LEDGER'
  | 'RAY_AUDIT'
  | 'SOURCE_LINEAGE'
  | 'RECONCILIATION'
  | 'VALIDATION'
  | 'PHASOR'
  | 'TIMING_PROFILE'
  | 'SOURCE_PACKET'
  | 'SOURCE_VERIFY'
  | 'REVIEW_ATTESTATION'
  | 'SIGNED_REVIEW'
  | 'COMPARE'
  | 'PACKAGE'
  | 'CATALOG'

const TAB_ICONS = {
  TIMELINE: Clock3,
  LEDGER: Table2,
  RAY_AUDIT: Radar,
  SOURCE_LINEAGE: GitBranch,
  RECONCILIATION: ListChecks,
  VALIDATION: ShieldAlert,
  PHASOR: Orbit,
  TIMING_PROFILE: FileCheck2,
  SOURCE_PACKET: FileCheck2,
  SOURCE_VERIFY: FileSearch,
  REVIEW_ATTESTATION: FileSignature,
  SIGNED_REVIEW: BadgeCheck,
  COMPARE: Columns3,
  PACKAGE: PackageCheck,
  CATALOG: Archive,
} as const

function offsetIst(value: string): string {
  return `${value}${value.length === 16 ? ':00' : ''}+05:30`
}

function istInput(value: string): string {
  const date = new Date(value)
  return new Date(date.getTime() + 330 * 60 * 1000).toISOString().slice(0, 16)
}

function plusHour(value: string): string {
  const date = new Date(value)
  return istInput(new Date(date.getTime() + 60 * 60 * 1000).toISOString())
}

function shortId(value: string | null | undefined): string {
  return value ? value.slice(0, 10) : '-'
}

function displayToken(value: string | null | undefined): string {
  if (!value) return 'Unavailable'
  return value
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replaceAll('_', ' ')
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function formatMoment(value: string): string {
  return new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Kolkata',
  }).format(new Date(value))
}

function formatDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return hours ? `${hours}h ${minutes}m` : `${minutes}m`
}

function units(value: number): string {
  return value.toFixed(2)
}

function signedUnits(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}`
}

function downloadText(content: string, type: string, filename: string) {
  const url = URL.createObjectURL(new Blob([content], { type }))
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

type TimingSourceArtifactDeclaration = {
  sourceId: string
  title: string
  sourceRole: string
  lineageId: string
  sha256: string
}

type TimingSourceClaimDeclaration = {
  claimId: string
  profilePath: string
  sourceId: string
  pageStart: number
  pageEnd: number
  excerptSha256: string
}

function timingSourceArtifacts(packet: unknown): TimingSourceArtifactDeclaration[] {
  if (!packet || typeof packet !== 'object') return []
  const raw = (packet as { sourceArtifacts?: unknown }).sourceArtifacts
  if (!Array.isArray(raw)) return []
  return raw.flatMap((item) => {
    if (!item || typeof item !== 'object') return []
    const value = item as Record<string, unknown>
    if (typeof value.sourceId !== 'string') return []
    return [{
      sourceId: value.sourceId,
      title: typeof value.title === 'string' ? value.title : value.sourceId,
      sourceRole: typeof value.sourceRole === 'string' ? value.sourceRole : 'UNKNOWN',
      lineageId: typeof value.lineageId === 'string' ? value.lineageId : 'UNKNOWN',
      sha256: typeof value.sha256 === 'string' ? value.sha256 : '',
    }]
  })
}

function timingSourceClaims(packet: unknown): TimingSourceClaimDeclaration[] {
  if (!packet || typeof packet !== 'object') return []
  const raw = (packet as { claims?: unknown }).claims
  if (!Array.isArray(raw)) return []
  return raw.flatMap((item) => {
    if (!item || typeof item !== 'object') return []
    const value = item as Record<string, unknown>
    if (typeof value.claimId !== 'string') return []
    return [{
      claimId: value.claimId,
      profilePath: typeof value.profilePath === 'string' ? value.profilePath : '',
      sourceId: typeof value.sourceId === 'string' ? value.sourceId : '',
      pageStart: typeof value.pageStart === 'number' ? value.pageStart : 0,
      pageEnd: typeof value.pageEnd === 'number' ? value.pageEnd : 0,
      excerptSha256: typeof value.excerptSha256 === 'string'
        ? value.excerptSha256
        : '',
    }]
  })
}

function fileBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(reader.error ?? new Error('File read failed'))
    reader.onload = () => {
      const result = String(reader.result ?? '')
      const delimiter = result.indexOf(',')
      if (delimiter < 0) {
        reject(new Error('File could not be encoded as base64'))
        return
      }
      resolve(result.slice(delimiter + 1))
    }
    reader.readAsDataURL(file)
  })
}

type Props = {
  currentRequest: ChakraLabRequest
}

export function SbcLinkedAuditWorkspace({ currentRequest }: Props) {
  const [instrumentIdentity, setInstrumentIdentity] = useState('FX:USDJPY')
  const [boundaryLocal, setBoundaryLocal] = useState(() => istInput(currentRequest.at))
  const [boundaryReason, setBoundaryReason] = useState('manual review boundary')
  const [terminalLocal, setTerminalLocal] = useState(() => plusHour(currentRequest.at))
  const [boundaries, setBoundaries] = useState<ChakraLabAuditBoundaryInput[]>([])
  const [audit, setAudit] = useState<ChakraLinkedAuditView | null>(null)
  const [phasor, setPhasor] = useState<ChakraFixedPhasorSeries | null>(null)
  const [timingAdmission, setTimingAdmission] =
    useState<ChakraTimingProfileAdmissionReport | null>(null)
  const [timingCandidate, setTimingCandidate] = useState<unknown | null>(null)
  const [timingCandidateLabel, setTimingCandidateLabel] = useState('')
  const [sourceReadiness, setSourceReadiness] =
    useState<ChakraTimingProfileSourceReadinessReport | null>(null)
  const [sourcePacket, setSourcePacket] = useState<unknown | null>(null)
  const [sourcePacketLabel, setSourcePacketLabel] = useState('')
  const [sourceVerification, setSourceVerification] =
    useState<ChakraTimingProfileSourceVerificationReport | null>(null)
  const [reviewBundle, setReviewBundle] = useState<unknown | null>(null)
  const [reviewBundleLabel, setReviewBundleLabel] = useState('')
  const [reviewAttestation, setReviewAttestation] = useState<unknown | null>(null)
  const [reviewAttestationLabel, setReviewAttestationLabel] = useState('')
  const [externalReview, setExternalReview] =
    useState<ChakraTimingProfileExternalReviewReport | null>(null)
  const [signedReviewEnvelope, setSignedReviewEnvelope] =
    useState<unknown | null>(null)
  const [signedReviewLabel, setSignedReviewLabel] = useState('')
  const [signedReview, setSignedReview] =
    useState<ChakraTimingProfileSignedReviewReport | null>(null)
  const [sourcePayloads, setSourcePayloads] =
    useState<Record<string, string>>({})
  const [sourcePayloadLabels, setSourcePayloadLabels] =
    useState<Record<string, string>>({})
  const [excerptPayloads, setExcerptPayloads] =
    useState<Record<string, string>>({})
  const [excerptPayloadLabel, setExcerptPayloadLabel] = useState('')
  const [activeTab, setActiveTab] = useState<AuditTab>('TIMELINE')
  const [selectedIntervalId, setSelectedIntervalId] = useState('')
  const [selectedClusterId, setSelectedClusterId] = useState('')
  const [selectedCellId, setSelectedCellId] = useState('')
  const [baselineIntervalId, setBaselineIntervalId] = useState('')
  const [comparisonIntervalIds, setComparisonIntervalIds] = useState<string[]>([])
  const [bookmarks, setBookmarks] = useState<ChakraAuditBookmarkInput[]>([])
  const [bookmarkTargetType, setBookmarkTargetType] = useState<ChakraAuditBookmarkTarget>('INTERVAL')
  const [bookmarkLabel, setBookmarkLabel] = useState('')
  const [bookmarkNote, setBookmarkNote] = useState('')
  const [packageBuild, setPackageBuild] = useState<ChakraAuditPackageBuild | null>(null)
  const [verification, setVerification] = useState<ChakraAuditPackageVerification | null>(null)
  const [catalogPackages, setCatalogPackages] = useState<ChakraReproducibleAuditPackage[]>([])
  const [catalogBuild, setCatalogBuild] = useState<ChakraAuditCatalogBuild | null>(null)
  const [catalogVerification, setCatalogVerification] = useState<ChakraAuditCatalogVerification | null>(null)
  const [busy, setBusy] = useState(false)
  const [packageBusy, setPackageBusy] = useState(false)
  const [catalogBusy, setCatalogBusy] = useState(false)
  const [timingBusy, setTimingBusy] = useState(false)
  const [sourcePacketBusy, setSourcePacketBusy] = useState(false)
  const [sourceVerificationBusy, setSourceVerificationBusy] = useState(false)
  const [externalReviewBusy, setExternalReviewBusy] = useState(false)
  const [signedReviewBusy, setSignedReviewBusy] = useState(false)
  const [error, setError] = useState('')
  const importInputRef = useRef<HTMLInputElement>(null)
  const catalogImportInputRef = useRef<HTMLInputElement>(null)
  const timingImportInputRef = useRef<HTMLInputElement>(null)
  const sourcePacketImportInputRef = useRef<HTMLInputElement>(null)
  const excerptPayloadImportInputRef = useRef<HTMLInputElement>(null)
  const reviewBundleImportInputRef = useRef<HTMLInputElement>(null)
  const reviewAttestationImportInputRef = useRef<HTMLInputElement>(null)
  const signedReviewImportInputRef = useRef<HTMLInputElement>(null)

  const selectedInterval = audit?.intervals.find(
    (item) => item.interval_id === selectedIntervalId,
  ) ?? audit?.intervals[0] ?? null
  const intervalId = selectedInterval?.interval_id ?? ''
  const ledgerRows = audit?.ledger_cells.filter(
    (item) => item.interval_id === intervalId,
  ) ?? []
  const rayRows = audit?.ray_rows.filter(
    (item) => item.interval_id === intervalId,
  ) ?? []
  const lineageRows = audit?.lineage_rows.filter(
    (item) => item.interval_id === intervalId,
  ) ?? []
  const reconciliationRows = audit?.reconciliations.filter(
    (item) => item.interval_id === intervalId,
  ) ?? []
  const phasorInterval = phasor?.intervals.find(
    (item) => item.interval_id === intervalId,
  ) ?? phasor?.intervals[0] ?? null
  const plottedPhasors = phasorInterval?.vectors.filter(
    (item) => item.projection_status === 'PLOTTED',
  ) ?? []
  const unknownPhasors = phasorInterval?.vectors.filter(
    (item) => item.projection_status === 'UNKNOWN_NOT_PLOTTED',
  ) ?? []
  const maxPhasorMagnitude = Math.max(
    1,
    ...plottedPhasors.map((item) => item.magnitude_units ?? 0),
  )
  const selectedCluster = audit?.ray_rows.find(
    (item) => item.cluster_id === selectedClusterId,
  ) ?? null
  const selectedLineage = audit?.lineage_rows.find(
    (item) => item.cluster_id === selectedClusterId,
  ) ?? null
  const selectedCell = audit?.ledger_cells.find(
    (item) => item.cell_id === selectedCellId,
  ) ?? null
  const bookmarkTargetId = bookmarkTargetType === 'AUDIT'
    ? audit?.audit_view_id ?? ''
    : bookmarkTargetType === 'INTERVAL'
      ? selectedInterval?.interval_id ?? ''
      : bookmarkTargetType === 'CELL'
        ? selectedCell?.cell_id ?? ''
        : selectedCluster?.cluster_id ?? ''
  const packageComparisons = packageBuild?.package.comparisons ?? []
  const sourceArtifactDeclarations = useMemo(
    () => timingSourceArtifacts(sourcePacket),
    [sourcePacket],
  )
  const sourceClaimDeclarations = useMemo(
    () => timingSourceClaims(sourcePacket),
    [sourcePacket],
  )
  const reviewAttestationTemplate = useMemo(() => {
    if (!reviewBundle || typeof reviewBundle !== 'object') return null
    const template = (reviewBundle as { attestationTemplate?: unknown })
      .attestationTemplate
    return template && typeof template === 'object' && !Array.isArray(template)
      ? template
      : null
  }, [reviewBundle])

  const sortedBoundaries = useMemo(
    () => [...boundaries].sort(
      (left, right) => left.request.at.localeCompare(right.request.at),
    ),
    [boundaries],
  )

  const auditRequest = (): ChakraLabAuditRequest => ({
    instrumentIdentity: instrumentIdentity.trim(),
    terminalEnd: offsetIst(terminalLocal),
    boundaries: sortedBoundaries,
  })

  const resetPackage = () => {
    setPackageBuild(null)
    setVerification(null)
  }

  const resetSourceVerification = () => {
    setSourceVerification(null)
    setSourcePayloads({})
    setSourcePayloadLabels({})
    setExcerptPayloads({})
    setExcerptPayloadLabel('')
  }

  const captureBoundary = () => {
    const capturedAt = offsetIst(boundaryLocal)
    if (boundaries.some((item) => item.request.at === capturedAt)) {
      setError('That boundary moment is already captured.')
      return
    }
    const captured: ChakraLabAuditBoundaryInput = {
      reason: boundaryReason.trim() || 'manual review boundary',
      request: {
        ...structuredClone(currentRequest),
        at: capturedAt,
      },
    }
    setBoundaries((current) => {
      const next = [...current, captured]
      return next.sort((left, right) => left.request.at.localeCompare(right.request.at))
    })
    const candidate = plusHour(capturedAt)
    setBoundaryLocal(candidate)
    if (new Date(offsetIst(terminalLocal)) <= new Date(capturedAt)) {
      setTerminalLocal(candidate)
    }
    setAudit(null)
    setPhasor(null)
    setBookmarks([])
    resetPackage()
    setError('')
  }

  const removeBoundary = (index: number) => {
    setBoundaries((current) => current.filter((_, itemIndex) => itemIndex !== index))
    setAudit(null)
    setPhasor(null)
    setBookmarks([])
    resetPackage()
  }

  const buildAudit = async () => {
    setBusy(true)
    setError('')
    setAudit(null)
    setPhasor(null)
    try {
      const request = auditRequest()
      const [result, fixedPhasor] = await Promise.all([
        fetchChakraLabAudit(request),
        fetchChakraLabFixedPhasor(request),
      ])
      if (fixedPhasor.source_ledger_id !== result.source_ledger_id) {
        throw new Error('Fixed phasor source does not match the linked P2 ledger')
      }
      setAudit(result)
      setPhasor(fixedPhasor)
      const firstInterval = result.intervals[0]
      setSelectedIntervalId(firstInterval?.interval_id ?? '')
      const firstRay = result.ray_rows.find(
        (item) => item.interval_id === firstInterval?.interval_id,
      )
      setSelectedClusterId(firstRay?.cluster_id ?? '')
      const firstCell = result.ledger_cells.find(
        (item) => item.interval_id === firstInterval?.interval_id,
      )
      setSelectedCellId(firstCell?.cell_id ?? '')
      setBaselineIntervalId(firstInterval?.interval_id ?? '')
      setComparisonIntervalIds(
        result.intervals.slice(1).map((item) => item.interval_id),
      )
      setBookmarks([])
      resetPackage()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }

  const evaluateTimingProfile = async (
    profile: unknown | null,
    label = '',
  ) => {
    setTimingBusy(true)
    setError('')
    setTimingCandidate(profile)
    setSourceReadiness(null)
    setSourcePacket(null)
    setSourcePacketLabel('')
    resetSourceVerification()
    try {
      const result = await fetchChakraTimingProfileAdmission(profile)
      setTimingAdmission(result)
      setTimingCandidateLabel(label)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setTimingBusy(false)
    }
  }

  const importTimingProfile = async (file: File | undefined) => {
    if (!file) return
    try {
      const profile = JSON.parse(await file.text()) as unknown
      await evaluateTimingProfile(profile, file.name)
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `Timing profile import failed: ${caught.message}`
          : String(caught),
      )
    } finally {
      if (timingImportInputRef.current) {
        timingImportInputRef.current.value = ''
      }
    }
  }

  const evaluateTimingSourcePacket = async (
    packet: unknown | null,
    label = '',
  ) => {
    setSourcePacketBusy(true)
    setError('')
    try {
      const result = await fetchChakraTimingSourcePacketReadiness(
        timingCandidate,
        packet,
      )
      setSourceReadiness(result)
      setSourcePacket(packet)
      setSourcePacketLabel(label)
      resetSourceVerification()
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setSourcePacketBusy(false)
    }
  }

  const importTimingSourcePacket = async (file: File | undefined) => {
    if (!file) return
    try {
      const packet = JSON.parse(await file.text()) as unknown
      await evaluateTimingSourcePacket(packet, file.name)
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `Source packet import failed: ${caught.message}`
          : String(caught),
      )
    } finally {
      if (sourcePacketImportInputRef.current) {
        sourcePacketImportInputRef.current.value = ''
      }
    }
  }

  const loadTimingSourceArtifact = async (
    sourceId: string,
    file: File | undefined,
  ) => {
    if (!file) return
    if (file.size > 64 * 1024 * 1024) {
      setError(`${sourceId}: source file exceeds the 64 MiB verification limit.`)
      return
    }
    try {
      const encoded = await fileBase64(file)
      setSourcePayloads((current) => ({ ...current, [sourceId]: encoded }))
      setSourcePayloadLabels((current) => ({
        ...current,
        [sourceId]: `${file.name} | ${(file.size / 1024 / 1024).toFixed(2)} MiB`,
      }))
      setSourceVerification(null)
      setError('')
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `Source file read failed: ${caught.message}`
          : String(caught),
      )
    }
  }

  const importTimingExcerptPayloads = async (file: File | undefined) => {
    if (!file) return
    try {
      const parsed = JSON.parse(await file.text()) as unknown
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('excerpt map must be a JSON object keyed by claimId')
      }
      const normalized: Record<string, string> = {}
      for (const [claimId, excerpt] of Object.entries(parsed)) {
        if (typeof excerpt !== 'string') {
          throw new Error(`${claimId} must contain exact UTF-8 text`)
        }
        normalized[claimId] = excerpt
      }
      setExcerptPayloads(normalized)
      setExcerptPayloadLabel(file.name)
      setSourceVerification(null)
      setError('')
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `Excerpt map import failed: ${caught.message}`
          : String(caught),
      )
    } finally {
      if (excerptPayloadImportInputRef.current) {
        excerptPayloadImportInputRef.current.value = ''
      }
    }
  }

  const downloadTimingExcerptTemplate = () => {
    const template = Object.fromEntries(
      sourceClaimDeclarations.map((claim) => [claim.claimId, '']),
    )
    downloadText(
      JSON.stringify(template, null, 2),
      'application/json',
      `${sourceReadiness?.packet_id ?? 'timing-source'}-excerpt-template.json`,
    )
  }

  const evaluateTimingSourceVerification = async (
    sourceValues: Record<string, string> | null = (
      Object.keys(sourcePayloads).length ? sourcePayloads : null
    ),
    excerptValues: Record<string, string> | null = (
      Object.keys(excerptPayloads).length ? excerptPayloads : null
    ),
  ) => {
    setSourceVerificationBusy(true)
    setError('')
    try {
      const result = await fetchChakraTimingSourceVerification(
        timingCandidate,
        sourcePacket,
        sourceValues,
        excerptValues,
      )
      setSourceVerification(result)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setSourceVerificationBusy(false)
    }
  }

  const clearTimingSourceVerification = () => {
    resetSourceVerification()
    void evaluateTimingSourceVerification(null, null)
  }

  const downloadTimingReviewBundle = () => {
    if (!sourceVerification?.review_bundle) return
    downloadText(
      JSON.stringify(
        {
          reviewBundleSha256: sourceVerification.review_bundle_sha256,
          reviewBundle: sourceVerification.review_bundle,
        },
        null,
        2,
      ),
      'application/json',
      `${sourceVerification.packet_id ?? 'timing-source'}-independent-review.json`,
    )
  }

  const importTimingReviewBundle = async (file: File | undefined) => {
    if (!file) return
    try {
      const parsed = JSON.parse(await file.text()) as unknown
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('review bundle file must contain a JSON object')
      }
      const wrapped = (parsed as { reviewBundle?: unknown }).reviewBundle
      const bundle = wrapped ?? parsed
      if (!bundle || typeof bundle !== 'object' || Array.isArray(bundle)) {
        throw new Error('reviewBundle must be a JSON object')
      }
      setReviewBundle(bundle)
      setReviewBundleLabel(file.name)
      setExternalReview(null)
      setSignedReviewEnvelope(null)
      setSignedReviewLabel('')
      setSignedReview(null)
      setError('')
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `Review bundle import failed: ${caught.message}`
          : String(caught),
      )
    } finally {
      if (reviewBundleImportInputRef.current) {
        reviewBundleImportInputRef.current.value = ''
      }
    }
  }

  const importTimingReviewAttestation = async (file: File | undefined) => {
    if (!file) return
    try {
      const parsed = JSON.parse(await file.text()) as unknown
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('attestation file must contain a JSON object')
      }
      const wrapped = (parsed as { attestation?: unknown }).attestation
      const attestation = wrapped ?? parsed
      if (
        !attestation
        || typeof attestation !== 'object'
        || Array.isArray(attestation)
      ) {
        throw new Error('attestation must be a JSON object')
      }
      setReviewAttestation(attestation)
      setReviewAttestationLabel(file.name)
      setExternalReview(null)
      setSignedReviewEnvelope(null)
      setSignedReviewLabel('')
      setSignedReview(null)
      setError('')
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `Review attestation import failed: ${caught.message}`
          : String(caught),
      )
    } finally {
      if (reviewAttestationImportInputRef.current) {
        reviewAttestationImportInputRef.current.value = ''
      }
    }
  }

  const evaluateTimingExternalReview = async (
    bundle: unknown | null = reviewBundle,
    attestation: unknown | null = reviewAttestation,
  ) => {
    setExternalReviewBusy(true)
    setError('')
    try {
      const result = await fetchChakraTimingExternalReview(bundle, attestation)
      setExternalReview(result)
      setSignedReview(null)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setExternalReviewBusy(false)
    }
  }

  const clearTimingExternalReview = () => {
    setReviewBundle(null)
    setReviewBundleLabel('')
    setReviewAttestation(null)
    setReviewAttestationLabel('')
    setExternalReview(null)
    setSignedReviewEnvelope(null)
    setSignedReviewLabel('')
    setSignedReview(null)
    void evaluateTimingExternalReview(null, null)
  }

  const useCurrentTimingReviewBundle = () => {
    if (!sourceVerification?.review_bundle) return
    const bundle = sourceVerification.review_bundle
    setReviewBundle(bundle)
    setReviewBundleLabel('Current verified S2 bundle')
    setReviewAttestation(null)
    setReviewAttestationLabel('')
    setExternalReview(null)
    setSignedReviewEnvelope(null)
    setSignedReviewLabel('')
    setSignedReview(null)
    setActiveTab('REVIEW_ATTESTATION')
    void evaluateTimingExternalReview(bundle, null)
  }

  const downloadTimingReviewAttestationTemplate = () => {
    if (!reviewAttestationTemplate) return
    downloadText(
      JSON.stringify(reviewAttestationTemplate, null, 2),
      'application/json',
      `${externalReview?.packet_id ?? 'timing-source'}-attestation-template.json`,
    )
  }

  const downloadTimingCertificationProposal = () => {
    if (!externalReview?.certification_proposal) return
    downloadText(
      JSON.stringify(
        {
          proposalSha256: externalReview.certification_proposal_sha256,
          proposal: externalReview.certification_proposal,
        },
        null,
        2,
      ),
      'application/json',
      `${externalReview.profile_id ?? 'timing-profile'}-certification-proposal.json`,
    )
  }

  const importTimingSignedReview = async (file: File | undefined) => {
    if (!file) return
    try {
      const parsed = JSON.parse(await file.text()) as unknown
      if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
        throw new Error('signed review file must contain a JSON object')
      }
      const wrapped = (parsed as { signedReview?: unknown }).signedReview
      const envelope = wrapped ?? parsed
      if (!envelope || typeof envelope !== 'object' || Array.isArray(envelope)) {
        throw new Error('signedReview must be a JSON object')
      }
      setSignedReviewEnvelope(envelope)
      setSignedReviewLabel(file.name)
      setSignedReview(null)
      setError('')
    } catch (caught) {
      setError(
        caught instanceof Error
          ? `Signed review import failed: ${caught.message}`
          : String(caught),
      )
    } finally {
      if (signedReviewImportInputRef.current) {
        signedReviewImportInputRef.current.value = ''
      }
    }
  }

  const evaluateTimingSignedReview = async (
    bundle: unknown | null = reviewBundle,
    attestation: unknown | null = reviewAttestation,
    envelope: unknown | null = signedReviewEnvelope,
  ) => {
    setSignedReviewBusy(true)
    setError('')
    try {
      const result = await fetchChakraTimingSignedReview(
        bundle,
        attestation,
        envelope,
      )
      setSignedReview(result)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setSignedReviewBusy(false)
    }
  }

  const clearTimingSignedReview = () => {
    setSignedReviewEnvelope(null)
    setSignedReviewLabel('')
    setSignedReview(null)
    void evaluateTimingSignedReview(reviewBundle, reviewAttestation, null)
  }

  const continueToTimingSignedReview = () => {
    setSignedReviewEnvelope(null)
    setSignedReviewLabel('')
    setSignedReview(null)
    setActiveTab('SIGNED_REVIEW')
    void evaluateTimingSignedReview(reviewBundle, reviewAttestation, null)
  }

  const downloadTimingSignedReviewTemplate = () => {
    if (!signedReview?.signed_review_template) return
    downloadText(
      JSON.stringify(signedReview.signed_review_template, null, 2),
      'application/json',
      `${signedReview.profile_id ?? 'timing-profile'}-signed-review-template.json`,
    )
  }

  const openAuditTab = (viewId: AuditTab) => {
    setActiveTab(viewId)
    if (
      viewId === 'TIMING_PROFILE'
      && timingAdmission == null
      && !timingBusy
    ) {
      void evaluateTimingProfile(null)
    }
    if (
      viewId === 'SOURCE_PACKET'
      && sourceReadiness == null
      && !sourcePacketBusy
    ) {
      void evaluateTimingSourcePacket(null)
    }
    if (
      viewId === 'SOURCE_VERIFY'
      && sourceVerification == null
      && !sourceVerificationBusy
    ) {
      void evaluateTimingSourceVerification(null, null)
    }
    if (
      viewId === 'REVIEW_ATTESTATION'
      && externalReview == null
      && !externalReviewBusy
    ) {
      void evaluateTimingExternalReview(null, null)
    }
    if (
      viewId === 'SIGNED_REVIEW'
      && signedReview == null
      && !signedReviewBusy
    ) {
      void evaluateTimingSignedReview(
        reviewBundle,
        reviewAttestation,
        signedReviewEnvelope,
      )
    }
  }

  const selectInterval = (item: ChakraAuditInterval) => {
    setSelectedIntervalId(item.interval_id)
    const nextRay = audit?.ray_rows.find(
      (row) => row.interval_id === item.interval_id,
    )
    const nextCell = audit?.ledger_cells.find(
      (row) => row.interval_id === item.interval_id,
    )
    setSelectedClusterId(nextRay?.cluster_id ?? '')
    setSelectedCellId(nextCell?.cell_id ?? '')
  }

  const selectCell = (item: ChakraAuditLedgerCell) => {
    setSelectedCellId(item.cell_id)
    setSelectedClusterId(item.cluster_ids[0] ?? '')
  }

  const selectRay = (item: ChakraAuditRay) => {
    setSelectedClusterId(item.cluster_id)
    setSelectedCellId(item.cell_ids[0] ?? '')
  }

  const openLedgerCell = (cellId: string) => {
    const nextCell = audit?.ledger_cells.find((item) => item.cell_id === cellId)
    if (!nextCell) return
    const nextInterval = audit?.intervals.find(
      (item) => item.interval_id === nextCell.interval_id,
    )
    if (nextInterval) {
      setSelectedIntervalId(nextInterval.interval_id)
    }
    setSelectedCellId(nextCell.cell_id)
    setSelectedClusterId(nextCell.cluster_ids[0] ?? '')
    setActiveTab('LEDGER')
  }

  const toggleComparison = (intervalIdToToggle: string) => {
    setComparisonIntervalIds((current) => (
      current.includes(intervalIdToToggle)
        ? current.filter((item) => item !== intervalIdToToggle)
        : [...current, intervalIdToToggle]
    ))
    resetPackage()
  }

  const addBookmark = () => {
    if (!bookmarkTargetId || !bookmarkLabel.trim() || !bookmarkNote.trim()) return
    setBookmarks((current) => [
      ...current,
      {
        targetType: bookmarkTargetType,
        targetId: bookmarkTargetId,
        label: bookmarkLabel.trim(),
        note: bookmarkNote.trim(),
        createdAt: new Date().toISOString(),
      },
    ])
    setBookmarkLabel('')
    setBookmarkNote('')
    resetPackage()
  }

  const removeBookmark = (index: number) => {
    setBookmarks((current) => current.filter((_, itemIndex) => itemIndex !== index))
    resetPackage()
  }

  const buildPackage = async () => {
    if (!audit || !baselineIntervalId || comparisonIntervalIds.length === 0) return
    setPackageBusy(true)
    setError('')
    setVerification(null)
    try {
      const result = await buildChakraLabAuditPackage({
        auditRequest: auditRequest(),
        baselineIntervalId,
        comparisonIntervalIds,
        bookmarks,
        sealedAt: new Date().toISOString(),
      })
      setPackageBuild(result)
      setActiveTab('COMPARE')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setPackageBusy(false)
    }
  }

  const verifyPackage = async (value = packageBuild?.package) => {
    if (!value) return
    setPackageBusy(true)
    setError('')
    try {
      const result = await verifyChakraLabAuditPackage(value)
      setVerification(result)
      setActiveTab('PACKAGE')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setPackageBusy(false)
    }
  }

  const importPackage = async (file: File | undefined) => {
    if (!file) return
    try {
      const parsed = JSON.parse(await file.text()) as ChakraReproducibleAuditPackage
      setPackageBuild({ package: parsed, htmlReport: '' })
      await verifyPackage(parsed)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      if (importInputRef.current) importInputRef.current.value = ''
    }
  }

  const addPackageToCatalog = () => {
    const value = packageBuild?.package
    if (!value || verification?.state !== 'PASS') return
    setCatalogPackages((current) => (
      current.some((item) => item.package_id === value.package_id)
        ? current
        : [...current, value]
    ))
    setCatalogBuild(null)
    setCatalogVerification(null)
    setError('')
  }

  const removeCatalogPackage = (packageId: string) => {
    setCatalogPackages((current) => (
      current.filter((item) => item.package_id !== packageId)
    ))
    setCatalogBuild(null)
    setCatalogVerification(null)
  }

  const buildCatalog = async () => {
    if (!catalogPackages.length) return
    setCatalogBusy(true)
    setError('')
    try {
      const now = new Date().toISOString()
      const result = await buildChakraLabAuditCatalog({
        packages: catalogPackages,
        createdAt: now,
        signedAt: now,
      })
      setCatalogBuild(result)
      setCatalogVerification(result.verification)
      setActiveTab('CATALOG')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setCatalogBusy(false)
    }
  }

  const verifyCatalog = async (
    bundle = catalogBuild?.bundle,
    fullReplay = true,
  ) => {
    if (!bundle) return
    setCatalogBusy(true)
    setError('')
    try {
      const result = await verifyChakraLabAuditCatalog(bundle, fullReplay)
      setCatalogVerification(result)
      setActiveTab('CATALOG')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setCatalogBusy(false)
    }
  }

  const importCatalog = async (file: File | undefined) => {
    if (!file) return
    try {
      const bundle = JSON.parse(
        await file.text(),
      ) as ChakraSignedAuditCatalogBundle
      setCatalogPackages(bundle.catalog.entries.map((item) => item.package))
      setCatalogBuild({
        bundle,
        verification: {
          contract: 'SBC_AUDIT_CATALOG_VERIFICATION_V1',
          state: 'FAIL',
          catalog_id: bundle.catalog.catalog_id,
          key_id: bundle.signature.key_id,
          catalog_hash_match: false,
          signature_valid: false,
          embedded_packages_valid: false,
          semantic_replay_state: 'NOT_PERFORMED',
          entry_count: bundle.catalog.entries.length,
          entry_verifications: [],
          errors: ['Imported bundle has not been verified yet.'],
        },
        signingIdentity: {
          algorithm: 'ED25519',
          keyId: bundle.signature.key_id,
          storage: 'LOCAL_USER_FILE',
          claim: 'Imported public signature; integrity must be verified before use.',
        },
      })
      await verifyCatalog(bundle, true)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      if (catalogImportInputRef.current) {
        catalogImportInputRef.current.value = ''
      }
    }
  }

  return (
    <div className="chakra-audit-shell">
      <aside className="chakra-audit-capture">
        <section>
          <div className="chakra-section-heading">
            <strong>Audit range</strong>
            <span>Explicit boundaries</span>
          </div>
          <label>
            Instrument identity
            <input
              value={instrumentIdentity}
              onChange={(event) => setInstrumentIdentity(event.target.value)}
            />
          </label>
          <label>
            Boundary moment (IST)
            <input
              type="datetime-local"
              value={boundaryLocal}
              onChange={(event) => setBoundaryLocal(event.target.value)}
            />
          </label>
          <label>
            Boundary reason
            <input
              value={boundaryReason}
              onChange={(event) => setBoundaryReason(event.target.value)}
            />
          </label>
          <button
            className="secondary-command chakra-audit-action"
            onClick={captureBoundary}
            title="Capture this explicit audit boundary"
          >
            <Plus size={13} />
            Capture boundary
          </button>
          <label>
            Terminal end (IST)
            <input
              type="datetime-local"
              value={terminalLocal}
              onChange={(event) => setTerminalLocal(event.target.value)}
            />
          </label>
          <button
            className="primary-command chakra-audit-action"
            onClick={() => void buildAudit()}
            disabled={busy || boundaries.length === 0}
          >
            <RefreshCw size={13} className={busy ? 'is-spinning' : ''} />
            {busy ? 'Compiling audit' : 'Compile linked audit'}
          </button>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>Captured boundaries</strong>
            <span>{boundaries.length}</span>
          </div>
          <div className="chakra-boundary-list">
            {sortedBoundaries.map((item, index) => (
              <div key={`${item.request.at}-${index}`} className="chakra-boundary-row">
                <button
                  className="chakra-boundary-moment"
                  onClick={() => setTerminalLocal(plusHour(item.request.at))}
                  title={item.request.at}
                >
                  <strong>{formatMoment(item.request.at)}</strong>
                  <span>{item.reason}</span>
                </button>
                <button
                  className="icon-button"
                  onClick={() => removeBoundary(index)}
                  aria-label={`Remove boundary ${index + 1}`}
                  title="Remove boundary"
                >
                  <Trash2 size={12} />
                </button>
              </div>
            ))}
            {!boundaries.length && (
              <span className="chakra-muted-row">No boundary captured</span>
            )}
          </div>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>P4 comparison package</strong>
            <span>{comparisonIntervalIds.length} selected</span>
          </div>
          <label>
            Baseline interval
            <select
              value={baselineIntervalId}
              onChange={(event) => {
                setBaselineIntervalId(event.target.value)
                setComparisonIntervalIds((current) => (
                  current.filter((item) => item !== event.target.value)
                ))
                resetPackage()
              }}
              disabled={!audit}
            >
              {(audit?.intervals ?? []).map((item, index) => (
                <option key={item.interval_id} value={item.interval_id}>
                  {index + 1} - {formatMoment(item.start_utc)}
                </option>
              ))}
            </select>
          </label>
          <div className="chakra-comparison-picks">
            {(audit?.intervals ?? [])
              .filter((item) => item.interval_id !== baselineIntervalId)
              .map((item, index) => (
                <button
                  key={item.interval_id}
                  className={comparisonIntervalIds.includes(item.interval_id) ? 'is-selected' : ''}
                  aria-pressed={comparisonIntervalIds.includes(item.interval_id)}
                  onClick={() => toggleComparison(item.interval_id)}
                >
                  <span>{index + 1}</span>
                  {formatMoment(item.start_utc)}
                </button>
              ))}
            {audit && audit.intervals.length < 2 && (
              <span className="chakra-muted-row">Capture at least two intervals</span>
            )}
          </div>
          <button
            className="primary-command chakra-audit-action"
            onClick={() => void buildPackage()}
            disabled={
              packageBusy
              || !audit
              || !baselineIntervalId
              || comparisonIntervalIds.length === 0
            }
          >
            <PackageCheck size={13} />
            {packageBusy ? 'Recomputing package' : 'Build sealed package'}
          </button>
          <input
            ref={importInputRef}
            className="chakra-package-file"
            type="file"
            accept="application/json,.json"
            onChange={(event) => void importPackage(event.target.files?.[0])}
          />
          <button
            className="secondary-command chakra-audit-action"
            onClick={() => importInputRef.current?.click()}
          >
            <Upload size={13} />
            Import and replay
          </button>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>P5 signed catalog</strong>
            <span>{catalogPackages.length} package(s)</span>
          </div>
          <button
            className="secondary-command chakra-audit-action"
            onClick={addPackageToCatalog}
            disabled={!packageBuild || verification?.state !== 'PASS'}
            title="Add the fully replay-verified P4 package to the local catalog"
          >
            <Archive size={13} />
            Add verified P4
          </button>
          <div className="chakra-catalog-picks">
            {catalogPackages.map((item) => (
              <div key={item.package_id}>
                <span>{item.instrument_identity}</span>
                <code>{shortId(item.package_id)}</code>
                <button
                  className="icon-button"
                  onClick={() => removeCatalogPackage(item.package_id)}
                  title="Remove package from catalog draft"
                  aria-label={`Remove package ${shortId(item.package_id)}`}
                >
                  <Trash2 size={11} />
                </button>
              </div>
            ))}
            {!catalogPackages.length && (
              <span className="chakra-muted-row">No verified P4 package added</span>
            )}
          </div>
          <button
            className="primary-command chakra-audit-action"
            onClick={() => void buildCatalog()}
            disabled={catalogBusy || !catalogPackages.length}
          >
            <Archive size={13} />
            {catalogBusy ? 'Sealing catalog' : 'Seal and sign catalog'}
          </button>
          <input
            ref={catalogImportInputRef}
            className="chakra-package-file"
            type="file"
            accept="application/json,.json"
            onChange={(event) => void importCatalog(event.target.files?.[0])}
          />
          <button
            className="secondary-command chakra-audit-action"
            onClick={() => catalogImportInputRef.current?.click()}
          >
            <Upload size={13} />
            Import signed catalog
          </button>
        </section>
      </aside>

      <section className="chakra-audit-main">
        <div className="chakra-audit-tabs" role="tablist" aria-label="SBC audit views">
          {[
            ...(audit?.views ?? [
              { view_id: 'TIMELINE', label: 'Timeline', purpose: 'Intervals' },
              { view_id: 'LEDGER', label: 'Ledger', purpose: 'Dimensions' },
              { view_id: 'RAY_AUDIT', label: 'Ray audit', purpose: 'Vedha directions' },
              { view_id: 'SOURCE_LINEAGE', label: 'Lineage', purpose: 'Sources' },
              { view_id: 'RECONCILIATION', label: 'Reconciliation', purpose: 'Checks' },
              { view_id: 'VALIDATION', label: 'Validation', purpose: 'Safety gates' },
            ]),
            {
              view_id: 'PHASOR',
              label: 'Fixed phasor',
              purpose: '0/pi scalar-equivalent visualization only',
            },
            {
              view_id: 'TIMING_PROFILE',
              label: 'Timing gate',
              purpose: 'Validate a candidate timing profile without enabling direction',
            },
            {
              view_id: 'SOURCE_PACKET',
              label: 'Source packet',
              purpose: 'Check page-cited evidence readiness for external review',
            },
            {
              view_id: 'SOURCE_VERIFY',
              label: 'Verify sources',
              purpose: 'Hash exact source bytes and build a non-certifying review bundle',
            },
            {
              view_id: 'REVIEW_ATTESTATION',
              label: 'Review attestation',
              purpose: 'Verify a completed external-review record without certifying it',
            },
            {
              view_id: 'SIGNED_REVIEW',
              label: 'Signed review',
              purpose: 'Verify a server-trusted reviewer signature without certifying it',
            },
            {
              view_id: 'COMPARE',
              label: 'Compare',
              purpose: 'Descriptive interval differences only',
            },
            {
              view_id: 'PACKAGE',
              label: 'Package',
              purpose: 'Export, import, and full replay verification',
            },
            {
              view_id: 'CATALOG',
              label: 'Catalog',
              purpose: 'Signed package exchange without cross-audit inference',
            },
          ].map((view) => {
            const viewId = view.view_id as AuditTab
            const Icon = TAB_ICONS[viewId]
            return (
              <button
                key={viewId}
                role="tab"
                aria-selected={activeTab === viewId}
                className={activeTab === viewId ? 'is-active' : ''}
                onClick={() => openAuditTab(viewId)}
                disabled={
                  (!audit && viewId === 'COMPARE')
                  || (!phasor && viewId === 'PHASOR')
                  || (!packageBuild && viewId === 'PACKAGE')
                  || (!catalogBuild && !catalogPackages.length && viewId === 'CATALOG')
                }
                title={view.purpose}
              >
                <Icon size={12} />
                {view.label}
              </button>
            )
          })}
        </div>

        {error && (
          <div className="chakra-audit-error">
            <ShieldAlert size={14} />
            {error}
          </div>
        )}

        {!audit
        && activeTab !== 'PACKAGE'
        && activeTab !== 'CATALOG'
        && activeTab !== 'TIMING_PROFILE'
        && activeTab !== 'SOURCE_PACKET'
        && activeTab !== 'SOURCE_VERIFY'
        && activeTab !== 'REVIEW_ATTESTATION'
        && activeTab !== 'SIGNED_REVIEW' ? (
          <div className="chakra-audit-empty">
            <Clock3 size={23} />
            <strong>Linked audit not compiled</strong>
            <span>SBC_LINKED_AUDIT_VIEW_V1</span>
          </div>
        ) : (
          <div className="chakra-audit-view">
            {activeTab === 'TIMELINE' && (
              <div className="chakra-audit-table is-timeline">
                <div className="chakra-audit-table-head">
                  <span>Interval</span><span>Start</span><span>End</span>
                  <span>Duration</span><span>Net</span><span>Gross</span>
                  <span>Coverage</span>
                </div>
                {(audit?.intervals ?? []).map((item, index) => (
                  <button
                    key={item.interval_id}
                    className={intervalId === item.interval_id ? 'is-selected' : ''}
                    onClick={() => selectInterval(item)}
                  >
                    <strong>{index + 1}</strong>
                    <span>{formatMoment(item.start_utc)}</span>
                    <span>{formatMoment(item.end_utc)}</span>
                    <span>{formatDuration(item.duration_seconds)}</span>
                    <span>{units(item.total_summary.net_guidance_units)}</span>
                    <span>{units(item.total_summary.gross_activation_units)}</span>
                    <span>{(item.total_summary.scoring_coverage_ratio * 100).toFixed(0)}%</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'LEDGER' && (
              <div className="chakra-audit-table is-ledger">
                <div className="chakra-audit-table-head">
                  <span>Axis</span><span>Key</span><span>Favorable</span>
                  <span>Adverse</span><span>Net</span><span>Gross</span>
                  <span>Unknown</span>
                </div>
                {ledgerRows.map((item) => (
                  <button
                    key={item.cell_id}
                    className={selectedCellId === item.cell_id ? 'is-selected' : ''}
                    onClick={() => selectCell(item)}
                  >
                    <strong>{displayToken(item.axis)}</strong>
                    <span>{displayToken(item.key)}</span>
                    <span>{units(item.summary.favorable_guidance_units)}</span>
                    <span>{units(item.summary.adverse_guidance_units)}</span>
                    <span>{units(item.summary.net_guidance_units)}</span>
                    <span>{units(item.summary.gross_activation_units)}</span>
                    <span>{item.summary.unknown_contribution_count}</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'RAY_AUDIT' && (
              <div className="chakra-audit-table is-rays">
                <div className="chakra-audit-table-head">
                  <span>Actor</span><span>Source</span><span>Direction</span>
                  <span>Target</span><span>Nature</span><span>Units</span>
                  <span>Status</span>
                </div>
                {rayRows.map((item) => (
                  <button
                    key={item.cluster_id}
                    className={selectedClusterId === item.cluster_id ? 'is-selected' : ''}
                    onClick={() => selectRay(item)}
                  >
                    <strong>{item.actor_identity ?? 'Missing'}</strong>
                    <span>{displayToken(item.source_nakshatra)}</span>
                    <span>{displayToken(item.vedha_direction)}</span>
                    <span>{displayToken(item.target_value)}</span>
                    <span>{displayToken(item.nature)}</span>
                    <span>{item.signed_guidance_units == null ? 'Unknown' : units(item.signed_guidance_units)}</span>
                    <span>{displayToken(item.status)}</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'SOURCE_LINEAGE' && (
              <div className="chakra-audit-table is-lineage">
                <div className="chakra-audit-table-head">
                  <span>Cluster</span><span>Snapshot</span><span>Foundation</span>
                  <span>Grid</span><span>Vedha</span><span>Witness</span>
                  <span>Status</span>
                </div>
                {lineageRows.map((item) => (
                  <button
                    key={item.cluster_id}
                    className={selectedClusterId === item.cluster_id ? 'is-selected' : ''}
                    onClick={() => setSelectedClusterId(item.cluster_id)}
                  >
                    <strong>{shortId(item.cluster_id)}</strong>
                    <span>{shortId(item.snapshot_id)}</span>
                    <span>{item.foundation_profile_id}</span>
                    <span>{item.grid_profile_id}</span>
                    <span>{item.vedha_profile_id}</span>
                    <span>{item.target_witness_set_id ?? 'Missing'}</span>
                    <span>{displayToken(item.status)}</span>
                  </button>
                ))}
              </div>
            )}

            {activeTab === 'RECONCILIATION' && (
              <div className="chakra-reconciliation-grid">
                {reconciliationRows.map((item) => (
                  <div key={`${item.interval_id}-${item.axis}`}>
                    <strong>{displayToken(item.axis)}</strong>
                    <span>{item.cell_count} cells</span>
                    <span>{item.cluster_count} clusters</span>
                    <em>{item.reconciled ? 'PASS' : 'FAIL'}</em>
                  </div>
                ))}
              </div>
            )}

            {activeTab === 'VALIDATION' && (
              <div className="chakra-validation-list">
                {(audit?.validation_gates ?? []).map((item) => (
                  <div key={item.gate_id} className={`is-${item.state.toLowerCase()}`}>
                    <span>{item.state}</span>
                    <strong>{item.label}</strong>
                    <p>{item.detail}</p>
                  </div>
                ))}
                <div className="chakra-blocked-capabilities">
                  <strong>Blocked capabilities</strong>
                  <div>
                    {(audit?.guardrails.blocked_capabilities ?? []).map((item) => (
                      <span key={item}>{displayToken(item)}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'PHASOR' && (
              !phasorInterval ? (
                <div className="chakra-audit-empty is-inline">
                  <Orbit size={21} />
                  <strong>Fixed phasor projection not compiled</strong>
                  <span>Compile the linked audit to run exact P2 parity checks.</span>
                </div>
              ) : (
                <div className="chakra-phasor-workspace">
                  <p className="chakra-phasor-warning">
                    Fixed 0/pi scalar encoding only. This is not a physical wave,
                    timing phase, market direction, confidence score, or extra vote.
                  </p>
                  <div className="chakra-phasor-summary">
                    <div>
                      <span>Real sum</span>
                      <strong>{signedUnits(phasorInterval.vector_real_sum_units)}</strong>
                      <em>P2 net {signedUnits(phasorInterval.source_net_units)}</em>
                    </div>
                    <div>
                      <span>Magnitude sum</span>
                      <strong>{units(phasorInterval.vector_magnitude_sum_units)}</strong>
                      <em>P2 gross {units(phasorInterval.source_gross_activation_units)}</em>
                    </div>
                    <div>
                      <span>Imaginary sum</span>
                      <strong>{units(phasorInterval.vector_imaginary_sum_units)}</strong>
                      <em>must remain zero</em>
                    </div>
                    <div>
                      <span>Known-score coherence</span>
                      <strong>
                        {(phasorInterval.known_scored_coherence_ratio * 100).toFixed(1)}%
                      </strong>
                      <em>descriptive cancellation only</em>
                    </div>
                  </div>

                  <div className="chakra-phasor-plot" aria-label="Fixed zero and pi phasor plot">
                    <svg
                      role="img"
                      aria-label="Scalar-equivalent phasors on a fixed real axis"
                      viewBox={`0 0 760 ${Math.max(150, plottedPhasors.length * 34 + 62)}`}
                    >
                      <defs>
                        <marker
                          id="chakra-phasor-positive-arrow"
                          markerWidth="7"
                          markerHeight="7"
                          refX="6"
                          refY="3.5"
                          orient="auto"
                        >
                          <path d="M0,0 L7,3.5 L0,7 Z" className="is-positive" />
                        </marker>
                        <marker
                          id="chakra-phasor-negative-arrow"
                          markerWidth="7"
                          markerHeight="7"
                          refX="6"
                          refY="3.5"
                          orient="auto"
                        >
                          <path d="M0,0 L7,3.5 L0,7 Z" className="is-negative" />
                        </marker>
                      </defs>
                      <text x="392" y="18" className="chakra-phasor-axis-label is-positive">
                        fixed 0
                      </text>
                      <text x="368" y="18" textAnchor="end" className="chakra-phasor-axis-label is-negative">
                        fixed pi
                      </text>
                      <line x1="380" y1="25" x2="380" y2={Math.max(135, plottedPhasors.length * 34 + 48)} className="chakra-phasor-zero" />
                      {plottedPhasors.map((item, index) => {
                        const y = 48 + index * 34
                        const magnitude = item.magnitude_units ?? 0
                        const length = 16 + (magnitude / maxPhasorMagnitude) * 250
                        const isPositive = item.fixed_angle === 'ZERO'
                        const x2 = isPositive ? 380 + length : 380 - length
                        return (
                          <g key={item.vector_id} className={isPositive ? 'is-positive' : 'is-negative'}>
                            <line x1="92" y1={y} x2="668" y2={y} className="chakra-phasor-row-axis" />
                            <text x="12" y={y + 3} className="chakra-phasor-actor">
                              {item.actor_identity ?? 'Missing evidence'}
                            </text>
                            <line
                              x1="380"
                              y1={y}
                              x2={x2}
                              y2={y}
                              className="chakra-phasor-vector"
                              markerEnd={`url(#chakra-phasor-${isPositive ? 'positive' : 'negative'}-arrow)`}
                            />
                            <text
                              x={isPositive ? x2 + 10 : x2 - 10}
                              y={y + 3}
                              textAnchor={isPositive ? 'start' : 'end'}
                              className="chakra-phasor-value"
                            >
                              {signedUnits(item.real_component_units ?? 0)}
                            </text>
                          </g>
                        )
                      })}
                    </svg>
                  </div>

                  {unknownPhasors.length > 0 && (
                    <div className="chakra-phasor-unknowns">
                      <strong>Unknown evidence stays unplotted</strong>
                      {unknownPhasors.map((item) => (
                        <div key={item.vector_id}>
                          <span>{item.actor_identity ?? item.source_evidence_id}</span>
                          <p>{item.unknown_reason}</p>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="chakra-phasor-gates">
                    {(phasor?.validation_gates ?? []).map((item) => (
                      <div key={item.gate_id} className={`is-${item.state.toLowerCase()}`}>
                        <span>{item.state}</span>
                        <strong>{item.label}</strong>
                        <p>{item.detail}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )
            )}

            {activeTab === 'TIMING_PROFILE' && (
              <div className="chakra-timing-gate-workspace">
                <p className="chakra-timing-gate-warning">
                  Admission check only. The app supplies no timing profile and
                  calculates no timing phase, direction, confidence, or trade output.
                </p>
                <div className="chakra-timing-gate-toolbar">
                  <input
                    ref={timingImportInputRef}
                    className="chakra-package-file"
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) => (
                      void importTimingProfile(event.target.files?.[0])
                    )}
                  />
                  <button
                    className="secondary-command"
                    onClick={() => timingImportInputRef.current?.click()}
                    disabled={timingBusy}
                  >
                    <Upload size={13} />
                    Load candidate JSON
                  </button>
                  <button
                    className="secondary-command"
                    onClick={() => void evaluateTimingProfile(null)}
                    disabled={timingBusy || !timingCandidateLabel}
                    title="Discard the in-memory candidate and show repository readiness"
                  >
                    <Trash2 size={13} />
                    Clear candidate
                  </button>
                  <span>
                    {timingCandidateLabel || 'No candidate loaded'}
                  </span>
                </div>

                {timingBusy && (
                  <div className="chakra-audit-empty is-inline">
                    <RefreshCw size={21} className="is-spinning" />
                    <strong>Checking admission gates</strong>
                    <span>No candidate is persisted.</span>
                  </div>
                )}

                {!timingBusy && timingAdmission && (
                  <>
                    <div className="chakra-timing-gate-summary">
                      <div>
                        <span>Candidate status</span>
                        <strong>{displayToken(timingAdmission.profile_status)}</strong>
                        <em>
                          {timingAdmission.profile_id ?? 'No profile identity'}
                        </em>
                      </div>
                      <div>
                        <span>Structure</span>
                        <strong>
                          {timingAdmission.structural_complete ? 'PASS' : 'NOT READY'}
                        </strong>
                        <em>all mandatory profile fields</em>
                      </div>
                      <div>
                        <span>Source registry</span>
                        <strong>
                          {timingAdmission.source_registry_admitted
                            ? 'ADMITTED'
                            : 'NOT ADMITTED'}
                        </strong>
                        <em>server-owned hash registry</em>
                      </div>
                      <div>
                        <span>Directional output</span>
                        <strong>UNAVAILABLE</strong>
                        <em>engine not implemented</em>
                      </div>
                      <div>
                        <span>Financial use</span>
                        <strong>BLOCKED</strong>
                        <em>prospective gate not passed</em>
                      </div>
                      <div>
                        <span>Execution</span>
                        <strong>LOCKED</strong>
                        <em>directional contribution 0.0</em>
                      </div>
                    </div>

                    {timingAdmission.candidate_profile_hash && (
                      <div className="chakra-timing-gate-identity">
                        <span>Candidate SHA-256</span>
                        <code>{timingAdmission.candidate_profile_hash}</code>
                      </div>
                    )}

                    <div className="chakra-timing-gate-list">
                      {timingAdmission.validation_gates.map((item) => (
                        <div
                          key={item.gate_id}
                          className={`is-${item.state.toLowerCase()}`}
                        >
                          <span>{item.state}</span>
                          <strong>{item.label}</strong>
                          <p>{item.detail}</p>
                          {item.missing_paths.length > 0 && (
                            <code>{item.missing_paths.join(' | ')}</code>
                          )}
                        </div>
                      ))}
                    </div>

                    <div className="chakra-blocked-capabilities">
                      <strong>Still blocked</strong>
                      <div>
                        {timingAdmission.guardrails.blocked_capabilities.map((item) => (
                          <span key={item}>{displayToken(item)}</span>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                {!timingBusy && !timingAdmission && (
                  <div className="chakra-audit-empty is-inline">
                    <FileCheck2 size={21} />
                    <strong>Admission gate not checked</strong>
                    <span>Open this view again to retry the read-only check.</span>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'SOURCE_PACKET' && (
              <div className="chakra-timing-gate-workspace">
                <p className="chakra-timing-gate-warning">
                  Readiness check only. JSON declarations are hash-pinned, but
                  S1 does not inspect source bytes, certify doctrine, register a
                  profile, calculate direction, or enable trading.
                </p>
                <div className="chakra-timing-gate-toolbar">
                  <input
                    ref={sourcePacketImportInputRef}
                    className="chakra-package-file"
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) => (
                      void importTimingSourcePacket(event.target.files?.[0])
                    )}
                  />
                  <button
                    className="secondary-command"
                    onClick={() => sourcePacketImportInputRef.current?.click()}
                    disabled={sourcePacketBusy || !timingCandidate}
                    title={
                      timingCandidate
                        ? 'Load a frozen source packet for the current candidate'
                        : 'Load a candidate in Timing gate first'
                    }
                  >
                    <Upload size={13} />
                    Load source packet
                  </button>
                  <button
                    className="secondary-command"
                    onClick={() => void evaluateTimingSourcePacket(null)}
                    disabled={sourcePacketBusy || !sourcePacketLabel}
                    title="Discard the in-memory source packet"
                  >
                    <Trash2 size={13} />
                    Clear packet
                  </button>
                  <span>
                    {sourcePacketLabel || 'No source packet loaded'}
                    {' | '}
                    {timingCandidateLabel || 'candidate required'}
                  </span>
                </div>

                {sourcePacketBusy && (
                  <div className="chakra-audit-empty is-inline">
                    <RefreshCw size={21} className="is-spinning" />
                    <strong>Checking source readiness</strong>
                    <span>No candidate or packet is persisted.</span>
                  </div>
                )}

                {!sourcePacketBusy && sourceReadiness && (
                  <>
                    <div className="chakra-timing-gate-summary is-source-readiness">
                      <div>
                        <span>Packet status</span>
                        <strong>{displayToken(sourceReadiness.packet_status)}</strong>
                        <em>{sourceReadiness.packet_id ?? 'No packet identity'}</em>
                      </div>
                      <div>
                        <span>Candidate structure</span>
                        <strong>
                          {sourceReadiness.candidate_structural_complete
                            ? 'PASS'
                            : 'NOT READY'}
                        </strong>
                        <em>T0 profile contract</em>
                      </div>
                      <div>
                        <span>Packet structure</span>
                        <strong>
                          {sourceReadiness.packet_structural_complete
                            ? 'PASS'
                            : 'NOT READY'}
                        </strong>
                        <em>exact hash and citations</em>
                      </div>
                      <div>
                        <span>Claim coverage</span>
                        <strong>
                          {sourceReadiness.claim_coverage_complete
                            ? 'COMPLETE'
                            : 'INCOMPLETE'}
                        </strong>
                        <em>candidate value bindings</em>
                      </div>
                      <div>
                        <span>Witness lineages</span>
                        <strong>
                          {sourceReadiness.independent_witness_coverage_complete
                            ? 'COMPLETE'
                            : 'INCOMPLETE'}
                        </strong>
                        <em>doctrine only</em>
                      </div>
                      <div>
                        <span>Conflicts</span>
                        <strong>
                          {sourceReadiness.conflicts_resolved ? 'CLEAR' : 'OPEN'}
                        </strong>
                        <em>unresolved items block review</em>
                      </div>
                      <div>
                        <span>External review</span>
                        <strong>PENDING</strong>
                        <em>required outside S1</em>
                      </div>
                      <div>
                        <span>Source certification</span>
                        <strong>BLOCKED</strong>
                        <em>registry remains server-owned</em>
                      </div>
                    </div>

                    {(sourceReadiness.candidate_profile_hash
                      || sourceReadiness.packet_hash) && (
                      <div className="chakra-source-packet-identities">
                        {sourceReadiness.candidate_profile_hash && (
                          <div>
                            <span>Candidate SHA-256</span>
                            <code>{sourceReadiness.candidate_profile_hash}</code>
                          </div>
                        )}
                        {sourceReadiness.packet_hash && (
                          <div>
                            <span>Packet SHA-256</span>
                            <code>{sourceReadiness.packet_hash}</code>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="chakra-source-coverage-list">
                      <header>
                        <strong>Claim coverage</strong>
                        <span>Primary | witness | research spec | lineages</span>
                      </header>
                      {sourceReadiness.claim_coverage.map((item) => (
                        <div
                          key={item.profile_path}
                          className={`is-${item.coverage_state.toLowerCase()}`}
                        >
                          <span>{item.coverage_state}</span>
                          <strong>{displayToken(item.profile_path.slice(1))}</strong>
                          <code>{item.claim_class}</code>
                          <em>
                            {item.primary_source_count}
                            {' | '}
                            {item.independent_witness_count}
                            {' | '}
                            {item.research_specification_count}
                            {' | '}
                            {item.independent_lineage_count}
                          </em>
                          <p>{item.detail}</p>
                        </div>
                      ))}
                    </div>

                    <div className="chakra-timing-gate-list">
                      {sourceReadiness.validation_gates.map((item) => (
                        <div
                          key={item.gate_id}
                          className={`is-${item.state.toLowerCase()}`}
                        >
                          <span>{item.state}</span>
                          <strong>{item.label}</strong>
                          <p>{item.detail}</p>
                          {item.missing_paths.length > 0 && (
                            <code>{item.missing_paths.join(' | ')}</code>
                          )}
                        </div>
                      ))}
                    </div>

                    <div className="chakra-blocked-capabilities">
                      <strong>Still blocked</strong>
                      <div>
                        {sourceReadiness.guardrails.blocked_capabilities.map((item) => (
                          <span key={item}>{displayToken(item)}</span>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                {!sourcePacketBusy && !sourceReadiness && (
                  <div className="chakra-audit-empty is-inline">
                    <FileCheck2 size={21} />
                    <strong>Source readiness not checked</strong>
                    <span>Open this view again to retry the read-only check.</span>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'SOURCE_VERIFY' && (
              <div className="chakra-timing-gate-workspace">
                <p className="chakra-timing-gate-warning">
                  S2 hashes exact local source bytes and exact UTF-8 excerpt
                  payloads. Files remain in memory and are excluded from the
                  export. Matching hashes do not prove page presence, doctrine
                  correctness, external review, certification, or trading value.
                </p>

                <div className="chakra-timing-gate-toolbar">
                  <input
                    ref={excerptPayloadImportInputRef}
                    className="chakra-package-file"
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) => (
                      void importTimingExcerptPayloads(event.target.files?.[0])
                    )}
                  />
                  <button
                    className="primary-command"
                    onClick={() => void evaluateTimingSourceVerification()}
                    disabled={
                      sourceVerificationBusy
                      || !timingCandidate
                      || !sourcePacket
                    }
                    title="Hash the loaded bytes and compare them with the frozen S1 packet"
                  >
                    <FileSearch size={13} />
                    Verify exact payloads
                  </button>
                  <button
                    className="secondary-command"
                    onClick={() => excerptPayloadImportInputRef.current?.click()}
                    disabled={sourceVerificationBusy || !sourcePacket}
                    title="Load a JSON object mapping every claimId to its exact UTF-8 excerpt"
                  >
                    <Upload size={13} />
                    Load excerpt map
                  </button>
                  <button
                    className="secondary-command"
                    onClick={downloadTimingExcerptTemplate}
                    disabled={!sourceClaimDeclarations.length}
                    title="Download the exact claimId keys required by this packet"
                  >
                    <Download size={13} />
                    Excerpt template
                  </button>
                  <button
                    className="secondary-command"
                    onClick={clearTimingSourceVerification}
                    disabled={
                      sourceVerificationBusy
                      || (
                        !Object.keys(sourcePayloads).length
                        && !Object.keys(excerptPayloads).length
                        && !sourceVerification
                      )
                    }
                    title="Discard all in-memory source and excerpt payloads"
                  >
                    <Trash2 size={13} />
                    Clear payloads
                  </button>
                  <span>
                    {Object.keys(sourcePayloads).length}
                    /
                    {sourceArtifactDeclarations.length}
                    {' source files | '}
                    {Object.keys(excerptPayloads).length}
                    /
                    {sourceClaimDeclarations.length}
                    {' excerpts'}
                  </span>
                </div>

                {!sourcePacket && (
                  <div className="chakra-audit-empty is-inline">
                    <FileSearch size={21} />
                    <strong>Frozen source packet required</strong>
                    <span>Load a candidate in Timing gate, then its packet in Source packet.</span>
                  </div>
                )}

                {Boolean(sourcePacket) && (
                  <>
                    <section className="chakra-source-verification-section">
                      <header>
                        <div>
                          <strong>Source artifacts</strong>
                          <span>Exact bytes only; 64 MiB maximum per file</span>
                        </div>
                        <em>
                          {Object.keys(sourcePayloads).length}
                          /
                          {sourceArtifactDeclarations.length}
                          {' loaded'}
                        </em>
                      </header>
                      <div className="chakra-source-file-list">
                        {sourceArtifactDeclarations.map((source) => (
                          <div key={source.sourceId}>
                            <span className={
                              sourcePayloads[source.sourceId]
                                ? 'is-loaded'
                                : 'is-missing'
                            }>
                              {sourcePayloads[source.sourceId] ? 'LOADED' : 'MISSING'}
                            </span>
                            <div>
                              <strong>{source.title}</strong>
                              <code>{source.sourceId}</code>
                              <small>
                                {displayToken(source.sourceRole)}
                                {' | '}
                                {source.lineageId}
                              </small>
                            </div>
                            <code title={source.sha256}>{shortId(source.sha256)}</code>
                            <span>{sourcePayloadLabels[source.sourceId] ?? 'No file selected'}</span>
                            <label className="secondary-command chakra-source-file-picker">
                              <Upload size={12} />
                              {sourcePayloads[source.sourceId] ? 'Replace' : 'Choose'}
                              <input
                                type="file"
                                onChange={(event) => {
                                  void loadTimingSourceArtifact(
                                    source.sourceId,
                                    event.target.files?.[0],
                                  )
                                  event.currentTarget.value = ''
                                }}
                              />
                            </label>
                          </div>
                        ))}
                      </div>
                    </section>

                    <section className="chakra-source-verification-section">
                      <header>
                        <div>
                          <strong>Excerpt payload map</strong>
                          <span>
                            Exact UTF-8 text, with no whitespace or line-ending normalization
                          </span>
                        </div>
                        <em>{excerptPayloadLabel || 'No map loaded'}</em>
                      </header>
                      <div className="chakra-source-excerpt-map">
                        {sourceClaimDeclarations.map((claim) => (
                          <div key={claim.claimId}>
                            <span className={
                              Object.hasOwn(excerptPayloads, claim.claimId)
                                ? 'is-loaded'
                                : 'is-missing'
                            }>
                              {Object.hasOwn(excerptPayloads, claim.claimId)
                                ? 'LOADED'
                                : 'MISSING'}
                            </span>
                            <strong>{displayToken(claim.profilePath.slice(1))}</strong>
                            <code>{claim.claimId}</code>
                            <small>
                              {claim.sourceId}
                              {' | pages '}
                              {claim.pageStart}
                              -
                              {claim.pageEnd}
                            </small>
                          </div>
                        ))}
                      </div>
                    </section>
                  </>
                )}

                {sourceVerificationBusy && (
                  <div className="chakra-audit-empty is-inline">
                    <RefreshCw size={21} className="is-spinning" />
                    <strong>Hashing exact evidence payloads</strong>
                    <span>Raw bytes and excerpt text are not persisted.</span>
                  </div>
                )}

                {!sourceVerificationBusy && sourceVerification && (
                  <>
                    <div className="chakra-timing-gate-summary is-source-verification">
                      <div>
                        <span>Verification</span>
                        <strong>
                          {displayToken(sourceVerification.verification_status)}
                        </strong>
                        <em>exact payload hashes</em>
                      </div>
                      <div>
                        <span>S1 packet</span>
                        <strong>
                          {sourceVerification.s1_ready_for_external_review
                            ? 'READY'
                            : 'NOT READY'}
                        </strong>
                        <em>declaration gate</em>
                      </div>
                      <div>
                        <span>Source bytes</span>
                        <strong>
                          {sourceVerification.all_source_bytes_verified
                            ? 'VERIFIED'
                            : 'INCOMPLETE'}
                        </strong>
                        <em>whole-file SHA-256</em>
                      </div>
                      <div>
                        <span>Excerpts</span>
                        <strong>
                          {sourceVerification.all_excerpt_payloads_verified
                            ? 'VERIFIED'
                            : 'INCOMPLETE'}
                        </strong>
                        <em>exact UTF-8 SHA-256</em>
                      </div>
                      <div>
                        <span>Review bundle</span>
                        <strong>
                          {sourceVerification.ready_for_independent_review
                            ? 'READY'
                            : 'BLOCKED'}
                        </strong>
                        <em>no source bytes included</em>
                      </div>
                      <div>
                        <span>Page truth</span>
                        <strong>UNCHECKED</strong>
                        <em>external visual review</em>
                      </div>
                      <div>
                        <span>Certification</span>
                        <strong>BLOCKED</strong>
                        <em>independent decision required</em>
                      </div>
                      <div>
                        <span>Execution</span>
                        <strong>LOCKED</strong>
                        <em>zero directional contribution</em>
                      </div>
                    </div>

                    {(sourceVerification.packet_hash
                      || sourceVerification.review_bundle_sha256) && (
                      <div className="chakra-source-packet-identities">
                        {sourceVerification.packet_hash && (
                          <div>
                            <span>Packet SHA-256</span>
                            <code>{sourceVerification.packet_hash}</code>
                          </div>
                        )}
                        {sourceVerification.review_bundle_sha256 && (
                          <div>
                            <span>Review bundle SHA-256</span>
                            <code>{sourceVerification.review_bundle_sha256}</code>
                          </div>
                        )}
                      </div>
                    )}

                    {sourceVerification.review_bundle && (
                      <div className="chakra-review-bundle-ready">
                        <div>
                          <strong>Independent-review bundle ready</strong>
                          <span>
                            It contains the candidate, frozen declarations,
                            hash observations, review instructions, and a blank
                            attestation template. It contains no books or excerpt text.
                          </span>
                        </div>
                        <div className="chakra-review-bundle-actions">
                          <button
                            className="primary-command"
                            onClick={useCurrentTimingReviewBundle}
                          >
                            <FileSignature size={13} />
                            Continue to attestation
                          </button>
                          <button
                            className="secondary-command"
                            onClick={downloadTimingReviewBundle}
                          >
                            <Download size={13} />
                            Download reviewer bundle
                          </button>
                        </div>
                      </div>
                    )}

                    {sourceVerification.source_artifact_checks.length > 0 && (
                      <div className="chakra-source-verification-results">
                        <header>
                          <strong>Source byte checks</strong>
                          <span>Expected vs observed whole-file SHA-256</span>
                        </header>
                        {sourceVerification.source_artifact_checks.map((item) => (
                          <div
                            key={item.source_id}
                            className={`is-${item.verification_state.toLowerCase()}`}
                          >
                            <span>{item.verification_state}</span>
                            <strong>{item.source_id}</strong>
                            <code>
                              {shortId(item.expected_sha256)}
                              {' / '}
                              {shortId(item.observed_sha256)}
                            </code>
                            <em>
                              {item.observed_byte_length == null
                                ? 'not loaded'
                                : `${item.observed_byte_length.toLocaleString()} bytes`}
                            </em>
                            <p>{item.detail}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    {sourceVerification.excerpt_payload_checks.length > 0 && (
                      <div className="chakra-source-verification-results">
                        <header>
                          <strong>Excerpt payload checks</strong>
                          <span>Hash match does not verify page presence</span>
                        </header>
                        {sourceVerification.excerpt_payload_checks.map((item) => (
                          <div
                            key={item.claim_id}
                            className={`is-${item.verification_state.toLowerCase()}`}
                          >
                            <span>{item.verification_state}</span>
                            <strong>{item.claim_id}</strong>
                            <code>
                              {shortId(item.expected_sha256)}
                              {' / '}
                              {shortId(item.observed_sha256)}
                            </code>
                            <em>
                              {item.observed_utf8_byte_length == null
                                ? 'not loaded'
                                : `${item.observed_utf8_byte_length.toLocaleString()} bytes`}
                            </em>
                            <p>{item.detail}</p>
                          </div>
                        ))}
                      </div>
                    )}

                    <div className="chakra-timing-gate-list">
                      {sourceVerification.validation_gates.map((item) => (
                        <div
                          key={item.gate_id}
                          className={`is-${item.state.toLowerCase()}`}
                        >
                          <span>{item.state}</span>
                          <strong>{item.label}</strong>
                          <p>{item.detail}</p>
                          {item.missing_ids.length > 0 && (
                            <code>{item.missing_ids.join(' | ')}</code>
                          )}
                        </div>
                      ))}
                    </div>

                    <div className="chakra-blocked-capabilities">
                      <strong>Still blocked after S2</strong>
                      <div>
                        {sourceVerification.guardrails.blocked_capabilities.map(
                          (item) => <span key={item}>{displayToken(item)}</span>,
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            {activeTab === 'REVIEW_ATTESTATION' && (
              <div className="chakra-timing-gate-workspace">
                <p className="chakra-timing-gate-warning">
                  S3 checks the internal integrity of a completed external-review
                  record. It does not authenticate the reviewer, prove reviewer
                  independence, certify the source doctrine, register a profile,
                  or unlock inference and trading.
                </p>

                <div className="chakra-timing-gate-toolbar">
                  <input
                    ref={reviewBundleImportInputRef}
                    className="chakra-package-file"
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) => (
                      void importTimingReviewBundle(event.target.files?.[0])
                    )}
                  />
                  <input
                    ref={reviewAttestationImportInputRef}
                    className="chakra-package-file"
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) => (
                      void importTimingReviewAttestation(event.target.files?.[0])
                    )}
                  />
                  <button
                    className="primary-command"
                    onClick={() => void evaluateTimingExternalReview()}
                    disabled={externalReviewBusy || !reviewBundle}
                    title="Check the bundle and completed attestation as one read-only record"
                  >
                    <FileSignature size={13} />
                    Verify review
                  </button>
                  <button
                    className="secondary-command"
                    onClick={() => reviewBundleImportInputRef.current?.click()}
                    disabled={externalReviewBusy}
                  >
                    <Upload size={13} />
                    Load review bundle
                  </button>
                  <button
                    className="secondary-command"
                    onClick={() => reviewAttestationImportInputRef.current?.click()}
                    disabled={externalReviewBusy}
                  >
                    <Upload size={13} />
                    Load attestation
                  </button>
                  <button
                    className="secondary-command"
                    onClick={downloadTimingReviewAttestationTemplate}
                    disabled={!reviewAttestationTemplate}
                    title="Download the exact blank decision record embedded in the bundle"
                  >
                    <Download size={13} />
                    Attestation template
                  </button>
                  <button
                    className="secondary-command"
                    onClick={clearTimingExternalReview}
                    disabled={
                      externalReviewBusy
                      || (!reviewBundle && !reviewAttestation && !externalReview)
                    }
                  >
                    <Trash2 size={13} />
                    Clear
                  </button>
                </div>

                <section className="chakra-source-verification-section">
                  <header>
                    <div>
                      <strong>Independent-review files</strong>
                      <span>
                        JSON is checked in memory and is not written to either registry
                      </span>
                    </div>
                    <em>
                      {[reviewBundle, reviewAttestation].filter(Boolean).length}
                      /2 loaded
                    </em>
                  </header>
                  <div className="chakra-external-review-inputs">
                    <div>
                      <span className={reviewBundle ? 'is-loaded' : 'is-missing'}>
                        {reviewBundle ? 'LOADED' : 'MISSING'}
                      </span>
                      <strong>Reviewer bundle</strong>
                      <span>{reviewBundleLabel || 'No bundle selected'}</span>
                      <small>S2 evidence observations and blank attestation</small>
                    </div>
                    <div>
                      <span className={
                        reviewAttestation ? 'is-loaded' : 'is-missing'
                      }>
                        {reviewAttestation ? 'LOADED' : 'MISSING'}
                      </span>
                      <strong>Completed attestation</strong>
                      <span>{reviewAttestationLabel || 'No attestation selected'}</span>
                      <small>Exact source, claim, and conflict decisions</small>
                    </div>
                  </div>
                </section>

                {externalReviewBusy && (
                  <div className="chakra-audit-empty is-inline">
                    <RefreshCw size={21} className="is-spinning" />
                    <strong>Checking the external-review record</strong>
                    <span>No certification or registry write is performed.</span>
                  </div>
                )}

                {!externalReviewBusy && externalReview && (
                  <>
                    <div className="chakra-timing-gate-summary is-source-verification">
                      <div>
                        <span>Review status</span>
                        <strong>{displayToken(externalReview.review_status)}</strong>
                        <em>record-coherence result</em>
                      </div>
                      <div>
                        <span>Bundle integrity</span>
                        <strong>
                          {externalReview.bundle_integrity_verified
                            ? 'VERIFIED'
                            : 'NOT VERIFIED'}
                        </strong>
                        <em>canonical SHA-256</em>
                      </div>
                      <div>
                        <span>Embedded S1</span>
                        <strong>
                          {externalReview.embedded_s1_ready ? 'PASS' : 'NOT READY'}
                        </strong>
                        <em>candidate and declarations</em>
                      </div>
                      <div>
                        <span>S2 evidence rows</span>
                        <strong>
                          {externalReview.s2_rows_verified ? 'PASS' : 'NOT VERIFIED'}
                        </strong>
                        <em>exact source and claim IDs</em>
                      </div>
                      <div>
                        <span>Attestation</span>
                        <strong>
                          {externalReview.attestation_complete
                            ? 'COMPLETE'
                            : 'INCOMPLETE'}
                        </strong>
                        <em>final decisions and notes</em>
                      </div>
                      <div>
                        <span>Review decision</span>
                        <strong>
                          {externalReview.review_approved ? 'APPROVED' : 'NOT APPROVED'}
                        </strong>
                        <em>reviewer-stated outcome</em>
                      </div>
                      <div>
                        <span>Human proposal</span>
                        <strong>
                          {externalReview.ready_for_human_certification_decision
                            ? 'READY'
                            : 'BLOCKED'}
                        </strong>
                        <em>not a certificate</em>
                      </div>
                      <div>
                        <span>Execution</span>
                        <strong>LOCKED</strong>
                        <em>zero directional contribution</em>
                      </div>
                    </div>

                    {(externalReview.review_bundle_sha256
                      || externalReview.attestation_sha256
                      || externalReview.certification_proposal_sha256) && (
                      <div className="chakra-source-packet-identities">
                        {externalReview.review_bundle_sha256 && (
                          <div>
                            <span>Review bundle SHA-256</span>
                            <code>{externalReview.review_bundle_sha256}</code>
                          </div>
                        )}
                        {externalReview.attestation_sha256 && (
                          <div>
                            <span>Attestation SHA-256</span>
                            <code>{externalReview.attestation_sha256}</code>
                          </div>
                        )}
                        {externalReview.certification_proposal_sha256 && (
                          <div>
                            <span>Proposal SHA-256</span>
                            <code>{externalReview.certification_proposal_sha256}</code>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="chakra-review-identity-warning">
                      <ShieldAlert size={15} />
                      <div>
                        <strong>Reviewer identity not authenticated</strong>
                        <span>
                          The app verifies record structure and exact decision
                          coverage only. A human must independently verify the
                          reviewer and decide whether certification is justified.
                        </span>
                      </div>
                    </div>

                    {externalReview.certification_proposal && (
                      <div className="chakra-review-bundle-ready">
                        <div>
                          <strong>Ready for human certification decision</strong>
                          <span>
                            This reproducible proposal is an input to a separate
                            human-controlled decision. Source certification,
                            registry writes, timing phase, and execution remain blocked.
                          </span>
                        </div>
                        <div className="chakra-review-bundle-actions">
                          <button
                            className="secondary-command"
                            onClick={downloadTimingCertificationProposal}
                          >
                            <Download size={13} />
                            Download proposal
                          </button>
                          <button
                            className="primary-command"
                            onClick={continueToTimingSignedReview}
                          >
                            <BadgeCheck size={13} />
                            Continue to signature
                          </button>
                        </div>
                      </div>
                    )}

                    <div className="chakra-timing-gate-list">
                      {externalReview.validation_gates.map((item) => (
                        <div
                          key={item.gate_id}
                          className={`is-${item.state.toLowerCase()}`}
                        >
                          <span>{item.state}</span>
                          <strong>{item.label}</strong>
                          <p>{item.detail}</p>
                          {item.affected_ids.length > 0 && (
                            <code>{item.affected_ids.join(' | ')}</code>
                          )}
                        </div>
                      ))}
                    </div>

                    {externalReview.missing_requirements.length > 0 && (
                      <div className="chakra-blocked-capabilities">
                        <strong>Missing review requirements</strong>
                        <div>
                          {externalReview.missing_requirements.map((item) => (
                            <span key={item}>{displayToken(item)}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="chakra-blocked-capabilities">
                      <strong>Still blocked after S3</strong>
                      <div>
                        {externalReview.guardrails.blocked_capabilities.map(
                          (item) => <span key={item}>{displayToken(item)}</span>,
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            {activeTab === 'SIGNED_REVIEW' && (
              <div className="chakra-timing-gate-workspace">
                <p className="chakra-timing-gate-warning">
                  S4 verifies an Ed25519 signature only against a server-owned,
                  human-curated reviewer-key registry. A passing signature does not
                  prove independence or doctrinal truth, certify the source, register
                  a timing profile, or unlock inference and trading.
                </p>

                <div className="chakra-timing-gate-toolbar">
                  <input
                    ref={reviewBundleImportInputRef}
                    className="chakra-package-file"
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) => (
                      void importTimingReviewBundle(event.target.files?.[0])
                    )}
                  />
                  <input
                    ref={reviewAttestationImportInputRef}
                    className="chakra-package-file"
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) => (
                      void importTimingReviewAttestation(event.target.files?.[0])
                    )}
                  />
                  <input
                    ref={signedReviewImportInputRef}
                    className="chakra-package-file"
                    type="file"
                    accept="application/json,.json"
                    onChange={(event) => (
                      void importTimingSignedReview(event.target.files?.[0])
                    )}
                  />
                  <button
                    className="primary-command"
                    onClick={() => void evaluateTimingSignedReview()}
                    disabled={
                      signedReviewBusy || !reviewBundle || !reviewAttestation
                    }
                    title="Re-run S3, resolve the reviewer key from the server registry, and verify the signature"
                  >
                    <BadgeCheck size={13} />
                    Verify signature
                  </button>
                  <button
                    className="secondary-command"
                    onClick={() => reviewBundleImportInputRef.current?.click()}
                    disabled={signedReviewBusy}
                  >
                    <Upload size={13} />
                    Load bundle
                  </button>
                  <button
                    className="secondary-command"
                    onClick={() => reviewAttestationImportInputRef.current?.click()}
                    disabled={signedReviewBusy}
                  >
                    <Upload size={13} />
                    Load attestation
                  </button>
                  <button
                    className="secondary-command"
                    onClick={() => signedReviewImportInputRef.current?.click()}
                    disabled={signedReviewBusy}
                  >
                    <Upload size={13} />
                    Load signature
                  </button>
                  <button
                    className="secondary-command"
                    onClick={downloadTimingSignedReviewTemplate}
                    disabled={!signedReview?.signed_review_template}
                    title="Download the exact S3-bound envelope an external reviewer must sign"
                  >
                    <Download size={13} />
                    Signature template
                  </button>
                  <button
                    className="secondary-command"
                    onClick={clearTimingSignedReview}
                    disabled={
                      signedReviewBusy
                      || (!signedReviewEnvelope && !signedReview)
                    }
                  >
                    <Trash2 size={13} />
                    Clear signature
                  </button>
                </div>

                <section className="chakra-source-verification-section">
                  <header>
                    <div>
                      <strong>Signed-review files</strong>
                      <span>
                        The public key is resolved only from the server registry
                      </span>
                    </div>
                    <em>
                      {[
                        reviewBundle,
                        reviewAttestation,
                        signedReviewEnvelope,
                      ].filter(Boolean).length}
                      /3 loaded
                    </em>
                  </header>
                  <div className="chakra-external-review-inputs is-three">
                    <div>
                      <span className={reviewBundle ? 'is-loaded' : 'is-missing'}>
                        {reviewBundle ? 'LOADED' : 'MISSING'}
                      </span>
                      <strong>Reviewer bundle</strong>
                      <span>{reviewBundleLabel || 'No bundle selected'}</span>
                      <small>Frozen S2 evidence and identity</small>
                    </div>
                    <div>
                      <span className={
                        reviewAttestation ? 'is-loaded' : 'is-missing'
                      }>
                        {reviewAttestation ? 'LOADED' : 'MISSING'}
                      </span>
                      <strong>Completed attestation</strong>
                      <span>
                        {reviewAttestationLabel || 'No attestation selected'}
                      </span>
                      <small>Approved exact source decisions</small>
                    </div>
                    <div>
                      <span className={
                        signedReviewEnvelope ? 'is-loaded' : 'is-missing'
                      }>
                        {signedReviewEnvelope ? 'LOADED' : 'MISSING'}
                      </span>
                      <strong>Signed envelope</strong>
                      <span>{signedReviewLabel || 'No signature selected'}</span>
                      <small>No client public key is accepted</small>
                    </div>
                  </div>
                </section>

                {signedReviewBusy && (
                  <div className="chakra-audit-empty is-inline">
                    <RefreshCw size={21} className="is-spinning" />
                    <strong>Checking the trusted reviewer signature</strong>
                    <span>No certification or registry write is performed.</span>
                  </div>
                )}

                {!signedReviewBusy && signedReview && (
                  <>
                    <div className="chakra-timing-gate-summary is-source-verification">
                      <div>
                        <span>Review status</span>
                        <strong>{displayToken(signedReview.review_status)}</strong>
                        <em>S4 signature result</em>
                      </div>
                      <div>
                        <span>S3 evidence</span>
                        <strong>{signedReview.s3_ready ? 'PASS' : 'NOT READY'}</strong>
                        <em>bundle and attestation rerun</em>
                      </div>
                      <div>
                        <span>Trust registry</span>
                        <strong>
                          {signedReview.reviewer_registry_valid
                            ? 'VALID'
                            : 'INVALID'}
                        </strong>
                        <em>server-owned, read-only</em>
                      </div>
                      <div>
                        <span>Reviewer key</span>
                        <strong>
                          {signedReview.reviewer_key_trusted
                            ? 'TRUSTED'
                            : 'UNTRUSTED'}
                        </strong>
                        <em>valid, scoped, non-revoked</em>
                      </div>
                      <div>
                        <span>Ed25519 signature</span>
                        <strong>
                          {signedReview.review_signature_valid
                            ? 'VERIFIED'
                            : 'NOT VERIFIED'}
                        </strong>
                        <em>exact canonical envelope</em>
                      </div>
                      <div>
                        <span>Identity binding</span>
                        <strong>
                          {signedReview.reviewer_identity_authenticated_to_registry
                            ? 'AUTHENTICATED'
                            : 'NOT AUTHENTICATED'}
                        </strong>
                        <em>registered key identity</em>
                      </div>
                      <div>
                        <span>Independence</span>
                        <strong>
                          {signedReview
                            .reviewer_independence_administratively_vetted
                            ? 'ADMIN VETTED'
                            : 'NOT VETTED'}
                        </strong>
                        <em>not cryptographic proof</em>
                      </div>
                      <div>
                        <span>Execution</span>
                        <strong>LOCKED</strong>
                        <em>zero directional contribution</em>
                      </div>
                    </div>

                    {(signedReview.review_bundle_sha256
                      || signedReview.attestation_sha256
                      || signedReview.certification_proposal_sha256
                      || signedReview.signed_review_sha256) && (
                      <div className="chakra-source-packet-identities">
                        {signedReview.review_bundle_sha256 && (
                          <div>
                            <span>Review bundle SHA-256</span>
                            <code>{signedReview.review_bundle_sha256}</code>
                          </div>
                        )}
                        {signedReview.attestation_sha256 && (
                          <div>
                            <span>Attestation SHA-256</span>
                            <code>{signedReview.attestation_sha256}</code>
                          </div>
                        )}
                        {signedReview.certification_proposal_sha256 && (
                          <div>
                            <span>Proposal SHA-256</span>
                            <code>
                              {signedReview.certification_proposal_sha256}
                            </code>
                          </div>
                        )}
                        {signedReview.signed_review_sha256 && (
                          <div>
                            <span>Signed envelope SHA-256</span>
                            <code>{signedReview.signed_review_sha256}</code>
                          </div>
                        )}
                      </div>
                    )}

                    <div className="chakra-review-identity-warning">
                      <ShieldAlert size={15} />
                      <div>
                        <strong>
                          Signature identity is narrower than human independence
                        </strong>
                        <span>
                          Ed25519 can prove that the registered key signed the exact
                          evidence. It cannot prove who physically controlled the key,
                          whether the reviewer was genuinely independent, or whether
                          the doctrinal conclusion is correct.
                        </span>
                      </div>
                    </div>

                    {signedReview.ready_for_manual_source_certification && (
                      <div className="chakra-review-bundle-ready">
                        <div>
                          <strong>Ready for manual source-certification review</strong>
                          <span>
                            The signature and trusted-key scope passed. A separate
                            human-reviewed Git change is still required for any source
                            certificate or timing-profile registry entry.
                          </span>
                        </div>
                      </div>
                    )}

                    <div className="chakra-timing-gate-list">
                      {signedReview.validation_gates.map((item) => (
                        <div
                          key={item.gate_id}
                          className={`is-${item.state.toLowerCase()}`}
                        >
                          <span>{item.state}</span>
                          <strong>{item.label}</strong>
                          <p>{item.detail}</p>
                        </div>
                      ))}
                    </div>

                    {signedReview.missing_requirements.length > 0 && (
                      <div className="chakra-blocked-capabilities">
                        <strong>Missing signature requirements</strong>
                        <div>
                          {signedReview.missing_requirements.map((item) => (
                            <span key={item}>{displayToken(item)}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="chakra-blocked-capabilities">
                      <strong>Still blocked after S4</strong>
                      <div>
                        {signedReview.guardrails.blocked_capabilities.map(
                          (item) => <span key={item}>{displayToken(item)}</span>,
                        )}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}

            {activeTab === 'COMPARE' && (
              !packageBuild ? (
                <div className="chakra-audit-empty is-inline">
                  <Columns3 size={21} />
                  <strong>Comparison package not built</strong>
                  <span>Select a baseline and at least one comparison interval.</span>
                </div>
              ) : (
                <div className="chakra-comparison-list">
                  <p className="chakra-comparison-warning">
                    Candidate minus baseline. These are descriptive ledger differences,
                    not market direction, confidence, performance, or trade signals.
                  </p>
                  {packageComparisons.map((comparison) => (
                    <section key={comparison.comparison_id} className="chakra-comparison-section">
                      <header>
                        <div>
                          <strong>{shortId(comparison.comparison_id)}</strong>
                          <span>
                            {shortId(comparison.baseline_interval_id)}
                            {' to '}
                            {shortId(comparison.comparison_interval_id)}
                          </span>
                        </div>
                        <div className="chakra-comparison-metrics">
                          <span>Net {signedUnits(comparison.total_delta.net_guidance_units)}</span>
                          <span>Gross {signedUnits(comparison.total_delta.gross_activation_units)}</span>
                          <span>Coverage {signedUnits(comparison.total_delta.scoring_coverage_ratio * 100)}%</span>
                          <span>Unknown {comparison.total_delta.unknown_contribution_count >= 0 ? '+' : ''}{comparison.total_delta.unknown_contribution_count}</span>
                        </div>
                      </header>
                      <div className="chakra-audit-table is-comparison">
                        <div className="chakra-audit-table-head">
                          <span>Axis</span><span>Key</span><span>Baseline</span>
                          <span>Comparison</span><span>Net delta</span>
                          <span>Gross delta</span><span>Unknown delta</span>
                        </div>
                        {comparison.cell_comparisons.map((item) => (
                          <button
                            key={`${comparison.comparison_id}-${item.axis}-${item.key}`}
                            onClick={() => {
                              openLedgerCell(
                                item.comparison_cell_id ?? item.baseline_cell_id ?? '',
                              )
                            }}
                          >
                            <strong>{displayToken(item.axis)}</strong>
                            <span>{displayToken(item.key)}</span>
                            <span>{item.baseline_cell_id ? units(item.baseline_summary?.net_guidance_units ?? 0) : 'Absent'}</span>
                            <span>{item.comparison_cell_id ? units(item.comparison_summary?.net_guidance_units ?? 0) : 'Absent'}</span>
                            <span>{signedUnits(item.delta.net_guidance_units)}</span>
                            <span>{signedUnits(item.delta.gross_activation_units)}</span>
                            <span>{item.delta.unknown_contribution_count >= 0 ? '+' : ''}{item.delta.unknown_contribution_count}</span>
                          </button>
                        ))}
                      </div>
                    </section>
                  ))}
                </div>
              )
            )}

            {activeTab === 'PACKAGE' && (
              !packageBuild ? (
                <div className="chakra-audit-empty is-inline">
                  <PackageCheck size={21} />
                  <strong>No sealed package</strong>
                  <span>Build or import a P4 package to inspect and verify it.</span>
                </div>
              ) : (
                <div className="chakra-package-view">
                  <header className="chakra-package-toolbar">
                    <div>
                      <strong>Sealed audit package</strong>
                      <span>{shortId(packageBuild.package.package_id)}</span>
                    </div>
                    <div>
                      <button
                        className="icon-button"
                        title="Download sealed JSON"
                        aria-label="Download sealed JSON"
                        onClick={() => downloadText(
                          JSON.stringify(packageBuild.package, null, 2),
                          'application/json',
                          `sbc-audit-${packageBuild.package.package_id.slice(0, 12)}.json`,
                        )}
                      >
                        <Download size={13} />
                      </button>
                      <button
                        className="icon-button"
                        title="Download readable HTML report"
                        aria-label="Download readable HTML report"
                        disabled={!packageBuild.htmlReport}
                        onClick={() => downloadText(
                          packageBuild.htmlReport,
                          'text/html',
                          `sbc-audit-${packageBuild.package.package_id.slice(0, 12)}.html`,
                        )}
                      >
                        <FileCheck2 size={13} />
                      </button>
                      <button
                        className="secondary-command"
                        disabled={packageBusy}
                        onClick={() => void verifyPackage()}
                      >
                        <RefreshCw size={12} />
                        Replay verify
                      </button>
                    </div>
                  </header>

                  <dl className="chakra-package-meta">
                    <div><dt>Package</dt><dd>{packageBuild.package.package_id}</dd></div>
                    <div><dt>Source audit</dt><dd>{packageBuild.package.source_audit_id}</dd></div>
                    <div><dt>Projection</dt><dd>{packageBuild.package.source_projection_hash}</dd></div>
                    <div><dt>Replay recipe</dt><dd>{packageBuild.package.replay_recipe_hash}</dd></div>
                    <div><dt>Sealed UTC</dt><dd>{packageBuild.package.sealed_at_utc}</dd></div>
                  </dl>

                  {verification && (
                    <div className={`chakra-package-verification is-${verification.state.toLowerCase()}`}>
                      <span>{verification.state}</span>
                      <strong>
                        {verification.state === 'PASS'
                          ? 'Full Chakra to P1 to P2 to P3 to P4 replay matched'
                          : 'Replay verification failed'}
                      </strong>
                      {verification.errors.map((item) => <p key={item}>{item}</p>)}
                    </div>
                  )}

                  <div className="chakra-validation-list">
                    {packageBuild.package.validation_gates.map((item) => (
                      <div key={item.gate_id} className={`is-${item.state.toLowerCase()}`}>
                        <span>{item.state}</span>
                        <strong>{item.label}</strong>
                        <p>{item.detail}</p>
                      </div>
                    ))}
                  </div>

                  <section>
                    <div className="chakra-section-heading">
                      <strong>Manual research bookmarks</strong>
                      <span>{packageBuild.package.bookmarks.length}</span>
                    </div>
                    <div className="chakra-package-bookmarks">
                      {packageBuild.package.bookmarks.map((item) => (
                        <div key={item.bookmark_id}>
                          <span>{displayToken(item.target_type)}</span>
                          <strong>{item.label}</strong>
                          <p>{item.note}</p>
                          <code>{shortId(item.target_id)}</code>
                        </div>
                      ))}
                      {!packageBuild.package.bookmarks.length && (
                        <span className="chakra-muted-row">No manual bookmarks</span>
                      )}
                    </div>
                  </section>
                </div>
              )
            )}

            {activeTab === 'CATALOG' && (
              !catalogBuild ? (
                <div className="chakra-audit-empty is-inline">
                  <Archive size={21} />
                  <strong>Signed catalog not built</strong>
                  <span>
                    Add at least one replay-verified P4 package, then seal the catalog.
                  </span>
                </div>
              ) : (
                <div className="chakra-package-view">
                  <header className="chakra-package-toolbar">
                    <div>
                      <strong>Signed P5 audit catalog</strong>
                      <span>{shortId(catalogBuild.bundle.catalog.catalog_id)}</span>
                    </div>
                    <div>
                      <button
                        className="icon-button"
                        title="Download signed catalog bundle"
                        aria-label="Download signed catalog bundle"
                        onClick={() => downloadText(
                          JSON.stringify(catalogBuild.bundle, null, 2),
                          'application/json',
                          `sbc-catalog-${catalogBuild.bundle.catalog.catalog_id.slice(0, 12)}.json`,
                        )}
                      >
                        <Download size={13} />
                      </button>
                      <button
                        className="secondary-command"
                        disabled={catalogBusy}
                        onClick={() => void verifyCatalog(
                          catalogBuild.bundle,
                          false,
                        )}
                        title="Check hashes and Ed25519 signature without semantic replay"
                      >
                        <FileCheck2 size={12} />
                        Integrity
                      </button>
                      <button
                        className="secondary-command"
                        disabled={catalogBusy}
                        onClick={() => void verifyCatalog(
                          catalogBuild.bundle,
                          true,
                        )}
                        title="Recompute every embedded P4 package after integrity verification"
                      >
                        <RefreshCw size={12} />
                        Full replay
                      </button>
                    </div>
                  </header>

                  <p className="chakra-comparison-warning">
                    Catalog membership and the Ed25519 signature prove portable
                    integrity and local provenance only. Packages are not added,
                    averaged, voted, ranked, or converted into market direction.
                  </p>

                  <dl className="chakra-package-meta">
                    <div><dt>Catalog</dt><dd>{catalogBuild.bundle.catalog.catalog_id}</dd></div>
                    <div><dt>Public key</dt><dd>{catalogBuild.bundle.signature.key_id}</dd></div>
                    <div><dt>Algorithm</dt><dd>{catalogBuild.bundle.signature.algorithm}</dd></div>
                    <div><dt>Signed UTC</dt><dd>{catalogBuild.bundle.signature.signed_at_utc}</dd></div>
                    <div><dt>Packages</dt><dd>{catalogBuild.bundle.catalog.entries.length}</dd></div>
                  </dl>

                  {catalogVerification && (
                    <div className={`chakra-package-verification is-${catalogVerification.state.toLowerCase()}`}>
                      <span>{catalogVerification.state}</span>
                      <strong>
                        {catalogVerification.state === 'PASS'
                          ? `Signature and structure matched; semantic replay ${displayToken(catalogVerification.semantic_replay_state)}`
                          : 'Catalog verification failed'}
                      </strong>
                      {catalogVerification.errors.map((item) => <p key={item}>{item}</p>)}
                    </div>
                  )}

                  <div className="chakra-validation-list">
                    {catalogBuild.bundle.catalog.validation_gates.map((item) => (
                      <div key={item.gate_id} className={`is-${item.state.toLowerCase()}`}>
                        <span>{item.state}</span>
                        <strong>{item.label}</strong>
                        <p>{item.detail}</p>
                      </div>
                    ))}
                  </div>

                  <section>
                    <div className="chakra-section-heading">
                      <strong>Embedded replay-verified P4 packages</strong>
                      <span>{catalogBuild.bundle.catalog.entries.length}</span>
                    </div>
                    <div className="chakra-catalog-entries">
                      {catalogBuild.bundle.catalog.entries.map((item) => {
                        const replay = catalogVerification?.entry_verifications.find(
                          (entry) => entry.package_id === item.package_id,
                        )
                        return (
                          <div key={item.entry_id}>
                            <div>
                              <strong>{item.instrument_identity}</strong>
                              <span>{formatMoment(item.sealed_at_utc)}</span>
                            </div>
                            <code>{shortId(item.package_id)}</code>
                            <span>
                              Structure {replay?.structural_integrity ?? 'PASS'}
                              {' | '}
                              Replay {replay?.semantic_replay ?? item.p4_replay_state}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  </section>
                </div>
              )
            )}
          </div>
        )}
      </section>

      <aside className="chakra-audit-inspector">
        <section>
          <div className="chakra-section-heading">
            <strong>Linked selection</strong>
            <span>{audit ? shortId(audit.audit_view_id) : '-'}</span>
          </div>
          <dl>
            <div><dt>Interval</dt><dd>{shortId(selectedInterval?.interval_id)}</dd></div>
            <div><dt>Cell</dt><dd>{shortId(selectedCell?.cell_id)}</dd></div>
            <div><dt>Cluster</dt><dd>{shortId(selectedCluster?.cluster_id)}</dd></div>
            <div><dt>Cutoff</dt><dd>{selectedInterval ? formatMoment(selectedInterval.evidence_cutoff_utc) : '-'}</dd></div>
          </dl>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>Primary evidence</strong>
            <span>{selectedCluster?.evidence_kind ?? '-'}</span>
          </div>
          <dl>
            <div><dt>Actor</dt><dd>{selectedCluster?.actor_identity ?? 'Unavailable'}</dd></div>
            <div><dt>Ray</dt><dd>{displayToken(selectedCluster?.vedha_direction)}</dd></div>
            <div><dt>Target</dt><dd>{displayToken(selectedCluster?.target_value)}</dd></div>
            <div><dt>Nature</dt><dd>{displayToken(selectedCluster?.nature)}</dd></div>
            <div><dt>Units</dt><dd>{selectedCluster?.signed_guidance_units == null ? 'Unknown' : units(selectedCluster.signed_guidance_units)}</dd></div>
          </dl>
          {selectedCluster?.unknown_reason && (
            <p className="chakra-audit-unknown">{selectedCluster.unknown_reason}</p>
          )}
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>Source lineage</strong>
            <span>{selectedLineage?.status ?? '-'}</span>
          </div>
          <dl>
            <div><dt>Lineage</dt><dd>{shortId(selectedLineage?.source_lineage_id)}</dd></div>
            <div><dt>Foundation</dt><dd>{selectedLineage?.foundation_profile_id ?? '-'}</dd></div>
            <div><dt>Grid</dt><dd>{selectedLineage?.grid_profile_id ?? '-'}</dd></div>
            <div><dt>Vedha</dt><dd>{selectedLineage?.vedha_profile_id ?? '-'}</dd></div>
          </dl>
          <div className="chakra-source-tags">
            {selectedLineage?.source_ids.map((item) => <span key={item}>{item}</span>)}
          </div>
        </section>

        <section>
          <div className="chakra-section-heading">
            <strong>Research bookmark</strong>
            <span>Not ML evidence</span>
          </div>
          <div className="chakra-bookmark-editor">
            <select
              value={bookmarkTargetType}
              onChange={(event) => setBookmarkTargetType(
                event.target.value as ChakraAuditBookmarkTarget,
              )}
              disabled={!audit}
            >
              <option value="AUDIT">Whole audit</option>
              <option value="INTERVAL">Selected interval</option>
              <option value="CELL">Selected ledger cell</option>
              <option value="CLUSTER">Selected evidence cluster</option>
            </select>
            <input
              value={bookmarkLabel}
              onChange={(event) => setBookmarkLabel(event.target.value)}
              placeholder="Bookmark label"
              disabled={!bookmarkTargetId}
            />
            <textarea
              value={bookmarkNote}
              onChange={(event) => setBookmarkNote(event.target.value)}
              placeholder="Manual observation only"
              disabled={!bookmarkTargetId}
            />
            <button
              className="secondary-command"
              onClick={addBookmark}
              disabled={
                !bookmarkTargetId
                || !bookmarkLabel.trim()
                || !bookmarkNote.trim()
              }
            >
              <BookmarkPlus size={12} />
              Add bookmark
            </button>
          </div>
          <div className="chakra-bookmark-drafts">
            {bookmarks.map((item, index) => (
              <div key={`${item.createdAt}-${index}`}>
                <button
                  className="icon-button"
                  aria-label={`Remove bookmark ${index + 1}`}
                  title="Remove bookmark"
                  onClick={() => removeBookmark(index)}
                >
                  <Trash2 size={11} />
                </button>
                <strong>{item.label}</strong>
                <span>{displayToken(item.targetType)} · {shortId(item.targetId)}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="chakra-audit-locks">
          <span>Read only</span>
          <span>No phase</span>
          <span>No direction</span>
          <span>Bookmarks not ML</span>
          <span>No execution</span>
        </section>
      </aside>
    </div>
  )
}
