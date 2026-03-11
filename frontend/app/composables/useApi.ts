// composables/useApi.ts
const BASE_URL = 'http://localhost:8000'

export function useApi() {
  // useState é compartilhado entre servidor e cliente no Nuxt.
  // No servidor, localStorage não existe — inicializa como null.
  // No cliente, após hidratação, useCookie garante que o valor persiste no F5.
  const tokenCookie = useCookie<string | null>('samba_token', {
    default: () => null,
    maxAge: 60 * 60 * 8, // 8 horas
    sameSite: 'lax',
  })

  // Estado reativo sincronizado com o cookie
  const accessToken = useState<string | null>('access_token', () => tokenCookie.value)

  // Mantém cookie e estado sincronizados
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

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    if (!isFormData) {
      headers['Content-Type'] = 'application/json'
    }

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