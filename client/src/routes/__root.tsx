import { createRootRouteWithContext, Link, Outlet } from '@tanstack/react-router';
import { QueryClient } from '@tanstack/react-query';
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools';

export const Route = createRootRouteWithContext<{
  queryClient: QueryClient;
}>()({
  component: RootComponent,
});

function RootComponent() {
  return (
    <>
      <div className="min-h-screen bg-zinc-50 dark:bg-zinc-900">
        <nav className="border-b border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-950">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 items-center justify-between">
              <div className="flex items-center gap-8">
                <Link to="/" className="text-xl font-bold text-zinc-900 dark:text-zinc-50">
                  Accessible PDF AI
                </Link>
                <div className="flex gap-4">
                  <Link
                    to="/"
                    className="text-sm font-medium text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-50 [&.active]:text-zinc-900 dark:[&.active]:text-zinc-50"
                  >
                    Home
                  </Link>
                  <Link
                    to="/upload"
                    className="text-sm font-medium text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-50 [&.active]:text-zinc-900 dark:[&.active]:text-zinc-50"
                  >
                    Upload
                  </Link>
                  <Link
                    to="/jobs"
                    className="text-sm font-medium text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-50 [&.active]:text-zinc-900 dark:[&.active]:text-zinc-50"
                  >
                    Jobs
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>
        <main>
          <Outlet />
        </main>
      </div>
      <TanStackRouterDevtools position="bottom-right" />
    </>
  );
}
