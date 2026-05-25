import { useAuthStore } from '@/stores/auth'
import { createRouter, createWebHistory } from 'vue-router'
import { routes } from './routes'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  // Redirect unauthenticated users to login
  if (!to.meta.public && !auth.isAuthenticated) {
    return '/login'
  }

  // Redirect already-authenticated users away from login
  if (to.name === 'login' && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }

  // Permission guard: if route declares a required permission, enforce it
  const requiredPermiso = to.meta.permiso as string | undefined
  if (requiredPermiso && !auth.user?.permisos?.some((p) => p.codigo === requiredPermiso)) {
    return { name: 'dashboard' }
  }
})

export default router
