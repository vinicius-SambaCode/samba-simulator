// middleware/auth.ts
export default defineNuxtRouteMiddleware((to) => {
  // Durante SSR, o cookie já está disponível via useCookie no useApi/useAuth.
  // Mas se por algum motivo o estado ainda não hidratou, deixa o client resolver.
  if (import.meta.server) return

  const { isAuthenticated, user, getDashboardRoute } = useAuth()

  if (to.path === '/login') {
    if (isAuthenticated.value && user.value) {
      return navigateTo(getDashboardRoute(user.value.role))
    }
    return
  }

  if (to.path === '/') {
    if (!isAuthenticated.value) return navigateTo('/login')
    if (user.value) return navigateTo(getDashboardRoute(user.value.role))
  }

  if (!isAuthenticated.value) return navigateTo('/login')

  const roleGuards: Record<string, string[]> = {
    '/dashboard/root':        ['root'],
    '/dashboard/coordenador': ['coordenador', 'root'],
    '/dashboard/professor':   ['professor', 'root'],
  }

  const requiredRoles = Object.entries(roleGuards).find(([path]) =>
    to.path.startsWith(path)
  )?.[1]

  if (requiredRoles && user.value && !requiredRoles.includes(user.value.role)) {
    return navigateTo(getDashboardRoute(user.value.role))
  }
})