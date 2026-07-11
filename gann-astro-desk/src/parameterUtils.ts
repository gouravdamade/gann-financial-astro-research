export function datetimeInputValue(value: string): string {
  return value.slice(0, 16)
}

export function datetimeParameterValue(value: string): string {
  return `${value}:00+05:30`
}

export function parseNumberList(value: string): number[] {
  return value
    .split(/[\s,]+/)
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => Number(item))
    .filter((item) => Number.isFinite(item))
}

export function toggleValue(values: string[], value: string): string[] {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value]
}

export function aspectLabel(value: string): string {
  return value.replace('_orb', '').replaceAll('_', ' ')
}
