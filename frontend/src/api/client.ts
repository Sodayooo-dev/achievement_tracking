import { readSaved } from '@/lib/storage'
let sessionAccess = readSaved<string>('ch.access', '')
export function setAccessToken(token: string) {
  sessionAccess = token
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
export async function request<T>(
  path: string,
  method = 'GET',
  body?: unknown,
  publicRequest = false,
): Promise<T> {
  const access = sessionAccess
  let response: Response
  try {
    response = await fetch(`/api/${path}`, {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(!publicRequest && access ? { Authorization: `Bearer ${access}` } : {}),
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    })
  } catch {
    throw new ApiError(0, {}, 'Cannot reach the server. Check your connection and try again.')
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
    /* Django may return an HTML error page on failures. */
  }
  if (!response.ok) {
    if (response.status === 401 && !publicRequest && access === sessionAccess)
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
                : 'Please check the highlighted fields.'),
          ),
    )
  }
  return (raw ? data : null) as T
}
