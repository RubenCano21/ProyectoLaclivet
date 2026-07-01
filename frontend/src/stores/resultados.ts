import {
    resultadoFlujoService,
    examenService,
    type OrdenExamenCompleto,
    type OrdenExamenResultadosForm,
    type ExamenPlantilla,
} from '@/services/catalogoService'
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

export const useResultadosStore = defineStore('resultados', () => {
    const items = ref<OrdenExamenCompleto[]>([])
    const loading = ref(false)
    const saving = ref(false)
    const error = ref<string | null>(null)
    const total = ref(0)
    const paginas = ref(1)
    const paginaActual = ref(1)

    const actual = ref<OrdenExamenCompleto | null>(null)
    const plantilla = ref<ExamenPlantilla | null>(null)
    const loadingDetalle = ref(false)

    async function fetchAll(page = 1, estado = '') {
        loading.value = true
        error.value = null
        try {
            const { data } = await resultadoFlujoService.getAll({ page, estado: estado || undefined })
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
            error.value = 'ID de solicitud inválido.'
            return
        }
        loadingDetalle.value = true
        error.value = null
        try {
            const { data } = await resultadoFlujoService.getCompleto(id)
            actual.value = data
            const { data: plantillaData } = await examenService.getPlantilla(data.examen as unknown as number)
            plantilla.value = plantillaData
        } catch (err) {
            error.value = extractError(err)
        } finally {
            loadingDetalle.value = false
        }
    }

    async function registrar(id: number, form: OrdenExamenResultadosForm): Promise<ApiResult> {
        saving.value = true
        error.value = null
        try {
            const { data } = await resultadoFlujoService.registrar(id, form)
            actual.value = data
            return { ok: true, data }
        } catch (err) {
            const msg = extractError(err)
            error.value = msg
            return { ok: false, error: msg }
        } finally {
            saving.value = false
        }
    }

    async function generarPdf(id: number): Promise<ApiResult> {
        error.value = null
        try {
            const { data } = await resultadoFlujoService.generarPdf(id)
            // El backend devuelve { success, message, pdf_url, pdf_name }, NO un OrdenExamenCompleto.
            // Actualizamos solo el campo archivo_pdf del registro actual para que la vista pueda descargarlo.
            if (data.success && data.pdf_url && actual.value) {
                actual.value = { ...actual.value, archivo_pdf: data.pdf_url }
            }
            return { ok: data.success, data }
        } catch (err) {
            const msg = extractError(err)
            error.value = msg
            return { ok: false, error: msg }
        }
    }

    return {
        items, loading, saving, error, total, paginas, paginaActual,
        actual, plantilla, loadingDetalle,
        fetchAll, fetchDetalle, registrar, generarPdf,
    }
})