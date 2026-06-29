import { type Muestra } from "@/models/muestra";
import api from "@/services/apiClient";
import type { AxiosError } from "axios";
import { defineStore } from "pinia";
import { ref } from "vue";


export type MuestraForm = {
  tipo: string
  estado: string
  fecha_recepcion: string
  observaciones: string
  paciente: number | null
  solicitud?: number | null
}

interface ApiResult {
    ok: boolean
    error?: string
}

function extractError(err: unknown): string {
    const axiosErr = err as AxiosError<Record<string, string | string[]>>
    const d = axiosErr.response?.data
    if (!d) return 'Error de conexion'
    for (const v of Object.values(d)) {
        if( Array.isArray(v) && v[0]) return String(v[0])
        if (typeof v === 'string') return v
    }
    return 'Error inesperado'
}

export const useMuestrasStore = defineStore('muestras', () => {
    const items = ref<Muestra[]>([])
    const loading = ref(false)
    const saving = ref(false)
    const error = ref<string | null>(null)
    const total = ref(0)
    const paginas = ref(1)
    const paginaActual = ref(1)

    async function fetchAll(page = 1, search = '') {
        loading.value = true
        error.value = null
        try {
            const { data } = await api.get('/muestras/', { params: { page, search}})
            items.value = data.resultados
            total.value = data.total
            paginas.value = data.paginas
            paginaActual.value = data.pagina_actual   
        } catch (err) {
            error.value = extractError(err)
        } finally {
            loading.value = false
        }
    }

    async function create( form: MuestraForm): Promise<ApiResult> {
        saving.value = true
        try {
            const { data } = await api.post('/muestras/', form)
            items.value.unshift(data)
            return { ok: true }
        } catch (err) {
            return { ok: false, error: extractError(err)}
        } finally {
            saving.value = false
        }
    }

    async function update(id: number, form: MuestraForm): Promise<ApiResult> {
    saving.value = true
    try {
      const { data } = await api.patch(`/muestras/${id}/`, form)
      const idx = items.value.findIndex(p => p.id === id)
      if (idx !== -1) items.value[idx] = data
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    } finally {
      saving.value = false
    }
  }

  async function remove(id: number): Promise<ApiResult> {
    try {
      await api.delete(`/muestras/${id}/`)
      items.value = items.value.filter(p => p.id !== id)
      return { ok: true }
    } catch (err) {
      return { ok: false, error: extractError(err) }
    }
  }

  return { items, loading, saving, error, total, paginas, paginaActual, fetchAll, create, update, remove }
})