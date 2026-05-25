import api from './apiClient'

export interface Resultado {
  id: number
  muestra: number
  examen: number
  valor: string
  unidad: string | null
  valor_referencia: string | null
  observaciones: string | null
  validado: boolean
  validado_por: number | null
  fecha_resultado: string
}

export type ResultadoForm = Omit<Resultado, 'id' | 'validado' | 'validado_por' | 'fecha_resultado'>

export const resultadoService = {
  getAll(page = 1) {
    return api.get('/resultados/', { params: { page } })
  },

  getById(id: number) {
    return api.get(`/resultados/${id}/`)
  },

  getByMuestra(muestraId: number) {
    return api.get('/resultados/', { params: { muestra: muestraId } })
  },

  create(form: ResultadoForm) {
    return api.post('/resultados/', form)
  },

  update(id: number, form: Partial<ResultadoForm>) {
    return api.patch(`/resultados/${id}/`, form)
  },

  validar(id: number) {
    return api.post(`/resultados/${id}/validar/`)
  },
}
