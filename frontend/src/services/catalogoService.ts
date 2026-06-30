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

// tipo_dato del backend: 'NUM' (numérico) | 'TXT' (texto libre) | 'SEL' (selección)
export type TipoDatoParametro = 'NUM' | 'TXT' | 'SEL'

export const TIPO_DATO_LABELS: Record<TipoDatoParametro, string> = {
  NUM: 'Numérico',
  TXT: 'Texto libre',
  SEL: 'Selección',
}

export interface Parametro {
  opciones_seleccion: string
  id: number
  nombre_parametro: string
  unidad_medida: string | null
  examen: number
  examen_nombre?: string
  // ── nuevos ──
  grupo: string | null
  tipo_dato: TipoDatoParametro
  opciones: string[] | null
  orden: number
}

export type ParametroForm = Omit<Parametro, 'id' | 'examen_nombre'>

// sexo del backend: 'A' (Ambos) | 'M' (Macho) | 'H' (Hembra)
export type SexoReferencia = 'A' | 'M' | 'H'

export const SEXO_LABELS: Record<SexoReferencia, string> = {
  A: 'Ambos',
  M: 'Macho',
  H: 'Hembra',
}

export interface ValorReferencia {
  id: number
  valor_min: string | null
  valor_max: string | null
  especie: string | null
  parametro: number
  parametro_nombre?: string
  // ── nuevos ──
  sexo: SexoReferencia
  texto_referencia: string | null
}

export type ValorReferenciaForm = Omit<ValorReferencia, 'id' | 'parametro_nombre'>

// ── Plantilla agrupada (para el formulario de captura de resultados) ──────
export interface ParametroPlantilla extends Parametro {
  valores_referencia: ValorReferencia[]
}

export interface GrupoPlantilla {
  nombre: string
  parametros: ParametroPlantilla[]
}

export interface ExamenPlantilla extends Examen {
  grupos: GrupoPlantilla[]
}

// ── Resultados ─────────────────────────────────────────────────────────────
export interface OrdenTrabajo {
  id: number
  paciente: number
  paciente_nombre?: string
  veterinario_solicitante: string
  fecha_creacion: string
  estado: 'PEND' | 'PROC' | 'VALD' | 'ENTR' | 'ANUL'
  observaciones_generales: string
}

export type OrdenTrabajoForm = Pick<OrdenTrabajo, 'paciente' | 'veterinario_solicitante' | 'observaciones_generales'>

export interface ResultadoParametro {
  id: number
  parametro: number
  parametro_nombre?: string
  valor_numerico: string | null
  valor_texto: string
  interpretacion: 'BAJO' | 'NORMAL' | 'ALTO' | ''
}

export interface OrdenExamen {
  id: number
  orden: number
  examen: number
  examen_nombre?: string
  muestra: number | null
  realizado_por: string
  validado_por: string
  fecha_resultado: string | null
  observaciones: string
  alteraciones: string
  diagnostico: string
  pronostico: string
  resultados: ResultadoParametro[]
}

export interface ResultadoParametroInput {
  parametro: number
  valor_numerico?: string | number | null
  valor_texto?: string
}

export interface OrdenExamenResultadosForm {
  observaciones?: string
  alteraciones?: string
  diagnostico?: string
  pronostico?: string
  realizado_por?: string
  resultados: ResultadoParametroInput[]
}

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
  getExamenes(search = '') {
    return api.get('/catalogos/examenes/', { params: { search, page_size: 50 } })
  }
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
  // Plantilla agrupada (grupos -> parametros -> valores_referencia), solo lectura
  getPlantilla(id: number) {
    return api.get<ExamenPlantilla>(`/catalogos/examenes/${id}/plantilla/`)
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

export const ordenTrabajoService = {
  getAll(params?: { paciente?: number; estado?: string }) {
    return api.get('/catalogos/ordenes-trabajo/', { params })
  },
  getById(id: number) {
    return api.get(`/catalogos/ordenes-trabajo/${id}/`)
  },
  create(form: OrdenTrabajoForm) {
    return api.post('/catalogos/ordenes-trabajo/', form)
  },
  update(id: number, form: Partial<OrdenTrabajoForm>) {
    return api.patch(`/catalogos/ordenes-trabajo/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/catalogos/ordenes-trabajo/${id}/`)
  },
}

export const ordenExamenService = {
  getAll(params?: { orden?: number }) {
    return api.get('/catalogos/orden-examenes/', { params })
  },
  getById(id: number) {
    return api.get<OrdenExamen>(`/catalogos/orden-examenes/${id}/`)
  },
  create(form: { orden: number; examen: number; muestra?: number | null }) {
    return api.post<OrdenExamen>('/catalogos/orden-examenes/', form)
  },
  delete(id: number) {
    return api.delete(`/catalogos/orden-examenes/${id}/`)
  },
  guardarResultados(id: number, form: OrdenExamenResultadosForm) {
    return api.patch<OrdenExamen>(`/catalogos/orden-examenes/${id}/resultados/`, form)
  },
}

export interface MuestraResumenOrden {
  id: number
  codigo: string
  tipo_muestra: string | null
  estado: string
}

export interface PacienteResumen {
  id: number
  nombre: string
  sexo: string
  especie: string | null
  raza: string | null
}

export interface PropietarioResumen {
  id: number
  nombre_completo: string | null
  email: string | null
  telefono: string | null
}

export interface MedicoResumen {
  id: number
  nombre_completo: string | null
  especialidad: string | null
  clinica_procedencia: string | null
}

export interface VeterinarioResumen {
  id: number
  nombre_completo: string
}

export interface OrdenExamenCompleto {
  id: number
  estado: 'pendiente' | 'en_proceso' | 'completado' | 'validado'
  examen: number
  examen_nombre: string
  solicitud_codigo: string | null
  fecha_solicitud: string | null
  paciente: PacienteResumen | null
  propietario: PropietarioResumen | null
  medico_solicitante: MedicoResumen | null
  veterinario_responsable: number | null
  veterinario_nombre: VeterinarioResumen | null
  muestra: MuestraResumenOrden | null
  resultados: ResultadoParametro[]
  observaciones: string
  alteraciones: string
  diagnostico: string
  pronostico: string
  fecha_resultado: string | null
  archivo_pdf: string | null
}

// ─── Servicios extendidos ────────────────────────────────────────────────────

export const resultadoFlujoService = {
  /** Lista de OrdenExamen, opcionalmente filtrado por estado (para la bandeja del Veterinario) */
  getAll(params?: { orden?: number; estado?: string; page?: number }) {
    return api.get('/catalogos/orden-examenes/', { params })
  },

  /** Detalle completo con paciente, propietario, médico, PDF — respeta permisos por rol en backend */
  getCompleto(id: number) {
    return api.get<OrdenExamenCompleto>(`/catalogos/orden-examenes/${id}/completo/`)
  },

  /** Registra resultados + cambia estado a completado (solo rol Veterinario) */
  registrar(id: number, form: OrdenExamenResultadosForm) {
    return api.post<OrdenExamenCompleto>(`/catalogos/orden-examenes/${id}/registrar-resultado/`, form)
  },

  /** Genera (o regenera) el PDF del resultado */
  generarPdf(id: number) {
    return api.post<OrdenExamenCompleto>(`/catalogos/orden-examenes/${id}/generar-pdf/`)
  },
}