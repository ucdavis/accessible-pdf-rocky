/**
 * Submit Job Worker
 * 
 * Submit a job for an already uploaded PDF to the processing queue.
 * 
 * TODO: Implement job submission endpoint
 * - Accept r2Key for existing PDF
 * - Generate job ID
 * - Send message to Cloudflare Queue
 * - Return job ID to client
 * 
 * Note: upload.ts already handles upload + submit in one step.
 * This endpoint is for re-processing or batch submissions.
 */

export interface Env {
  JOB_QUEUE: Queue;
  FASTAPI_URL: string;
}

export default {
  async fetch(req: Request, _env: Env): Promise<Response> {
    if (req.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    // TODO: Implement job submission
    // Expected body: { r2Key: string }
    // const body = await req.json();
    // const jobId = crypto.randomUUID();
    // 
    // await env.JOB_QUEUE.send({
    //   jobId,
    //   r2Key: body.r2Key,
    //   timestamp: Date.now()
    // });
    //
    // return new Response(JSON.stringify({ jobId }), {
    //   headers: { "Content-Type": "application/json" }
    // });

    return new Response("Not implemented", { status: 501 });
  },
};
