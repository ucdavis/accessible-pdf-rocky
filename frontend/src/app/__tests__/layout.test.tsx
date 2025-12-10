import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import RootLayout from "../layout";

describe("RootLayout", () => {
  test("renders children correctly", () => {
    render(
      <RootLayout>
        <div data-testid="child-content">Test content</div>
      </RootLayout>,
    );
    const child = screen.getByTestId("child-content");
    expect(child).toBeInTheDocument();
    expect(child).toHaveTextContent("Test content");
  });

  test("renders multiple children", () => {
    render(
      <RootLayout>
        <div data-testid="first">First</div>
        <div data-testid="second">Second</div>
      </RootLayout>,
    );
    expect(screen.getByTestId("first")).toBeInTheDocument();
    expect(screen.getByTestId("second")).toBeInTheDocument();
  });
});
