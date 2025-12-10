export default function Jobs() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 dark:bg-black">
      <main className="flex w-full max-w-4xl flex-col gap-8 p-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold tracking-tight text-black dark:text-zinc-50">
            Processing Jobs
          </h1>
          <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">
            View status of your PDF accessibility checks
          </p>
        </div>

        <div className="rounded-lg border border-zinc-200 bg-white p-8 dark:border-zinc-800 dark:bg-zinc-900">
          <p className="text-center text-zinc-500 dark:text-zinc-400">
            No jobs yet. Upload a PDF to get started.
          </p>
        </div>

        {/* TODO: Implement job list
          - Fetch jobs from API
          - Display job status (submitted, running, completed, failed)
          - Link to individual job details
          - Auto-refresh for running jobs
        */}
      </main>
    </div>
  );
}
