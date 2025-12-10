import { describe, test, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import Page from '../page'

describe('Home Page', () => {
  test('renders the Next.js logo', () => {
    render(<Page />)
    const logo = screen.getByAltText('Next.js logo')
    expect(logo).toBeInTheDocument()
  })

  test('renders the main heading', () => {
    render(<Page />)
    const heading = screen.getByRole('heading', {
      name: /To get started, edit the page.tsx file/i,
    })
    expect(heading).toBeInTheDocument()
  })

  test('renders links to Templates and Learning resources', () => {
    render(<Page />)
    const templatesLink = screen.getByRole('link', { name: /Templates/i })
    const learningLink = screen.getByRole('link', { name: /Learning/i })
    expect(templatesLink).toBeInTheDocument()
    expect(learningLink).toBeInTheDocument()
  })

  test('renders Deploy Now button with Vercel logo', () => {
    render(<Page />)
    const deployButton = screen.getByRole('link', { name: /Deploy Now/i })
    expect(deployButton).toBeInTheDocument()
    const vercelLogo = screen.getByAltText('Vercel logomark')
    expect(vercelLogo).toBeInTheDocument()
  })

  test('renders Documentation link', () => {
    render(<Page />)
    const docsLink = screen.getByRole('link', { name: /Documentation/i })
    expect(docsLink).toBeInTheDocument()
  })
})
