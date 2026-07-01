import {
  solicitudFlujoService,
  type SolicitudCompleta,
  type CrearSolicitudConExamenesForm,
} from '@/services/solicitudService'
import type { AxiosError } from 'axios'
import { defineStore } from 'pinia'
import { ref } from 'vue'

interface ApiResult {
  ok: boolean
  error?: string
  data?: any
}

function extractError(err: unknown): string {
  const axiosErr = err as AxiosError<Record<string, string | string[]>>
  const d = axiosErr.response?.data
  if (!d) return 'Error de conexión'
  for (const v of Object.values(d)) {
    if (Array.isArray(v) && v[0]) return String(v[0])
    if (typeof v === 'string') return v
  }
  return 'Error inesperado'
}

export const useSolicitudesStore = defineStore('solicitudes', () => {
  const items = ref<SolicitudCompleta[]>([])
  const loading = ref(false)
  const saving = ref(false)
  const error = ref<string | null>(null)
  const total = ref(0)
  const paginas = ref(1)
  const paginaActual = ref(1)
  const filtroEstado = ref<string>('')

  const actual = ref<SolicitudCompleta | null>(null)
  const loadingDetalle = ref(false)

  async function fetchAll(page = 1, estado = '') {
    loading.value = true
    error.value = null
    filtroEstado.value = estado
    try {
      const { data } = await solicitudFlujoService.getAllFiltrado(page, estado)
      items.value = data.resultados ?? data.results ?? []
      total.value = data.total ?? data.count ?? items.value.length
      paginas.value = data.paginas ?? 1
      paginaActual.value = data.pagina_actual ?? page
    } catch (err) {
      error.value = extractError(err)
    } finally {
      loading.value = false
    }
  }

  async function fetchDetalle(id: number) {
    if (!id || Number.isNaN(id)) {
        error.value = 'ID de solicitud inválido'
        return
    }
    loadingDetalle.value = true
    error.value = null
    try {
      const { data } = await solicitudFlujoService.getCompleto(id)
      actual.value = data
    } catch (err) {
      error.value = extractError(err)
    } finally {
      loadingDetalle.value = false
    }
  }

  async function crear(form: CrearSolicitudConExamenesForm): Promise<ApiResult> {
    saving.value = true
    try {
      const { data } = await solicitudFlujoService.crearConExamenes(form)
      await fetchAll(paginaActual.value, filtroEstado.value)
      return { ok: true, data }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    } finally {
      saving.value = false
    }
  }

  async function cambiarEstado(id: number, estado: string): Promise<ApiResult> {
    try {
      const { data } = await solicitudFlujoService.cambiarEstado(id, estado)
      const idx = items.value.findIndex(s => s.id === id)
      if (idx !== -1) items.value[idx] = data
      if (actual.value?.id === id) actual.value = data
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  return {
    items, loading, saving, error, total, paginas, paginaActual, filtroEstado,
    actual, loadingDetalle,
    fetchAll, fetchDetalle, crear, cambiarEstado,
  }
})