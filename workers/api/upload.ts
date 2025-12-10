export interface Env {
  PDF_BUCKET: R2Bucket;
  JOB_QUEUE: Queue;
}

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    if (req.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    const contentType = req.headers.get("content-type") || "";
    if (!contentType.includes("multipart/form-data")) {
      return new Response("Expected multipart/form-data", { status: 400 });
    }

    const formData = await req.formData();
    const file = formData.get("file") as File | null;
    if (!file) return new Response("Missing file", { status: 400 });

    const jobId = crypto.randomUUID();
    const key = `raw/${jobId}.pdf`;

    await env.PDF_BUCKET.put(key, await file.arrayBuffer());

    await env.JOB_QUEUE.send({
      jobId,
      r2Key: key,
      timestamp: Date.now(),
    });

    return new Response(JSON.stringify({ jobId }), {
      headers: { "Content-Type": "application/json" },
    });
  },
};