// API client for .NET server endpoints

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export interface Job {
  id: string;
  slurmId?: string | null;
  status: 'Submitted' | 'Running' | 'Completed' | 'Failed';
  r2Key: string;
  createdAt: string;
  updatedAt: string;
  resultsUrl?: string | null;
  userId?: string | null;
  error?: string | null;
}

export interface ApiError {
  detail: string;
}

/**
 * Get job status by ID
 */
export async function getJobStatus(jobId: string): Promise<Job> {
  const response = await fetch(`${API_BASE_URL}/job/status/${jobId}`);
  
  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to fetch job status');
  }
  
  return response.json();
}

/**
 * List all jobs with optional filters
 */
export async function listJobs(params?: {
  status?: Job['status'];
  userId?: string;
  limit?: number;
}): Promise<Job[]> {
  const searchParams = new URLSearchParams();
  
  if (params?.status) {
    searchParams.append('status', params.status);
  }
  if (params?.userId) {
    searchParams.append('userId', params.userId);
  }
  if (params?.limit) {
    searchParams.append('limit', params.limit.toString());
  }
  
  const url = `${API_BASE_URL}/job${searchParams.toString() ? `?${searchParams.toString()}` : ''}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    const error: ApiError = await response.json();
    throw new Error(error.detail || 'Failed to fetch jobs');
  }
  
  return response.json();
}

/**
 * Format date for display
 */
export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString();
}

/**
 * Get status color for badge
 */
export function getStatusColor(status: Job['status']): string {
  switch (status) {
    case 'Submitted':
      return 'bg-blue-100 text-blue-800';
    case 'Running':
      return 'bg-yellow-100 text-yellow-800';
    case 'Completed':
      return 'bg-green-100 text-green-800';
    case 'Failed':
      return 'bg-red-100 text-red-800';
    default:
      return 'bg-gray-100 text-gray-800';
  }
}
