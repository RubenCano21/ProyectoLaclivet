import api from '@/lib/api'
import type { AxiosError } from 'axios'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Propietario {
  id: number
  ci: string
  nombre: string
  apellido: string
  correo: string
  telefono: string
  direccion: string
}

export type PropietarioForm = Omit<Propietario, 'id'>

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

export const usePropietariosStore = defineStore('propietarios', () => {
  const items = ref<Propietario[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)

  async function fetchAll() {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/propietarios/')
      items.value = data
    } catch (err) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function create(form: PropietarioForm): Promise<ApiResult> {
    saving.value = true
    try {
      const { data } = await api.post('/propietarios/', form)
      items.value.unshift(data)
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    } finally {
      saving.value = false
    }
  }

  async function update(id: number, form: PropietarioForm): Promise<ApiResult> {
    saving.value = true
    try {
      const { data } = await api.patch(`/propietarios/${id}/`, form)
      const idx = items.value.findIndex(p => p.id === id)
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
      await api.delete(`/propietarios/${id}/`)
      items.value = items.value.filter(p => p.id !== id)
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  return { items, loading, saving, error, fetchAll, create, update, remove }
})
