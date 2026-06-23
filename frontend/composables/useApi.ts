/**
 * API request composable.
 * Wraps fetch calls to the FastAPI backend with auth header support.
 */
export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const getToken = (): string | null => {
    if (import.meta.client) {
      return localStorage.getItem('token')
    }
    return null
  }

  const request = async <T>(
    path: string,
    options: {
      method?: string
      body?: any
      params?: Record<string, any>
    } = {}
  ): Promise<T> => {
    const { method = 'GET', body, params } = options

    // Build URL with query params
    const url = new URL(`${apiBase}${path}`)
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          url.searchParams.set(key, String(value))
        }
      })
    }

    // Build headers
    const headers: Record<string, string> = {}
    const token = getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    if (body && !(body instanceof FormData)) {
      headers['Content-Type'] = 'application/json'
    }

    const response = await fetch(url.toString(), {
      method,
      headers,
      body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `API error: ${response.status}`)
    }

    return response.json()
  }

  return {
    get: <T>(path: string, params?: Record<string, any>) =>
      request<T>(path, { method: 'GET', params }),
    post: <T>(path: string, body?: any) =>
      request<T>(path, { method: 'POST', body }),
    put: <T>(path: string, body?: any) =>
      request<T>(path, { method: 'PUT', body }),
    delete: <T>(path: string) =>
      request<T>(path, { method: 'DELETE' }),
    upload: <T>(path: string, formData: FormData) =>
      request<T>(path, { method: 'POST', body: formData }),
  }
}
