/**
 * Job Status Badge Component
 * 
 * Displays job status with appropriate styling
 * 
 * TODO: Implement status badge with colors
 * - submitted: gray
 * - running: blue
 * - completed: green
 * - failed: red
 */

type JobStatus = "submitted" | "running" | "completed" | "failed";

interface JobStatusBadgeProps {
  status: JobStatus;
}

export default function JobStatusBadge({ status }: JobStatusBadgeProps) {
  const colors = {
    submitted: "bg-zinc-200 text-zinc-700 dark:bg-zinc-700 dark:text-zinc-300",
    running: "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
    completed: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    failed: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
  };

  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${colors[status]}`}
    >
      {status}
    </span>
  );
}
