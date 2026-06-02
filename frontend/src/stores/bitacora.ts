import api from '@/services/apiClient'
import type { AxiosError } from 'axios'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Bitacora {
  id: number
  modulo: string | null
  accion_realizada: string | null
  fecha: string
  direccion_ip: string | null
  usuario: number | null
  usuario_email: string | null
}

interface ApiResult {
  ok: boolean
  error?: string
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

export const useBitacoraStore = defineStore('bitacora', () => {
  const items = ref<Bitacora[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const paginas = ref(1)
  const paginaActual = ref(1)

  async function fetchAll(page = 1) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/bitacora/', { params: { page } })
      items.value = data.resultados ?? data ?? []
      total.value = data.total ?? items.value.length
      paginas.value = data.paginas ?? 1
      paginaActual.value = data.pagina_actual ?? 1
    } catch (err) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function remove(id: number): Promise<ApiResult> {
    try {
      await api.delete(`/bitacora/${id}/`)
      items.value = items.value.filter(b => b.id !== id)
      total.value = Math.max(0, total.value - 1)
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  return { items, loading, error, total, paginas, paginaActual, fetchAll, remove }
})
