"use client";

/**
 * PDF Upload Form Component
 * 
 * TODO: Implement file upload functionality
 * - File input with drag-and-drop
 * - PDF validation (file type, size)
 * - Upload progress indicator
 * - Call Cloudflare Worker upload API
 * - Navigate to job status page on success
 */

export default function UploadForm() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-zinc-300 bg-white p-12 dark:border-zinc-700 dark:bg-zinc-900">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-zinc-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
            aria-hidden="true"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth={2}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <p className="mt-4 text-sm text-zinc-600 dark:text-zinc-400">
            Drag and drop your PDF here, or click to browse
          </p>
          <p className="mt-2 text-xs text-zinc-500">PDF files only</p>
        </div>
      </div>

      <button
        disabled
        className="rounded-full bg-zinc-200 px-6 py-3 text-sm font-medium text-zinc-400 dark:bg-zinc-800"
      >
        Upload functionality coming soon
      </button>
    </div>
  );
}
