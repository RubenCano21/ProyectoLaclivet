import api from '@/services/apiClient'

export const portalService = {
  /** Lista solo las mascotas del propietario autenticado (filtro en backend) */
  getMisMascotas() {
    return api.get('/pacientes/', { params: { page_size: 100 } })
  },

  /** Detalle de una mascota (backend verifica ownership) */
  getMiMascota(id: number) {
    return api.get(`/pacientes/${id}/`)
  },

  /** Historial clínico-laboratorial de una mascota */
  getHistorialMascota(id: number) {
    return api.get(`/pacientes/${id}/historial/`)
  },

  /** Resultados completados/validados del propietario autenticado */
  getMisResultados() {
    return api.get('/propietarios/mis-resultados/')
  },
}
