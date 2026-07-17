import {
  ChevronLeft,
  ChevronRight,
  History,
  Pause,
  Play,
  ShieldCheck,
  X,
} from 'lucide-react'
import { replayClockLabel } from '../barReplay'
import type { BarReplaySnapshot } from '../types'

type BarReplayControlsProps = {
  replay: BarReplaySnapshot | null
  selecting: boolean
  playing: boolean
  busy: boolean
  disabled?: boolean
  onSelectStart: () => void
  onPrevious: () => void
  onNext: () => void
  onTogglePlaying: () => void
  onExit: () => void
}

export function BarReplayControls({
  replay,
  selecting,
  playing,
  busy,
  disabled = false,
  onSelectStart,
  onPrevious,
  onNext,
  onTogglePlaying,
  onExit,
}: BarReplayControlsProps) {
  if (!replay) {
    return (
      <button
        className={`bar-replay-launch ${selecting ? 'is-active' : ''}`}
        onClick={onSelectStart}
        disabled={disabled || busy}
        title={disabled ? 'Bar Replay is available for historical charts' : 'Choose a closed candle to start timestamp-safe Bar Replay'}
      >
        <History size={13} />
        {selecting ? 'Click a candle' : 'Bar Replay'}
      </button>
    )
  }
  return (
    <div className="bar-replay-controls" aria-label="Timestamp-safe Bar Replay controls">
      <span className="bar-replay-clock">
        <ShieldCheck size={12} />
        <strong>{replayClockLabel(replay.cutoffUtc)}</strong>
        <small>{replay.position}/{replay.totalBars}</small>
      </span>
      <button className="icon-button" onClick={onPrevious} disabled={busy || !replay.previousCutoffUtc} title="Previous closed bar" aria-label="Previous closed bar"><ChevronLeft size={14} /></button>
      <button className="icon-button" onClick={onTogglePlaying} disabled={busy || (!playing && !replay.nextCutoffUtc)} title={playing ? 'Pause replay' : 'Play replay'} aria-label={playing ? 'Pause replay' : 'Play replay'}>{playing ? <Pause size={14} /> : <Play size={14} />}</button>
      <button className="icon-button" onClick={onNext} disabled={busy || !replay.nextCutoffUtc} title="Next closed bar" aria-label="Next closed bar"><ChevronRight size={14} /></button>
      <button className="icon-button" onClick={onExit} disabled={busy} title="Exit Bar Replay" aria-label="Exit Bar Replay"><X size={14} /></button>
    </div>
  )
}
