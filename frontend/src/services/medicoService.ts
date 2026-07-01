import api from './apiClient'

export interface MedicoVeterinario {
  id: number
  nombre: string
  apellido: string
  especialidad: string | null
  genero: string | null
  correo: string | null
  telefono: string | null
  direccion: string | null
}

export type MedicoForm = Omit<MedicoVeterinario, 'id'>

export const medicoService = {
  getAll() {
    return api.get('/medicos/')
  },
  getById(id: number) {
    return api.get(`/medicos/${id}/`)
  },
  create(form: MedicoForm) {
    return api.post('/medicos/', form)
  },
  update(id: number, form: Partial<MedicoForm>) {
    return api.patch(`/medicos/${id}/`, form)
  },
  delete(id: number) {
    return api.delete(`/medicos/${id}/`)
  },

  buscar(search = '') {
    return api.get('/medicos/', { params: { search, page_size: 20 } })
  }
}
