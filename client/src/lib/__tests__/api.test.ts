import { describe, expect, it } from 'vitest';
import { getJobStatus, listJobs, formatDate, getStatusColor } from '../api';

describe('api client', () => {
  describe('exports', () => {
    it('should export getJobStatus function', () => {
      expect(getJobStatus).toBeDefined();
      expect(typeof getJobStatus).toBe('function');
    });

    it('should export listJobs function', () => {
      expect(listJobs).toBeDefined();
      expect(typeof listJobs).toBe('function');
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
  });
});
