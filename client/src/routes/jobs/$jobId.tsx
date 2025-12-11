import { createFileRoute, Link } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { getJobStatus, getStatusColor, formatDate } from '../../lib/api';

export const Route = createFileRoute('/jobs/$jobId')({
  component: JobDetailComponent,
});

function JobDetailComponent() {
  const { jobId } = Route.useParams();
  const { data: job, isLoading, error } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => getJobStatus(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      // Poll every 5 seconds if job is running or submitted
      return status === 'Running' || status === 'Submitted' ? 5000 : false;
    },
  });

  if (isLoading) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <p className="text-center text-zinc-600 dark:text-zinc-400">Loading job...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="rounded-md bg-red-50 p-4 dark:bg-red-900/20">
          <p className="text-sm text-red-800 dark:text-red-200">
            Error loading job: {error.message}
          </p>
        </div>
        <div className="mt-6">
          <Link
            to="/jobs"
            className="text-sm font-semibold text-zinc-900 dark:text-zinc-50"
          >
            ← Back to jobs
          </Link>
        </div>
      </div>
    );
  }

  if (!job) {
    return null;
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="mb-6">
        <Link
          to="/jobs"
          className="text-sm font-semibold text-zinc-900 dark:text-zinc-50"
        >
          ← Back to jobs
        </Link>
      </div>

      <div className="overflow-hidden bg-white shadow sm:rounded-lg dark:bg-zinc-900">
        <div className="px-4 py-6 sm:px-6">
          <h3 className="text-base font-semibold leading-7 text-zinc-900 dark:text-zinc-50">
            Job Information
          </h3>
          <p className="mt-1 max-w-2xl text-sm leading-6 text-zinc-500 dark:text-zinc-400">
            Processing details and status
          </p>
        </div>
        <div className="border-t border-zinc-200 px-4 py-6 sm:px-6 dark:border-zinc-800">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Job ID</dt>
              <dd className="mt-1 text-sm text-zinc-900 dark:text-zinc-50">{job.id}</dd>
            </div>

            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Status</dt>
              <dd className="mt-1">
                <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${getStatusColor(job.status)}`}>
                  {job.status}
                </span>
              </dd>
            </div>

            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Created</dt>
              <dd className="mt-1 text-sm text-zinc-900 dark:text-zinc-50">
                {formatDate(job.createdAt)}
              </dd>
            </div>

            <div className="sm:col-span-1">
              <dt className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Updated</dt>
              <dd className="mt-1 text-sm text-zinc-900 dark:text-zinc-50">
                {formatDate(job.updatedAt)}
              </dd>
            </div>

            {job.slurmId && (
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-zinc-500 dark:text-zinc-400">SLURM ID</dt>
                <dd className="mt-1 text-sm text-zinc-900 dark:text-zinc-50">{job.slurmId}</dd>
              </div>
            )}

            {job.resultsUrl && (
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-zinc-500 dark:text-zinc-400">Results</dt>
                <dd className="mt-1 text-sm">
                  <a
                    href={job.resultsUrl}
                    className="text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-50"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Download Results →
                  </a>
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>
    </div>
  );
}
