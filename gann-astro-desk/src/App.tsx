import './App.css'
import { lazy, Suspense, useEffect, useState } from 'react'
import { MainWorkspace } from './views/MainWorkspace'
import { MobileCompanionSetup } from './components/MobileCompanionSetup'
import { fetchRuntimeProfile } from './runtimeProfile'
import { disconnectCompanion, getCompanionSession, restoreCompanionSession, startCompanionStream } from './companion'
import type { RuntimeProfile } from './types'

const AnalyzeAspectWindow = lazy(() => import('./views/AnalyzeAspectWindow').then((module) => ({
  default: module.AnalyzeAspectWindow,
})))

export default function App() {
  const [profile, setProfile] = useState<RuntimeProfile | null>(null)
  const [profileError, setProfileError] = useState('')
  const [companionPaired, setCompanionPaired] = useState(() => getCompanionSession() != null)
  const [companionChecked, setCompanionChecked] = useState(false)

  useEffect(() => {
    let active = true
    void fetchRuntimeProfile()
      .then((runtime) => {
        if (active) setProfile(runtime)
      })
      .catch((error: unknown) => {
        if (active) setProfileError(error instanceof Error ? error.message : 'Unable to identify runtime')
      })
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!profile || profile.backendMode !== 'remote_companion') {
      if (profile) setCompanionChecked(true)
      return
    }
    let active = true
    void restoreCompanionSession()
      .then((session) => {
        if (active) setCompanionPaired(session != null)
      })
      .catch(() => {
        if (active) setCompanionPaired(false)
      })
      .finally(() => {
        if (active) setCompanionChecked(true)
      })
    return () => {
      active = false
    }
  }, [profile])

  useEffect(() => {
    if (companionPaired) void startCompanionStream().catch(() => undefined)
  }, [companionPaired])

  useEffect(() => {
    if (profile?.backendMode !== 'remote_companion') return
    let disposed = false
    let unlisten: (() => void) | undefined
    const invalidate = () => {
      if (disposed) return
      void disconnectCompanion().catch(() => undefined)
      setCompanionPaired(false)
    }
    window.addEventListener('gann-astro-companion-invalid', invalidate)
    if ('__TAURI_INTERNALS__' in window) {
      void import('@tauri-apps/api/event')
        .then(({ listen }) => listen('companion-session-invalid', invalidate))
        .then((stop) => {
          if (disposed) stop()
          else unlisten = stop
        })
    }
    return () => {
      disposed = true
      unlisten?.()
      window.removeEventListener('gann-astro-companion-invalid', invalidate)
    }
  }, [profile?.backendMode])

  if (profileError) {
    return <main className="loading-state"><strong>Runtime unavailable</strong><span>{profileError}</span></main>
  }
  if (!profile) {
    return <main className="loading-state"><strong>Opening workspace</strong></main>
  }
  if (profile.backendMode === 'remote_companion' && !companionChecked) {
    return <main className="loading-state"><strong>Restoring secure companion session</strong></main>
  }
  if (profile.backendMode === 'remote_companion' && !profile.configured && !companionPaired) {
    return <MobileCompanionSetup onPaired={() => setCompanionPaired(true)} />
  }

  const params = new URLSearchParams(window.location.search)
  if (params.get('view') === 'analyze' && params.get('family')) {
    return (
      <Suspense fallback={<main className="loading-state"><strong>Opening aspect review</strong></main>}>
        <AnalyzeAspectWindow
          familyKey={String(params.get('family'))}
          initialEventId={params.get('event')}
        />
      </Suspense>
    )
  }
  return <MainWorkspace showCompanionGateway={profile.backendMode === 'managed_sidecar'} />
}
