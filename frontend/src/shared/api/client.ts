// Base URL of the Django API from .env (VITE_API_BASE_URL), e.g. https://api.example.com.
// API paths have no trailing slash, e.g. /auth/me.
const BASE_URL = import.meta.env.VITE_API_BASE_URL

const CSRF_COOKIE = 'csrftoken'
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS'])

/** API error response: { code, message, errors? }. errors only exists for validation errors. */
interface ErrorBody {
	code?: string
	message?: string
	/** Errors per field, nested fields joined with a dot, e.g. ingredients.0.amount */
	errors?: Record<string, string[]>
}

/** API error response, e.g. field errors like { email: ['...'] } or code email_taken */
export class ApiError extends Error {
	constructor(
		readonly status: number,
		readonly data: unknown,
	) {
		super((data as ErrorBody | undefined)?.message ?? `API-Anfrage fehlgeschlagen (${status})`)
	}

	/** API error code, e.g. validation_error, email_taken or consent_required */
	get code(): string | null {
		return (this.data as ErrorBody | undefined)?.code ?? null
	}

	/** API field errors, empty without validation errors */
	get fieldErrors(): Record<string, string[]> {
		return (this.data as ErrorBody | undefined)?.errors ?? {}
	}

	/** Whether the API reports an error for this field, e.g. password for a weak password */
	hasFieldError(field: string): boolean {
		return (this.fieldErrors[field]?.length ?? 0) > 0
	}
}

/** Response of paginated lists (recipes, food search), 20 items each */
export interface Paginated<T> {
	count: number
	next: string | null
	previous: string | null
	results: T[]
}

export interface ApiRequestOptions {
	method?: 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE'
	/** Sent as JSON, FormData as multipart/form-data */
	body?: unknown
	/** Do not refresh on 401, e.g. for the sign-in request itself */
	skipRefresh?: boolean
}

let onSessionExpired: (() => void) | null = null
let pendingRefresh: Promise<boolean> | null = null

/** Called when even the refresh token can no longer be renewed */
export function setSessionExpiredHandler(handler: () => void): void {
	onSessionExpired = handler
}

function readCookie(name: string): string | null {
	const match = document.cookie.split('; ').find((cookie) => cookie.startsWith(`${name}=`))

	return match ? decodeURIComponent(match.slice(name.length + 1)) : null
}

async function csrfToken(): Promise<string | null> {
	if (!readCookie(CSRF_COOKIE)) {
		await fetch(`${BASE_URL}/auth/csrf`, { credentials: 'include' })
	}

	return readCookie(CSRF_COOKIE)
}

/** Query string from params. Arrays are repeated (?equipment=oven&equipment=stove). */
export function toQuery(
	params: Record<string, string | number | boolean | readonly string[] | null | undefined>,
): string {
	const search = new URLSearchParams()

	for (const [key, value] of Object.entries(params)) {
		if (value === null || value === undefined || value === '' || value === false) continue

		for (const item of Array.isArray(value) ? value : [value]) search.append(key, String(item))
	}

	const query = search.toString()

	return query ? `?${query}` : ''
}

async function send(path: string, options: ApiRequestOptions): Promise<Response> {
	const method = options.method ?? 'GET'
	const headers: Record<string, string> = { Accept: 'application/json' }
	const isForm = options.body instanceof FormData

	// For FormData the browser sets the Content-Type including the boundary itself
	if (options.body !== undefined && !isForm) headers['Content-Type'] = 'application/json'

	if (!SAFE_METHODS.has(method)) {
		const token = await csrfToken()

		if (token) headers['X-CSRFToken'] = token
	}

	return fetch(`${BASE_URL}${path}`, {
		method,
		headers,
		credentials: 'include',
		body:
			options.body === undefined
				? undefined
				: isForm
					? (options.body as FormData)
					: JSON.stringify(options.body),
	})
}

/**
 * Fetches a new access token. When several requests hit a 401 at the same time, they share one
 * refresh; otherwise the rotated refresh token would already be blocked the second time.
 */
export function refreshSession(): Promise<boolean> {
	pendingRefresh ??= send('/auth/refresh', { method: 'POST' })
		.then((response) => response.ok)
		.catch(() => false)
		.finally(() => {
			pendingRefresh = null
		})

	return pendingRefresh
}

async function parse(response: Response): Promise<unknown> {
	if (response.status === 204) return undefined

	const text = await response.text()

	try {
		return text ? JSON.parse(text) : undefined
	} catch {
		// E.g. an HTML error page from the proxy when the backend is not running
		return undefined
	}
}

/** Throws ApiError on an error response. An expired access token is refreshed once. */
export async function apiRequest<T = void>(
	path: string,
	options: ApiRequestOptions = {},
): Promise<T> {
	let response = await send(path, options)

	if (response.status === 401 && !options.skipRefresh) {
		if (await refreshSession()) {
			response = await send(path, options)
		} else {
			onSessionExpired?.()
		}
	}

	const data = await parse(response)

	if (!response.ok) throw new ApiError(response.status, data)

	return data as T
}
