export interface Muestra {
  id: number
  codigo: string
  tipo: string | null
  tipo_muestra: string | null
  estado: string
  fecha_recepcion: string | null
  observaciones: string | null
  paciente: number | null
  paciente_nombre: string | null
  solicitud: number | null
  solicitud_codigo: string | null
}