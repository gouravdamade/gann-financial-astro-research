import type {
  Candle,
  ChartParameters,
  PlanetaryLineGroup,
  PlanetaryLineOverlaySettings,
} from './types'

export const PLANETARY_LINE_PLANETS = [
  { planet: 'SUN', label: 'Sun', color: '#f2b84b' },
  { planet: 'MOON', label: 'Moon', color: '#c7d2df' },
  { planet: 'MERCURY', label: 'Mercury', color: '#70c1a8' },
  { planet: 'VENUS', label: 'Venus', color: '#df8fb4' },
  { planet: 'MARS', label: 'Mars', color: '#ef8354' },
  { planet: 'JUPITER', label: 'Jupiter', color: '#d9a441' },
  { planet: 'SATURN', label: 'Saturn', color: '#8fa1b4' },
  { planet: 'RAHU', label: 'Rahu', color: '#8d79c6' },
  { planet: 'KETU', label: 'Ketu', color: '#b8875b' },
  { planet: 'URANUS', label: 'Uranus', color: '#56bfc8' },
  { planet: 'NEPTUNE', label: 'Neptune', color: '#628dde' },
  { planet: 'PLUTO', label: 'Pluto', color: '#a2768d' },
  { planet: 'AVG(ALL)', label: 'AVG (All)', color: '#f2e96b' },
] as const

export const PLANETARY_LINE_MAX_VALUES = 12
export const PLANETARY_LINE_MAX_LINES = 96
export const PLANETARY_LINE_DEFAULT_SAMPLE_LIMIT = 600
const PLANETARY_LINE_CONTEXT_SAMPLE_COUNT = 72

type ParameterSeed = Pick<ChartParameters, 'nValues' | 'harmonics' | 'degrees'>

function cleanValues(
  values: unknown,
  fallback: number[],
  minimum: number,
  maximum: number,
): number[] {
  if (!Array.isArray(values)) return fallback
  const clean = values
    .map(Number)
    .filter((value) => Number.isFinite(value) && value >= minimum && value <= maximum)
    .filter((value, index, list) => list.indexOf(value) === index)
    .slice(0, PLANETARY_LINE_MAX_VALUES)
  return clean.length ? clean : fallback
}

export function defaultPlanetaryLineOverlaySettings(
  seed?: Partial<ParameterSeed>,
): PlanetaryLineOverlaySettings {
  const nValues = cleanValues(seed?.nValues, [1.2, 1.4, 1.6], 0.000001, 100_000)
  const fValues = cleanValues(seed?.harmonics, [0.12, 0.18], 0.000001, 1_000)
  const degrees = cleanValues(seed?.degrees, [360, 180], 0.000001, 360)
  return {
    contract: 'GANN_PLANETARY_LINE_LAB_SETTINGS_V1',
    visible: false,
    sampleLimit: PLANETARY_LINE_DEFAULT_SAMPLE_LIMIT,
    groups: PLANETARY_LINE_PLANETS.map(({ planet, color }) => ({
      planet,
      enabled: planet === 'AVG(ALL)',
      color,
      mode: 'direct',
      nValues: [...nValues],
      fValues: [...fValues],
      degrees: [...degrees],
    })),
  }
}

export function normalizePlanetaryLineSettings(
  value: PlanetaryLineOverlaySettings | undefined,
  seed?: Partial<ParameterSeed>,
): PlanetaryLineOverlaySettings {
  const defaults = defaultPlanetaryLineOverlaySettings(seed)
  if (!value || value.contract !== 'GANN_PLANETARY_LINE_LAB_SETTINGS_V1') return defaults
  const byPlanet = new Map(value.groups?.map((group) => [group.planet.toUpperCase(), group]) ?? [])
  return {
    ...defaults,
    visible: Boolean(value.visible),
    sampleLimit: Math.max(120, Math.min(1_200, Math.round(Number(value.sampleLimit) || defaults.sampleLimit))),
    groups: defaults.groups.map((fallback) => {
      const group = byPlanet.get(fallback.planet)
      if (!group) return fallback
      return {
        planet: fallback.planet,
        enabled: Boolean(group.enabled),
        color: /^#[0-9a-f]{6}$/i.test(group.color) ? group.color : fallback.color,
        mode: group.mode === 'mirror' || group.mode === 'both' ? group.mode : 'direct',
        nValues: cleanValues(group.nValues, fallback.nValues, 0.000001, 100_000),
        fValues: cleanValues(group.fValues, fallback.fValues, 0.000001, 1_000),
        degrees: cleanValues(group.degrees, fallback.degrees, 0.000001, 360),
      }
    }),
  }
}

export function parsePlanetaryLineValues(
  text: string,
  label: string,
  minimum: number,
  maximum: number,
): number[] {
  const tokens = text.split(/[\s,;]+/).filter(Boolean)
  if (!tokens.length) throw new Error(`${label} needs at least one number`)
  if (tokens.length > PLANETARY_LINE_MAX_VALUES) {
    throw new Error(`${label} allows at most ${PLANETARY_LINE_MAX_VALUES} values`)
  }
  const values = tokens.map((token) => Number(token))
  if (values.some((value) => !Number.isFinite(value) || value < minimum || value > maximum)) {
    throw new Error(`${label} values must be between ${minimum} and ${maximum}`)
  }
  return values.filter((value, index, list) => list.indexOf(value) === index)
}

export function planetaryLineGroupCount(group: PlanetaryLineGroup): number {
  if (!group.enabled) return 0
  const directions = group.mode === 'both' ? 2 : 1
  return group.nValues.length * group.fValues.length * group.degrees.length * directions
}

export function planetaryLineCount(settings: PlanetaryLineOverlaySettings): number {
  return settings.groups.reduce((total, group) => total + planetaryLineGroupCount(group), 0)
}

export function sampledVisibleCandleTimes(
  candles: Candle[],
  visibleStartUtc: string | undefined,
  visibleEndUtc: string | undefined,
  limit: number,
): number[] {
  if (!candles.length) return []
  const start = visibleStartUtc ? new Date(visibleStartUtc).getTime() / 1_000 : candles[0].time
  const end = visibleEndUtc ? new Date(visibleEndUtc).getTime() / 1_000 : candles.at(-1)!.time
  const span = Math.max(0, end - start)
  const paddedStart = start - span * 0.08
  const paddedEnd = end + span * 0.08
  const visible = candles.filter((candle) => candle.time >= paddedStart && candle.time <= paddedEnd)
  const source = visible.length ? visible : candles
  const safeLimit = Math.max(2, Math.min(1_200, Math.round(limit)))

  const sample = (items: Candle[], count: number) => {
    if (items.length <= count) return items.map((candle) => candle.time)
    const indices = new Set<number>([0, items.length - 1])
    for (let position = 1; position < count - 1; position += 1) {
      indices.add(Math.round(position * (items.length - 1) / (count - 1)))
    }
    return [...indices].sort((left, right) => left - right).map((index) => items[index].time)
  }

  const hasViewport = Boolean(visibleStartUtc && visibleEndUtc)
  if (!hasViewport || candles.length <= safeLimit) return sample(candles, safeLimit)

  // Preserve sparse whole-chart anchors while adding dense viewport points. That
  // keeps a rendered Live SR line continuous through a fast wheel zoom while
  // the next exact viewport request is still being calculated.
  const contextCount = Math.min(PLANETARY_LINE_CONTEXT_SAMPLE_COUNT, Math.max(2, Math.floor(safeLimit / 4)))
  const viewportCount = Math.max(2, safeLimit - contextCount)
  return [...new Set([
    ...sample(candles, contextCount),
    ...sample(source, viewportCount),
  ])].sort((left, right) => left - right)
}

export function enabledPlanetaryLineGroups(settings: PlanetaryLineOverlaySettings): PlanetaryLineGroup[] {
  return settings.groups.filter((group) => group.enabled)
}
