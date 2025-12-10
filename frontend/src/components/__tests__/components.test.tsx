/**
 * Tests for frontend components
 */
import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import JobStatusBadge from "../JobStatusBadge";
import UploadForm from "../UploadForm";

describe("JobStatusBadge", () => {
  const cases = [
    { status: "submitted", colorClass: "bg-zinc-200" },
    { status: "running", colorClass: "bg-blue-100" },
    { status: "completed", colorClass: "bg-green-100" },
    { status: "failed", colorClass: "bg-red-100" },
  ] as const;

  test.each(cases)(
    "renders %s status with correct styling",
    ({ status, colorClass }) => {
      render(<JobStatusBadge status={status} />);
      const badge = screen.getByText(status);
      expect(badge).toBeInTheDocument();
      expect(badge.className).toContain(colorClass);
      expect(badge.className).toContain("rounded-full");
      expect(badge.className).toContain("px-3");
      expect(badge.className).toContain("py-1");
    },
  );
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
