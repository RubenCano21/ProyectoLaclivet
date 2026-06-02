import api from '@/services/apiClient'
import type { AxiosError } from 'axios'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Medico {
  id: number
  nombre: string
  apellido: string
  especialidad: string | null
  genero: 'M' | 'F' | 'O' | null
  correo: string | null
  telefono: string | null
  direccion: string | null
}

export interface MedicoForm {
  nombre: string
  apellido: string
  especialidad?: string | null
  genero?: 'M' | 'F' | 'O' | null
  correo?: string | null
  telefono?: string | null
  direccion?: string | null
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

export const useMedicosStore = defineStore('medicos', () => {
  const items = ref<Medico[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const paginas = ref(1)
  const paginaActual = ref(1)

  async function fetchAll(page = 1) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/medicos/', { params: { page } })
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

  async function create(form: MedicoForm): Promise<ApiResult> {
    saving.value = true
    try {
      const { data } = await api.post('/medicos/', form)
      items.value.unshift(data)
      total.value += 1
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    } finally {
      saving.value = false
    }
  }

  async function update(id: number, form: MedicoForm): Promise<ApiResult> {
    saving.value = true
    try {
      const { data } = await api.patch(`/medicos/${id}/`, form)
      const idx = items.value.findIndex(m => m.id === id)
      if (idx !== -1) items.value[idx] = data
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    } finally {
      saving.value = false
    }
  }

  async function remove(id: number): Promise<ApiResult> {
    try {
      await api.delete(`/medicos/${id}/`)
      items.value = items.value.filter(m => m.id !== id)
      total.value = Math.max(0, total.value - 1)
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  return { items, loading, saving, error, total, paginas, paginaActual, fetchAll, create, update, remove }
})
