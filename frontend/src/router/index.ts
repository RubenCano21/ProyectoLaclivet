import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    permiso?: string
    roles?: string[]
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})


// Strip trailing slashes (e.g. /propietarios/ → /propietarios)
router.beforeEach((to) => {
  if (to.path !== '/' && to.path.endsWith('/')) {
    return { path: to.path.slice(0, -1), query: to.query, hash: to.hash, replace: true }
  }
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  // Redirect unauthenticated users to login
  if (!to.meta.public && !auth.isAuthenticated) {
    return '/login'
  }

  // Redirect already-authenticated users away from login
  if (to.name === 'login' && auth.isAuthenticated) {
    const esPropietario = auth.user?.rol?.nombre === 'Propietario'
    return esPropietario ? { name: 'portal-mascotas' } : { name: 'dashboard' }
  }

  // Redirect Propietario away from staff dashboard to their portal
  if (to.name === 'dashboard' && auth.user?.rol?.nombre === 'Propietario') {
    return { name: 'portal-mascotas' }
  }

  // Role guard: user must have one of the declared roles
  const requiredRoles = to.meta.roles as string[] | undefined
  if (requiredRoles && !requiredRoles.includes(auth.user?.rol?.nombre ?? '')) {
    // Propietario trying to access staff routes → portal; staff → dashboard
    return auth.user?.rol?.nombre === 'Propietario'
      ? { name: 'portal-mascotas' }
      : { name: 'dashboard' }
  }

  // Permission guard: user must have the declared permission code
  const requiredPermiso = to.meta.permiso as string | undefined
  if (requiredPermiso && !auth.user?.permisos?.some((p) => p.codigo === requiredPermiso)) {
    return { name: 'dashboard' }
  }
})

export default router
