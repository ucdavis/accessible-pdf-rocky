/**
 * Tests for frontend/src/lib/api.ts
 */
import { describe, test, expect } from "vitest";
import { uploadPdf, getJobStatus, listJobs, downloadResult } from "../api";
import type { Job } from "../api";

describe("api module", () => {
  test("imports successfully", async () => {
    const api = await import("../api");
    expect(api).toBeDefined();
  });

  test("exports Job interface type", () => {
    // Type assertion to verify Job interface exists
    const job: Job = {
      id: "test-id",
      status: "submitted",
      createdAt: "2024-01-01T00:00:00Z",
      updatedAt: "2024-01-01T00:00:00Z",
    };
    expect(job).toBeDefined();
  });

  describe("uploadPdf", () => {
    test("is defined", () => {
      expect(uploadPdf).toBeDefined();
    });

    test("throws Not implemented error", async () => {
      const mockFile = new File(["test"], "test.pdf", { type: "application/pdf" });
      await expect(uploadPdf(mockFile)).rejects.toThrow("Not implemented");
    });
  });

  describe("getJobStatus", () => {
    test("is defined", () => {
      expect(getJobStatus).toBeDefined();
    });

    test("throws Not implemented error", async () => {
      await expect(getJobStatus("test-job-id")).rejects.toThrow("Not implemented");
    });
  });

  describe("listJobs", () => {
    test("is defined", () => {
      expect(listJobs).toBeDefined();
    });

    test("throws Not implemented error", async () => {
      await expect(listJobs()).rejects.toThrow("Not implemented");
    });
  });

  describe("downloadResult", () => {
    test("is defined", () => {
      expect(downloadResult).toBeDefined();
    });

    test("throws Not implemented error", async () => {
      await expect(downloadResult("test-job-id")).rejects.toThrow("Not implemented");
    });
  });

  // TODO: Add tests for future API implementation:
  // - uploadPdf() sends correct FormData request
  // - uploadPdf() returns job ID on success
  // - uploadPdf() handles network errors gracefully
  // - getJobStatus() fetches job status correctly
  // - getJobStatus() handles 404 for missing jobs
  // - listJobs() returns array of jobs
  // - listJobs() handles empty job list
  // - downloadResult() returns signed R2 URL
  // - API functions use correct base URL from environment
});
