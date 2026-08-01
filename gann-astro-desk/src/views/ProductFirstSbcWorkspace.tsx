import { CalendarClock, ChevronLeft, ChevronRight, CircleHelp, Grid3X3, Layers3, Orbit, ShieldCheck, SlidersHorizontal } from 'lucide-react'
import { useState, type CSSProperties } from 'react'
import type { ChakraFixedPhasorInterval, ChakraGridCell, ChakraLabSnapshot, ChartPayload, CurrencyPairEvidence } from '../types'

type Props = {
  chart?: ChartPayload | null
  snapshot: ChakraLabSnapshot | null
  selectedCell: string
  onSelectCell: (cell: string) => void
  onSelectMoment: (value: string) => void
  currencyPairEvidence?: CurrencyPairEvidence | null
  selectedAspectLabel?: string | null
  fixedPhasorInterval?: ChakraFixedPhasorInterval | null
  phasorBusy: boolean
  phasorError: string
  onLoadFixedPhasor: () => void
}

function display(value: string | null | undefined): string {
  if (!value) return 'Unavailable'
  return value.replaceAll('_', ' ').toLowerCase().replace(/\b\w/g, (letter) => letter.toUpperCase())
}

function cellKey(cell: ChakraGridCell): string {
  return `${cell.row}:${cell.column}`
}

function toIstInput(epochSeconds: number): string {
  return new Date((epochSeconds + 19_800) * 1000).toISOString().slice(0, 16)
}

function momentInput(snapshot: ChakraLabSnapshot | null): string {
  return snapshot?.requested_at_local.slice(0, 16) ?? ''
}

function compactAspectLabel(value: string): string {
  return value.replace('AVG(ALL)', 'AVG').replaceAll('|', ' / ')
}

export function ProductFirstSbcWorkspace({
  chart,
  snapshot,
  selectedCell,
  onSelectCell,
  onSelectMoment,
  currencyPairEvidence = null,
  selectedAspectLabel = null,
  fixedPhasorInterval = null,
  phasorBusy,
  phasorError,
  onLoadFixedPhasor,
}: Props) {
  const [sideView, setSideView] = useState<'TIME' | 'PROFILE' | null>(null)
  const [draftMoment, setDraftMoment] = useState('')
  const [wheelOpen, setWheelOpen] = useState(false)
  const [selectedVectorId, setSelectedVectorId] = useState('')
  const guidance = snapshot?.guidance ?? null
  const candles = chart?.candles.slice(-110) ?? []
  const firstTime = candles[0]?.time ?? 0
  const lastTime = candles.at(-1)?.time ?? firstTime + 1
  const rangeSeconds = Math.max(1, lastTime - firstTime)
  const highs = candles.map((candle) => candle.high)
  const lows = candles.map((candle) => candle.low)
  const low = lows.length ? Math.min(...lows) : 0
  const high = highs.length ? Math.max(...highs) : 1
  const priceSpan = Math.max(0.000001, high - low)
  const chartWidth = 1000
  const chartHeight = 440
  const selectedEpoch = snapshot ? Date.parse(snapshot.as_of_utc) / 1000 : lastTime
  const xFor = (epoch: number) => 28 + ((epoch - firstTime) / rangeSeconds) * 944
  const yFor = (price: number) => 28 + ((high - price) / priceSpan) * 360
  const candleWidth = Math.max(2, Math.min(11, 820 / Math.max(candles.length, 1)))
  const visibleAspects = (chart?.aspects ?? []).filter((aspect) => (
    aspect.end >= firstTime && aspect.start <= lastTime
  ))
  const selected = snapshot?.grid.cells.find((cell) => cellKey(cell) === selectedCell)
  const targetCells = new Set(guidance?.contributions.map((item) => (
    `${item.target.row}:${item.target.column}`
  )) ?? [])
  const contextCells = new Set(snapshot?.target_context.flatMap((layer) => (
    layer.values.map((value) => `${layer.layer}:${value}`)
  )) ?? [])
  const readiness = snapshot?.actor_readiness.filter((item) => item.requested) ?? []
  const selectedCandleIndex = candles.length
    ? candles.reduce((closest, candle, index) => (
      Math.abs(candle.time - selectedEpoch) < Math.abs(candles[closest].time - selectedEpoch) ? index : closest
    ), 0)
    : -1
  const unknownCount = readiness.filter((item) => item.status !== 'READY').length
    + (guidance?.contributions.filter((item) => item.signed_guidance_units == null).length ?? 0)
  const supportive = Math.abs(guidance?.favorable_guidance_units ?? 0)
  const obstructive = Math.abs(guidance?.adverse_guidance_units ?? 0)
  const gross = supportive + obstructive
  const conflict = guidance && supportive > 0 && obstructive > 0
    ? 'Mixed support and obstruction'
    : guidance?.adverse_guidance_units
      ? 'Obstruction only'
      : guidance?.favorable_guidance_units
        ? 'Support only'
        : 'No resolved contribution'
  const baseScore = currencyPairEvidence?.base.doctrineNetScore ?? currencyPairEvidence?.base.netScore ?? null
  const quoteScore = currencyPairEvidence?.quote.doctrineNetScore ?? currencyPairEvidence?.quote.netScore ?? null
  const pairScore = currencyPairEvidence?.pair.doctrineNetScore ?? currencyPairEvidence?.pair.netScore ?? null
  const commonMode = baseScore != null && quoteScore != null ? (baseScore + quoteScore) / 2 : null
  const pairConflict = currencyPairEvidence?.pair.doctrineConflictRatio ?? currencyPairEvidence?.pair.conflictRatio ?? null
  const plottedVectors = fixedPhasorInterval?.vectors.filter((vector) => vector.projection_status === 'PLOTTED') ?? []
  const unknownVectors = fixedPhasorInterval?.vectors.filter((vector) => vector.projection_status === 'UNKNOWN_NOT_PLOTTED') ?? []
  const maxVectorMagnitude = Math.max(1, ...plottedVectors.map((vector) => vector.magnitude_units ?? 0))
  const selectedVector = plottedVectors.find((vector) => vector.vector_id === selectedVectorId) ?? plottedVectors[0] ?? null

  return (
    <section className={`product-first-sbc${sideView || currencyPairEvidence || wheelOpen ? ' has-product-first-panel' : ''}`} aria-label="Integrated Sarvatobhadra Chakra workspace">
      <header className="product-first-sbc-summary">
        <div className="product-first-summary-title">
          <Layers3 size={16} />
          <div>
            <strong>Integrated SBC workspace</strong>
            <span>{chart ? `${chart.symbol} ${chart.timeframe} market context` : 'No market context loaded'}</span>
          </div>
        </div>
        <div className="product-first-metric">
          <span>Supportive</span>
          <strong>{guidance ? supportive.toFixed(1) : 'Unknown'}</strong>
        </div>
        <div className="product-first-metric is-adverse">
          <span>Obstructive</span>
          <strong>{guidance ? obstructive.toFixed(1) : 'Unknown'}</strong>
        </div>
        <div className="product-first-metric">
          <span>Gross activity</span>
          <strong>{guidance ? gross.toFixed(1) : 'Unknown'}</strong>
        </div>
        <div className="product-first-metric">
          <span>Conflict</span>
          <strong>{conflict}</strong>
        </div>
        <div className="product-first-metric">
          <span>Coverage / unknown</span>
          <strong>{guidance ? `${Math.round(guidance.scoring_coverage_ratio * 100)}% / ${unknownCount}` : 'Unavailable'}</strong>
        </div>
        <span className="product-first-lock"><ShieldCheck size={12} /> Read-only experimental</span>
        <div className="product-first-view-controls" aria-label="Workspace view controls">
          <button
            className={sideView === 'TIME' ? 'is-active' : ''}
            onClick={() => {
              setDraftMoment(momentInput(snapshot))
              setSideView((current) => current === 'TIME' ? null : 'TIME')
            }}
          >
            <CalendarClock size={12} /> Time
          </button>
          <button
            className={sideView === 'PROFILE' ? 'is-active' : ''}
            onClick={() => setSideView((current) => current === 'PROFILE' ? null : 'PROFILE')}
          >
            <SlidersHorizontal size={12} /> Profile
          </button>
          <button
            className={wheelOpen ? 'is-active' : ''}
            onClick={() => {
              setWheelOpen((current) => !current)
              if (!fixedPhasorInterval && !phasorBusy) onLoadFixedPhasor()
            }}
          >
            <Orbit size={12} /> Wheel
          </button>
        </div>
      </header>

      {sideView === 'TIME' && (
        <section className="product-first-time-profile" aria-label="Selected time view">
          <div>
            <CalendarClock size={15} />
            <div><strong>Selected time</strong><span>Changes the same timestamp used by price, event lanes, and the Chakra.</span></div>
          </div>
          <div className="product-first-time-actions">
            <button
              title="Previous loaded candle"
              disabled={selectedCandleIndex <= 0}
              onClick={() => onSelectMoment(toIstInput(candles[selectedCandleIndex - 1].time))}
            ><ChevronLeft size={14} /> Previous candle</button>
            <input
              type="datetime-local"
              value={draftMoment}
              aria-label="Selected IST moment"
              onChange={(event) => setDraftMoment(event.target.value)}
            />
            <button
              className="is-primary"
              disabled={!draftMoment}
              onClick={() => onSelectMoment(draftMoment)}
            >Synchronize moment</button>
            <button
              title="Next loaded candle"
              disabled={selectedCandleIndex < 0 || selectedCandleIndex >= candles.length - 1}
              onClick={() => onSelectMoment(toIstInput(candles[selectedCandleIndex + 1].time))}
            >Next candle <ChevronRight size={14} /></button>
          </div>
          <div className="product-first-time-facts">
            <span><b>IST</b>{snapshot ? new Intl.DateTimeFormat('en-IN', { dateStyle: 'full', timeStyle: 'medium', timeZone: 'Asia/Kolkata' }).format(new Date(snapshot.as_of_utc)) : 'Unavailable'}</span>
            <span><b>Location</b>{snapshot ? `${snapshot.location.latitude.toFixed(4)}, ${snapshot.location.longitude.toFixed(4)}` : 'Unavailable'}</span>
            <span><b>Chart candle</b>{selectedCandleIndex >= 0 ? `${selectedCandleIndex + 1} of ${candles.length}` : 'No chart candle'}</span>
          </div>
          {snapshot && <div className="product-first-panchanga-strip">
            <span>Tithi <b>{display(snapshot.foundation_snapshot.panchanga.tithi_name)}</b></span>
            <span>Paksha <b>{display(snapshot.foundation_snapshot.panchanga.paksha)}</b></span>
            <span>Yoga <b>{display(snapshot.foundation_snapshot.panchanga.yoga_name)}</b></span>
            <span>Karana <b>{display(snapshot.foundation_snapshot.panchanga.karana_name)}</b></span>
            <span>Weekday <b>{display(snapshot.foundation_snapshot.panchanga.vara.weekday)}</b></span>
          </div>}
        </section>
      )}

      {sideView === 'PROFILE' && (
        <section className="product-first-time-profile" aria-label="Current profile view">
          <div>
            <SlidersHorizontal size={15} />
            <div><strong>Current profile</strong><span>These are the existing read-only configurations behind the synchronized display.</span></div>
          </div>
          <div className="product-first-profile-facts">
            <span><b>Foundation</b>{snapshot ? display(snapshot.foundation_snapshot.profile_id) : 'Unavailable'}</span>
            <span><b>Chakra grid</b>{snapshot ? display(snapshot.grid.grid_profile_id) : 'Unavailable'}</span>
            <span><b>Vedha guidance</b>{snapshot?.guidance ? display(snapshot.guidance.vedha_profile_id) : 'No resolved guidance'}</span>
            <span><b>Active actors</b>{readiness.length ? readiness.map((item) => item.body).join(', ') : 'None selected'}</span>
            <span><b>Included layers</b>{snapshot?.grid.certified_layers.length ? snapshot.grid.certified_layers.map(display).join(', ') : 'Unavailable'}</span>
          </div>
          <p className="product-first-profile-note">This workspace reports the loaded profile context only. It does not alter a formula, create a market call, or unlock any execution path.</p>
        </section>
      )}

      {currencyPairEvidence && (
        <section className="product-first-fx-panel" aria-label="USDJPY relative context">
          <div>
            <Layers3 size={15} />
            <div>
              <strong>USDJPY relative context</strong>
              <span>{selectedAspectLabel ?? 'Selected aspect'} · existing provisional research arithmetic only</span>
            </div>
          </div>
          <dl>
            <div><dt>{currencyPairEvidence.base.label}</dt><dd>{baseScore == null ? 'Unknown' : baseScore.toFixed(3)}</dd></div>
            <div><dt>{currencyPairEvidence.quote.label}</dt><dd>{quoteScore == null ? 'Unknown' : quoteScore.toFixed(3)}</dd></div>
            <div><dt>Base minus quote</dt><dd>{pairScore == null ? 'Unknown' : pairScore.toFixed(3)}</dd></div>
            <div><dt>Common mode</dt><dd>{commonMode == null ? 'Unknown' : commonMode.toFixed(3)}</dd></div>
            <div><dt>Conflict</dt><dd>{pairConflict == null ? 'Unknown' : `${(pairConflict * 100).toFixed(1)}%`}</dd></div>
          </dl>
          <p>Both currencies remain visible. These descriptive values are not a price prediction and cannot unlock an order or execution path.</p>
        </section>
      )}

      {wheelOpen && (
        <section className="product-first-wheel" aria-label="Fixed phasor wheel">
          <div className="product-first-wheel-heading">
            <Orbit size={15} />
            <div><strong>Fixed real-axis phasor wheel</strong><span>Existing scalar display only: 0 at right, pi at left. It is not timing phase, a vote, or a price signal.</span></div>
          </div>
          {phasorBusy && <p className="product-first-wheel-state">Loading the read-only fixed-vector display for this selected timestamp.</p>}
          {phasorError && <p className="product-first-wheel-state is-error">{phasorError}</p>}
          {!phasorBusy && !phasorError && !fixedPhasorInterval && <p className="product-first-wheel-state">No fixed-vector display is available for this selected timestamp.</p>}
          {fixedPhasorInterval && <>
            <div className="product-first-wheel-layout">
              <svg viewBox="0 0 300 300" role="img" aria-label="Fixed zero and pi circular phasor display">
                <circle cx="150" cy="150" r="118" className="product-first-wheel-ring" />
                <line x1="24" y1="150" x2="276" y2="150" className="product-first-wheel-axis" />
                <text x="276" y="142" textAnchor="end" className="product-first-wheel-label is-positive">fixed 0</text>
                <text x="24" y="142" className="product-first-wheel-label is-negative">fixed pi</text>
                <circle cx="150" cy="150" r="5" className="product-first-wheel-origin" />
                {plottedVectors.map((vector, index) => {
                  const magnitude = vector.magnitude_units ?? 0
                  const radius = 24 + (magnitude / maxVectorMagnitude) * 88
                  const verticalOffset = (index - (plottedVectors.length - 1) / 2) * 8
                  const positive = vector.fixed_angle === 'ZERO'
                  const x = 150 + (positive ? radius : -radius)
                  const y = 150 + verticalOffset
                  return <g
                    key={vector.vector_id}
                    className={`product-first-wheel-vector ${positive ? 'is-positive' : 'is-negative'}${selectedVector?.vector_id === vector.vector_id ? ' is-selected' : ''}`}
                    onClick={() => setSelectedVectorId(vector.vector_id)}
                  >
                    <line x1="150" y1="150" x2={x} y2={y} />
                    <circle cx={x} cy={y} r="6" />
                  </g>
                })}
              </svg>
              <div className="product-first-wheel-detail">
                <span>Selected vector</span>
                {selectedVector ? <>
                  <strong>{selectedVector.actor_identity ?? 'Unlabelled contribution'}</strong>
                  <div><em>Fixed side</em><b>{selectedVector.fixed_angle === 'ZERO' ? '0 / right' : 'Pi / left'}</b></div>
                  <div><em>Scalar units</em><b>{(selectedVector.real_component_units ?? 0).toFixed(1)}</b></div>
                  <div><em>Target</em><b>{selectedVector.target_value ?? 'Unknown'}</b></div>
                </> : <p>No resolved vector was plotted.</p>}
              </div>
            </div>
            <div className="product-first-wheel-summary">
              <span>Real sum <b>{fixedPhasorInterval.vector_real_sum_units.toFixed(1)}</b></span>
              <span>Gross magnitude <b>{fixedPhasorInterval.vector_magnitude_sum_units.toFixed(1)}</b></span>
              <span>Imaginary sum <b>{fixedPhasorInterval.vector_imaginary_sum_units.toFixed(1)}</b></span>
              <span>Known coverage <b>{(fixedPhasorInterval.known_scored_coherence_ratio * 100).toFixed(1)}%</b></span>
            </div>
            {unknownVectors.length > 0 && <p className="product-first-wheel-unknown">{unknownVectors.length} unknown vector{unknownVectors.length === 1 ? '' : 's'} remain unplotted.</p>}
          </>}
        </section>
      )}

      <div className="product-first-sbc-body">
        <section className="product-first-market-panel">
          <div className="product-first-panel-heading">
            <div>
              <strong>Price and aspect context</strong>
              <span>Click a candle to synchronize the SBC moment in IST</span>
            </div>
            <time>{snapshot ? new Intl.DateTimeFormat('en-IN', {
              dateStyle: 'medium', timeStyle: 'short', timeZone: 'Asia/Kolkata',
            }).format(new Date(snapshot.as_of_utc)) : 'Moment unavailable'}</time>
          </div>
          {candles.length ? (
            <div className="product-first-market-viewport">
              <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} role="img" aria-label="Price chart with aspect event lanes">
                <rect x="0" y="0" width={chartWidth} height={chartHeight} className="product-first-chart-bg" />
                {[0, 1, 2, 3, 4].map((index) => {
                  const y = 28 + index * 90
                  const price = high - (priceSpan * index) / 4
                  return <g key={index}>
                    <line x1="28" y1={y} x2="972" y2={y} className="product-first-chart-grid" />
                    <text x="4" y={y + 3} className="product-first-chart-axis">{price.toFixed(3)}</text>
                  </g>
                })}
                {visibleAspects.map((aspect, index) => {
                  const x = Math.max(28, xFor(Math.max(firstTime, aspect.start)))
                  const end = Math.min(972, xFor(Math.min(lastTime, aspect.end)))
                  const lane = index % 4
                  const y = 4 + lane * 19
                  return <g key={aspect.eventId} className="product-first-aspect-lane">
                    <rect x={x} y={y} width={Math.max(2, end - x)} height="16" fill={aspect.color} />
                    {end - x > 74 && <text x={x + 4} y={y + 11}>{compactAspectLabel(aspect.aspectLabel)}</text>}
                  </g>
                })}
                {candles.map((candle) => {
                  const x = xFor(candle.time)
                  const up = candle.close >= candle.open
                  const bodyTop = yFor(Math.max(candle.open, candle.close))
                  const bodyBottom = yFor(Math.min(candle.open, candle.close))
                  return <g key={candle.time} className="product-first-candle" onClick={() => onSelectMoment(toIstInput(candle.time))}>
                    <line x1={x} y1={yFor(candle.high)} x2={x} y2={yFor(candle.low)} className={up ? 'is-up' : 'is-down'} />
                    <rect x={x - candleWidth / 2} y={bodyTop} width={candleWidth} height={Math.max(1.2, bodyBottom - bodyTop)} className={up ? 'is-up' : 'is-down'} />
                  </g>
                })}
                <line x1={xFor(selectedEpoch)} y1="24" x2={xFor(selectedEpoch)} y2="392" className="product-first-selected-moment" />
                <text x={Math.min(835, Math.max(32, xFor(selectedEpoch) + 5))} y="420" className="product-first-chart-axis">Selected moment</text>
              </svg>
            </div>
          ) : (
            <div className="product-first-empty"><CircleHelp size={20} /><span>Open this workspace from a loaded chart to see price and aspect context.</span></div>
          )}
          <div className="product-first-event-strip">
            <strong>Visible aspects</strong>
            {visibleAspects.slice(0, 12).map((aspect) => (
              <span key={aspect.eventId} style={{ borderColor: aspect.color }} title={`${aspect.startIso} to ${aspect.endIso}`}>
                {compactAspectLabel(aspect.aspectLabel)}
              </span>
            ))}
            {!visibleAspects.length && <em>No aspects in the loaded chart range</em>}
          </div>
        </section>

        <section className="product-first-chakra-panel">
          <div className="product-first-panel-heading">
            <div><strong>81-cell Chakra</strong><span>Selected cell follows evidence and manual clicks</span></div>
            <Grid3X3 size={15} />
          </div>
          {snapshot ? (
            <div className="product-first-chakra-grid" style={{
              '--chakra-columns': snapshot.grid.columns,
              '--chakra-rows': snapshot.grid.rows,
            } as CSSProperties}>
              {snapshot.grid.cells.map((cell) => {
                const key = cellKey(cell)
                const primary = cell.entries.find((entry) => entry.layer === 'NAKSHATRA') ?? cell.entries[0]
                const isContext = cell.entries.some((entry) => contextCells.has(`${entry.layer}:${entry.value}`))
                return <button
                  key={key}
                  className={[
                    'product-first-chakra-cell',
                    selectedCell === key ? 'is-selected' : '',
                    targetCells.has(key) ? 'is-hit' : '',
                    isContext ? 'is-context' : '',
                  ].filter(Boolean).join(' ')}
                  onClick={() => onSelectCell(key)}
                  title={cell.entries.map((entry) => `${entry.layer}: ${entry.value}`).join('\n')}
                >
                  <small>{cell.row},{cell.column}</small>
                  <strong>{primary ? display(primary.value) : '·'}</strong>
                </button>
              })}
            </div>
          ) : <div className="product-first-empty"><span>Calculating the Chakra snapshot.</span></div>}
        </section>

        <aside className="product-first-why-drawer">
          <div className="product-first-panel-heading">
            <div><strong>Why this state</strong><span>Evidence only, not a market call</span></div>
            <CircleHelp size={15} />
          </div>
          <section className="product-first-why-card">
            <span>Current state</span>
            <strong>{guidance ? display(guidance.guidance_band) : 'Unknown'}</strong>
            <p>{conflict}. Coverage is {guidance ? `${Math.round(guidance.scoring_coverage_ratio * 100)}%` : 'unavailable'}; unresolved inputs remain explicit.</p>
          </section>
          <section className="product-first-why-card">
            <span>Selected Chakra cell</span>
            {selected?.entries.map((entry) => <div key={`${entry.layer}:${entry.value}`}><em>{display(entry.layer)}</em><strong>{display(entry.value)}</strong></div>)}
            {!selected?.entries.length && <p>No certified layer at this cell.</p>}
          </section>
          <section className="product-first-why-card">
            <span>Resolved Vedha evidence</span>
            {(guidance?.contributions ?? []).slice(0, 9).map((item, index) => (
              <button key={`${item.body}-${index}`} onClick={() => onSelectCell(`${item.target.row}:${item.target.column}`)}>
                <strong>{item.body}</strong><em>{display(item.direction)} → {display(item.target.value)}</em><b>{item.signed_guidance_units == null ? 'Unknown' : item.signed_guidance_units.toFixed(1)}</b>
              </button>
            ))}
            {!guidance?.contributions.length && <p>No resolved Vedha contribution for this moment.</p>}
          </section>
          <section className="product-first-why-card">
            <span>Actor readiness</span>
            {readiness.map((item) => <div key={item.body}><em>{item.body}</em><strong>{display(item.status)}</strong></div>)}
          </section>
        </aside>
      </div>
    </section>
  )
}
