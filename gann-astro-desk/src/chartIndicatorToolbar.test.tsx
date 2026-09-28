// @vitest-environment jsdom

import '@testing-library/jest-dom/vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ChartIndicatorToolbar } from './components/MarketChart'

describe('ChartIndicatorToolbar', () => {
  it('makes Indicators, RSI, and Fields & Waves discoverable without hovering', async () => {
    const user = userEvent.setup()
    const onToggleRsi = vi.fn()
    const onToggleRsiSettings = vi.fn()
    const onToggleFieldsWavesMenu = vi.fn()

    render(<ChartIndicatorToolbar
      rsiVisible
      rsiPeriod={14}
      fieldsWavesEnabled
      activityVisible={false}
      fieldsWavesMenuOpen={false}
      onToggleRsi={onToggleRsi}
      onToggleRsiSettings={onToggleRsiSettings}
      onToggleFieldsWavesMenu={onToggleFieldsWavesMenu}
    />)

    expect(screen.getByRole('toolbar', { name: 'Indicators' })).toBeInTheDocument()
    expect(screen.getByText('Indicators')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /RSI 14/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Fields & Waves/i })).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /Fields & Waves/i }))
    await user.click(screen.getByRole('button', { name: /RSI 14/i }))
    await user.click(screen.getByRole('button', { name: 'RSI settings' }))
    expect(onToggleFieldsWavesMenu).toHaveBeenCalledTimes(1)
    expect(onToggleRsi).toHaveBeenCalledTimes(1)
    expect(onToggleRsiSettings).toHaveBeenCalledTimes(1)
  })
})
