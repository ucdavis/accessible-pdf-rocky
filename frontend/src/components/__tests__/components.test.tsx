/**
 * Tests for frontend components
 */
import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import JobStatusBadge from "../JobStatusBadge";
import UploadForm from "../UploadForm";

describe("JobStatusBadge", () => {
  test("renders submitted status correctly", () => {
    render(<JobStatusBadge status="submitted" />);
    const badge = screen.getByText("submitted");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-zinc-200");
  });

  test("renders running status with blue styling", () => {
    render(<JobStatusBadge status="running" />);
    const badge = screen.getByText("running");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-blue-100");
  });

  test("renders completed status with green styling", () => {
    render(<JobStatusBadge status="completed" />);
    const badge = screen.getByText("completed");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-green-100");
  });

  test("renders failed status with red styling", () => {
    render(<JobStatusBadge status="failed" />);
    const badge = screen.getByText("failed");
    expect(badge).toBeInTheDocument();
    expect(badge.className).toContain("bg-red-100");
  });

  test("applies common badge styling to all statuses", () => {
    render(<JobStatusBadge status="submitted" />);
    const badge = screen.getByText("submitted");
    expect(badge.className).toContain("rounded-full");
    expect(badge.className).toContain("px-3");
    expect(badge.className).toContain("py-1");
  });
});

describe("UploadForm", () => {
  test("renders the upload area with descriptive text", () => {
    render(<UploadForm />);
    const text = screen.getByText(/Drag and drop your PDF here/i);
    expect(text).toBeInTheDocument();
  });

  test("displays PDF file type restriction", () => {
    render(<UploadForm />);
    const restriction = screen.getByText(/PDF files only/i);
    expect(restriction).toBeInTheDocument();
  });

  test("renders upload icon with proper aria-hidden attribute", () => {
    const { container } = render(<UploadForm />);
    const icon = container.querySelector('svg[aria-hidden="true"]');
    expect(icon).not.toBeNull();
  });

  test("displays disabled upload button with coming soon message", () => {
    render(<UploadForm />);
    const button = screen.getByRole("button", {
      name: /Upload functionality coming soon/i,
    });
    expect(button).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  /**
   * TODO: Add tests for future upload functionality
   * Track progress in GitHub issue #TBD
   *
   * Planned test coverage:
   * - Handles file selection via input
   * - Handles drag and drop file upload
   * - Validates file type (PDF only)
   * - Validates file size limits
   * - Submits form with valid file
   * - Displays upload progress indicator
   * - Handles submission errors
   * - Navigates to job status page on success
   */
});
