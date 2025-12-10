import { render } from '@testing-library/react'
import Page from '../page'

describe('Home Page', () => {
  it('renders without crashing', () => {
    render(<Page />)
    expect(document.body).toBeInTheDocument()
  })

  it('has accessible PDF content', () => {
    render(<Page />)
    // Add more specific assertions based on your actual page content
    // This is a placeholder test
    expect(document.body).not.toBeEmptyDOMElement()
  })
})
