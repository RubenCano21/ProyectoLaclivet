import api from './apiClient'

// ─── Tipos ────────────────────────────────────────────────────────────────────

export interface CatalogoExamen {
  id: number
  nombre: string
  area: string | null
  precio: string | null
}

export type CatalogoExamenForm = Omit<CatalogoExamen, 'id'>

export interface Examen {
  id: number
  nombre_examen: string
  categoria: string | null
  descripcion: string | null
  catalogo: number
  catalogo_nombre?: string
}

export type ExamenForm = Omit<Examen, 'id' | 'catalogo_nombre'>

export interface Parametro {
  id: number
  nombre_parametro: string
  unidad_medida: string | null
  examen: number
  examen_nombre?: string
}

export type ParametroForm = Omit<Parametro, 'id' | 'examen_nombre'>

export interface ValorReferencia {
  id: number
  valor_min: string | null
  valor_max: string | null
  especie: string | null
  parametro: number
  parametro_nombre?: string
}

export type ValorReferenciaForm = Omit<ValorReferencia, 'id' | 'parametro_nombre'>

// ─── Servicios ────────────────────────────────────────────────────────────────

export const catalogoService = {
  getAll() {
    return api.get('/catalogos/')
  },
  getById(id: number) {
    return api.get(`/catalogos/${id}/`)
  },
  create(form: CatalogoExamenForm) {
    return api.post('/catalogos/', form)
  },
  update(id: number, form: Partial<CatalogoExamenForm>) {
    return api.patch(`/catalogos/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/catalogos/${id}/`)
  },
}

export const examenService = {
  getAll() {
    return api.get('/catalogos/examenes/')
  },
  getById(id: number) {
    return api.get(`/catalogos/examenes/${id}/`)
  },
  create(form: ExamenForm) {
    return api.post('/catalogos/examenes/', form)
  },
  update(id: number, form: Partial<ExamenForm>) {
    return api.patch(`/catalogos/examenes/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/catalogos/examenes/${id}/`)
  },
}

export const parametroService = {
  getAll() {
    return api.get('/catalogos/parametros/')
  },
  getById(id: number) {
    return api.get(`/catalogos/parametros/${id}/`)
  },
  create(form: ParametroForm) {
    return api.post('/catalogos/parametros/', form)
  },
  update(id: number, form: Partial<ParametroForm>) {
    return api.patch(`/catalogos/parametros/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/catalogos/parametros/${id}/`)
  },
}

export const valorReferenciaService = {
  getAll() {
    return api.get('/catalogos/valores-referencia/')
  },
  getById(id: number) {
    return api.get(`/catalogos/valores-referencia/${id}/`)
  },
  create(form: ValorReferenciaForm) {
    return api.post('/catalogos/valores-referencia/', form)
  },
  update(id: number, form: Partial<ValorReferenciaForm>) {
    return api.patch(`/catalogos/valores-referencia/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/catalogos/valores-referencia/${id}/`)
  },
}
