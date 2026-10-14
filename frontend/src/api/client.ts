import { readSaved, save } from '@/lib/storage'
let sessionAccess = readSaved<string>('ch.access', '')
let sessionRefresh = readSaved<string>('ch.refresh', '')
let epoch = 0
let renewing: Promise<boolean> | null = null
export function setAccessToken(token: string, refresh = '') {
  epoch++
  sessionAccess = token
  sessionRefresh = refresh
  renewing = null
}
export class ApiError extends Error {
  constructor(
    public status: number,
    public fields: Record<string, unknown>,
    message: string,
  ) {
    super(message)
  }
}
async function renew(): Promise<boolean> {
  if (!sessionRefresh) return false
  if (renewing) return renewing
  const generation = epoch,
    token = sessionRefresh
  const task = (async () => {
    try {
      const response = await fetch('/api/token/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: token }),
        signal: AbortSignal.timeout(20000),
      })
      if (!response.ok) return false
      const data = await response.json()
      if (generation !== epoch || typeof data.access !== 'string') return false
      sessionAccess = data.access
      if (data.refresh) sessionRefresh = data.refresh
      save('ch.access', sessionAccess)
      save('ch.refresh', sessionRefresh)
      window.dispatchEvent(new CustomEvent('token-refreshed', { detail: sessionAccess }))
      return true
    } catch {
      return false
    }
  })()
  renewing = task
  try {
    return await task
  } finally {
    if (renewing === task) renewing = null
  }
}
export async function request<T>(
  path: string,
  method = 'GET',
  body?: unknown,
  publicRequest = false,
  retried = false,
): Promise<T> {
  const access = sessionAccess,
    generation = epoch,
    multipart = body instanceof FormData
  let response: Response
  try {
    response = await fetch('/api/' + path, {
      method,
      headers: {
        ...(!multipart ? { 'Content-Type': 'application/json' } : {}),
        ...(!publicRequest && access ? { Authorization: 'Bearer ' + access } : {}),
      },
      ...(body === undefined
        ? {}
        : { body: multipart ? (body as FormData) : JSON.stringify(body) }),
      signal: AbortSignal.timeout(20000),
    })
  } catch (error) {
    throw new ApiError(
      0,
      {},
      error instanceof Error && (error.name === 'TimeoutError' || error.name === 'AbortError')
        ? 'The server took too long. Please retry.'
        : 'Cannot reach the server. Check your connection and try again.',
    )
  }
  if (response.status === 401 && !publicRequest && !retried && generation === epoch) {
    if ((access !== sessionAccess && sessionAccess) || (await renew()))
      return request<T>(path, method, body, publicRequest, true)
  }
  const raw = await response.text()
  let data: Record<string, unknown> = {}
  try {
    data = raw ? JSON.parse(raw) : {}
  } catch {
    if (response.ok)
      throw new ApiError(
        response.status,
        {},
        'The server returned an unreadable response. Try again.',
      )
  }
  if (!response.ok) {
    if (response.status === 401 && !publicRequest && generation === epoch)
      window.dispatchEvent(new Event('session-expired'))
    throw new ApiError(
      response.status,
      data,
      response.status === 403
        ? 'Developer access only.'
        : String(
            data.message ??
              data.detail ??
              (response.status >= 500
                ? 'The server could not complete this request.'
                : Array.isArray(data.non_field_errors)
                  ? data.non_field_errors.join(' ')
                  : 'Please check the highlighted fields.'),
          ),
    )
  }
  return (raw ? data : null) as T
}
