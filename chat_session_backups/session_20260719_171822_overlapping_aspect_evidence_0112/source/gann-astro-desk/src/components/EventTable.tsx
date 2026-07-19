import type { AspectWindow } from '../types'

type EventTableProps = {
  events: AspectWindow[]
  selectedId?: string | null
  onSelect: (event: AspectWindow) => void
}

function durationLabel(minutes: number): string {
  if (minutes >= 1440) return `${(minutes / 1440).toFixed(1)}d`
  return `${(minutes / 60).toFixed(1)}h`
}

export function EventTable({ events, selectedId, onSelect }: EventTableProps) {
  return (
    <div className="event-table-wrap">
      <table className="event-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Transit to natal</th>
            <th>Aspect</th>
            <th>Duration</th>
            <th>Orb</th>
            <th>Known history</th>
            <th>72h</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr
              key={event.eventId}
              className={event.eventId === selectedId ? 'is-selected' : ''}
              onClick={() => onSelect(event)}
            >
              <td>{new Date(event.start * 1000).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</td>
              <td><span className="event-swatch" style={{ background: event.color }} />{event.transitBody} to {event.natalBody}</td>
              <td>{event.aspectLabel}</td>
              <td>{durationLabel(event.durationMinutes)}</td>
              <td>{event.peakOrbDeg.toFixed(3)} deg</td>
              <td>{event.knownPriorCount} prior</td>
              <td className={event.outcome === 'UP' ? 'positive' : event.outcome === 'DOWN' ? 'negative' : ''}>
                {event.returnPct == null ? 'pending' : `${event.returnPct > 0 ? '+' : ''}${event.returnPct.toFixed(2)}%`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
