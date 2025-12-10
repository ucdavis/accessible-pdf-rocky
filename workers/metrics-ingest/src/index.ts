/**
 * Metrics Ingestion Worker
 *
 * Receives metrics from HPC and FastAPI controller, stores in D1,
 * and exposes Prometheus-compatible endpoint for monitoring.
 */

export interface Env {
	METRICS_DB: D1Database;
	METRICS_AUTH_TOKEN: string;
	METRICS_RETENTION_DAYS?: string; // Optional, defaults to 7
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

interface MetricPayload {
	source: string; // "hpc" or "fastapi"
	timestamp: number; // Unix timestamp (seconds)
	metrics: Record<string, number>;
}

interface MetricRow {
	id: number;
	source: string;
	timestamp: number;
	metric_name: string;
	metric_value: number;
}

export default {
	async fetch(request: Request, env: Env, _ctx: ExecutionContext): Promise<Response> {
		const url = new URL(request.url);

		// CORS headers for browser access
		// Note: Using '*' for Access-Control-Allow-Origin. In production, consider
		// restricting to specific trusted origins via environment variable.
		const corsHeaders = {
			'Access-Control-Allow-Origin': '*',
			'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
			'Access-Control-Allow-Headers': 'Content-Type, Authorization',
		};

		if (request.method === 'OPTIONS') {
			return new Response(null, { headers: corsHeaders });
		}

		try {
			// POST /ingest - receive metrics from HPC/FastAPI
			if (url.pathname === '/ingest' && request.method === 'POST') {
				return await handleIngest(request, env, corsHeaders);
			}

			// GET /metrics - Prometheus-compatible export
			if (url.pathname === '/metrics' && request.method === 'GET') {
				return await handlePrometheusMetrics(env);
			}

			// GET /api/metrics - JSON API for dashboards
			if (url.pathname === '/api/metrics' && request.method === 'GET') {
				return await handleApiMetrics(url, env, corsHeaders);
			}

			// GET /api/sources - list available sources
			if (url.pathname === '/api/sources' && request.method === 'GET') {
				return await handleApiSources(env, corsHeaders);
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

	async scheduled(event: ScheduledEvent, env: Env, _ctx: ExecutionContext): Promise<void> {
		// Automated data retention - delete old metrics
		const retentionDays = parseInt(env.METRICS_RETENTION_DAYS || '7', 10);
		const cutoffTimestamp = Math.floor(Date.now() / 1000) - retentionDays * 86400;

		console.log(
			`Cleaning up metrics older than ${retentionDays} days (timestamp < ${cutoffTimestamp})`
		);

		try {
			const result = await env.METRICS_DB.prepare(
				'DELETE FROM metrics WHERE timestamp < ?'
			).bind(cutoffTimestamp).run();

			console.log(
				`Data retention cleanup completed. Rows deleted: ${result.meta.changes || 0}`
			);
		} catch (error) {
			console.error('Failed to clean up old metrics:', error);
			// Don't throw - let the cron trigger retry
		}
	},
};

async function handleIngest(request: Request, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	// Authenticate (using timing-safe comparison)
	const authHeader = request.headers.get('Authorization');
	const expectedToken = `Bearer ${env.METRICS_AUTH_TOKEN}`;
	if (!authHeader || !timingSafeEqual(authHeader, expectedToken)) {
		return new Response('Unauthorized', { status: 401, headers: corsHeaders });
	}

	// Parse JSON with error handling
	let payload: MetricPayload;
	try {
		payload = await request.json();
	} catch {
		return new Response('Invalid JSON payload', {
			status: 400,
			headers: corsHeaders,
		});
	}

	// Validate payload
	if (!payload.source || !payload.timestamp || !payload.metrics) {
		return new Response('Invalid payload: missing source, timestamp, or metrics', {
			status: 400,
			headers: corsHeaders,
		});
	}

	if (typeof payload.metrics !== 'object') {
		return new Response('Invalid payload: metrics must be an object', {
			status: 400,
			headers: corsHeaders,
		});
	}

	// Insert metrics into D1
	const stmt = env.METRICS_DB.prepare(`
		INSERT INTO metrics (source, timestamp, metric_name, metric_value)
		VALUES (?, ?, ?, ?)
	`);

	const batch = [];
	for (const [name, value] of Object.entries(payload.metrics)) {
		if (typeof value !== 'number') {
			console.warn(`Skipping non-numeric metric: ${name}=${value}`);
			continue;
		}
		batch.push(stmt.bind(payload.source, payload.timestamp, name, value));
	}

	if (batch.length > 0) {
		await env.METRICS_DB.batch(batch);
	}

	return new Response(
		JSON.stringify({
			status: 'ok',
			inserted: batch.length,
		}),
		{
			status: 200,
			headers: { ...corsHeaders, 'Content-Type': 'application/json' },
		}
	);
}

async function handlePrometheusMetrics(env: Env): Promise<Response> {
	// Get latest metrics for each metric name + source combination
	const { results } = await env.METRICS_DB.prepare(`
		SELECT 
			m1.source,
			m1.metric_name,
			m1.metric_value,
			m1.timestamp
		FROM metrics m1
		INNER JOIN (
			SELECT source, metric_name, MAX(timestamp) as max_timestamp
			FROM metrics
			WHERE timestamp > ?
			GROUP BY source, metric_name
		) m2 ON m1.source = m2.source 
			AND m1.metric_name = m2.metric_name 
			AND m1.timestamp = m2.max_timestamp
		ORDER BY m1.source, m1.metric_name
	`).bind(Math.floor(Date.now() / 1000) - 600).all(); // Last 10 minutes

	// Convert to Prometheus format
	let output = '';
	const groupedMetrics = new Map<string, MetricRow[]>();

	for (const row of results as MetricRow[]) {
		if (!groupedMetrics.has(row.metric_name)) {
			groupedMetrics.set(row.metric_name, []);
		}
		groupedMetrics.get(row.metric_name)!.push(row);
	}

	for (const [metricName, rows] of groupedMetrics) {
		// Add HELP and TYPE comments (assume all are gauges for simplicity)
		const sources = [...new Set(rows.map((r) => r.source))].join(', ');
		output += `# HELP ${metricName} Metric from ${sources}\n`;
		output += `# TYPE ${metricName} gauge\n`;

		for (const row of rows) {
			output += `${metricName}{source="${row.source}"} ${row.metric_value} ${row.timestamp * 1000}\n`;
		}
	}

	return new Response(output, {
		headers: { 'Content-Type': 'text/plain; version=0.0.4' },
	});
}

async function handleApiMetrics(url: URL, env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	const source = url.searchParams.get('source');
	const window = url.searchParams.get('window') || '1h';
	const metricName = url.searchParams.get('metric');

	const windowSeconds = parseWindow(window);
	const startTime = Math.floor(Date.now() / 1000) - windowSeconds;

	let query = `
		SELECT source, timestamp, metric_name, metric_value
		FROM metrics
		WHERE timestamp > ?
	`;
	const params: (string | number)[] = [startTime];

	if (source) {
		query += ' AND source = ?';
		params.push(source);
	}

	if (metricName) {
		query += ' AND metric_name = ?';
		params.push(metricName);
	}

	query += ' ORDER BY timestamp DESC LIMIT 10000';

	const { results } = await env.METRICS_DB.prepare(query).bind(...params).all();

	return new Response(JSON.stringify(results, null, 2), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
}

async function handleApiSources(env: Env, corsHeaders: Record<string, string>): Promise<Response> {
	const { results } = await env.METRICS_DB.prepare(`
		SELECT DISTINCT source
		FROM metrics
		WHERE timestamp > ?
		ORDER BY source
	`).bind(Math.floor(Date.now() / 1000) - 3600).all(); // Last hour

	const sources = results.map((row: { source: string }) => row.source);

	return new Response(JSON.stringify(sources, null, 2), {
		headers: { ...corsHeaders, 'Content-Type': 'application/json' },
	});
}

function parseWindow(window: string): number {
	const match = window.match(/^(\d+)([smhd])$/);
	if (!match) return 3600; // Default 1h in seconds

	const [, num, unit] = match;
	const multipliers: Record<string, number> = {
		s: 1,
		m: 60,
		h: 3600,
		d: 86400,
	};
	return parseInt(num) * multipliers[unit];
}
