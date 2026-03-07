// middleware/auth.ts
export default defineNuxtRouteMiddleware((to) => {
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
    '/dashboard/root': ['root'],
    '/dashboard/coordenador': ['coordenador', 'root'],
    '/dashboard/professor': ['professor', 'root'],
  }

  const requiredRoles = Object.entries(roleGuards).find(([path]) =>
    to.path.startsWith(path)
  )?.[1]

  if (requiredRoles && user.value && !requiredRoles.includes(user.value.role)) {
    return navigateTo(getDashboardRoute(user.value.role))
  }
})