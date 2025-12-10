import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import Upload from "../page";

describe("Upload", () => {
  test("renders upload heading", () => {
    render(<Upload />);
    const heading = screen.getByRole("heading", { name: /Upload PDF/i });
    expect(heading).toBeInTheDocument();
  });

  test("displays descriptive text about uploading", () => {
    render(<Upload />);
    const description = screen.getByText(
      /Upload a PDF file to check its accessibility/i,
    );
    expect(description).toBeInTheDocument();
  });

  test("renders upload area with drag and drop text", () => {
    render(<Upload />);
    const dragDropText = screen.getByText(
      /Drag and drop your PDF here, or click to browse/i,
    );
    expect(dragDropText).toBeInTheDocument();
  });

  test("displays PDF file type restriction", () => {
    render(<Upload />);
    const restriction = screen.getByText(/PDF files only/i);
    expect(restriction).toBeInTheDocument();
  });

  test("renders upload icon with proper aria-hidden attribute", () => {
    const { container } = render(<Upload />);
    const icon = container.querySelector('svg[aria-hidden="true"]');
    expect(icon).not.toBeNull();
  });

  test("displays disabled upload button with coming soon message", () => {
    render(<Upload />);
    const button = screen.getByRole("button", {
      name: /Upload functionality coming soon/i,
    });
    expect(button).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  test("renders within a main landmark", () => {
    render(<Upload />);
    const main = screen.getByRole("main");
    expect(main).toBeInTheDocument();
  });
});
