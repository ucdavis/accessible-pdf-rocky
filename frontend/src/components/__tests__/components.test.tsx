/**
 * Tests for frontend components
 */
import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import JobStatusBadge from "../JobStatusBadge";
import UploadForm from "../UploadForm";

describe("JobStatusBadge", () => {
  test("imports successfully", () => {
    expect(JobStatusBadge).toBeDefined();
  });

  test("renders submitted status correctly", () => {
    render(<JobStatusBadge status="submitted" />);
    const badge = screen.getByText("submitted");
    expect(badge).toBeDefined();
    expect(badge.className).toContain("bg-zinc-200");
  });

  test("renders running status with blue styling", () => {
    render(<JobStatusBadge status="running" />);
    const badge = screen.getByText("running");
    expect(badge).toBeDefined();
    expect(badge.className).toContain("bg-blue-100");
  });

  test("renders completed status with green styling", () => {
    render(<JobStatusBadge status="completed" />);
    const badge = screen.getByText("completed");
    expect(badge).toBeDefined();
    expect(badge.className).toContain("bg-green-100");
  });

  test("renders failed status with red styling", () => {
    render(<JobStatusBadge status="failed" />);
    const badge = screen.getByText("failed");
    expect(badge).toBeDefined();
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
  test("imports successfully", () => {
    expect(UploadForm).toBeDefined();
  });

  test("renders the upload area with descriptive text", () => {
    render(<UploadForm />);
    const text = screen.getByText(/Drag and drop your PDF here/i);
    expect(text).toBeDefined();
  });

  test("displays PDF file type restriction", () => {
    render(<UploadForm />);
    const restriction = screen.getByText(/PDF files only/i);
    expect(restriction).toBeDefined();
  });

  test("renders upload icon with proper aria-hidden attribute", () => {
    const { container } = render(<UploadForm />);
    const icon = container.querySelector('svg[aria-hidden="true"]');
    expect(icon).toBeDefined();
  });

  test("displays disabled upload button with coming soon message", () => {
    render(<UploadForm />);
    const button = screen.getByRole("button", {
      name: /Upload functionality coming soon/i,
    });
    expect(button).toBeDefined();
    expect(button.hasAttribute("disabled")).toBe(true);
  });

  test("renders without crashing", () => {
    const { container } = render(<UploadForm />);
    expect(container).toBeTruthy();
  });

  // TODO: Add tests for future upload functionality:
  // - Handles file selection via input
  // - Handles drag and drop file upload
  // - Validates file type (PDF only)
  // - Validates file size limits
  // - Submits form with valid file
  // - Displays upload progress indicator
  // - Handles submission errors
  // - Navigates to job status page on success
});
