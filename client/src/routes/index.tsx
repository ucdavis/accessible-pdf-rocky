import { createFileRoute, Link } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  component: HomeComponent,
});

function HomeComponent() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 sm:text-6xl">
          Accessible PDF AI
        </h1>
        <p className="mt-6 text-lg leading-8 text-zinc-600 dark:text-zinc-400">
          Automate PDF accessibility remediation using modern AI models.
          Leverage existing HPC infrastructure for cost-effective processing.
        </p>
        <div className="mt-10 flex items-center justify-center gap-x-6">
          <Link
            to="/upload"
            className="rounded-md bg-zinc-900 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-zinc-700 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            Upload PDF
          </Link>
          <Link
            to="/jobs"
            className="text-sm font-semibold leading-6 text-zinc-900 dark:text-zinc-50"
          >
            View Jobs <span aria-hidden="true">→</span>
          </Link>
        </div>
      </div>

      <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-4xl">
        <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-10 lg:max-w-none lg:grid-cols-2 lg:gap-y-16">
          <div className="relative pl-16">
            <dt className="text-base font-semibold leading-7 text-zinc-900 dark:text-zinc-50">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-900 dark:bg-zinc-50">
                <span className="text-white dark:text-zinc-900">AI</span>
              </div>
              Modern AI Models
            </dt>
            <dd className="mt-2 text-base leading-7 text-zinc-600 dark:text-zinc-400">
              Uses LayoutLMv3, BLIP-2, and other state-of-the-art models for document understanding
              and alt-text generation.
            </dd>
          </div>

          <div className="relative pl-16">
            <dt className="text-base font-semibold leading-7 text-zinc-900 dark:text-zinc-50">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-900 dark:bg-zinc-50">
                <span className="text-white dark:text-zinc-900">⚡</span>
              </div>
              Batch Processing
            </dt>
            <dd className="mt-2 text-base leading-7 text-zinc-600 dark:text-zinc-400">
              Enable processing of large document collections without manual review using HPC
              integration.
            </dd>
          </div>

          <div className="relative pl-16">
            <dt className="text-base font-semibold leading-7 text-zinc-900 dark:text-zinc-50">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-900 dark:bg-zinc-50">
                <span className="text-white dark:text-zinc-900">✓</span>
              </div>
              WCAG 2.1 AA Compliance
            </dt>
            <dd className="mt-2 text-base leading-7 text-zinc-600 dark:text-zinc-400">
              Automated enforcement, not just checking. Easily upgrade compliance standards.
            </dd>
          </div>

          <div className="relative pl-16">
            <dt className="text-base font-semibold leading-7 text-zinc-900 dark:text-zinc-50">
              <div className="absolute left-0 top-0 flex h-10 w-10 items-center justify-center rounded-lg bg-zinc-900 dark:bg-zinc-50">
                <span className="text-white dark:text-zinc-900">$</span>
              </div>
              Cost Efficient
            </dt>
            <dd className="mt-2 text-base leading-7 text-zinc-600 dark:text-zinc-400">
              Leverage existing HPC infrastructure for cost-effective processing at scale.
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
}
