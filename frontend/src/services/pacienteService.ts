import api from './apiClient'

// ─── Tipos ────────────────────────────────────────────────────────────────────

export interface Especie {
  id: number
  nombre: string
}

export type EspecieForm = Omit<Especie, 'id'>

export interface Raza {
  id: number
  nombre: string
  descripcion?: string | null
  especie: number
  especie_nombre?: string
}

export type RazaForm = {
  nombre: string
  descripcion?: string | null
  especie: number
}

export interface Propietario {
  id: number
  ci: string
  nombre: string
  apellido: string
  correo: string
  telefono: string
  direccion: string
}

export type PropietarioForm = Omit<Propietario, 'id'>

export interface Paciente {
  id: number
  nombre: string
  sexo: string
  tamanio: string
  color: string
  fecha_nacimiento: string | null
  propietario: number
  propietario_nombre: string
  raza: number
  raza_nombre: string
  especie_nombre: string
}

export type PacienteForm = Omit<Paciente, 'id'>

export interface Antecedente {
  id: number
  paciente: number
  tipo: string
  tipo_display: string
  descripcion: string
  fecha_registro: string
  registrado_por: number | null
  registrado_por_email: string | null
}

export type AntecedenteForm = {
  paciente: number
  tipo: string
  descripcion: string
}

export interface HistorialSolicitud {
  id: number
  codigo: string
  fecha_solicitud: string
  estado: string
  observaciones: string | null
  medico_veterinario: string | null
  examenes: Array<{ examen: string | null; precio_aplicado: number }>
}

export interface HistorialResponse {
  paciente: Paciente
  antecedentes: Antecedente[]
  total_visitas: number
  solicitudes: HistorialSolicitud[]
}

// ─── Especies ─────────────────────────────────────────────────────────────────

export const especieService = {
  getAll() {
    return api.get<Especie[]>('/pacientes/especies/', { params: { page_size: 100 } })
  },
  getById(id: number) {
    return api.get<Especie>(`/pacientes/especies/${id}/`)
  },
  create(form: EspecieForm) {
    return api.post<Especie>('/pacientes/especies/', form)
  },
  update(id: number, form: EspecieForm) {
    return api.put<Especie>(`/pacientes/especies/${id}/`, form)
  },
  patch(id: number, form: Partial<EspecieForm>) {
    return api.patch<Especie>(`/pacientes/especies/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/pacientes/especies/${id}/`)
  },
}

// ─── Razas ────────────────────────────────────────────────────────────────────

export const razaService = {
  getAll(especieId?: number) {
    return api.get<Raza[]>('/pacientes/razas/', {
      params: { page_size: 100, ...(especieId ? { especie: especieId } : {}) },
    })
  },
  getById(id: number) {
    return api.get<Raza>(`/pacientes/razas/${id}/`)
  },
  create(form: RazaForm) {
    return api.post<Raza>('/pacientes/razas/', form)
  },
  update(id: number, form: RazaForm) {
    return api.put<Raza>(`/pacientes/razas/${id}/`, form)
  },
  patch(id: number, form: Partial<RazaForm>) {
    return api.patch<Raza>(`/pacientes/razas/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/pacientes/razas/${id}/`)
  },
}

// ─── Antecedentes ─────────────────────────────────────────────────────────────

export const antecedenteService = {
  getAll() {
    return api.get<Antecedente[]>('/pacientes/antecedentes/')
  },
  getById(id: number) {
    return api.get<Antecedente>(`/pacientes/antecedentes/${id}/`)
  },
  getByPaciente(pacienteId: number) {
    return api.get<Antecedente[]>('/pacientes/antecedentes/', { params: { paciente: pacienteId } })
  },
  create(form: AntecedenteForm) {
    return api.post<Antecedente>('/pacientes/antecedentes/', form)
  },
  update(id: number, form: AntecedenteForm) {
    return api.put<Antecedente>(`/pacientes/antecedentes/${id}/`, form)
  },
  patch(id: number, form: Partial<AntecedenteForm>) {
    return api.patch<Antecedente>(`/pacientes/antecedentes/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/pacientes/antecedentes/${id}/`)
  },
}

// ─── Propietarios ─────────────────────────────────────────────────────────────

export const propietarioService = {
  getAll(page = 1) {
    return api.get('/propietarios/', { params: { page } })
  },
  getById(id: number) {
    return api.get<Propietario>(`/propietarios/${id}/`)
  },
  create(form: PropietarioForm) {
    return api.post<Propietario>('/propietarios/', form)
  },
  update(id: number, form: PropietarioForm) {
    return api.put<Propietario>(`/propietarios/${id}/`, form)
  },
  patch(id: number, form: Partial<PropietarioForm>) {
    return api.patch<Propietario>(`/propietarios/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/propietarios/${id}/`)
  },
  search(q: string) {
    return api.get('/propietarios/', { params: { search: q } })
  },
}

// ─── Pacientes ────────────────────────────────────────────────────────────────

export const pacienteService = {
  getAll(page = 1) {
    return api.get('/pacientes/', { params: { page } })
  },
  getById(id: number) {
    return api.get<Paciente>(`/pacientes/${id}/`)
  },
  getByPropietario(propietarioId: number) {
    return api.get('/pacientes/', { params: { propietario: propietarioId } })
  },
  create(form: PacienteForm) {
    return api.post<Paciente>('/pacientes/', form)
  },
  update(id: number, form: PacienteForm) {
    return api.put<Paciente>(`/pacientes/${id}/`, form)
  },
  patch(id: number, form: Partial<PacienteForm>) {
    return api.patch<Paciente>(`/pacientes/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/pacientes/${id}/`)
  },
  getHistorial(id: number) {
    return api.get(`/pacientes/${id}/historial/`)
  },
}
