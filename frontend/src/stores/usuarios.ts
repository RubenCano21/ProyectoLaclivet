import api from '@/lib/api'
import type { AxiosError } from 'axios'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Usuario {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  fecha_creacion: string
  is_active: boolean
  is_staff: boolean
}

function extractError(err: unknown): string {
  const axiosErr = err as AxiosError<Record<string, string | string[]>>
  const d = axiosErr.response?.data
  if (!d) return 'Error de conexión'
  for (const v of Object.values(d)) {
    if (Array.isArray(v) && v[0]) return String(v[0])
    if (typeof v === 'string') return v
  }
  return 'Error inesperado'
}

export const useUsuariosStore = defineStore('usuarios', () => {
  const items = ref<Usuario[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/usuarios/')
      items.value = data
    } catch (err) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  return { items, loading, error, fetchAll }
})
