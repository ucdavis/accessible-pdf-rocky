/**
 * Tests for frontend/src/app/jobs/page.tsx
 */
import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Jobs from "../page";

describe("Jobs page", () => {
  test("renders the page heading", () => {
    render(<Jobs />);
    const heading = screen.getByRole("heading", {
      level: 1,
      name: /Processing Jobs/i,
    });
    expect(heading).toBeInTheDocument();
  });

  test("renders the page description", () => {
    render(<Jobs />);
    const description = screen.getByText(
      /View status of your PDF accessibility checks/i
    );
    expect(description).toBeInTheDocument();
  });

  test("displays empty state message when no jobs exist", () => {
    render(<Jobs />);
    const emptyMessage = screen.getByText(
      /No jobs yet. Upload a PDF to get started./i
    );
    expect(emptyMessage).toBeInTheDocument();
  });

  test("has proper semantic structure with main element", () => {
    render(<Jobs />);
    const main = screen.getByRole("main");
    expect(main).toBeInTheDocument();
  });

  /**
   * TODO: Add tests for future API integration
   * Track progress in GitHub issue #TBD
   *
   * Planned test coverage:
   * - Fetches and displays jobs from API
   * - Displays job statuses with JobStatusBadge component
   * - Handles loading state during fetch
   * - Links to individual job details pages
   * - Handles fetch errors gracefully with error messages
   * - Auto-refreshes job list for running jobs
   */
});
