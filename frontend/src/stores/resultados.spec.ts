import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

// Mockeamos el servicio HTTP: no queremos golpear el backend real en tests unitarios.
vi.mock('@/services/catalogoService', () => ({
  resultadoFlujoService: {
    getAll: vi.fn(),
    getCompleto: vi.fn(),
    registrar: vi.fn(),
    generarPdf: vi.fn(),
  },
  examenService: {
    getPlantilla: vi.fn(),
  },
}))

import { useResultadosStore } from '@/stores/resultados'
import { resultadoFlujoService } from '@/services/catalogoService'

describe('useResultadosStore.generarPdf', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('actualiza archivo_pdf en `actual` usando `pdf_url` de la respuesta (regresión del bug de PDF)', async () => {
    const store = useResultadosStore()
    // Simula que ya se cargó el detalle de la orden de examen
    store.actual = {
      id: 3,
      estado: 'completado',
      examen: 1,
      examen_nombre: 'Hemograma',
      solicitud_codigo: 'SOL-1',
      fecha_solicitud: null,
      paciente: null,
      propietario: null,
      medico_solicitante: null,
      veterinario_responsable: null,
      veterinario_nombre: null,
      muestra: null,
      resultados: [],
      observaciones: '',
      alteraciones: '',
      diagnostico: '',
      pronostico: '',
      fecha_resultado: null,
      archivo_pdf: null,
    }

    // El backend NO devuelve un OrdenExamenCompleto, sino { success, message, pdf_url, pdf_name }
    vi.mocked(resultadoFlujoService.generarPdf).mockResolvedValue({
      data: {
        success: true,
        message: 'PDF generado exitosamente',
        pdf_url: 'http://localhost:8000/media/resultados/resultado_OE3.pdf',
        pdf_name: 'resultado_OE3.pdf',
      },
    } as any)

    const res = await store.generarPdf(3)

    expect(res.ok).toBe(true)
    expect(store.actual?.archivo_pdf).toBe('http://localhost:8000/media/resultados/resultado_OE3.pdf')
    // El resto del objeto `actual` no debe perderse (antes se sobreescribía por completo)
    expect(store.actual?.examen_nombre).toBe('Hemograma')
  })

  it('reporta error cuando el backend responde success: false', async () => {
    const store = useResultadosStore()
    vi.mocked(resultadoFlujoService.generarPdf).mockResolvedValue({
      data: { success: false, message: 'No se pudo generar el PDF', pdf_url: '', pdf_name: '' },
    } as any)

    const res = await store.generarPdf(99)
    expect(res.ok).toBe(false)
  })
})

