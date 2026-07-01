import api from '@/services/apiClient'

export interface BiResumen {
  total_muestras: number
  total_solicitudes: number
  total_pacientes: number
  total_ingresos: number
  solicitudes_pendientes: number
  muestras_pendientes: number
  muestras_este_mes: number
  muestras_mes_anterior: number
  solicitudes_este_mes: number
  solicitudes_mes_anterior: number
  ingresos_este_mes: number
}

export interface BiSerie {
  labels: string[]
  datos: number[]
}

export const biService = {
  getResumen()            { return api.get<BiResumen>('/bi/resumen/') },
  getMuestrasPorMes()     { return api.get<BiSerie>('/bi/muestras-por-mes/') },
  getSolicitudesPorMes()  { return api.get<BiSerie>('/bi/solicitudes-por-mes/') },
  getIngresosPorMes()     { return api.get<BiSerie>('/bi/ingresos-por-mes/') },
  getSolicitudesEstado()  { return api.get<BiSerie>('/bi/solicitudes-estado/') },
  getTiposMuestra()       { return api.get<BiSerie>('/bi/tipos-muestra/') },
  getMuestrasEstado()     { return api.get<BiSerie>('/bi/muestras-estado/') },
  getEspecies()           { return api.get<BiSerie>('/bi/especies/') },
  getExamenesTop()        { return api.get<BiSerie>('/bi/examenes-top/') },
}

