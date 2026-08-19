// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { RefreshStatusChip } from './components/RefreshStatusChip'
import type { ProspectiveRefreshStatus } from './types'

const failedStatus: ProspectiveRefreshStatus = {
  contract: 'GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1',
  enabled: true,
  state: 'error',
  message: 'This closed bar already has a failed refresh attempt; inspect the run before retrying.',
  lastCheckedAtUtc: '2026-08-19T03:45:46Z',
  latestClosedBarUtc: '2026-08-19T03:00:00Z',
  activeRun: {
    runId: 'run-failed-n',
    contract: 'GANN_PROSPECTIVE_ARTIFACT_REFRESH_V1',
    sourceBarOpenUtc: '2026-08-19T02:00:00Z',
    sourceBarCloseUtc: '2026-08-19T03:00:00Z',
    status: 'failed',
    stage: 'failed',
    message: 'Prospective refresh failed before activation.',
    sourceSnapshotId: null,
    priceSourceId: null,
    generationJobId: null,
    artifactId: null,
    parameters: {},
    error: 'MT5 server-time normalization failed',
    createdAtUtc: '2026-08-19T03:45:45Z',
    updatedAtUtc: '2026-08-19T03:45:46Z',
    finishedAtUtc: '2026-08-19T03:45:46Z',
  },
  recentRuns: [],
  lastError: 'MT5 server-time normalization failed',
  executionAllowed: false,
}

describe('RefreshStatusChip', () => {
  it('distinguishes a preserved historical failure and exposes its lineage', async () => {
    const user = userEvent.setup()
    const onRefresh = vi.fn()
    render(<RefreshStatusChip status={failedStatus} busy={false} onRefresh={onRefresh} />)

    expect(screen.getByText('Historical failure')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Check for a later eligible closed bar' })).toHaveAttribute(
      'title',
      expect.stringContaining('does not retry that bar'),
    )
    await user.click(screen.getByText('Inspect failed run'))
    expect(screen.getByText('run-failed-n')).toBeInTheDocument()
    expect(screen.getByText('MT5 server-time normalization failed')).toBeInTheDocument()
    expect(screen.getByText('Source snapshot').nextElementSibling).toHaveTextContent('none')
    await user.click(screen.getByRole('button', { name: 'Check for a later eligible closed bar' }))
    expect(onRefresh).toHaveBeenCalledTimes(1)
  })
})
