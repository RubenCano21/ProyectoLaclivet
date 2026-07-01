import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mockeamos apiClient para no golpear el backend real.
vi.mock('@/services/apiClient', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  },
}))

import { useMuestrasStore, type MuestraForm } from '@/stores/muestras'
import api from '@/services/apiClient'

describe('useMuestrasStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('create() envía `tipo_muestra` (no `tipo`) al backend — regresión del bug de nombre de campo', async () => {
    const store = useMuestrasStore()
    vi.mocked(api.post).mockResolvedValue({
      data: { id: 1, codigo: 'MUE-TEST', tipo_muestra: 'sangre', estado: 'pendiente' },
    } as any)

    const form: MuestraForm = {
      tipo_muestra: 'sangre',
      estado: 'pendiente',
      fecha_recepcion: '2026-06-30',
      observaciones: '',
      paciente: 5,
    }
    const res = await store.create(form)

    expect(res.ok).toBe(true)
    const payloadEnviado = vi.mocked(api.post).mock.calls[0][1] as MuestraForm
    expect(payloadEnviado).toHaveProperty('tipo_muestra', 'sangre')
    expect(payloadEnviado).not.toHaveProperty('tipo')
  })

  it('fetchAll() mapea correctamente la paginación en español del backend', async () => {
    const store = useMuestrasStore()
    vi.mocked(api.get).mockResolvedValue({
      data: {
        resultados: [{ id: 1, codigo: 'MUE-1', tipo_muestra: 'sangre', estado: 'pendiente' }],
        total: 1,
        paginas: 1,
        pagina_actual: 1,
      },
    } as any)

    await store.fetchAll()

    expect(store.items).toHaveLength(1)
    expect(store.total).toBe(1)
    expect(store.paginas).toBe(1)
    expect(store.paginaActual).toBe(1)
    expect(store.loading).toBe(false)
  })
})

