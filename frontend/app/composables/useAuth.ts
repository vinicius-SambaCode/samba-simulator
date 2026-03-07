// composables/useAuth.ts
export type UserRole = 'root' | 'coordenador' | 'professor'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  escola?: string
}

const MOCK_USERS: Record<string, User> = {
  root: {
    id: '1',
    name: 'Admin Root',
    email: 'root@smesp.edu.br',
    role: 'root',
  },
  coordenador: {
    id: '2',
    name: 'Maria Silva',
    email: 'msilva@emef.smesp.edu.br',
    role: 'coordenador',
    escola: 'EMEF Prof. João Pessoa',
  },
  professor: {
    id: '3',
    name: 'Carlos Mendes',
    email: 'cmendes@emef.smesp.edu.br',
    role: 'professor',
    escola: 'EMEF Prof. João Pessoa',
  },
}

const currentUser = ref<User | null>(null)

export function useAuth() {
  const roleRoutes: Record<UserRole, string> = {
    root: '/dashboard/root',
    coordenador: '/dashboard/coordenador',
    professor: '/dashboard/professor',
  }

  async function login(email: string, password: string): Promise<boolean> {
    await new Promise(r => setTimeout(r, 800))
    let mockUser: User | undefined
    if (email.startsWith('root')) mockUser = MOCK_USERS.root
    else if (email.startsWith('coord')) mockUser = MOCK_USERS.coordenador
    else mockUser = MOCK_USERS.professor
    if (mockUser) {
      currentUser.value = mockUser
      return true
    }
    return false
  }

  async function logout() {
    currentUser.value = null
    await navigateTo('/login')
  }

  function getDashboardRoute(role: UserRole) {
    return roleRoutes[role]
  }

  return {
    user: readonly(currentUser),
    isAuthenticated: computed(() => !!currentUser.value),
    login,
    logout,
    getDashboardRoute,
  }
}