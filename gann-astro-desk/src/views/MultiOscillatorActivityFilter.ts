import type { MultiOscillatorActivityEvent } from '../types'

/**
 * Match display filter labels to canonical compiler identities without
 * changing the immutable event record or its hash inputs.
 */
export function canonicalAspectFilterKey(value: string | null | undefined): string {
  return (value ?? '').trim().toUpperCase()
}

export function eventMatchesActivityFilters(
  event: MultiOscillatorActivityEvent,
  activeBodies: string[],
  activeAspects: string[],
): boolean {
  if (!activeBodies.includes(event.transitBody)) return false
  const eventAspectKey = canonicalAspectFilterKey(event.aspectType)
  return activeAspects.some((aspect) => canonicalAspectFilterKey(aspect) === eventAspectKey)
}
