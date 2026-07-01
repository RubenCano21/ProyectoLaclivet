import { type IncidenciaMuestra } from "@/models/muestra";
import api from "@/services/apiClient";
import type { AxiosError } from "axios";
import { defineStore } from "pinia";
import { ref } from "vue";

export type IncidenciaForm = {
  muestra: number
  descripcion: string
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
        if (Array.isArray(v) && v[0]) return String(v[0])
        if (typeof v === 'string') return v
    }
    return 'Error inesperado'
}

export const useIncidenciasStore = defineStore('incidencias', () => {
    const items = ref<IncidenciaMuestra[]>([])
    const loading = ref(false)
    const saving = ref(false)
    const error = ref<string | null>(null)
    const total = ref(0)
    const paginas = ref(1)
    const paginaActual = ref(1)

    async function fetchAll(page = 1) {
        loading.value = true
        error.value = null
        try {
            const { data } = await api.get('/muestras/incidencias/', { params: { page } })
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

    async function create(form: IncidenciaForm): Promise<ApiResult> {
        saving.value = true
        try {
            const { data } = await api.post('/muestras/incidencias/', form)
            items.value.unshift(data)
            total.value += 1
            return { ok: true }
        } catch (err) {
            return { ok: false, error: extractError(err) }
        } finally {
            saving.value = false
        }
    }

    async function update(id: number, form: IncidenciaForm): Promise<ApiResult> {
        saving.value = true
        try {
            const { data } = await api.patch(`/muestras/incidencias/${id}/`, form)
            const idx = items.value.findIndex(i => i.id === id)
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
            await api.delete(`/muestras/incidencias/${id}/`)
            items.value = items.value.filter(i => i.id !== id)
            total.value = Math.max(0, total.value - 1)
            return { ok: true }
        } catch (err) {
            return { ok: false, error: extractError(err) }
        }
    }

    return { items, loading, saving, error, total, paginas, paginaActual, fetchAll, create, update, remove }
})
