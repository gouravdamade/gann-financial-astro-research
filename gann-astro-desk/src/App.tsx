import './App.css'
import { lazy, Suspense } from 'react'
import { MainWorkspace } from './views/MainWorkspace'

const AnalyzeAspectWindow = lazy(() => import('./views/AnalyzeAspectWindow').then((module) => ({
  default: module.AnalyzeAspectWindow,
})))

export default function App() {
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
