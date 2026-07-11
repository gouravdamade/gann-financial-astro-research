import type { AspectWindow } from './types'

function windowLabel(familyKey: string): string {
  return `analyze-${familyKey.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 48)}`
}

export async function openAnalyzeAspect(aspect: AspectWindow): Promise<void> {
  const query = new URLSearchParams({
    view: 'analyze',
    family: aspect.familyKey,
    event: aspect.eventId,
  })
  const url = `${window.location.origin}${window.location.pathname}?${query}`
  if ('__TAURI_INTERNALS__' in window) {
    const { WebviewWindow } = await import('@tauri-apps/api/webviewWindow')
    const label = windowLabel(aspect.familyKey)
    const existing = await WebviewWindow.getByLabel(label)
    if (existing) {
      await existing.setFocus()
      return
    }
    new WebviewWindow(label, {
      url,
      title: `Analyze Aspect - ${aspect.transitBody} to ${aspect.natalBody} ${aspect.aspectLabel}`,
      width: 1480,
      height: 900,
      minWidth: 1080,
      minHeight: 700,
      resizable: true,
      center: true,
    })
    return
  }
  window.open(url, windowLabel(aspect.familyKey), 'popup,width=1480,height=900,resizable=yes')
}
