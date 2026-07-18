// @vitest-environment jsdom

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'

import { ToolRail } from './ToolRail'

describe('ToolRail', () => {
  it('exposes the complete drawing workflow and preference controls', async () => {
    const user = userEvent.setup()
    const onToolChange = vi.fn()
    const onPreferencesChange = vi.fn()

    render(
      <ToolRail
        activeTool="select"
        onToolChange={onToolChange}
        onPreferencesChange={onPreferencesChange}
        preferences={{
          favoriteTools: ['horizontal', 'gann', 'fibonacci'],
          magnetMode: 'weak',
          keepDrawing: false,
        }}
      />,
    )

    for (const name of [
      'Select aspect or drawing',
      'Crosshair',
      'Add annotation',
      'Horizontal line',
      'Vertical line',
      'Gann fan',
      'Fibonacci retracement',
      'Toggle active drawing tool favorite',
      'OHLC magnet weak',
      'Toggle keep drawing',
      'Undo last drawing',
      'Reset chart view',
      'Clear manual drawings',
    ]) {
      expect(screen.getByRole('button', { name })).toBeTruthy()
    }

    await user.click(screen.getByRole('button', { name: 'Fibonacci retracement' }))
    expect(onToolChange).toHaveBeenCalledWith('fibonacci')

    await user.click(screen.getByRole('button', { name: 'OHLC magnet weak' }))
    expect(onPreferencesChange).toHaveBeenCalledWith({ magnetMode: 'strong' })
  })
})
