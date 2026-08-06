import type {
  ChartConditionedPolarityRangeInterval,
  FxPairRelativeCategoricalField,
  FxPairRelativeCategoricalInterval,
  SynchronizedIndependentRange,
} from './types'

type SideBalance = {
  state: ChartConditionedPolarityRangeInterval['polarityState'] | 'UNKNOWN_SIDE_EVIDENCE'
  balance: number | null
  supportiveActive: boolean
  adverseActive: boolean
  grossActivity: number | null
  conflict: boolean
  unknownReason: string | null
}

function instant(value: string): number {
  return Date.parse(value)
}

function intervalAt(
  intervals: ChartConditionedPolarityRangeInterval[],
  startUtc: string,
): ChartConditionedPolarityRangeInterval | null {
  const at = instant(startUtc)
  return intervals.find((interval) => (
    instant(interval.startUtc) <= at && at < instant(interval.endUtc)
  )) ?? null
}

function sideBalance(interval: ChartConditionedPolarityRangeInterval | null): SideBalance {
  if (!interval || interval.polarityState === 'UNKNOWN') {
    return {
      state: 'UNKNOWN_SIDE_EVIDENCE',
      balance: null,
      supportiveActive: false,
      adverseActive: false,
      grossActivity: null,
      conflict: false,
      unknownReason: interval?.reason ?? 'NO_ACTIVE_REVIEWED_SIDE_EVENT',
    }
  }

  const supportive = interval.supportiveActive
  const adverse = interval.adverseActive
  const grossActivity = Number(supportive) + Number(adverse)
  const net = Number(supportive) - Number(adverse)
  return {
    state: interval.polarityState,
    // Explicitly neutral source intervals are known zero. Other known states
    // with no active component remain a known zero, never an implicit unknown.
    balance: grossActivity > 0 ? net / grossActivity : 0,
    supportiveActive: supportive,
    adverseActive: adverse,
    grossActivity,
    conflict: supportive && adverse,
    unknownReason: null,
  }
}

function stateForPair(
  base: SideBalance,
  quote: SideBalance,
  pairDisplay: number | null,
): FxPairRelativeCategoricalInterval['state'] {
  if (base.balance == null || quote.balance == null || pairDisplay == null) return 'UNKNOWN_SIDE_EVIDENCE'
  if (base.state === 'MIXED' || quote.state === 'MIXED' || base.conflict || quote.conflict) return 'MIXED'
  if (pairDisplay > 0) return 'SUPPORTIVE'
  if (pairDisplay < 0) return 'ADVERSE'
  return 'NEUTRAL'
}

function mergeBoundaries(range: SynchronizedIndependentRange): string[] {
  const values = new Set<string>([range.rangeStartUtc, range.rangeEndUtc])
  for (const side of ['USD', 'JPY'] as const) {
    for (const interval of range.aspectFields[side].intervals) {
      values.add(interval.startUtc)
      values.add(interval.endUtc)
    }
  }
  return [...values]
    .filter((value) => Number.isFinite(instant(value)))
    .sort((left, right) => instant(left) - instant(right))
}

/**
 * Builds exact pair steps from the union of existing USD and JPY boundaries.
 * It never samples, stretches, smooths, or substitutes missing evidence.
 */
export function compileFxPairRelativeCategoricalField(
  range: SynchronizedIndependentRange,
): FxPairRelativeCategoricalField {
  const boundaries = mergeBoundaries(range)
  const intervals: FxPairRelativeCategoricalInterval[] = []
  for (let index = 0; index < boundaries.length - 1; index += 1) {
    const startUtc = boundaries[index]
    const endUtc = boundaries[index + 1]
    if (instant(endUtc) <= instant(startUtc)) continue
    const baseSource = intervalAt(range.aspectFields.USD.intervals, startUtc)
    const quoteSource = intervalAt(range.aspectFields.JPY.intervals, startUtc)
    const base = sideBalance(baseSource)
    const quote = sideBalance(quoteSource)
    const pairRaw = base.balance == null || quote.balance == null ? null : base.balance - quote.balance
    const pairDisplay = pairRaw == null ? null : Math.max(-1, Math.min(1, pairRaw / 2))
    const state = stateForPair(base, quote, pairDisplay)
    const unknownReason = state === 'UNKNOWN_SIDE_EVIDENCE'
      ? [base.unknownReason, quote.unknownReason].filter(Boolean).join('; ') || 'UNKNOWN_SIDE_EVIDENCE'
      : null
    intervals.push({
      intervalId: `FX_PAIR_RELATIVE:${startUtc}:${endUtc}`,
      startUtc,
      endUtc,
      state,
      baseBalance: base.balance,
      quoteBalance: quote.balance,
      pairRaw,
      pairDisplay,
      baseSupportiveActive: base.supportiveActive,
      baseAdverseActive: base.adverseActive,
      baseGrossActivity: base.grossActivity,
      quoteSupportiveActive: quote.supportiveActive,
      quoteAdverseActive: quote.adverseActive,
      quoteGrossActivity: quote.grossActivity,
      commonActivity: base.grossActivity == null || quote.grossActivity == null
        ? null
        : Math.min(base.grossActivity, quote.grossActivity),
      conflict: base.conflict || quote.conflict,
      coverage: state === 'UNKNOWN_SIDE_EVIDENCE' ? 'UNKNOWN' : 'KNOWN',
      unknownReason,
      sourceIntervalIds: {
        base: baseSource?.intervalId ?? null,
        quote: quoteSource?.intervalId ?? null,
      },
    })
  }

  return {
    contract: 'FX_PAIR_RELATIVE_CATEGORICAL_FIELD_V1',
    schemaVersion: 1,
    instrumentKind: 'FX',
    baseIdentity: 'USD',
    quoteIdentity: 'JPY',
    rangeStartUtc: range.rangeStartUtc,
    rangeEndUtc: range.rangeEndUtc,
    intervals,
    magnitudeState: 'MAGNITUDE_NOT_CONFIGURED',
    classification: 'MODERN_ENGINEERING_RESEARCH_TRANSFORM',
    guardrails: {
      classicalDoctrine: false,
      marketForecast: false,
      sbcConfirmation: false,
      curveFitting: false,
      smoothing: false,
      executionAllowed: false,
      automaticOrderPlacement: false,
    },
  }
}
