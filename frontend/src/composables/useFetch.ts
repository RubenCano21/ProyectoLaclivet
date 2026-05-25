import { ref } from 'vue'
import api from '@/services/apiClient'
import type { AxiosRequestConfig } from 'axios'

/**
 * Generic composable for HTTP requests.
 * Manages loading state, data and error in a consistent way across all views.
 *
 * @example
 * const { data, loading, error, execute } = useFetch<Paciente[]>('/pacientes/')
 * onMounted(execute)
 */
export function useFetch<T = unknown>(url: string, config?: AxiosRequestConfig) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function execute(overrideConfig?: AxiosRequestConfig): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<T>(url, { ...config, ...overrideConfig })
      data.value = response.data
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: Record<string, unknown> } }
      const d = axiosErr.response?.data
      if (d) {
        const first = Object.values(d)[0]
        error.value = Array.isArray(first) ? String(first[0]) : String(first ?? 'Error al cargar datos')
      } else {
        error.value = 'Error de conexión'
      }
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, execute }
}
