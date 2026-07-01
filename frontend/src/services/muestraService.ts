import type { Muestra } from '@/models/muestra'
import api from '@/services/apiClient'

export type MuestraForm = Omit<Muestra, 'id' | 'codigo' | 'fecha_recepcion'>

export const muestraService = {
  getAll(page = 1) {
    return api.get('/muestras/', { params: { page } })
  },

  getById(id: number) {
    return api.get(`/muestras/${id}/`)
  },

  create(form: MuestraForm) {
    return api.post('/muestras/', form)
  },

  update(id: number, form: Partial<MuestraForm>) {
    return api.patch(`/muestras/${id}/`, form)
  },

  registrarIncidencia(id: number, descripcion: string) {
    return api.post('/muestras/incidencias/', { muestra: id, descripcion })
  },

  getIncidencias(id: number) {
    return api.get('/muestras/incidencias/', { params: { muestra: id } })
  },

  delete(id: number) {
    return api.delete(`/muestras/${id}`)
  }
}
