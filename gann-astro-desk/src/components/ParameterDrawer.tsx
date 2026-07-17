import {
  Check,
  CheckCircle2,
  Database,
  HardDriveDownload,
  LoaderCircle,
  Play,
  Plus,
  Radio,
  RotateCcw,
  Save,
  ShieldCheck,
  Square,
  Trash2,
  X,
} from 'lucide-react'
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  activateDataArtifact,
  cancelGenerationJob,
  createGenerationJob,
  createMt5HistorySnapshot,
  deleteParameterProfile,
  fetchDataArtifacts,
  fetchGenerationJobs,
  fetchMt5HistorySnapshots,
  fetchPriceSources,
  promoteMt5HistorySnapshot,
  saveParameterProfile,
} from '../api'
import {
  aspectLabel,
  datetimeInputValue,
  datetimeParameterValue,
  parseNumberList,
  toggleValue,
} from '../parameterUtils'
import {
  automaticAspectMinDurationMinutes,
  formatAspectDuration,
} from '../aspectTimeframePolicy'
import {
  boundRequestedRangeToSource,
  chartTimeframeForSource,
  mt5SourceTimeframeForChart,
} from '../mt5ResearchWorkflow'
import { useVisibilityPolling } from '../useVisibilityPolling'
import type {
  ChartParameters,
  DataArtifact,
  GenerationJob,
  Mt5HistorySnapshot,
  ParameterSchema,
  PriceSource,
  SavedParameterProfile,
} from '../types'

type ParameterDrawerProps = {
  open: boolean
  busy: boolean
  schema: ParameterSchema
  parameters: ChartParameters
  profiles: SavedParameterProfile[]
  activeArtifactId: string
  onClose: () => void
  onApply: (parameters: ChartParameters) => Promise<void>
  onArtifactActivated: (artifact: DataArtifact) => Promise<void>
  onProfilesChange: (profiles: SavedParameterProfile[]) => void
}

export function ParameterDrawer({
  open,
  busy,
  schema,
  parameters,
  profiles,
  activeArtifactId,
  onClose,
  onApply,
  onArtifactActivated,
  onProfilesChange,
}: ParameterDrawerProps) {
  const [draft, setDraft] = useState<ChartParameters>(parameters)
  const [profileName, setProfileName] = useState('')
  const [selectedProfileId, setSelectedProfileId] = useState('')
  const [excludedCandidate, setExcludedCandidate] = useState('')
  const [profileBusy, setProfileBusy] = useState(false)
  const [generationBusy, setGenerationBusy] = useState(false)
  const [generationError, setGenerationError] = useState('')
  const [jobs, setJobs] = useState<GenerationJob[]>([])
  const [artifacts, setArtifacts] = useState<DataArtifact[]>([])
  const [artifactCandidate, setArtifactCandidate] = useState('')
  const [snapshotBusy, setSnapshotBusy] = useState(false)
  const [promotionBusy, setPromotionBusy] = useState(false)
  const [automaticResearchBusy, setAutomaticResearchBusy] = useState(false)
  const [snapshotMessage, setSnapshotMessage] = useState('')
  const [snapshotCandidate, setSnapshotCandidate] = useState('')
  const [snapshots, setSnapshots] = useState<Mt5HistorySnapshot[]>([])
  const [priceSources, setPriceSources] = useState<PriceSource[]>(schema.options.priceSources)
  const notifiedArtifact = useRef(activeArtifactId)
  const hasActiveGenerationJob = jobs.some((job) => ['queued', 'running', 'cancelling'].includes(job.status))

  useEffect(() => {
    if (open) setDraft(structuredClone(parameters))
  }, [open, parameters])

  useEffect(() => {
    if (!open) return
    Promise.all([fetchMt5HistorySnapshots(), fetchPriceSources()])
      .then(([nextSnapshots, nextSources]) => {
        setSnapshots(nextSnapshots)
        setPriceSources(nextSources)
      })
      .catch((reason) => setSnapshotMessage(reason instanceof Error ? reason.message : String(reason)))
  }, [open])

  useEffect(() => {
    notifiedArtifact.current = activeArtifactId
  }, [activeArtifactId])

  const refreshGenerationState = useCallback(async () => {
    try {
      const [nextJobs, nextArtifacts] = await Promise.all([
        fetchGenerationJobs(),
        fetchDataArtifacts(),
      ])
      setJobs(nextJobs)
      setArtifacts(nextArtifacts)
      const active = nextArtifacts.find((item) => item.isActive)
      if (active && active.artifactId !== notifiedArtifact.current) {
        notifiedArtifact.current = active.artifactId
        await onArtifactActivated(active)
      }
    } catch (reason) {
      setGenerationError(reason instanceof Error ? reason.message : String(reason))
    }
  }, [onArtifactActivated])
  useVisibilityPolling(refreshGenerationState, {
    enabled: open,
    intervalMs: hasActiveGenerationJob ? 1500 : 10000,
  })

  const selectedPriceSource = priceSources.find(
    (source) => source.priceSourceId === draft.priceSourceId,
  ) ?? priceSources.find((source) => source.priceSourceId === 'baseline') ?? null
  const range = selectedPriceSource && !selectedPriceSource.builtIn
    ? { start: selectedPriceSource.dateStart, end: selectedPriceSource.dateEnd }
    : schema.dataRanges[draft.timeframe] ?? { start: draft.start, end: draft.end }
  const selectedProfile = useMemo(
    () => profiles.find((item) => item.profileId === selectedProfileId) ?? null,
    [profiles, selectedProfileId],
  )
  const activeJob = jobs.find((job) => ['queued', 'running', 'cancelling'].includes(job.status)) ?? null
  const latestJob = activeJob ?? jobs[0] ?? null
  const activeArtifact = artifacts.find((artifact) => artifact.isActive) ?? null
  const automaticAspectMinimum = automaticAspectMinDurationMinutes(draft.timeframe)

  if (!open) return null

  const saveProfile = async () => {
    const name = profileName.trim() || selectedProfile?.name || 'Research profile'
    setProfileBusy(true)
    try {
      const saved = await saveParameterProfile({
        profileId: selectedProfile?.profileId,
        name,
        parameters: draft,
        isDefault: selectedProfile?.isDefault ?? false,
      })
      const remaining = profiles.filter((item) => item.profileId !== saved.profileId)
      onProfilesChange([saved, ...remaining])
      setSelectedProfileId(saved.profileId)
      setProfileName(saved.name)
    } finally {
      setProfileBusy(false)
    }
  }

  const removeProfile = async () => {
    if (!selectedProfile) return
    setProfileBusy(true)
    try {
      await deleteParameterProfile(selectedProfile.profileId)
      onProfilesChange(profiles.filter((item) => item.profileId !== selectedProfile.profileId))
      setSelectedProfileId('')
      setProfileName('')
    } finally {
      setProfileBusy(false)
    }
  }

  const generateSource = async () => {
    setGenerationBusy(true)
    setGenerationError('')
    try {
      const job = await createGenerationJob({
        label: profileName.trim() || undefined,
        parameters: { ...draft, dataSource: 'research' },
        autoActivate: true,
      })
      setJobs((current) => [job, ...current.filter((item) => item.jobId !== job.jobId)])
    } catch (reason) {
      setGenerationError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setGenerationBusy(false)
    }
  }

  const stopGeneration = async () => {
    if (!activeJob) return
    setGenerationBusy(true)
    try {
      const job = await cancelGenerationJob(activeJob.jobId)
      setJobs((current) => current.map((item) => item.jobId === job.jobId ? job : item))
    } catch (reason) {
      setGenerationError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setGenerationBusy(false)
    }
  }

  const activateArtifact = async () => {
    if (!artifactCandidate) return
    setGenerationBusy(true)
    setGenerationError('')
    try {
      const artifact = await activateDataArtifact(artifactCandidate)
      notifiedArtifact.current = artifact.artifactId
      setArtifacts((current) => current.map((item) => ({
        ...item,
        isActive: item.artifactId === artifact.artifactId,
      })))
      await onArtifactActivated(artifact)
      setArtifactCandidate('')
    } catch (reason) {
      setGenerationError(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setGenerationBusy(false)
    }
  }

  const snapshotMt5Range = async () => {
    setSnapshotBusy(true)
    setSnapshotMessage('')
    try {
      const snapshot = await createMt5HistorySnapshot({
        symbol: draft.symbol,
        timeframe: mt5SourceTimeframeForChart(draft.timeframe),
        start: draft.start,
        end: draft.end,
      })
      setSnapshotMessage(
        `${snapshot.barCount.toLocaleString()} closed bars saved at ${new Date(snapshot.capturedAtUtc).toLocaleString()}`,
      )
      setSnapshots(await fetchMt5HistorySnapshots())
      setSnapshotCandidate(snapshot.snapshotId)
    } catch (reason) {
      setSnapshotMessage(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setSnapshotBusy(false)
    }
  }

  const promoteSnapshot = async () => {
    if (!snapshotCandidate) return
    setPromotionBusy(true)
    setSnapshotMessage('')
    try {
      const promoted = await promoteMt5HistorySnapshot(snapshotCandidate)
      const nextSources = await fetchPriceSources()
      const nextSnapshots = await fetchMt5HistorySnapshots()
      setPriceSources(nextSources)
      setSnapshots(nextSnapshots)
      setSnapshotCandidate('')
      setDraft((current) => ({
        ...current,
        dataSource: 'research',
        priceSourceId: promoted.priceSourceId,
        timeframe: chartTimeframeForSource(current.timeframe, promoted.sourceTimeframe),
        start: promoted.dateStart,
        end: promoted.dateEnd,
      }))
      setSnapshotMessage(`Verified and promoted ${promoted.barCount.toLocaleString()} closed bars`)
    } catch (reason) {
      setSnapshotMessage(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setPromotionBusy(false)
    }
  }

  const selectPriceSource = (priceSourceId: string) => {
    const source = priceSources.find((item) => item.priceSourceId === priceSourceId)
    if (!source || source.builtIn) {
      setDraft({ ...draft, priceSourceId: 'baseline' })
      return
    }
    setDraft({
      ...draft,
      priceSourceId: source.priceSourceId,
      timeframe: chartTimeframeForSource(draft.timeframe, source.sourceTimeframe),
      start: source.dateStart,
      end: source.dateEnd,
    })
  }

  const fetchMt5AndGenerate = async () => {
    setAutomaticResearchBusy(true)
    setSnapshotMessage('Connecting to MT5 and requesting closed bars...')
    setGenerationError('')
    try {
      const requestedStart = draft.start
      const requestedEnd = draft.end
      const sourceTimeframe = mt5SourceTimeframeForChart(draft.timeframe)
      const snapshot = await createMt5HistorySnapshot({
        symbol: draft.symbol,
        timeframe: sourceTimeframe,
        start: requestedStart,
        end: requestedEnd,
      })
      setSnapshotMessage(`Captured ${snapshot.barCount.toLocaleString()} closed ${sourceTimeframe} bars; verifying archive...`)
      const promoted = await promoteMt5HistorySnapshot(
        snapshot.snapshotId,
        `${draft.symbol} ${sourceTimeframe} self-service ${new Date(snapshot.capturedAtUtc).toLocaleString()}`,
      )
      const bounded = boundRequestedRangeToSource(requestedStart, requestedEnd, promoted)
      const nextDraft: ChartParameters = {
        ...draft,
        dataSource: 'research',
        priceSourceId: promoted.priceSourceId,
        start: bounded.start,
        end: bounded.end,
      }
      setDraft(nextDraft)
      const [nextSources, nextSnapshots] = await Promise.all([
        fetchPriceSources(),
        fetchMt5HistorySnapshots(),
      ])
      setPriceSources(nextSources)
      setSnapshots(nextSnapshots)
      const job = await createGenerationJob({
        label: `${draft.symbol} ${draft.timeframe} ${bounded.start.slice(0, 10)} to ${bounded.end.slice(0, 10)}`,
        parameters: nextDraft,
        autoActivate: true,
      })
      setJobs((current) => [job, ...current.filter((item) => item.jobId !== job.jobId)])
      const coverage = bounded.startCovered && bounded.endCovered
        ? 'Full requested range received.'
        : 'Broker history was partial; the generated range was bounded to available closed bars.'
      setSnapshotMessage(
        `${promoted.barCount.toLocaleString()} verified ${sourceTimeframe} bars. ${coverage} Corrected TN generation queued.`,
      )
    } catch (reason) {
      setSnapshotMessage(reason instanceof Error ? reason.message : String(reason))
    } finally {
      setAutomaticResearchBusy(false)
    }
  }

  return (
    <div className="parameter-backdrop" role="presentation">
      <aside className="parameter-drawer" aria-label="Chart and astronomy parameters">
        <header className="parameter-header">
          <div>
            <span className="eyebrow">Workspace parameters</span>
            <strong>Chart generation profile</strong>
          </div>
          <button className="icon-button" onClick={onClose} title="Close parameters"><X size={18} /></button>
        </header>

        <div className="parameter-scroll">
          <section className="parameter-section profile-section">
            <div className="parameter-section-title"><Save size={15} /><strong>Profiles</strong></div>
            <div className="parameter-inline">
              <select
                value={selectedProfileId}
                onChange={(event) => {
                  const profile = profiles.find((item) => item.profileId === event.target.value)
                  setSelectedProfileId(event.target.value)
                  if (profile) {
                    setDraft(structuredClone(profile.parameters))
                    setProfileName(profile.name)
                  }
                }}
              >
                <option value="">Unsaved profile</option>
                {profiles.map((profile) => <option value={profile.profileId} key={profile.profileId}>{profile.name}</option>)}
              </select>
              <button className="icon-button danger" disabled={!selectedProfile || profileBusy} onClick={removeProfile} title="Delete profile"><Trash2 size={15} /></button>
            </div>
            <div className="parameter-inline">
              <input value={profileName} onChange={(event) => setProfileName(event.target.value)} placeholder="Profile name" />
              <button className="secondary-command" disabled={profileBusy} onClick={saveProfile}><Save size={14} /> Save</button>
            </div>
          </section>

          <section className="parameter-section generation-section">
            <div className="parameter-section-title">
              <Database size={15} />
              <strong>Corrected data artifacts</strong>
              <span>{schema.generation.astronomyContract.split('_').slice(0, 2).join(' ')}</span>
            </div>
            <div className="artifact-active-row">
              <div>
                <span>Active source</span>
                <strong>{activeArtifact?.label ?? 'Loading artifact registry'}</strong>
              </div>
              {activeArtifact && (
                <span>{activeArtifact.eventCount ?? '-'} events / {activeArtifact.touchCount ?? '-'} touches</span>
              )}
            </div>
            <div className="parameter-inline">
              <select value={artifactCandidate} onChange={(event) => setArtifactCandidate(event.target.value)}>
                <option value="">Switch data source</option>
                {artifacts.filter((artifact) => !artifact.isActive).map((artifact) => (
                  <option value={artifact.artifactId} key={artifact.artifactId}>
                    {artifact.label} ({artifact.eventCount ?? '-'} / {artifact.touchCount ?? '-'})
                  </option>
                ))}
              </select>
              <button className="icon-button" disabled={!artifactCandidate || generationBusy} onClick={activateArtifact} title="Activate selected artifact"><RotateCcw size={15} /></button>
            </div>
            {latestJob && (
              <div className={`generation-job-status is-${latestJob.status}`}>
                <div className="generation-job-heading">
                  <span>
                    {latestJob.status === 'completed' ? <CheckCircle2 size={14} /> : <LoaderCircle size={14} />}
                    {latestJob.label}
                  </span>
                  <strong>{Math.round(latestJob.progress)}%</strong>
                </div>
                <div className="generation-progress" aria-label={`Generation ${Math.round(latestJob.progress)} percent`}>
                  <span style={{ width: `${Math.max(0, Math.min(100, latestJob.progress))}%` }} />
                </div>
                <p>{latestJob.message}</p>
                {latestJob.error && <details><summary>Generator error</summary><pre>{latestJob.error}</pre></details>}
              </div>
            )}
            {generationError && <div className="generation-inline-error">{generationError}</div>}
            <div className="generation-actions">
              <button
                className="secondary-command"
                disabled={Boolean(activeJob) || generationBusy || busy || draft.dataSource !== 'research' || draft.mode !== 'TN' || !draft.aspects.length}
                onClick={generateSource}
                title={draft.dataSource === 'research' ? 'Build and activate a corrected TN artifact' : 'Switch to Research mode before generating'}
              >
                {generationBusy ? <LoaderCircle size={14} /> : <Database size={14} />}
                Generate corrected source
              </button>
              {activeJob && (
                <button className="icon-button danger" disabled={generationBusy} onClick={stopGeneration} title="Cancel generation"><Square size={13} /></button>
              )}
            </div>
          </section>

          <section className="parameter-section">
            <div className="parameter-section-title"><Database size={15} /><strong>Market source</strong></div>
            <div className="parameter-segmented">
              <button className={draft.dataSource === 'research' ? 'is-active' : ''} onClick={() => setDraft({ ...draft, dataSource: 'research' })}><Database size={14} /> Research</button>
              <button className={draft.dataSource === 'live' ? 'is-active' : ''} onClick={() => setDraft({ ...draft, dataSource: 'live' })}><Radio size={14} /> MT5 live</button>
            </div>
            <div className="parameter-grid two-column">
              <label>Symbol<input value={draft.symbol} onChange={(event) => setDraft({ ...draft, symbol: event.target.value.toUpperCase() })} /></label>
              <label>Timeframe
                <select value={draft.timeframe} onChange={(event) => {
                  const timeframe = event.target.value as ChartParameters['timeframe']
                  const compatible = selectedPriceSource?.builtIn
                    || (selectedPriceSource?.sourceTimeframe === 'M30' && timeframe === 'M30')
                    || (selectedPriceSource?.sourceTimeframe === 'H1' && timeframe !== 'M30')
                  setDraft({ ...draft, timeframe, priceSourceId: compatible ? draft.priceSourceId : 'baseline' })
                }}>
                  {schema.options.timeframes.map((value) => <option key={value}>{value}</option>)}
                </select>
              </label>
            </div>
            {draft.dataSource === 'research' ? (
              <>
                <label>Price archive
                  <select value={draft.priceSourceId} onChange={(event) => selectPriceSource(event.target.value)}>
                    {priceSources.map((source) => (
                      <option
                        key={source.priceSourceId}
                        value={source.priceSourceId}
                        disabled={!source.verified || (!source.builtIn && !['M30', 'H1'].includes(source.sourceTimeframe))}
                      >
                        {source.label}{source.builtIn ? '' : ` (${source.sourceTimeframe}, ${source.barCount.toLocaleString()})`}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="parameter-grid two-column">
                  <label>Start<input type="datetime-local" value={datetimeInputValue(draft.start)} onChange={(event) => setDraft({ ...draft, start: datetimeParameterValue(event.target.value) })} /></label>
                  <label>End<input type="datetime-local" value={datetimeInputValue(draft.end)} onChange={(event) => setDraft({ ...draft, end: datetimeParameterValue(event.target.value) })} /></label>
                </div>
                <button
                  className="primary-command mt5-fetch-command"
                  disabled={automaticResearchBusy || snapshotBusy || promotionBusy || Boolean(activeJob) || generationBusy || busy || draft.mode !== 'TN' || !draft.aspects.length}
                  onClick={fetchMt5AndGenerate}
                  title="Fetch closed bars from MT5, verify an immutable archive, and generate corrected TN aspects"
                >
                  {automaticResearchBusy ? <LoaderCircle size={14} /> : <HardDriveDownload size={14} />}
                  {automaticResearchBusy ? 'Preparing research chart' : 'Fetch MT5 and build aspects'}
                </button>
                <p className="mt5-fetch-help">
                  Uses {mt5SourceTimeframeForChart(draft.timeframe)} source bars for the {draft.timeframe} view, verifies the broker range, and activates the completed chart automatically.
                </p>
                <button className="secondary-command" disabled={snapshotBusy} onClick={snapshotMt5Range}>
                  {snapshotBusy ? <LoaderCircle size={14} /> : <HardDriveDownload size={14} />}
                  Snapshot MT5 range
                </button>
                <div className="parameter-inline">
                  <select value={snapshotCandidate} onChange={(event) => setSnapshotCandidate(event.target.value)}>
                    <option value="">Promote captured snapshot</option>
                    {snapshots.map((snapshot) => (
                      <option
                        key={snapshot.snapshotId}
                        value={snapshot.snapshotId}
                        disabled={Boolean(snapshot.promotedPriceSourceId) || !['M30', 'H1'].includes(snapshot.timeframe)}
                      >
                        {snapshot.symbol} {snapshot.timeframe} | {snapshot.barCount.toLocaleString()} bars
                        {snapshot.promotedPriceSourceId ? ' | promoted' : ''}
                      </option>
                    ))}
                  </select>
                  <button
                    className="icon-button"
                    disabled={!snapshotCandidate || promotionBusy}
                    onClick={promoteSnapshot}
                    title="Verify and promote snapshot"
                  >
                    {promotionBusy ? <LoaderCircle size={14} /> : <ShieldCheck size={15} />}
                  </button>
                </div>
                {snapshotMessage && <div className="parameter-range">{snapshotMessage}</div>}
              </>
            ) : (
              <label>Live bars<input type="number" min={20} max={5000} value={draft.liveBarCount} onChange={(event) => setDraft({ ...draft, liveBarCount: Number(event.target.value) })} /></label>
            )}
            <div className="parameter-range">Available {new Date(range.start).toLocaleDateString()} - {new Date(range.end).toLocaleDateString()}</div>
          </section>

          <section className="parameter-section">
            <div className="parameter-section-title"><Check size={15} /><strong>Aspect mode</strong></div>
            <div className="parameter-segmented">
              {schema.options.modes.map((mode) => (
                <button
                  key={mode.id}
                  className={draft.mode === mode.id ? 'is-active' : ''}
                  disabled={!mode.available}
                  onClick={() => setDraft({ ...draft, mode: mode.id })}
                  title={mode.available ? mode.label : `${mode.label} generator pending`}
                >{mode.id}</button>
              ))}
            </div>
            <div className="parameter-subtitle">Aspects</div>
            <div className="parameter-chip-grid">
              {schema.options.aspects.map((aspect) => (
                <button key={aspect} className={draft.aspects.includes(aspect) ? 'is-active' : ''} onClick={() => setDraft({ ...draft, aspects: toggleValue(draft.aspects, aspect) })}>{aspectLabel(aspect)}</button>
              ))}
            </div>
          </section>

          <section className="parameter-section">
            <div className="parameter-section-title"><Check size={15} /><strong>Planet bodies</strong></div>
            <div className="parameter-subtitle">Transit bodies <button onClick={() => setDraft({ ...draft, transitBodies: [] })}>All</button></div>
            <div className="parameter-chip-grid bodies">
              {schema.options.transitBodies.map((body) => (
                <button key={body} className={!draft.transitBodies.length || draft.transitBodies.includes(body) ? 'is-active' : ''} onClick={() => setDraft({ ...draft, transitBodies: toggleValue(draft.transitBodies, body) })}>{body}</button>
              ))}
            </div>
            <div className="parameter-subtitle">Natal bodies <button onClick={() => setDraft({ ...draft, natalBodies: [] })}>All</button></div>
            <div className="parameter-chip-grid bodies">
              {schema.options.natalBodies.map((body) => (
                <button key={body} className={!draft.natalBodies.length || draft.natalBodies.includes(body) ? 'is-active' : ''} onClick={() => setDraft({ ...draft, natalBodies: toggleValue(draft.natalBodies, body) })}>{body}</button>
              ))}
            </div>
          </section>

          <section className="parameter-section">
            <div className="parameter-section-title"><Check size={15} /><strong>Event filters</strong></div>
            <label className="toggle-row"><span>Touch-linked cases only</span><input type="checkbox" checked={draft.onlyTouched} onChange={(event) => setDraft({ ...draft, onlyTouched: event.target.checked })} /></label>
            <label className="toggle-row">
              <span className="toggle-row-copy">
                <span>Timeframe-aware duration</span>
                <small>{draft.timeframe} minimum {formatAspectDuration(automaticAspectMinimum)}</small>
              </span>
              <input
                type="checkbox"
                checked={draft.aspectDurationMode === 'auto'}
                onChange={(event) => setDraft({
                  ...draft,
                  aspectDurationMode: event.target.checked ? 'auto' : 'manual',
                })}
              />
            </label>
            <div className="parameter-grid two-column">
              <label>{draft.aspectDurationMode === 'auto' ? 'Applied minimum' : 'Min minutes'}<input type="number" min={0} disabled={draft.aspectDurationMode === 'auto'} value={draft.aspectDurationMode === 'auto' ? automaticAspectMinimum : draft.minDurationMinutes} onChange={(event) => setDraft({ ...draft, minDurationMinutes: Number(event.target.value) })} /></label>
              <label>Max minutes<input type="number" min={0} value={draft.maxDurationMinutes ?? ''} onChange={(event) => setDraft({ ...draft, maxDurationMinutes: event.target.value ? Number(event.target.value) : null })} /></label>
            </div>
            <div className="parameter-subtitle">Excluded families</div>
            <div className="parameter-inline">
              <select value={excludedCandidate} onChange={(event) => setExcludedCandidate(event.target.value)}>
                <option value="">Select family</option>
                {schema.options.familyKeys.map((family) => <option value={family} key={family}>{family}</option>)}
              </select>
              <button className="icon-button" disabled={!excludedCandidate || draft.excludedFamilyKeys.includes(excludedCandidate)} onClick={() => {
                setDraft({ ...draft, excludedFamilyKeys: [...draft.excludedFamilyKeys, excludedCandidate] })
                setExcludedCandidate('')
              }} title="Exclude family"><Plus size={15} /></button>
            </div>
            <div className="exclusion-list">
              {draft.excludedFamilyKeys.map((family) => (
                <button key={family} onClick={() => setDraft({ ...draft, excludedFamilyKeys: draft.excludedFamilyKeys.filter((item) => item !== family) })}>{family}<X size={12} /></button>
              ))}
            </div>
          </section>

          <section className="parameter-section">
            <div className="parameter-section-title"><Check size={15} /><strong>Planetary SR</strong><span>rebuild input</span></div>
            <label>Harmonics f<input value={draft.harmonics.join(', ')} onChange={(event) => setDraft({ ...draft, harmonics: parseNumberList(event.target.value) })} /></label>
            <label>n values<input value={draft.nValues.join(', ')} onChange={(event) => setDraft({ ...draft, nValues: parseNumberList(event.target.value) })} /></label>
            <label>Degrees<input value={draft.degrees.join(', ')} onChange={(event) => setDraft({ ...draft, degrees: parseNumberList(event.target.value) })} /></label>
            <div className="parameter-grid two-column">
              <label>Epsilon<input type="number" step="0.01" value={draft.epsilon} onChange={(event) => setDraft({ ...draft, epsilon: Number(event.target.value) })} /></label>
              <label>Price zone<input type="number" step="0.01" value={draft.priceZone} onChange={(event) => setDraft({ ...draft, priceZone: Number(event.target.value) })} /></label>
            </div>
          </section>

          <section className="parameter-section">
            <div className="parameter-section-title"><Check size={15} /><strong>Birth / IPO reference</strong><span>rebuild input</span></div>
            <label>Label<input value={draft.reference.label} onChange={(event) => setDraft({ ...draft, reference: { ...draft.reference, label: event.target.value } })} /></label>
            <div className="parameter-grid two-column">
              <label>Date<input type="date" value={draft.reference.date} onChange={(event) => setDraft({ ...draft, reference: { ...draft.reference, date: event.target.value } })} /></label>
              <label>Time<input type="time" step="1" value={draft.reference.time} onChange={(event) => setDraft({ ...draft, reference: { ...draft.reference, time: event.target.value } })} /></label>
              <label>UTC offset<input value={draft.reference.utcOffset} onChange={(event) => setDraft({ ...draft, reference: { ...draft.reference, utcOffset: event.target.value } })} /></label>
              <label>Latitude<input type="number" step="0.0001" value={draft.reference.latitude} onChange={(event) => setDraft({ ...draft, reference: { ...draft.reference, latitude: Number(event.target.value) } })} /></label>
              <label>Longitude<input type="number" step="0.0001" value={draft.reference.longitude} onChange={(event) => setDraft({ ...draft, reference: { ...draft.reference, longitude: Number(event.target.value) } })} /></label>
            </div>
          </section>
        </div>

        <footer className="parameter-footer">
          <div className="generation-status"><span className="status-dot" /> {activeJob ? `${activeJob.stage} ${Math.round(activeJob.progress)}%` : 'TN worker ready'}</div>
          <button className="primary-command" disabled={busy || draft.mode !== 'TN' || !draft.aspects.length} onClick={() => onApply(draft)}><Play size={15} /> {busy ? 'Loading' : 'Apply view'}</button>
        </footer>
      </aside>
    </div>
  )
}
