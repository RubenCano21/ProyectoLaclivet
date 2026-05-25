import api from './apiClient'

export interface LoginPayload {
  email: string
  password: string
}

export interface LoginResponse {
  access: string
  refresh: string
  usuario: Record<string, unknown>
}

export const authService = {
  login(payload: LoginPayload) {
    return api.post<LoginResponse>('/usuarios/auth/login/', payload)
  },

  refresh(refreshToken: string) {
    return api.post<{ access: string }>('/usuarios/auth/refresh/', { refresh: refreshToken })
  },

  getPerfil() {
    return api.get('/usuarios/perfil/')
  },

  updatePerfil(form: Record<string, unknown>) {
    return api.put('/usuarios/perfil/', form)
  },

  cambiarPassword(form: { password_actual: string; password_nuevo: string; password_nuevo2: string }) {
    return api.post('/usuarios/auth/cambiar-password/', form)
  },
}
