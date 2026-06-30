import api from './apiClient'

// ─── Tipos ────────────────────────────────────────────────────────────────────

export interface Cobro {
  id: number
  monto_total: string | null
  metodo_pago: string | null
  fecha: string | null
}

export type CobroForm = {
  monto_total: string | null
  metodo_pago: string | null
  fecha: string
}

export interface SolicitudExamen {
  id: number
  codigo: string
  fecha_solicitud: string
  observaciones: string | null
  estado: string
  cobro: number | null
  paciente: number | null
  medico_veterinario: number | null
  medico_nombre: string | null
  paciente_nombre: string | null
}

export type SolicitudForm = {
  codigo: string
  observaciones?: string | null
  estado: string
  cobro?: number | null
  paciente?: number | null
  medico_veterinario?: number | null
}

export interface DetalleSolicitud {
  id: number
  precio_aplicado: string | null
  solicitud: number
  solicitud_codigo: string
  examen: number | null
  examen_nombre: string | null
}

export type DetalleForm = {
  precio_aplicado?: string | null
  solicitud: number
  examen: number
}

// ─── Servicios ────────────────────────────────────────────────────────────────

export const cobroService = {
  getAll() {
    return api.get('/recepcion/cobros/')
  },
  getById(id: number) {
    return api.get(`/recepcion/cobros/${id}/`)
  },
  create(form: CobroForm) {
    return api.post('/recepcion/cobros/', form)
  },
  update(id: number, form: Partial<CobroForm>) {
    return api.patch(`/recepcion/cobros/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/recepcion/cobros/${id}/`)
  },
}

export const solicitudService = {
  getAll(page = 1) {
    return api.get('/recepcion/solicitudes/', { params: { page } })
  },
  getById(id: number) {
    return api.get(`/recepcion/solicitudes/${id}/`)
  },
  create(form: SolicitudForm) {
    return api.post('/recepcion/solicitudes/', form)
  },
  update(id: number, form: Partial<SolicitudForm>) {
    return api.patch(`/recepcion/solicitudes/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/recepcion/solicitudes/${id}/`)
  },
}

export const detalleService = {
  getAll() {
    return api.get('/recepcion/detalles/')
  },
  create(form: DetalleForm) {
    return api.post('/recepcion/detalles/', form)
  },
  delete(id: number) {
    return api.delete(`/recepcion/detalles/${id}/`)
  },
}

export interface MuestraResumen {
  id: number
  codigo: string
  tipo_muestra: string | null
  estado: string
}

export interface DetalleSolicitudCompleto {
  id: number
  precio_aplicado: string | null
  examen: number
  examen_nombre: string
  requiere_muestra: boolean
  muestra: MuestraResumen | null   // antes: muestras: MuestraResumen[]
  tiene_resultado: boolean
  estado_resultado: string | null
}

export interface SolicitudCompleta extends SolicitudExamen {
  detalles: DetalleSolicitudCompleto[]
}

export type CrearSolicitudConExamenesForm = {
  paciente: number
  medico_veterinario?: number | null
  examenes_ids: number[]
  observaciones?: string
}

// ─── Servicios extendidos ────────────────────────────────────────────────────

export const solicitudFlujoService = {
  /** Lista con filtro por estado, usando datos completos (detalles + muestras) */
  getAllFiltrado(page = 1, estado?: string) {
    return api.get('/recepcion/solicitudes/listado/', { params: { page, estado: estado || undefined } })
  },

  /** Detalle completo: exámenes, muestras, estado de resultado */
  getCompleto(id: number) {
    return api.get(`/recepcion/solicitudes/${id}/completo/`)
  },

  /** Crea la solicitud + detalles + verifica/genera muestras automáticamente */
  crearConExamenes(form: CrearSolicitudConExamenesForm) {
    return api.post('/recepcion/solicitudes/crear-con-examenes/', form)
  },

  cambiarEstado(id: number, estado: string) {
    return api.patch(`/recepcion/solicitudes/${id}/cambiar-estado/`, { estado })
  },
}
