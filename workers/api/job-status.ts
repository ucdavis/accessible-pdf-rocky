/**
 * Job Status Worker
 * 
 * Proxy requests to FastAPI controller for job status.
 * 
 * TODO: Implement job status endpoint
 * - Extract job ID from URL or query params
 * - Proxy request to FastAPI controller
 * - Return job status, results URL, error messages
 * - Cache responses for completed jobs
 */

export interface Env {
  FASTAPI_URL: string;
}

export default {
  async fetch(req: Request, _env: Env): Promise<Response> {
    if (req.method !== "GET") {
      return new Response("Method not allowed", { status: 405 });
    }

    // TODO: Implement status fetching
    // Parse job ID from URL
    // const url = new URL(req.url);
    // const jobId = url.searchParams.get("jobId");
    // 
    // if (!jobId) {
    //   return new Response("Missing jobId", { status: 400 });
    // }
    //
    // // Proxy to FastAPI controller
    // const res = await fetch(`${env.FASTAPI_URL}/status/${jobId}`);
    // return res;

    return new Response("Not implemented", { status: 501 });
  },
};
