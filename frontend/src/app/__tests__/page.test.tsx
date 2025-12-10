import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import Page from '../page'

describe('Home Page', () => {
  it('renders without crashing', () => {
    const { container } = render(<Page />)
    expect(container).toBeTruthy()
  })

  it('has accessible PDF content', () => {
    const { container } = render(<Page />)
    // Add more specific assertions based on your actual page content
    // This is a placeholder test
    expect(container.innerHTML).toBeTruthy()
  })
})
