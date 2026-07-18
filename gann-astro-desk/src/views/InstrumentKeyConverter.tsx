import { Check, Languages } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import {
  suggestInstrumentInitialKey,
  type InstrumentKeyCandidate,
  type InstrumentReadingMode,
} from '../instrumentKeyConverter'

type Props = {
  onApply: (candidate: InstrumentKeyCandidate) => void
}

function candidateId(candidate: InstrumentKeyCandidate): string {
  return `${candidate.layer}:${candidate.key}`
}

export function InstrumentKeyConverter({ onApply }: Props) {
  const [instrument, setInstrument] = useState('')
  const [mode, setMode] = useState<InstrumentReadingMode>('ticker')
  const suggestion = useMemo(
    () => suggestInstrumentInitialKey(instrument, mode),
    [instrument, mode],
  )
  const [selectedId, setSelectedId] = useState('')

  useEffect(() => {
    const onlyCandidate = suggestion.candidates[0]
    setSelectedId(
      suggestion.candidates.length === 1 && onlyCandidate
        ? candidateId(onlyCandidate)
        : '',
    )
  }, [suggestion])

  const selected = suggestion.candidates.find(
    (item) => candidateId(item) === selectedId,
  )

  return (
    <details className="chakra-key-converter">
      <summary>
        <Languages size={13} />
        <strong>English stock key converter</strong>
        <span>Advisory</span>
      </summary>
      <div className="chakra-key-converter-body">
        <label>
          Stock name or ticker
          <input
            value={instrument}
            placeholder="USDJPY or AAPL"
            onChange={(event) => setInstrument(event.target.value)}
          />
        </label>
        <label>
          Reading basis
          <select
            value={mode}
            onChange={(event) => setMode(event.target.value as InstrumentReadingMode)}
          >
            <option value="ticker">Ticker, spoken letter-by-letter</option>
            <option value="company">English company name</option>
          </select>
        </label>

        {suggestion.status !== 'empty' && (
          <div className={`chakra-key-result is-${suggestion.status}`}>
            <div>
              <span>Hindi sound</span>
              <strong>{suggestion.spokenHindi || 'Human review needed'}</strong>
            </div>
            <div>
              <span>First Latin</span>
              <strong>{suggestion.leadingLatin || '—'}</strong>
            </div>
            <p>{suggestion.explanation}</p>

            {suggestion.candidates.length > 0 && (
              <>
                <label>
                  Suggested Chakra key
                  <select
                    value={selectedId}
                    onChange={(event) => setSelectedId(event.target.value)}
                  >
                    {suggestion.candidates.length > 1 && (
                      <option value="">Choose after checking pronunciation</option>
                    )}
                    {suggestion.candidates.map((item) => (
                      <option key={candidateId(item)} value={candidateId(item)}>
                        {item.layer} · {item.key} · {item.glyph}
                        {item.hindiInitial !== item.glyph ? ` (sound ${item.hindiInitial})` : ''}
                      </option>
                    ))}
                  </select>
                </label>
                {selected && (
                  <div className="chakra-key-selection-note">
                    <span>{selected.confidence === 'exact' ? 'Exact spoken initial' : 'Review required'}</span>
                    <p>{selected.reason}</p>
                  </div>
                )}
                <button
                  className="secondary-command chakra-key-apply"
                  disabled={!selected}
                  onClick={() => selected && onApply(selected)}
                >
                  <Check size={12} />
                  Use selected key
                </button>
              </>
            )}
          </div>
        )}

        <small>
          Suggestions are not accepted instrument mappings or financial signals.
          Applying only copies one certified key into Context.
        </small>
      </div>
    </details>
  )
}
