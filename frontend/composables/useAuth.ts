/**
 * Authentication composable.
 * Manages login state, token storage, and user info.
 */

interface User {
  id: number
  email: string
  nickname: string
  avatar_url: string
  auth_provider: string
  created_at: string
}

export const useAuth = () => {
  const api = useApi()
  const user = useState<User | null>('auth-user', () => null)
  const isLoggedIn = computed(() => !!user.value)

  const setToken = (token: string) => {
    if (import.meta.client) {
      localStorage.setItem('token', token)
    }
  }

  const removeToken = () => {
    if (import.meta.client) {
      localStorage.removeItem('token')
    }
  }

  const getToken = (): string | null => {
    if (import.meta.client) {
      return localStorage.getItem('token')
    }
    return null
  }

  const fetchUser = async () => {
    try {
      const token = getToken()
      if (!token) {
        user.value = null
        return
      }
      const data = await api.get<User>('/api/auth/me')
      user.value = data
    } catch {
      user.value = null
      removeToken()
    }
  }

  const login = async (email: string, password: string) => {
    const data = await api.post<{ access_token: string }>('/api/auth/login', { email, password })
    setToken(data.access_token)
    await fetchUser()
  }

  const register = async (email: string, password: string, nickname?: string) => {
    const data = await api.post<{ access_token: string }>('/api/auth/register', {
      email,
      password,
      nickname,
    })
    setToken(data.access_token)
    await fetchUser()
  }

  const logout = () => {
    removeToken()
    user.value = null
    navigateTo('/login')
  }

  // Initialize: try to fetch user on composable creation
  const init = async () => {
    if (getToken() && !user.value) {
      await fetchUser()
    }
  }

  return {
    user,
    isLoggedIn,
    login,
    register,
    logout,
    fetchUser,
    init,
  }
}
