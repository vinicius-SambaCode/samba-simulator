// composables/useApi.ts
export function useApi() {
  const config = useRuntimeConfig()
  const BASE_URL = config.public.apiBase as string

  const tokenCookie = useCookie<string | null>('samba_token', {
    default: () => null,
    maxAge: 60 * 60 * 8,
    sameSite: 'lax',
  })

  const accessToken = useState<string | null>('access_token', () => tokenCookie.value)

  watch(accessToken, (val) => {
    tokenCookie.value = val
  })

  async function request<T>(
    method: string,
    path: string,
    body?: Record<string, unknown> | FormData,
    isFormData = false,
  ): Promise<T> {
    const headers: Record<string, string> = {}
    const token = accessToken.value ?? tokenCookie.value
    if (token) headers['Authorization'] = `Bearer ${token}`
    if (!isFormData) headers['Content-Type'] = 'application/json'

    const res = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      credentials: 'include',
      body: body
        ? isFormData
          ? (body as FormData)
          : JSON.stringify(body)
        : undefined,
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: `Erro ${res.status}` }))
      throw { data: err, status: res.status, message: err.detail ?? `Erro ${res.status}` }
    }

    if (res.status === 204) return undefined as T
    return res.json() as Promise<T>
  }

  return {
    get:    <T>(path: string) => request<T>('GET', path),
    post:   <T>(path: string, body: Record<string, unknown>) => request<T>('POST', path, body),
    put:    <T>(path: string, body: Record<string, unknown>) => request<T>('PUT', path, body),
    patch:  <T>(path: string, body: Record<string, unknown>) => request<T>('PATCH', path, body),
    delete: <T>(path: string) => request<T>('DELETE', path),
    upload: <T>(path: string, formData: FormData) => request<T>('POST', path, formData, true),
    accessToken,
  }
}
