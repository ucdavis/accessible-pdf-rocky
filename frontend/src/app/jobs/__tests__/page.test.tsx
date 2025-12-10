/**
 * Tests for frontend/src/app/jobs/page.tsx
 */
import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Jobs from "../page";

describe("Jobs page", () => {
  test("imports successfully", async () => {
    const jobsPage = await import("../page");
    expect(jobsPage).toBeDefined();
  });

  test("renders the page heading", () => {
    render(<Jobs />);
    const heading = screen.getByRole("heading", { name: /Processing Jobs/i });
    expect(heading).toBeDefined();
  });

  test("renders the page description", () => {
    render(<Jobs />);
    const description = screen.getByText(
      /View status of your PDF accessibility checks/i
    );
    expect(description).toBeDefined();
  });

  test("displays empty state message when no jobs exist", () => {
    render(<Jobs />);
    const emptyMessage = screen.getByText(
      /No jobs yet. Upload a PDF to get started./i
    );
    expect(emptyMessage).toBeDefined();
  });

  test("renders without crashing", () => {
    const { container } = render(<Jobs />);
    expect(container).toBeTruthy();
  });

  test("has proper semantic structure with main element", () => {
    render(<Jobs />);
    const main = screen.getByRole("main");
    expect(main).toBeDefined();
  });

  // TODO: Add tests for future API integration:
  // - Fetches and displays jobs from API
  // - Displays job statuses with JobStatusBadge
  // - Handles loading state during fetch
  // - Links to individual job details
  // - Handles fetch errors gracefully
  // - Auto-refreshes for running jobs
});
