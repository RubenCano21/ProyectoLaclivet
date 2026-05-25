import api from './apiClient'

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
  especie: string
  raza: string
  sexo: string
  fecha_nacimiento: string | null
  propietario: number
}

export type PacienteForm = Omit<Paciente, 'id'>

export const propietarioService = {
  getAll(page = 1) {
    return api.get('/propietarios/', { params: { page } })
  },

  getById(id: number) {
    return api.get(`/propietarios/${id}/`)
  },

  create(form: PropietarioForm) {
    return api.post('/propietarios/', form)
  },

  update(id: number, form: Partial<PropietarioForm>) {
    return api.patch(`/propietarios/${id}/`, form)
  },

  delete(id: number) {
    return api.delete(`/propietarios/${id}/`)
  },

  search(q: string) {
    return api.get('/propietarios/', { params: { search: q } })
  },
}

export const pacienteService = {
  getAll(page = 1) {
    return api.get('/pacientes/', { params: { page } })
  },

  getById(id: number) {
    return api.get(`/pacientes/${id}/`)
  },

  getByPropietario(propietarioId: number) {
    return api.get('/pacientes/', { params: { propietario: propietarioId } })
  },

  create(form: PacienteForm) {
    return api.post('/pacientes/', form)
  },

  update(id: number, form: Partial<PacienteForm>) {
    return api.patch(`/pacientes/${id}/`, form)
  },

  delete(id: number) {
    return api.delete(`/pacientes/${id}/`)
  },

  getHistorial(id: number) {
    return api.get(`/pacientes/${id}/historial/`)
  },
}
