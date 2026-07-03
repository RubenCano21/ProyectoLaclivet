import api from '@/services/apiClient'

// ── Interfaces ────────────────────────────────────────────────────────────────

export interface BiResumen {
  total_muestras: number
  total_solicitudes: number
  total_pacientes: number
  total_ingresos: number
  solicitudes_pendientes: number
  muestras_pendientes: number
  muestras_rechazadas: number
  tasa_rechazo: number
  parametros_fuera_rango: number
  muestras_este_mes: number
  muestras_mes_anterior: number
  solicitudes_este_mes: number
  solicitudes_mes_anterior: number
  ingresos_este_mes: number
  ingresos_mes_anterior: number
}

export interface BiSerie {
  labels: string[]
  datos: number[]
  especies?: string[]
}

export interface BiAlerta {
  resultados: { parametro: string; interpretacion: string; total: number }[]
  total_alto: number
  total_bajo: number
  labels: string[]
  datos: number[]
}

export interface BiInsight {
  tipo: 'alerta' | 'advertencia' | 'info' | 'exito'
  titulo: string
  mensaje: string
}

export interface BiInsightsResponse {
  insights: BiInsight[]
  total: number
}

export interface ReporteMuestra {
  id: number
  codigo: string
  tipo_muestra: string
  estado: string
  fecha_recepcion: string | null
  paciente: string
  especie: string
  solicitud_codigo: string
  observaciones: string
}

export interface ReporteSolicitud {
  id: number
  codigo: string
  estado: string
  fecha_solicitud: string
  paciente: string
  especie: string
  medico_veterinario: string
  monto_total: number | null
  metodo_pago: string | null
  examenes: string[]
}

export interface ReporteExamen {
  id: number
  examen: string
  catalogo: string
  estado: string
  fecha_resultado: string | null
  paciente: string
  especie: string
  veterinario: string
  observaciones: string
}

export interface ReporteResponse<T> {
  total: number
  resultados: T[]
}

export interface FiltrosReporte {
  fecha_inicio?: string
  fecha_fin?: string
  estado?: string
  tipo_muestra?: string
  catalogo?: string
  columnas?: string
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function buildParams(filtros: FiltrosReporte & { formato?: string; meses?: number }) {
  const params: Record<string, string> = {}
  if (filtros.fecha_inicio) params.fecha_inicio = filtros.fecha_inicio
  if (filtros.fecha_fin)    params.fecha_fin    = filtros.fecha_fin
  if (filtros.estado)       params.estado       = filtros.estado
  if (filtros.tipo_muestra) params.tipo_muestra = filtros.tipo_muestra
  if (filtros.catalogo)     params.catalogo     = filtros.catalogo
  if (filtros.columnas)     params.columnas     = filtros.columnas
  if (filtros.formato)      params.formato      = filtros.formato
  if (filtros.meses)        params.meses        = String(filtros.meses)
  return params
}

// ── Servicio ──────────────────────────────────────────────────────────────────

export const biService = {
  // ── KPIs y gráficas base (soportan ?meses=N) ────────────────────────────
  getResumen()                        { return api.get<BiResumen>('/bi/resumen/') },
  getMuestrasPorMes(meses = 6)        { return api.get<BiSerie>('/bi/muestras-por-mes/', { params: { meses } }) },
  getSolicitudesPorMes(meses = 6)     { return api.get<BiSerie>('/bi/solicitudes-por-mes/', { params: { meses } }) },
  getIngresosPorMes(meses = 6)        { return api.get<BiSerie>('/bi/ingresos-por-mes/', { params: { meses } }) },
  getSolicitudesEstado()              { return api.get<BiSerie>('/bi/solicitudes-estado/') },
  getTiposMuestra()                   { return api.get<BiSerie>('/bi/tipos-muestra/') },
  getMuestrasEstado()                 { return api.get<BiSerie>('/bi/muestras-estado/') },
  getEspecies()                       { return api.get<BiSerie>('/bi/especies/') },
  getExamenesTop()                    { return api.get<BiSerie>('/bi/examenes-top/') },

  // ── Nuevos endpoints analíticos ─────────────────────────────────────────
  getIngresosPorMetodoPago()          { return api.get<BiSerie>('/bi/ingresos-metodo-pago/') },
  getRendimientoVeterinarios()        { return api.get<BiSerie>('/bi/rendimiento-veterinarios/') },
  getAlertasParametros()              { return api.get<BiAlerta>('/bi/alertas-parametros/') },
  getPacientesMasActivos()            { return api.get<BiSerie>('/bi/pacientes-activos/') },
  getInsights()                       { return api.get<BiInsightsResponse>('/bi/insights/') },

  // ── Chatbot IA ──────────────────────────────────────────────────────────
  chatbot(pregunta: string) {
    return api.post<{ respuesta?: string; error?: string }>('/bi/chatbot/', { pregunta })
  },

  // ── Reportes dinámicos ──────────────────────────────────────────────────
  getReporteMuestras(filtros: FiltrosReporte) {
    return api.get<ReporteResponse<ReporteMuestra>>('/bi/reporte-muestras/', { params: buildParams(filtros) })
  },
  getReporteSolicitudes(filtros: FiltrosReporte) {
    return api.get<ReporteResponse<ReporteSolicitud>>('/bi/reporte-solicitudes/', { params: buildParams(filtros) })
  },
  getReporteExamenes(filtros: FiltrosReporte) {
    return api.get<ReporteResponse<ReporteExamen>>('/bi/reporte-examenes/', { params: buildParams(filtros) })
  },

  /** Descarga PDF del reporte como Blob */
  descargarPdf(tipo: 'muestras' | 'solicitudes' | 'examenes', filtros: FiltrosReporte) {
    return api.get(`/bi/reporte-${tipo}/`, {
      params: buildParams({ ...filtros, formato: 'pdf' }),
      responseType: 'blob',
    })
  },

  /** Descarga CSV del reporte como Blob */
  descargarCsv(tipo: 'muestras' | 'solicitudes' | 'examenes', filtros: FiltrosReporte) {
    return api.get(`/bi/reporte-${tipo}/`, {
      params: buildParams({ ...filtros, formato: 'csv' }),
      responseType: 'blob',
    })
  },
}

