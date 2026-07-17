import {
  AlertTriangle,
  CircleDot,
  RefreshCw,
  ShieldCheck,
} from 'lucide-react'
import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
} from 'react'
import { fetchChakraLabSnapshot } from '../api'
import type {
  ChakraDignityState,
  ChakraGridCell,
  ChakraLabRequest,
  ChakraLabSnapshot,
  ChakraMotionClass,
} from '../types'


const BODIES = [
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
const FIXED_BODIES = new Set(['SUN', 'MOON', 'RAHU', 'KETU'])

type Body = (typeof BODIES)[number]
type ActorState = {
  selected: boolean
  motionClass: '' | ChakraMotionClass
  dignity: ChakraDignityState
}

function initialActors(): Record<Body, ActorState> {
  return Object.fromEntries(
    BODIES.map((body) => [
      body,
      {
        selected: true,
        motionClass: '',
        dignity: 'ORDINARY',
      },
    ]),
  ) as Record<Body, ActorState>
}

function currentIstInput(): string {
  return new Date(Date.now() + 330 * 60 * 1000).toISOString().slice(0, 16)
}

function offsetIst(localValue: string): string {
  const seconds = localValue.length === 16 ? ':00' : ''
  return `${localValue}${seconds}+05:30`
}

function splitValues(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim().toUpperCase())
    .filter(Boolean)
}

function displayToken(value: string): string {
  return value.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function cellKey(cell: ChakraGridCell): string {
  return `${cell.row}:${cell.column}`
}

type Props = {
  defaultLatitude: number
  defaultLongitude: number
}

export function ChakraLabWorkspace({
  defaultLatitude,
  defaultLongitude,
}: Props) {
  const [atLocal, setAtLocal] = useState(currentIstInput)
  const [latitude, setLatitude] = useState(defaultLatitude)
  const [longitude, setLongitude] = useState(defaultLongitude)
  const [altitudeM, setAltitudeM] = useState(0)
  const [vowels, setVowels] = useState('')
  const [nameInitials, setNameInitials] = useState('')
  const [actors, setActors] = useState(initialActors)
  const [snapshot, setSnapshot] = useState<ChakraLabSnapshot | null>(null)
  const [selectedCell, setSelectedCell] = useState('5:5')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const initialRun = useRef(false)

  const request = useMemo<ChakraLabRequest>(() => ({
    at: offsetIst(atLocal),
    timezone: 'Asia/Kolkata',
    latitude,
    longitude,
    altitudeM,
    bodies: [...BODIES],
    actors: BODIES
      .filter((body) => actors[body].selected)
      .map((body) => ({
        body,
        ...(actors[body].motionClass
          ? { motionClass: actors[body].motionClass as ChakraMotionClass }
          : {}),
        dignity: actors[body].dignity,
      })),
    foundationProfileId: 'sbc_raman_foundation_v1',
    gridProfileId: 'sbc_81_rotation_normalized_partial_v1',
    vedhaProfileId: 'phaladeepika_editor_vedha_guidance_v1',
    vowels: splitValues(vowels),
    nameInitials: splitValues(nameInitials),
  }), [
    actors,
    altitudeM,
    atLocal,
    latitude,
    longitude,
    nameInitials,
    vowels,
  ])

  const loadSnapshot = useCallback(async () => {
    setBusy(true)
    setError('')
    try {
      setSnapshot(await fetchChakraLabSnapshot(request))
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : String(caught))
    } finally {
      setBusy(false)
    }
  }, [request])

  useEffect(() => {
    if (initialRun.current) return
    initialRun.current = true
    void loadSnapshot()
  }, [loadSnapshot])

  const contextKeys = useMemo(() => new Set(
    snapshot?.target_context.flatMap((layer) => (
      layer.values.map((value) => `${layer.layer}:${value}`)
    )) ?? [],
  ), [snapshot])
  const targetCoordinates = useMemo(() => new Set(
    snapshot?.guidance?.actor_resolutions.flatMap((actor) => (
      actor.targets.map((target) => `${target.row}:${target.column}`)
    )) ?? [],
  ), [snapshot])
  const hitCoordinates = useMemo(() => new Set(
    snapshot?.guidance?.contributions.map((item) => (
      `${item.target.row}:${item.target.column}`
    )) ?? [],
  ), [snapshot])
  const selected = snapshot?.grid.cells.find((cell) => cellKey(cell) === selectedCell)
  const guidance = snapshot?.guidance
  const resolvedByBody = new Map(
    guidance?.actor_resolutions.map((actor) => [actor.body, actor]) ?? [],
  )

  const updateActor = (body: Body, patch: Partial<ActorState>) => {
    setActors((current) => ({
      ...current,
      [body]: { ...current[body], ...patch },
    }))
  }

  return (
    <section className="chakra-lab-workspace">
      <div className="chakra-command-strip">
        <div className="chakra-title-block">
          <CircleDot size={17} />
          <div>
            <strong>Sarvatobhadra Chakra</strong>
            <span>Raman sidereal · current-moment context</span>
          </div>
        </div>
        <span className="chakra-contract-chip"><ShieldCheck size={12} /> Read only</span>
        <span className="chakra-contract-chip">No lookahead</span>
        <span className="chakra-contract-chip is-warning">Not financially validated</span>
        <div className="chakra-command-spacer" />
        {snapshot && (
          <span className="chakra-snapshot-id" title={snapshot.snapshot_id}>
            {snapshot.snapshot_id.slice(0, 12)}
          </span>
        )}
        <button
          className="secondary-command chakra-run-button"
          onClick={() => void loadSnapshot()}
          disabled={busy}
        >
          <RefreshCw size={14} className={busy ? 'is-spinning' : ''} />
          {busy ? 'Calculating' : 'Refresh snapshot'}
        </button>
      </div>

      <div className="chakra-lab-body">
        <aside className="chakra-settings-panel">
          <section>
            <div className="chakra-section-heading">
              <strong>Moment</strong>
              <span>IST</span>
            </div>
            <label>
              Timestamp
              <input
                type="datetime-local"
                value={atLocal}
                onChange={(event) => setAtLocal(event.target.value)}
              />
            </label>
            <div className="chakra-coordinate-grid">
              <label>
                Latitude
                <input
                  type="number"
                  step="0.0001"
                  value={latitude}
                  onChange={(event) => setLatitude(Number(event.target.value))}
                />
              </label>
              <label>
                Longitude
                <input
                  type="number"
                  step="0.0001"
                  value={longitude}
                  onChange={(event) => setLongitude(Number(event.target.value))}
                />
              </label>
            </div>
            <label>
              Altitude (m)
              <input
                type="number"
                step="1"
                value={altitudeM}
                onChange={(event) => setAltitudeM(Number(event.target.value))}
              />
            </label>
          </section>

          <section>
            <div className="chakra-section-heading">
              <strong>Context</strong>
              <span>Optional</span>
            </div>
            <label>
              Vowel keys
              <input
                value={vowels}
                placeholder="A, AA"
                onChange={(event) => setVowels(event.target.value)}
              />
            </label>
            <label>
              Name-initial keys
              <input
                value={nameInitials}
                placeholder="KA, RA"
                onChange={(event) => setNameInitials(event.target.value)}
              />
            </label>
          </section>

          <section className="chakra-actors-section">
            <div className="chakra-section-heading">
              <strong>Vedha actors</strong>
              <span>Explicit motion</span>
            </div>
            <div className="chakra-actor-header">
              <span />
              <span>Body</span>
              <span>Motion</span>
              <span>Dignity</span>
            </div>
            {BODIES.map((body) => (
              <div className="chakra-actor-row" key={body}>
                <input
                  type="checkbox"
                  checked={actors[body].selected}
                  onChange={(event) => updateActor(body, { selected: event.target.checked })}
                  aria-label={`Include ${body}`}
                />
                <strong>{body}</strong>
                {FIXED_BODIES.has(body) ? (
                  <span className="chakra-fixed-motion">Fixed</span>
                ) : (
                  <select
                    value={actors[body].motionClass}
                    onChange={(event) => updateActor(body, {
                      motionClass: event.target.value as ActorState['motionClass'],
                    })}
                    aria-label={`${body} motion`}
                  >
                    <option value="">Required</option>
                    <option value="DIRECT_SWIFT">Direct / swift</option>
                    <option value="MEAN">Mean</option>
                    <option value="RETROGRADE">Retrograde</option>
                  </select>
                )}
                <select
                  value={actors[body].dignity}
                  onChange={(event) => updateActor(body, {
                    dignity: event.target.value as ChakraDignityState,
                  })}
                  aria-label={`${body} dignity`}
                >
                  <option value="ORDINARY">Ordinary</option>
                  <option value="EXALTED">Exalted</option>
                  <option value="DEBILITATED">Debilitated</option>
                </select>
              </div>
            ))}
          </section>
        </aside>

        <section className="chakra-board-panel">
          {error && (
            <div className="chakra-error-band">
              <AlertTriangle size={14} />
              <span>{error}</span>
            </div>
          )}
          {snapshot ? (
            <>
              <div className="chakra-board-context">
                <div>
                  <strong>{new Date(snapshot.requested_at_local).toLocaleString()}</strong>
                  <span>{snapshot.foundation_snapshot.astronomy_contract}</span>
                </div>
                <div>
                  <strong>{snapshot.foundation_snapshot.panchanga.tithi_name}</strong>
                  <span>
                    {snapshot.foundation_snapshot.panchanga.paksha} · {snapshot.foundation_snapshot.panchanga.vara.weekday}
                  </span>
                </div>
                <div className="chakra-legend">
                  <span><i className="is-context" /> Context</span>
                  <span><i className="is-target" /> Ray</span>
                  <span><i className="is-hit" /> Matched</span>
                </div>
              </div>
              <div className="chakra-grid-viewport">
                <div className="chakra-grid" style={{
                  '--chakra-columns': snapshot.grid.columns,
                  '--chakra-rows': snapshot.grid.rows,
                } as CSSProperties}>
                  {snapshot.grid.cells.map((cell) => {
                    const key = cellKey(cell)
                    const isContext = cell.entries.some((entry) => (
                      contextKeys.has(`${entry.layer}:${entry.value}`)
                    ))
                    const primary = cell.entries.find((entry) => entry.layer === 'NAKSHATRA')
                      ?? cell.entries.find((entry) => entry.layer === 'RASHI')
                      ?? cell.entries[0]
                    return (
                      <button
                        key={key}
                        className={[
                          'chakra-cell',
                          isContext ? 'is-context' : '',
                          targetCoordinates.has(key) ? 'is-target' : '',
                          hitCoordinates.has(key) ? 'is-hit' : '',
                          selectedCell === key ? 'is-selected' : '',
                        ].filter(Boolean).join(' ')}
                        onClick={() => setSelectedCell(key)}
                        title={cell.entries.map((entry) => `${entry.layer}: ${entry.value}`).join('\n')}
                      >
                        <small>{cell.row},{cell.column}</small>
                        {primary ? <strong>{displayToken(primary.value)}</strong> : <strong>·</strong>}
                        <em>{cell.entries.map((entry) => entry.layer.slice(0, 3)).join(' · ')}</em>
                      </button>
                    )
                  })}
                </div>
              </div>
            </>
          ) : (
            <div className="chakra-empty-state">
              <CircleDot size={24} />
              <strong>{busy ? 'Calculating snapshot' : 'Snapshot unavailable'}</strong>
            </div>
          )}
        </section>

        <aside className="chakra-evidence-panel">
          <section className="chakra-score-section">
            <div className="chakra-section-heading">
              <strong>Guidance ledger</strong>
              <span>{guidance?.financial_validation_status ?? 'PENDING'}</span>
            </div>
            <div className="chakra-score-line">
              <strong>
                {guidance ? `${(guidance.normalized_guidance_score * 100).toFixed(1)}%` : '—'}
              </strong>
              <span>{guidance ? displayToken(guidance.guidance_band) : 'No resolved actors'}</span>
            </div>
            <div className="chakra-score-metrics">
              <div><span>Favorable</span><strong>{guidance?.favorable_guidance_units.toFixed(1) ?? '—'}</strong></div>
              <div><span>Adverse</span><strong>{guidance?.adverse_guidance_units.toFixed(1) ?? '—'}</strong></div>
              <div><span>Net</span><strong>{guidance?.net_guidance_units.toFixed(1) ?? '—'}</strong></div>
              <div><span>Coverage</span><strong>{guidance ? `${(guidance.scoring_coverage_ratio * 100).toFixed(0)}%` : '—'}</strong></div>
            </div>
          </section>

          <section>
            <div className="chakra-section-heading">
              <strong>Actor evidence</strong>
              <span>{snapshot?.actor_readiness.filter((item) => item.status === 'READY').length ?? 0} ready</span>
            </div>
            <div className="chakra-evidence-list">
              {snapshot?.actor_readiness.filter((item) => item.requested).map((item) => {
                const resolution = resolvedByBody.get(item.body)
                return (
                  <div className={`chakra-evidence-row is-${item.status.toLowerCase()}`} key={item.body}>
                    <strong>{item.body}</strong>
                    <span>{displayToken(item.source_nakshatra)}</span>
                    <span>{resolution?.direction ?? displayToken(item.status)}</span>
                    <em>{resolution?.nature ?? item.motion_class ?? '—'}</em>
                  </div>
                )
              })}
            </div>
          </section>

          <section>
            <div className="chakra-section-heading">
              <strong>Matched cells</strong>
              <span>{guidance?.matched_target_count ?? 0}</span>
            </div>
            <div className="chakra-contribution-list">
              {guidance?.contributions.length ? guidance.contributions.map((item, index) => (
                <button
                  key={`${item.body}-${item.target.row}-${item.target.column}-${index}`}
                  onClick={() => setSelectedCell(`${item.target.row}:${item.target.column}`)}
                >
                  <strong>{item.body}</strong>
                  <span>{item.target.layer}: {displayToken(item.target.value)}</span>
                  <em>{item.signed_guidance_units?.toFixed(1) ?? 'Unresolved'}</em>
                </button>
              )) : <span className="chakra-muted-row">No matched target cells</span>}
            </div>
          </section>

          <section>
            <div className="chakra-section-heading">
              <strong>Cell inspector</strong>
              <span>{selectedCell}</span>
            </div>
            <div className="chakra-cell-evidence">
              {selected?.entries.length ? selected.entries.map((entry) => (
                <div key={`${entry.layer}-${entry.value}`}>
                  <span>{displayToken(entry.layer)}</span>
                  <strong>{displayToken(entry.value)}</strong>
                </div>
              )) : <span className="chakra-muted-row">No certified layer in this cell</span>}
            </div>
          </section>
        </aside>
      </div>
    </section>
  )
}
