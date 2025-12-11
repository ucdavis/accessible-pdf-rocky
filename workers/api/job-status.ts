/**
 * Job Status Worker
 * 
 * Proxy requests to .NET server for job status.
 * 
 * TODO: Implement job status endpoint
 * - Extract job ID from URL or query params
 * - Proxy request to .NET server
 * - Return job status, results URL, error messages
 * - Cache responses for completed jobs
 */

export interface Env {
  SERVER_URL: string;
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
    // // Proxy to .NET server
    // const res = await fetch(`${env.SERVER_URL}/status/${jobId}`);
    // return res;

    return new Response("Not implemented", { status: 501 });
  },
};
