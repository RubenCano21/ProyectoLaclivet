import api from '@/lib/api'
import type { AxiosError } from 'axios'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UsuarioResumen {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  fecha_creacion: string
  is_active: boolean
  is_staff: boolean
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
  username: string
  email: string
  password: string
  password2: string
  first_name: string
  last_name?: string
  telefono?: string | null
  direccion?: string | null
  fecha_nacimiento?: string | null
}

/** Campos que el admin puede editar en PUT/PATCH /usuarios/<pk>/ */
export interface AdminActualizarForm {
  first_name?: string
  last_name?: string
  email?: string
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

// Mantener compatibilidad con código existente
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

  /** GET /usuarios/?page=X — lista usuarios paginados (solo admin) */
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

  /** GET /usuarios/<pk>/ — detalle de un usuario (solo admin) */
  async function fetchById(id: number): Promise<{ ok: boolean; data?: UsuarioDetalle; error?: string }> {
    try {
      const { data } = await api.get(`/usuarios/${id}/`)
      return { ok: true, data }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  /** POST /auth/registro/ — registrar un nuevo usuario */
  async function register(params: RegisterForm): Promise<{ ok: boolean; data?: UsuarioDetalle; error?: string }> {
    try {
      const { data } = await api.post('/auth/registro/', params)
      return { ok: true, data }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  /** PUT/PATCH /usuarios/<pk>/ — actualizar usuario como admin */
  async function update(id: number, form: AdminActualizarForm): Promise<{ ok: boolean; data?: UsuarioDetalle; error?: string }> {
    try {
      const { data } = await api.patch(`/usuarios/${id}/`, form)
      // Reflejar cambios en la lista local si el ítem existe
      const idx = items.value.findIndex(u => u.id === id)
      if (idx !== -1) {
        items.value[idx] = { ...items.value[idx], ...data }
      }
      return { ok: true, data }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  /** DELETE /usuarios/<pk>/ — eliminar usuario (solo admin) */
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
