import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'

/**
 * Composable that wraps the auth store, exposing session state and actions
 * in a convenient way for components.
 */
export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()
  const { user, isAuthenticated, loading, error } = storeToRefs(authStore)

  async function login(email: string, password: string) {
    const ok = await authStore.login(email, password)
    if (ok) router.push({ name: 'dashboard' })
    return ok
  }

  function logout() {
    authStore.logout()
    router.push({ name: 'login' })
  }

  function hasPermission(codigo: string): boolean {
    return user.value?.permisos?.some((p) => p.codigo === codigo) ?? false
  }

  function hasRole(nombre: string): boolean {
    return user.value?.rol?.nombre === nombre
  }

  return { user, isAuthenticated, loading, error, login, logout, hasPermission, hasRole }
}
