import type { AspectWindow } from './types'

export function canToggleReview(occurrence: AspectWindow): boolean {
  return occurrence.reviewSource !== 'legacy_completed_review'
}

export function nextReviewStatus(occurrence: AspectWindow): 'pending' | 'reviewed' {
  return occurrence.reviewed ? 'pending' : 'reviewed'
}

export function reviewButtonLabel(occurrence: AspectWindow, saving: boolean): string {
  if (saving) return 'Saving'
  if (occurrence.reviewSource === 'legacy_completed_review') return 'Legacy review complete'
  return occurrence.reviewed ? 'Reviewed' : 'Mark reviewed'
}
