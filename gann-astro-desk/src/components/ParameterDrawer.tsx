import {
  Check,
  Database,
  Play,
  Plus,
  Radio,
  Save,
  Trash2,
  X,
} from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import {
  deleteParameterProfile,
  saveParameterProfile,
} from '../api'
import {
  aspectLabel,
  datetimeInputValue,
  datetimeParameterValue,
  parseNumberList,
  toggleValue,
} from '../parameterUtils'
import type {
  ChartParameters,
  ParameterSchema,
  SavedParameterProfile,
} from '../types'

type ParameterDrawerProps = {
  open: boolean
  busy: boolean
  schema: ParameterSchema
  parameters: ChartParameters
  profiles: SavedParameterProfile[]
  onClose: () => void
  onApply: (parameters: ChartParameters) => Promise<void>
  onProfilesChange: (profiles: SavedParameterProfile[]) => void
}

export function ParameterDrawer({
  open,
  busy,
  schema,
  parameters,
  profiles,
  onClose,
  onApply,
  onProfilesChange,
}: ParameterDrawerProps) {
  const [draft, setDraft] = useState<ChartParameters>(parameters)
  const [profileName, setProfileName] = useState('')
  const [selectedProfileId, setSelectedProfileId] = useState('')
  const [excludedCandidate, setExcludedCandidate] = useState('')
  const [profileBusy, setProfileBusy] = useState(false)

  useEffect(() => {
    if (open) setDraft(structuredClone(parameters))
  }, [open, parameters])

  const range = schema.dataRanges[draft.timeframe]
  const selectedProfile = useMemo(
    () => profiles.find((item) => item.profileId === selectedProfileId) ?? null,
    [profiles, selectedProfileId],
  )

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

          <section className="parameter-section">
            <div className="parameter-section-title"><Database size={15} /><strong>Market source</strong></div>
            <div className="parameter-segmented">
              <button className={draft.dataSource === 'research' ? 'is-active' : ''} onClick={() => setDraft({ ...draft, dataSource: 'research' })}><Database size={14} /> Research</button>
              <button className={draft.dataSource === 'live' ? 'is-active' : ''} onClick={() => setDraft({ ...draft, dataSource: 'live' })}><Radio size={14} /> MT5 live</button>
            </div>
            <div className="parameter-grid two-column">
              <label>Symbol<input value={draft.symbol} onChange={(event) => setDraft({ ...draft, symbol: event.target.value.toUpperCase() })} /></label>
              <label>Timeframe
                <select value={draft.timeframe} onChange={(event) => setDraft({ ...draft, timeframe: event.target.value as ChartParameters['timeframe'] })}>
                  {schema.options.timeframes.map((value) => <option key={value}>{value}</option>)}
                </select>
              </label>
            </div>
            {draft.dataSource === 'research' ? (
              <div className="parameter-grid two-column">
                <label>Start<input type="datetime-local" value={datetimeInputValue(draft.start)} onChange={(event) => setDraft({ ...draft, start: datetimeParameterValue(event.target.value) })} /></label>
                <label>End<input type="datetime-local" value={datetimeInputValue(draft.end)} onChange={(event) => setDraft({ ...draft, end: datetimeParameterValue(event.target.value) })} /></label>
              </div>
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
            <div className="parameter-grid two-column">
              <label>Min minutes<input type="number" min={0} value={draft.minDurationMinutes} onChange={(event) => setDraft({ ...draft, minDurationMinutes: Number(event.target.value) })} /></label>
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
          <div className="generation-status"><span className="status-dot" /> TN source filters ready</div>
          <button className="primary-command" disabled={busy || draft.mode !== 'TN' || !draft.aspects.length} onClick={() => onApply(draft)}><Play size={15} /> {busy ? 'Loading' : 'Apply view'}</button>
        </footer>
      </aside>
    </div>
  )
}
