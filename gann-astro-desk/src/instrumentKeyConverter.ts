export type InstrumentKeyLayer = 'VOWEL' | 'NAME_INITIAL'
export type InstrumentReadingMode = 'ticker' | 'company'
export type InstrumentMappingConfidence = 'exact' | 'review'

export type InstrumentKeyCandidate = {
  layer: InstrumentKeyLayer
  key: string
  glyph: string
  hindiInitial: string
  confidence: InstrumentMappingConfidence
  reason: string
}

export type InstrumentKeySuggestion = {
  contract: 'SBC_ENGLISH_INITIAL_ADVISORY_V1'
  normalizedInput: string
  mode: InstrumentReadingMode
  spokenHindi: string
  leadingLatin: string
  candidates: InstrumentKeyCandidate[]
  status: 'empty' | 'ready' | 'review' | 'unsupported'
  explanation: string
}

type CandidateSeed = Omit<InstrumentKeyCandidate, 'reason'> & {
  reason?: string
}

const candidate = (
  layer: InstrumentKeyLayer,
  key: string,
  glyph: string,
  hindiInitial: string,
  confidence: InstrumentMappingConfidence = 'exact',
  reason = '',
): CandidateSeed => ({
  layer,
  key,
  glyph,
  hindiInitial,
  confidence,
  reason,
})

const TICKER_LETTERS: Record<string, {
  spokenHindi: string
  candidates: CandidateSeed[]
}> = {
  A: { spokenHindi: 'ए', candidates: [candidate('VOWEL', 'E', 'ए', 'ए')] },
  B: { spokenHindi: 'बी', candidates: [] },
  C: { spokenHindi: 'सी', candidates: [candidate('NAME_INITIAL', 'SA', 'स', 'स')] },
  D: { spokenHindi: 'डी', candidates: [candidate('NAME_INITIAL', 'DDA', 'ड', 'ड')] },
  E: { spokenHindi: 'ई', candidates: [candidate('VOWEL', 'II', 'ई', 'ई')] },
  F: { spokenHindi: 'एफ', candidates: [candidate('VOWEL', 'E', 'ए', 'ए')] },
  G: { spokenHindi: 'जी', candidates: [candidate('NAME_INITIAL', 'JA', 'ज', 'ज')] },
  H: { spokenHindi: 'एच', candidates: [candidate('VOWEL', 'E', 'ए', 'ए')] },
  I: { spokenHindi: 'आई', candidates: [candidate('VOWEL', 'AI', 'ऐ', 'ऐ')] },
  J: { spokenHindi: 'जे', candidates: [candidate('NAME_INITIAL', 'JA', 'ज', 'ज')] },
  K: { spokenHindi: 'के', candidates: [candidate('NAME_INITIAL', 'KA', 'क', 'क')] },
  L: { spokenHindi: 'एल', candidates: [candidate('VOWEL', 'E', 'ए', 'ए')] },
  M: { spokenHindi: 'एम', candidates: [candidate('VOWEL', 'E', 'ए', 'ए')] },
  N: { spokenHindi: 'एन', candidates: [candidate('VOWEL', 'E', 'ए', 'ए')] },
  O: { spokenHindi: 'ओ', candidates: [candidate('VOWEL', 'O', 'ओ', 'ओ')] },
  P: { spokenHindi: 'पी', candidates: [candidate('NAME_INITIAL', 'PA', 'प', 'प')] },
  Q: { spokenHindi: 'क्यू', candidates: [candidate('NAME_INITIAL', 'KA', 'क', 'क')] },
  R: { spokenHindi: 'आर', candidates: [candidate('VOWEL', 'AA', 'आ', 'आ')] },
  S: { spokenHindi: 'एस', candidates: [candidate('VOWEL', 'E', 'ए', 'ए')] },
  T: { spokenHindi: 'टी', candidates: [candidate('NAME_INITIAL', 'TTA', 'ट', 'ट')] },
  U: { spokenHindi: 'यू', candidates: [candidate('NAME_INITIAL', 'YA', 'य', 'य')] },
  V: { spokenHindi: 'वी', candidates: [candidate('NAME_INITIAL', 'VA', 'व', 'व')] },
  W: { spokenHindi: 'डब्ल्यू', candidates: [candidate('NAME_INITIAL', 'DDA', 'ड', 'ड')] },
  X: { spokenHindi: 'एक्स', candidates: [candidate('VOWEL', 'E', 'ए', 'ए')] },
  Y: { spokenHindi: 'वाय', candidates: [candidate('NAME_INITIAL', 'VA', 'व', 'व')] },
  Z: {
    spokenHindi: 'ज़ेड',
    candidates: [
      candidate(
        'NAME_INITIAL',
        'JA',
        'ज',
        'ज़',
        'review',
        'The certified board has JA/ज but no exact za/ज़ cell.',
      ),
    ],
  },
}

const COMPANY_DIGRAPHS: Record<string, CandidateSeed[]> = {
  BH: [candidate('NAME_INITIAL', 'BHA', 'भ', 'भ')],
  CH: [candidate('NAME_INITIAL', 'CHA', 'च', 'च')],
  DH: [
    candidate(
      'NAME_INITIAL',
      'DA',
      'द',
      'ध',
      'review',
      'The certified board has DA/द but no exact dha/ध cell.',
    ),
  ],
  GH: [
    candidate(
      'NAME_INITIAL',
      'GA',
      'ग',
      'घ',
      'review',
      'The certified board has GA/ग but no exact gha/घ cell.',
    ),
  ],
  KH: [candidate('NAME_INITIAL', 'KHA', 'ख', 'ख')],
  PH: [
    candidate(
      'NAME_INITIAL',
      'PA',
      'प',
      'फ',
      'review',
      'The certified board has PA/प but no exact pha/फ cell.',
    ),
  ],
  SH: [
    candidate(
      'NAME_INITIAL',
      'SA',
      'स',
      'श',
      'review',
      'The certified board has SA/स but no exact sha/श cell.',
    ),
  ],
  TH: [
    candidate(
      'NAME_INITIAL',
      'TA',
      'त',
      'थ',
      'review',
      'The certified board has TA/त but no exact tha/थ cell.',
    ),
  ],
}

const COMPANY_INITIALS: Record<string, CandidateSeed[]> = {
  A: [
    candidate('VOWEL', 'A', 'अ', 'अ', 'review'),
    candidate('VOWEL', 'AI', 'ऐ', 'ऐ', 'review'),
  ],
  B: [],
  C: [
    candidate('NAME_INITIAL', 'KA', 'क', 'क', 'review'),
    candidate('NAME_INITIAL', 'SA', 'स', 'स', 'review'),
  ],
  D: [
    candidate('NAME_INITIAL', 'DA', 'द', 'द', 'review'),
    candidate('NAME_INITIAL', 'DDA', 'ड', 'ड', 'review'),
  ],
  E: [
    candidate('VOWEL', 'E', 'ए', 'ए', 'review'),
    candidate('VOWEL', 'I', 'इ', 'इ', 'review'),
  ],
  F: [
    candidate(
      'NAME_INITIAL',
      'PA',
      'प',
      'फ',
      'review',
      'The certified board has PA/प but no exact pha/फ cell.',
    ),
  ],
  G: [
    candidate('NAME_INITIAL', 'GA', 'ग', 'ग', 'review'),
    candidate('NAME_INITIAL', 'JA', 'ज', 'ज', 'review'),
  ],
  H: [candidate('NAME_INITIAL', 'HA', 'ह', 'ह', 'review')],
  I: [
    candidate('VOWEL', 'I', 'इ', 'इ', 'review'),
    candidate('VOWEL', 'AI', 'ऐ', 'ऐ', 'review'),
  ],
  J: [candidate('NAME_INITIAL', 'JA', 'ज', 'ज', 'review')],
  K: [candidate('NAME_INITIAL', 'KA', 'क', 'क', 'review')],
  L: [candidate('NAME_INITIAL', 'LA', 'ल', 'ल', 'review')],
  M: [candidate('NAME_INITIAL', 'MA', 'म', 'म', 'review')],
  N: [candidate('NAME_INITIAL', 'NA', 'न', 'न', 'review')],
  O: [
    candidate('VOWEL', 'O', 'ओ', 'ओ', 'review'),
    candidate('VOWEL', 'AU', 'औ', 'औ', 'review'),
  ],
  P: [candidate('NAME_INITIAL', 'PA', 'प', 'प', 'review')],
  Q: [candidate('NAME_INITIAL', 'KA', 'क', 'क', 'review')],
  R: [candidate('NAME_INITIAL', 'RA', 'र', 'र', 'review')],
  S: [candidate('NAME_INITIAL', 'SA', 'स', 'स', 'review')],
  T: [
    candidate('NAME_INITIAL', 'TA', 'त', 'त', 'review'),
    candidate('NAME_INITIAL', 'TTA', 'ट', 'ट', 'review'),
  ],
  U: [
    candidate('VOWEL', 'A', 'अ', 'अ', 'review'),
    candidate('VOWEL', 'U', 'उ', 'उ', 'review'),
    candidate('VOWEL', 'UU', 'ऊ', 'ऊ', 'review'),
    candidate('NAME_INITIAL', 'YA', 'य', 'य', 'review'),
  ],
  V: [candidate('NAME_INITIAL', 'VA', 'व', 'व', 'review')],
  W: [candidate('NAME_INITIAL', 'VA', 'व', 'व', 'review')],
  X: [
    candidate('NAME_INITIAL', 'JA', 'ज', 'ज', 'review'),
    candidate('NAME_INITIAL', 'KA', 'क', 'क', 'review'),
  ],
  Y: [candidate('NAME_INITIAL', 'YA', 'य', 'य', 'review')],
  Z: [
    candidate(
      'NAME_INITIAL',
      'JA',
      'ज',
      'ज़',
      'review',
      'The certified board has JA/ज but no exact za/ज़ cell.',
    ),
  ],
}

function withDefaultReason(
  seed: CandidateSeed,
  mode: InstrumentReadingMode,
): InstrumentKeyCandidate {
  return {
    ...seed,
    reason: seed.reason || (
      mode === 'ticker'
        ? 'Derived from the standard spoken English letter name.'
        : 'English company-name pronunciation must be confirmed by a human reviewer.'
    ),
  }
}

function emptySuggestion(
  normalizedInput: string,
  mode: InstrumentReadingMode,
  explanation: string,
): InstrumentKeySuggestion {
  return {
    contract: 'SBC_ENGLISH_INITIAL_ADVISORY_V1',
    normalizedInput,
    mode,
    spokenHindi: '',
    leadingLatin: '',
    candidates: [],
    status: normalizedInput ? 'unsupported' : 'empty',
    explanation,
  }
}

export function suggestInstrumentInitialKey(
  rawInput: string,
  mode: InstrumentReadingMode,
): InstrumentKeySuggestion {
  const normalizedInput = rawInput.trim().toUpperCase()
  if (!normalizedInput) {
    return emptySuggestion('', mode, 'Enter an English stock name or ticker.')
  }

  const letters = normalizedInput.match(/[A-Z]/g) ?? []
  if (!letters.length) {
    return emptySuggestion(
      normalizedInput,
      mode,
      'No Latin A-Z letter was found. This advisory converter does not infer non-English names.',
    )
  }

  const leadingLatin = letters[0]
  if (!leadingLatin) {
    return emptySuggestion(
      normalizedInput,
      mode,
      'No usable leading Latin letter was found.',
    )
  }
  if (mode === 'ticker') {
    const spokenHindi = letters
      .map((letter) => TICKER_LETTERS[letter]?.spokenHindi ?? letter)
      .join('-')
    const candidates = (TICKER_LETTERS[leadingLatin]?.candidates ?? [])
      .map((item) => withDefaultReason(item, mode))
    if (!candidates.length) {
      return {
        ...emptySuggestion(normalizedInput, mode, ''),
        spokenHindi,
        leadingLatin,
        explanation:
          `The spoken ticker begins ${TICKER_LETTERS[leadingLatin]?.spokenHindi ?? leadingLatin}, `
          + 'but its first sound has no exact certified Chakra key. Record it for human review.',
      }
    }
    return {
      contract: 'SBC_ENGLISH_INITIAL_ADVISORY_V1',
      normalizedInput,
      mode,
      spokenHindi,
      leadingLatin,
      candidates,
      status: candidates.every((item) => item.confidence === 'exact') ? 'ready' : 'review',
      explanation:
        'Ticker mode spells the symbol letter-by-letter. It does not use the company-name pronunciation.',
    }
  }

  const leadingPair = normalizedInput.match(/[A-Z]{2}/)?.[0] ?? ''
  const seeds = COMPANY_DIGRAPHS[leadingPair] ?? COMPANY_INITIALS[leadingLatin] ?? []
  const candidates = seeds.map((item) => withDefaultReason(item, mode))
  const spokenHindi = candidates.length
    ? [...new Set(candidates.map((item) => item.hindiInitial))].join(' / ')
    : ''
  if (!candidates.length) {
    return {
      ...emptySuggestion(normalizedInput, mode, ''),
      spokenHindi,
      leadingLatin,
      explanation:
        'The likely company-name initial has no exact certified Chakra key. '
        + 'Supply a reviewed pronunciation and mapping instead of forcing a nearest letter.',
    }
  }
  return {
    contract: 'SBC_ENGLISH_INITIAL_ADVISORY_V1',
    normalizedInput,
    mode,
    spokenHindi,
    leadingLatin,
    candidates,
    status: 'review',
    explanation:
      'Company-name mode uses spelling only to suggest candidates. Confirm the actual spoken first sound before applying one.',
  }
}
