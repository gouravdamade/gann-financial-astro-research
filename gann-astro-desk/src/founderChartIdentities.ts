// Immutable R3 research identities. These wire only the accepted registry
// records into synchronized requests; they do not admit polarity events.
export const FOUNDER_ACCEPTED_FX_SIDE_CHARTS = {
  USD: {
    chartId: 'FX_CURRENCY_USD_US_INDEPENDENCE_17760704T165602Z_V1',
    chartHypothesisId: 'USD_US_INDEPENDENCE_PHILADELPHIA_EXACT_TIME_RESEARCH_V1',
  },
  JPY: {
    chartId: 'FX_CURRENCY_JPY_YEN_IPO_18890210T150000Z_V1',
    chartHypothesisId: 'JPY_YEN_IPO_TOKYO_EXACT_TIME_RESEARCH_V1',
  },
} as const
