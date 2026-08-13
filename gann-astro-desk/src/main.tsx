import { Component, StrictMode, type ErrorInfo, type ReactNode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { recordFrontendDiagnostic } from './api'

function reportBootstrapFailure() {
  void recordFrontendDiagnostic('app_bootstrap', performance.now(), false).catch(() => undefined)
}

function showFatalBootstrapFailure() {
  reportBootstrapFailure()
  const root = document.getElementById('root')
  if (!root) return
  root.innerHTML = `
    <main class="bootstrap-fallback is-error" role="alert">
      <strong>Workspace could not be displayed</strong>
      <span>Restart Gann Astro Desk. The research data and execution locks remain unchanged.</span>
    </main>`
}

class AppErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  state = { failed: false }

  static getDerivedStateFromError() {
    return { failed: true }
  }

  componentDidCatch(_error: Error, _errorInfo: ErrorInfo) {
    reportBootstrapFailure()
  }

  render() {
    if (this.state.failed) {
      return (
        <main className="bootstrap-fallback is-error" role="alert">
          <strong>Workspace could not be displayed</strong>
          <span>Restart Gann Astro Desk. The research data and execution locks remain unchanged.</span>
        </main>
      )
    }
    return this.props.children
  }
}

window.addEventListener('error', reportBootstrapFailure)
window.addEventListener('unhandledrejection', reportBootstrapFailure)

try {
  const root = document.getElementById('root')
  if (!root) throw new Error('Application root is missing')
  createRoot(root).render(
    <StrictMode>
      <AppErrorBoundary>
        <App />
      </AppErrorBoundary>
    </StrictMode>,
  )
} catch {
  showFatalBootstrapFailure()
}
