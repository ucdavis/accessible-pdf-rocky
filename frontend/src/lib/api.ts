/**
 * API Client for Cloudflare Worker endpoints
 * 
 * TODO: Implement API client functions
 * - uploadPdf: Upload PDF to R2
 * - submitJob: Submit job to queue
 * - getJobStatus: Get job status by ID
 * - listJobs: List all jobs
 * - downloadResult: Get signed URL for result PDF
 */

// const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export interface Job {
  id: string;
  status: "submitted" | "running" | "completed" | "failed";
  createdAt: string;
  updatedAt: string;
  resultsUrl?: string;
  error?: string;
}

export async function uploadPdf(_file: File): Promise<{ jobId: string }> {
  // TODO: Implement PDF upload to Cloudflare Worker
  // - Create FormData with file
  // - POST to /api/upload
  // - Return job ID
  throw new Error("Not implemented");
}

export async function getJobStatus(_jobId: string): Promise<Job> {
  // TODO: Implement job status fetch
  // - GET /api/jobs/:id
  // - Parse and return job status
  throw new Error("Not implemented");
}

export async function listJobs(): Promise<Job[]> {
  // TODO: Implement job list fetch
  // - GET /api/jobs
  // - Return array of jobs
  throw new Error("Not implemented");
}

export async function downloadResult(_jobId: string): Promise<string> {
  // TODO: Implement result download URL fetch
  // - GET /api/jobs/:id/download
  // - Return signed R2 URL
  throw new Error("Not implemented");
}
