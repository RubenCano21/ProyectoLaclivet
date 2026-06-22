import api from '@/services/apiClient'
import type { AxiosError } from 'axios'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UsuarioResumen {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  ci: string | null          // ← agregar
  fecha_creacion: string
  is_active: boolean
  is_staff: boolean
  rol: { id: number; nombre: string; descripcion: string } | null
}

export interface UsuarioDetalle extends UsuarioResumen {
  telefono: string | null
  direccion: string | null
  fecha_nacimiento: string | null
  fecha_actualizacion: string
  rol: { id: number; nombre: string; descripcion: string } | null
  permisos: { id: number; nombre: string; codigo: string; descripcion: string }[]
}

export interface RegisterForm {
  email: string
  first_name: string
  last_name?: string
  ci?: string | null         // ← agregar
  telefono?: string | null
  direccion?: string | null
  fecha_nacimiento?: string | null
  rol_id?: number | null
  // password y password2 eliminados — el backend los genera automáticamente
}

export interface AdminActualizarForm {
  first_name?: string
  last_name?: string
  email?: string
  ci?: string | null         // ← agregar
  telefono?: string | null
  direccion?: string | null
  fecha_nacimiento?: string | null
  is_active?: boolean
  is_staff?: boolean
  rol_id?: number | null
}

export interface ApiResult {
  ok: boolean
  error?: string
}

export type Usuario = UsuarioResumen

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
  const items = ref<UsuarioResumen[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const paginas = ref(1)
  const paginaActual = ref(1)

  async function fetchAll(page = 1) {
    loading.value = true
    error.value = null
    try {
      const { data } = await api.get('/usuarios/', { params: { page } })
      items.value = data.resultados
      total.value = data.total
      paginas.value = data.paginas
      paginaActual.value = data.pagina_actual
    } catch (err) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchById(id: number): Promise<{ ok: boolean; data?: UsuarioDetalle; error?: string }> {
    try {
      const { data } = await api.get(`/usuarios/${id}/`)
      return { ok: true, data }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  async function register(params: RegisterForm): Promise<{ ok: boolean; data?: UsuarioDetalle; error?: string }> {
    try {
      const { data } = await api.post('/usuarios/auth/registro/', params)
      return { ok: true, data: data.usuario ?? data }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  async function update(id: number, form: AdminActualizarForm): Promise<{ ok: boolean; data?: UsuarioDetalle; error?: string }> {
    try {
      const { data } = await api.patch(`/usuarios/${id}/`, form)
      const idx = items.value.findIndex(u => u.id === id)
      if (idx !== -1) {
        items.value[idx] = { ...items.value[idx], ...data }
      }
      return { ok: true, data }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  async function remove(id: number): Promise<ApiResult> {
    try {
      await api.delete(`/usuarios/${id}/`)
      items.value = items.value.filter(p => p.id !== id)
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  return { items, loading, error, total, paginas, paginaActual, fetchAll, fetchById, register, update, remove }
})