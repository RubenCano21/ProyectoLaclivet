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