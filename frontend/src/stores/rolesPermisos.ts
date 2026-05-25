import api from '@/services/apiClient'
import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Permiso {
  id: number
  nombre: string
  codigo: string
  descripcion: string
}

export interface Rol {
  id: number
  nombre: string
  descripcion: string
  permisos: Permiso[]
}

export const useRolesPermisosStore = defineStore('rolesPermisos', () => {
  const roles = ref<Rol[]>([])
  const permisos = ref<Permiso[]>([])
  const loading = ref(false)
  const saving = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      const [rolesRes, permisosRes] = await Promise.all([
        api.get('/usuarios/roles/'),
        api.get('/usuarios/permisos/'),
      ])
      roles.value = rolesRes.data
      permisos.value = permisosRes.data
    } finally {
      loading.value = false
    }
  }

  async function updateRolPermisos(rolId: number, permisoIds: number[]): Promise<{ ok: boolean; error?: string }> {
    saving.value = true
    try {
      const { data } = await api.put(`/usuarios/roles/${rolId}/permisos/`, { permisos: permisoIds })
      const idx = roles.value.findIndex(r => r.id === rolId)
      if (idx !== -1) roles.value[idx] = data
      return { ok: true }
    } catch {
      return { ok: false, error: 'Error al actualizar permisos del rol' }
    } finally {
      saving.value = false
    }
  }

  async function asignarRolUsuario(userId: number, rolId: number | null): Promise<{ ok: boolean; error?: string }> {
    saving.value = true
    try {
      await api.patch(`/usuarios/${userId}/asignar-rol/`, { rol_id: rolId })
      return { ok: true }
    } catch {
      return { ok: false, error: 'Error al asignar el rol' }
    } finally {
      saving.value = false
    }
  }

  return { roles, permisos, loading, saving, fetchAll, updateRolPermisos, asignarRolUsuario }
})
