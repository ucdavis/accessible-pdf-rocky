/**
 * Database API Worker
 *
 * Provides REST API for D1 database operations.
 * FastAPI controller calls this worker for all database interactions.
 */

export interface Env {
	JOBS_DB: D1Database;
	DB_AUTH_TOKEN: string;
	ALLOWED_ORIGIN?: string; // Optional, defaults to '*' for development
}

/**
 * Timing-safe string comparison to prevent timing attacks.
 * Compares two strings in constant time regardless of where they differ.
 */
function timingSafeEqual(a: string, b: string): boolean {
	if (a.length !== b.length) return false;
	let result = 0;
	for (let i = 0; i < a.length; i++) {
		result |= a.charCodeAt(i) ^ b.charCodeAt(i);
	}
	return result === 0;
}

interface Job {
	id: string;
	slurm_id?: string;
	status: string;
	r2_key: string;
	created_at: number;
	updated_at: number;
	results_url?: string;
	user_id?: string;
}

interface User {
	id: string;
	email: string;
	name?: string;
	organization?: string;
	created_at: number;
	is_active: number; // SQLite: 0 = false, 1 = true
}

interface ProcessingMetric {
	id: string;
	job_id: string;
	processing_time_seconds?: number;
	pdf_pages?: number;
	pdf_size_bytes?: number;
	success: number; // SQLite: 0 = false, 1 = true
	error_message?: string;
	created_at: number;
}

export default {
	async fetch(request: Request, env: Env, _ctx: ExecutionContext): Promise<Response> {
		const url = new URL(request.url);

		// CORS headers
		// Note: ALLOWED_ORIGIN can be set via environment variable for production
		const corsHeaders = {
			'Access-Control-Allow-Origin': env.ALLOWED_ORIGIN || '*',
			'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
			'Access-Control-Allow-Headers': 'Content-Type, Authorization',
		};

		if (request.method === 'OPTIONS') {
			return new Response(null, { headers: corsHeaders });
		}

		// Authentication (using timing-safe comparison)
		const authHeader = request.headers.get('Authorization');
		const expectedToken = `Bearer ${env.DB_AUTH_TOKEN}`;
		if (!authHeader || !timingSafeEqual(authHeader, expectedToken)) {
			return new Response('Unauthorized', { status: 401, headers: corsHeaders });
		}

		try {
			// Job endpoints
			if (url.pathname.startsWith('/jobs')) {
				if (request.method === 'POST' && url.pathname === '/jobs') {
					return await createJob(request, env, corsHeaders);
				}
				if (request.method === 'GET' && url.pathname === '/jobs') {
					return await listJobs(url, env, corsHeaders);
				}
				const jobIdMatch = url.pathname.match(/^\/jobs\/([^/]+)$/);
				if (jobIdMatch) {
					const jobId = jobIdMatch[1];
					if (request.method === 'GET') {
						return await getJob(jobId, env, corsHeaders);
					}
					if (request.method === 'PUT') {
						return await updateJob(jobId, request, env, corsHeaders);
					}
					if (request.method === 'DELETE') {
						return await deleteJob(jobId, env, corsHeaders);
					}
				}
			}

			// User endpoints
			if (url.pathname.startsWith('/users')) {
				if (request.method === 'POST' && url.pathname === '/users') {
					return await createUser(request, env, corsHeaders);
				}
				const userIdMatch = url.pathname.match(/^\/users\/([^/]+)$/);
				if (userIdMatch) {
					const userId = userIdMatch[1];
					if (request.method === 'GET') {
						return await getUser(userId, env, corsHeaders);
					}
				}
			}

			// Processing metrics endpoints
			if (url.pathname === '/metrics' && request.method === 'POST') {
				return await createMetric(request, env, corsHeaders);
			}

		return new Response('Not Found', { status: 404, headers: corsHeaders });
		} catch (error) {
			console.error('Error handling request:', error);
			const message = error instanceof Error ? error.message : 'Unknown error';
			return new Response(`Internal Server Error: ${message}`, {
				status: 500,
				headers: corsHeaders,
			});
		}
	},
};

// Job operations
async function createJob(request: Request, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	const job: Partial<Job> = await request.json();

	if (!job.id || !job.r2_key) {
		return new Response('Missing required fields: id, r2_key', { status: 400, headers: corsHeaders });
	}

	const now = Math.floor(Date.now() / 1000);
	const status = job.status || 'submitted';

	await env.JOBS_DB.prepare(
		`INSERT INTO jobs (id, slurm_id, status, r2_key, created_at, updated_at, results_url, user_id)
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
	)
		.bind(job.id, job.slurm_id || null, status, job.r2_key, now, now, job.results_url || null, job.user_id || null)
		.run();

	return new Response(JSON.stringify({ id: job.id, status, created_at: now }), {
		status: 201,
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
}

async function getJob(jobId: string, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	const { results } = await env.JOBS_DB.prepare('SELECT * FROM jobs WHERE id = ?').bind(jobId).all();

	if (!results || results.length === 0) {
		return new Response('Job not found', { status: 404, headers: corsHeaders });
	}

	return new Response(JSON.stringify(results[0]), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
}

async function listJobs(url: URL, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	const status = url.searchParams.get('status');
	const userId = url.searchParams.get('user_id');
	
	// Validate and cap limit parameter
	const MAX_LIMIT = 1000;
	const parsedLimit = parseInt(url.searchParams.get('limit') || '100', 10);
	const limit = Number.isNaN(parsedLimit) ? 100 : Math.min(Math.max(1, parsedLimit), MAX_LIMIT);

	let query = 'SELECT * FROM jobs WHERE 1=1';
	const params: (string | number)[] = [];

	if (status) {
		query += ' AND status = ?';
		params.push(status);
	}
	if (userId) {
		query += ' AND user_id = ?';
		params.push(userId);
	}

	query += ' ORDER BY created_at DESC LIMIT ?';
	params.push(limit);

	const { results } = await env.JOBS_DB.prepare(query).bind(...params).all();

	return new Response(JSON.stringify(results || []), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
}

async function updateJob(
	jobId: string,
	request: Request,
	env: Env,
	corsHeaders: Record<string, string>
): Promise<Response> {
	const updates: Partial<Job> = await request.json();
	const now = Math.floor(Date.now() / 1000);

	const setClauses: string[] = ['updated_at = ?'];
	const params: (string | number | null)[] = [now];

	if (updates.status !== undefined) {
		setClauses.push('status = ?');
		params.push(updates.status);
	}
	if (updates.slurm_id !== undefined) {
		setClauses.push('slurm_id = ?');
		params.push(updates.slurm_id || null);
	}
	if (updates.results_url !== undefined) {
		setClauses.push('results_url = ?');
		params.push(updates.results_url || null);
	}

	params.push(jobId);

	const query = `UPDATE jobs SET ${setClauses.join(', ')} WHERE id = ?`;
	await env.JOBS_DB.prepare(query).bind(...params).run();

	// Return updated job
	return await getJob(jobId, env, corsHeaders);
}

async function deleteJob(jobId: string, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	await env.JOBS_DB.prepare('DELETE FROM jobs WHERE id = ?').bind(jobId).run();

	return new Response(null, { status: 204, headers: corsHeaders });
}

// User operations
async function createUser(request: Request, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	const user: Partial<User> = await request.json();

	if (!user.id || !user.email) {
		return new Response('Missing required fields: id, email', { status: 400, headers: corsHeaders });
	}

	const now = Math.floor(Date.now() / 1000);

	await env.JOBS_DB.prepare(
		`INSERT INTO users (id, email, name, organization, created_at, is_active)
		 VALUES (?, ?, ?, ?, ?, ?)`
	)
		.bind(user.id, user.email, user.name || null, user.organization || null, now, user.is_active ?? 1)
		.run();

	return new Response(JSON.stringify({ id: user.id, email: user.email, created_at: now }), {
		status: 201,
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
}

async function getUser(userId: string, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	const { results } = await env.JOBS_DB.prepare('SELECT * FROM users WHERE id = ?').bind(userId).all();

	if (!results || results.length === 0) {
		return new Response('User not found', { status: 404, headers: corsHeaders });
	}

	return new Response(JSON.stringify(results[0]), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
}

// Processing metrics operations
async function createMetric(request: Request, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	const metric: Partial<ProcessingMetric> = await request.json();

	if (!metric.id || !metric.job_id) {
		return new Response('Missing required fields: id, job_id', { status: 400, headers: corsHeaders });
	}

	// Verify job exists to prevent orphaned metrics
	const { results } = await env.JOBS_DB.prepare('SELECT id FROM jobs WHERE id = ?').bind(metric.job_id).all();
	if (!results || results.length === 0) {
		return new Response('Referenced job_id not found', { status: 400, headers: corsHeaders });
	}

	const now = Math.floor(Date.now() / 1000);

	await env.JOBS_DB.prepare(
		`INSERT INTO processing_metrics (id, job_id, processing_time_seconds, pdf_pages, pdf_size_bytes, success, error_message, created_at)
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
	)
		.bind(
			metric.id,
			metric.job_id,
			metric.processing_time_seconds || null,
			metric.pdf_pages || null,
			metric.pdf_size_bytes || null,
			metric.success ?? 0,
			metric.error_message || null,
			now
		)
		.run();

	return new Response(JSON.stringify({ id: metric.id, job_id: metric.job_id, created_at: now }), {
		status: 201,
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
}
