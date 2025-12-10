import { describe, test, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import JobDetail from "../page";

describe("JobDetail", () => {
  test("renders job details heading", async () => {
    render(await JobDetail({ params: Promise.resolve({ id: "test-123" }) }));
    const heading = screen.getByRole("heading", { name: /Job Details/i });
    expect(heading).toBeInTheDocument();
  });

  test("displays the job ID from params", async () => {
    const jobId = "abc-123-def";
    render(await JobDetail({ params: Promise.resolve({ id: jobId }) }));
    const idText = screen.getByText(`Job ID: ${jobId}`);
    expect(idText).toBeInTheDocument();
  });

  test("renders status section with loading state", async () => {
    render(await JobDetail({ params: Promise.resolve({ id: "test-123" }) }));
    const statusHeading = screen.getByRole("heading", { name: /Status/i });
    expect(statusHeading).toBeInTheDocument();
    const loadingText = screen.getByText(/Loading\.\.\./i);
    expect(loadingText).toBeInTheDocument();
  });

  test("renders results section with placeholder text", async () => {
    render(await JobDetail({ params: Promise.resolve({ id: "test-123" }) }));
    const resultsHeading = screen.getByRole("heading", { name: /Results/i });
    expect(resultsHeading).toBeInTheDocument();
    const placeholderText = screen.getByText(
      /Results will appear here when processing is complete/i,
    );
    expect(placeholderText).toBeInTheDocument();
  });

  test("renders within a main landmark", async () => {
    render(await JobDetail({ params: Promise.resolve({ id: "test-123" }) }));
    const main = screen.getByRole("main");
    expect(main).toBeInTheDocument();
  });
});
