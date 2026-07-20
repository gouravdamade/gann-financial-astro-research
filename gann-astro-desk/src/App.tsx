import './App.css'
import { lazy, Suspense, useEffect, useState } from 'react'
import { MainWorkspace } from './views/MainWorkspace'
import { MobileCompanionSetup } from './components/MobileCompanionSetup'
import { fetchRuntimeProfile } from './runtimeProfile'
import { getCompanionSession } from './companion'
import type { RuntimeProfile } from './types'

const AnalyzeAspectWindow = lazy(() => import('./views/AnalyzeAspectWindow').then((module) => ({
  default: module.AnalyzeAspectWindow,
})))

export default function App() {
  const [profile, setProfile] = useState<RuntimeProfile | null>(null)
  const [profileError, setProfileError] = useState('')
  const [companionPaired, setCompanionPaired] = useState(() => getCompanionSession() != null)

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

  if (profileError) {
    return <main className="loading-state"><strong>Runtime unavailable</strong><span>{profileError}</span></main>
  }
  if (!profile) {
    return <main className="loading-state"><strong>Opening workspace</strong></main>
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
  return <MainWorkspace />
}
