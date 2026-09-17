type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'

type RefreshHandler = () => Promise<string | null>

interface RequestOptions {
  /** Bei 401 keine Erneuerung versuchen, etwa für Anmelden oder die Erneuerung selbst */
  skipRefresh?: boolean
}

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL

let accessToken: string | null = null
let refreshHandler: RefreshHandler | null = null
let pendingRefresh: Promise<string | null> | null = null

export class HttpError extends Error {
  readonly status: number
  readonly data: unknown

  constructor(status: number, data: unknown) {
    super(`Anfrage fehlgeschlagen mit Status ${status}`)
    this.name = 'HttpError'
    this.status = status
    this.data = data
  }
}

export function setAccessToken(token: string | null): void {
  accessToken = token
}

export function setRefreshHandler(handler: RefreshHandler): void {
  refreshHandler = handler
}

function refreshOnce(): Promise<string | null> {
  if (!refreshHandler) return Promise.resolve(null)

  pendingRefresh ??= refreshHandler().finally(() => {
    pendingRefresh = null
  })

  return pendingRefresh
}

async function readBody(response: Response): Promise<unknown> {
  if (response.status === 204) return null

  const contentType = response.headers.get('Content-Type') ?? ''

  if (!contentType.includes('application/json')) return null

  return response.json()
}

function send(method: HttpMethod, endpoint: string, payload: unknown): Promise<Response> {
  const headers = new Headers({ Accept: 'application/json' })

  if (payload !== undefined) headers.set('Content-Type', 'application/json')
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

  return fetch(API_BASE_URL + endpoint, {
    method,
    headers,
    credentials: 'include',
    body: payload === undefined ? undefined : JSON.stringify(payload),
  })
}

export async function request<T>(
  method: HttpMethod,
  endpoint: string,
  payload?: unknown,
  options: RequestOptions = {},
): Promise<T> {
  let response = await send(method, endpoint, payload)

  if (response.status === 401 && accessToken && !options.skipRefresh) {
    const newToken = await refreshOnce()

    if (newToken) response = await send(method, endpoint, payload)
  }

  const data = await readBody(response)

  if (!response.ok) throw new HttpError(response.status, data)

  return data as T
}

export const http = {
  get: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>('GET', endpoint, undefined, options),
  post: <T>(endpoint: string, payload?: unknown, options?: RequestOptions) =>
    request<T>('POST', endpoint, payload, options),
  put: <T>(endpoint: string, payload?: unknown, options?: RequestOptions) =>
    request<T>('PUT', endpoint, payload, options),
  patch: <T>(endpoint: string, payload?: unknown, options?: RequestOptions) =>
    request<T>('PATCH', endpoint, payload, options),
  delete: <T>(endpoint: string, options?: RequestOptions) =>
    request<T>('DELETE', endpoint, undefined, options),
}
