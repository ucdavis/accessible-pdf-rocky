import { describe, expect, it, beforeEach, vi } from 'vitest';
import { getJobStatus, listJobs, formatDate, getStatusColor, type Job } from '../api';

describe('api client', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    vi.unstubAllGlobals();
  });

  describe('getJobStatus', () => {
    it('should fetch and return job status successfully', async () => {
      const mockJob: Job = {
        id: '123e4567-e89b-12d3-a456-426614174000',
        status: 'Running',
        r2Key: 'test.pdf',
        createdAt: '2024-01-01T12:00:00Z',
        updatedAt: '2024-01-01T12:30:00Z',
        slurmId: '12345',
      };

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockJob,
      });
      vi.stubGlobal('fetch', mockFetch);

      const result = await getJobStatus('123e4567-e89b-12d3-a456-426614174000');

      expect(mockFetch).toHaveBeenCalledWith('/api/job/status/123e4567-e89b-12d3-a456-426614174000');
      expect(result).toEqual(mockJob);
    });

    it('should throw error when fetch fails', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        statusText: 'Not Found',
        json: async () => ({ detail: 'Job not found' }),
      });
      vi.stubGlobal('fetch', mockFetch);

      await expect(getJobStatus('invalid-id')).rejects.toThrow('Job not found');
    });

    it('should throw generic error when error detail is missing', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        statusText: 'Bad Request',
        json: async () => ({}),
      });
      vi.stubGlobal('fetch', mockFetch);

      await expect(getJobStatus('invalid-id')).rejects.toThrow('Failed to fetch job status');
    });
  });

  describe('listJobs', () => {
    it('should fetch and return list of jobs', async () => {
      const mockJobs: Job[] = [
        {
          id: '123',
          status: 'Completed',
          r2Key: 'test1.pdf',
          createdAt: '2024-01-01T12:00:00Z',
          updatedAt: '2024-01-01T13:00:00Z',
        },
        {
          id: '456',
          status: 'Running',
          r2Key: 'test2.pdf',
          createdAt: '2024-01-01T14:00:00Z',
          updatedAt: '2024-01-01T14:30:00Z',
        },
      ];

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockJobs,
      });
      vi.stubGlobal('fetch', mockFetch);

      const result = await listJobs();

      expect(mockFetch).toHaveBeenCalledWith('/api/job');
      expect(result).toEqual(mockJobs);
    });

    it('should include query parameters when provided', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => [],
      });
      vi.stubGlobal('fetch', mockFetch);

      await listJobs({ status: 'Completed', limit: 10 });

      expect(mockFetch).toHaveBeenCalledWith('/api/job?status=Completed&limit=10');
    });

    it('should throw error when fetch fails', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        statusText: 'Unauthorized',
        json: async () => ({ detail: 'Unauthorized' }),
      });
      vi.stubGlobal('fetch', mockFetch);

      await expect(listJobs()).rejects.toThrow('Unauthorized');
    });

    it('should throw generic error when error detail is missing', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        statusText: 'Bad Request',
        json: async () => ({}),
      });
      vi.stubGlobal('fetch', mockFetch);

      await expect(listJobs()).rejects.toThrow('Failed to fetch jobs');
    });
  });

  describe('formatDate', () => {
    it('should format ISO date string to locale string', () => {
      const dateString = '2024-01-01T12:00:00Z';
      const formatted = formatDate(dateString);
      expect(formatted).toBeDefined();
      expect(typeof formatted).toBe('string');
      // Just verify it's a valid date output
      expect(formatted.length).toBeGreaterThan(0);
    });
  });

  describe('getStatusColor', () => {
    it('should return blue for Submitted status', () => {
      expect(getStatusColor('Submitted')).toBe('bg-blue-100 text-blue-800');
    });

    it('should return yellow for Running status', () => {
      expect(getStatusColor('Running')).toBe('bg-yellow-100 text-yellow-800');
    });

    it('should return green for Completed status', () => {
      expect(getStatusColor('Completed')).toBe('bg-green-100 text-green-800');
    });

    it('should return red for Failed status', () => {
      expect(getStatusColor('Failed')).toBe('bg-red-100 text-red-800');
    });

    it('should return gray for unknown status (default case)', () => {
      // @ts-expect-error Testing default case with invalid status
      expect(getStatusColor('Unknown')).toBe('bg-gray-100 text-gray-800');
    });
  });
});
