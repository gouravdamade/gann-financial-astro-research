import './App.css'
import { AnalyzeAspectWindow } from './views/AnalyzeAspectWindow'
import { MainWorkspace } from './views/MainWorkspace'

export default function App() {
  const params = new URLSearchParams(window.location.search)
  if (params.get('view') === 'analyze' && params.get('family')) {
    return (
      <AnalyzeAspectWindow
        familyKey={String(params.get('family'))}
        initialEventId={params.get('event')}
      />
    )
  }
  return <MainWorkspace />
}
