// composables/useAuth.ts
type BackendRole = 'ADMIN' | 'COORDINATOR' | 'TEACHER' | 'admin' | 'coordinator' | 'teacher'

export type UserRole = 'root' | 'coordenador' | 'professor'

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
  roles: UserRole[]
  mustChangePassword: boolean
}

function mapRole(backendRole: string): UserRole {
  const map: Record<string, UserRole> = {
    ADMIN:       'root',
    admin:       'root',
    COORDINATOR: 'coordenador',
    coordinator: 'coordenador',
    TEACHER:     'professor',
    teacher:     'professor',
  }
  return map[backendRole] ?? 'professor'
}

export function useAuth() {
  const currentUser = useState<User | null>('current_user', () => null)
  const { get, accessToken } = useApi()

  const roleRoutes: Record<UserRole, string> = {
    root:        '/dashboard/root',
    coordenador: '/dashboard/coordenador',
    professor:   '/dashboard/professor',
  }

  function getDashboardRoute(role: UserRole) {
    return roleRoutes[role]
  }

  async function fetchMe() {
    try {
      const me = await get<{
        id: number
        name: string
        email: string
        roles: BackendRole[]
        must_change_password: boolean
      }>('/auth/me')

      const mappedRoles = me.roles.map(mapRole)
      const priority: UserRole[] = ['root', 'coordenador', 'professor']
      const primaryRole = priority.find(r => mappedRoles.includes(r)) ?? 'professor'

      currentUser.value = {
        id:                 me.id,
        name:               me.name,
        email:              me.email,
        role:               primaryRole,
        roles:              mappedRoles,
        mustChangePassword: me.must_change_password ?? false,
      }
    } catch {
      currentUser.value = null
      accessToken.value = null
    }
  }

  async function login(email: string, password: string): Promise<'ok' | 'change_password' | 'error'> {
    try {
      const formData = new URLSearchParams()
      formData.append('username', email)
      formData.append('password', password)

      const res = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        credentials: 'include',
        body: formData.toString(),
      })

      if (!res.ok) return 'error'

      const data = await res.json()
      accessToken.value = data.access_token

      await fetchMe()
      if (!currentUser.value) return 'error'

      if (currentUser.value.mustChangePassword) return 'change_password'
      return 'ok'
    } catch {
      return 'error'
    }
  }

  async function logout() {
    try {
      await fetch('http://localhost:8000/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(accessToken.value ? { Authorization: `Bearer ${accessToken.value}` } : {}),
        },
        credentials: 'include',
        body: JSON.stringify({ logout_all: false }),
      })
    } catch {}

    currentUser.value = null
    accessToken.value = null
    await navigateTo('/login')
  }

  return {
    user:            readonly(currentUser),
    isAuthenticated: computed(() => !!currentUser.value),
    login,
    logout,
    fetchMe,
    getDashboardRoute,
  }
}
