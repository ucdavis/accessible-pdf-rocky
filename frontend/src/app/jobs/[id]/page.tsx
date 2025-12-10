export default function JobDetail({ params }: { params: { id: string } }) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <main className="flex w-full max-w-4xl flex-col gap-8 p-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tight text-black dark:text-zinc-50">
            Job Details
          </h1>
          <p className="mt-2 text-sm text-zinc-500 dark:text-zinc-400">
            Job ID: {params.id}
          </p>
        </div>

        <div className="rounded-lg border border-zinc-200 bg-white p-8 dark:border-zinc-800 dark:bg-zinc-900">
          <div className="space-y-4">
            <div>
              <h2 className="text-lg font-semibold text-black dark:text-zinc-50">
                Status
              </h2>
              <p className="text-zinc-600 dark:text-zinc-400">Loading...</p>
            </div>

            <div>
              <h2 className="text-lg font-semibold text-black dark:text-zinc-50">
                Results
              </h2>
              <p className="text-zinc-500 dark:text-zinc-400">
                Results will appear here when processing is complete
              </p>
            </div>
          </div>
        </div>

        {/* TODO: Implement job detail view
          - Fetch job status from API
          - Poll for updates while job is running
          - Display SLURM job ID
          - Show processing progress/logs
          - Display results when complete
          - Download links for accessible PDF
          - Error messages for failed jobs
        */}
      </main>
    </div>
  );
}
