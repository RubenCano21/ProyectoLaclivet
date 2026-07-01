<script setup lang="ts">
import { onMounted, computed, reactive, watch, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useResultadosStore } from '@/stores/resultados'
import { useAuthStore } from '@/stores/auth'

import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'

import {
  ArrowLeft, Loader2, AlertCircle, Save, FileDown, CheckCircle2, BadgeCheck,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const store = useResultadosStore()
const authStore = useAuthStore()

const validando = ref(false)
const puedeValidar = computed(() =>
  authStore.tienePermiso('validar_resultados') && store.actual?.estado === 'completado'
)

async function validarDesde() {
  if (!id.value) return
  validando.value = true
  await store.validar(id.value)
  validando.value = false
}

const id = computed(() => Number(route.params.id))

function precargarFormulario() {
  // limpiar antes de precargar (por si veníamos de otra captura)
  for (const key of Object.keys(valores)) delete valores[Number(key)]

  if (store.actual) {
    for (const r of store.actual.resultados) {
      valores[r.parametro] = {
        valor_numerico: r.valor_numerico != null ? String(r.valor_numerico) : '',
        valor_texto: r.valor_texto || '',
      }
    }
    observaciones.observaciones = store.actual.observaciones || ''
    observaciones.alteraciones = store.actual.alteraciones || ''
    observaciones.diagnostico = store.actual.diagnostico || ''
    observaciones.pronostico = store.actual.pronostico || ''
  }

  // inicializar vacíos los parámetros que aún no tienen valor capturado
  if (store.plantilla) {
    for (const g of store.plantilla.grupos) {
      for (const p of g.parametros) {
        if (!valores[p.id]) valores[p.id] = { valor_numerico: '', valor_texto: '' }
      }
    }
  }
}

async function cargarTodo() {
  if (!id.value || Number.isNaN(id.value)) return
  await store.fetchDetalle(id.value)
  precargarFormulario()
}

// valor capturado por parametro_id
const valores = reactive<Record<number, { valor_numerico: string; valor_texto: string }>>({})
const observaciones = reactive({ observaciones: '', alteraciones: '', diagnostico: '', pronostico: '' })

onMounted(() => {
  if (id.value && !Number.isNaN(id.value)) cargarTodo()
})

watch(() => route.params.id, () => {
  if (id.value && !Number.isNaN(id.value)) cargarTodo()
})

const esEditable = computed(() => {
  const estado = store.actual?.estado
  return estado === 'pendiente' || estado === 'en_proceso'
})

function getReferencia(p: any) {
  // toma la primera referencia disponible (idealmente filtrada por especie/sexo en backend al evaluar)
  const ref = p.valores_referencia?.[0]
  if (!ref) return null
  if (ref.valor_min != null || ref.valor_max != null) {
    return `${ref.valor_min ?? '–'} a ${ref.valor_max ?? '–'}`
  }
  return ref.texto_referencia || null
}

function getValor(parametroId: number) {
  if (!valores[parametroId]) {
    valores[parametroId] = { valor_numerico: '', valor_texto: '' }
  }
  return valores[parametroId]
}

function getInterpretacionGuardada(parametroId: number) {
  const r = store.actual?.resultados.find(x => x.parametro === parametroId)
  return r?.interpretacion || ''
}

const INTERP_COLOR: Record<string, string> = {
  ALTO: 'text-red-600 font-semibold',
  BAJO: 'text-blue-600 font-semibold',
  NORMAL: 'text-green-600',
}

async function guardar() {
  if (!store.plantilla) return

  const resultados = store.plantilla.grupos.flatMap(g =>
    g.parametros.map(p => {
      const v = getValor(p.id)
      const payload: any = { parametro: p.id }
      if (p.tipo_dato === 'NUM') {
        payload.valor_numerico = v.valor_numerico !== '' ? Number(v.valor_numerico) : null
      } else {
        payload.valor_texto = v.valor_texto || ''
      }
      return payload
    })
  )

  const res = await store.registrar(id.value, {
    ...observaciones,
    resultados,
  })

  if (res.ok) {
    await store.fetchDetalle(id.value)
  }
}

async function generarYDescargarPdf() {
  const res = await store.generarPdf(id.value)
  if (res.ok) {
    // Usar la pdf_url devuelta directamente por el backend o la que quedó en el store
    const url = res.data?.pdf_url || store.actual?.archivo_pdf
    if (url) {
      window.open(url, '_blank')
    }
  }
}
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger class="-ml-1" />
        <Separator orientation="vertical" class="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/dashboard">Inicio</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink href="/resultados">Resultados</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{{ store.actual?.examen_nombre || '...' }}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6 max-w-4xl">
        <Button variant="ghost" size="sm" class="w-fit gap-2 -ml-2" @click="router.push({ name: 'resultados' })">
          <ArrowLeft class="h-4 w-4" /> Volver a Resultados
        </Button>

        <div v-if="store.loadingDetalle" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando examen…</span>
        </div>

        <div v-else-if="store.error"
          class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ store.error }}
        </div>

        <template v-else-if="store.actual && store.plantilla && store.plantilla.id === store.actual.examen">
          <!-- Cabecera -->
          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <div class="flex items-start justify-between">
              <div>
                <h1 class="text-xl font-bold">{{ store.actual.examen_nombre }}</h1>
                <p class="text-sm text-muted-foreground mt-1">
                  {{ store.actual.paciente?.nombre }} · {{ store.actual.paciente?.especie }} {{
                    store.actual.paciente?.raza ? `(${store.actual.paciente.raza})` : '' }}
                </p>
              </div>
              <span v-if="store.actual.estado === 'completado' || store.actual.estado === 'validado'"
                class="inline-flex items-center gap-1 rounded-full border border-green-200 bg-green-50 px-3 py-1 text-xs font-medium text-green-700">
                <CheckCircle2 class="h-3.5 w-3.5" /> {{ store.actual.estado === 'validado' ? 'Validado' : 'Completado'
                }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-4 mt-4 text-sm">
              <div>
                <p class="text-muted-foreground">Solicitud</p>
                <p class="font-medium">{{ store.actual.solicitud_codigo }}</p>
              </div>
              <div>
                <p class="text-muted-foreground">Médico solicitante</p>
                <p class="font-medium">{{ store.actual.medico_solicitante?.nombre_completo || '—' }}</p>
              </div>
            </div>
          </div>

          <!-- Tabla de parámetros, expandida por grupo -->
          <div v-for="grupo in store.plantilla.grupos" :key="grupo.nombre"
            class="rounded-xl border bg-white shadow-xs overflow-hidden">
            <div class="bg-muted/40 px-4 py-2.5 font-semibold text-sm border-b">{{ grupo.nombre }}</div>
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b bg-muted/10 text-muted-foreground">
                  <th class="px-4 py-2 text-left font-medium">Parámetro</th>
                  <th class="px-4 py-2 text-left font-medium w-40">Resultado</th>
                  <th class="px-4 py-2 text-left font-medium w-24">Unidad</th>
                  <th class="px-4 py-2 text-left font-medium w-36">Ref.</th>
                  <th class="px-4 py-2 text-left font-medium w-24">Interp.</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in grupo.parametros" :key="p.id" class="border-b last:border-0">
                  <td class="px-4 py-2.5">{{ p.nombre_parametro }}</td>
                  <td class="px-4 py-2.5">
                    <Input v-if="p.tipo_dato === 'NUM'" v-model="getValor(p.id).valor_numerico" type="number"
                      step="0.001" :disabled="!esEditable" class="h-8" />
                    <Select v-else-if="p.tipo_dato === 'SEL'" v-model="getValor(p.id).valor_texto"
                      :disabled="!esEditable">
                      <SelectTrigger class="h-8">
                        <SelectValue placeholder="—" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem v-for="op in p.opciones || []" :key="op" :value="op">{{ op }}</SelectItem>
                      </SelectContent>
                    </Select>
                    <Input v-else v-model="getValor(p.id).valor_texto" :disabled="!esEditable" class="h-8" />
                  </td>
                  <td class="px-4 py-2.5 text-muted-foreground">{{ p.unidad_medida || '—' }}</td>
                  <td class="px-4 py-2.5 text-muted-foreground text-xs">{{ getReferencia(p) || '—' }}</td>
                  <td class="px-4 py-2.5">
                    <span :class="INTERP_COLOR[getInterpretacionGuardada(p.id)] || 'text-muted-foreground'"
                      class="text-xs">
                      {{ getInterpretacionGuardada(p.id) || '—' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Observaciones clínicas -->
          <div class="rounded-xl border bg-white p-5 shadow-xs space-y-4">
            <h2 class="font-semibold text-sm">Observaciones clínicas</h2>
            <div class="space-y-1.5">
              <label class="text-xs text-muted-foreground">Observaciones generales</label>
              <Textarea v-model="observaciones.observaciones" :disabled="!esEditable" rows="2" />
            </div>
            <div class="space-y-1.5">
              <label class="text-xs text-muted-foreground">Alteraciones</label>
              <Textarea v-model="observaciones.alteraciones" :disabled="!esEditable" rows="2" />
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="text-xs text-muted-foreground">Diagnóstico</label>
                <Textarea v-model="observaciones.diagnostico" :disabled="!esEditable" rows="2" />
              </div>
              <div class="space-y-1.5">
                <label class="text-xs text-muted-foreground">Pronóstico</label>
                <Input v-model="observaciones.pronostico" :disabled="!esEditable" />
              </div>
            </div>
          </div>

          <div v-if="store.error"
            class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
            <AlertCircle class="h-4 w-4 shrink-0" />
            {{ store.error }}
          </div>

          <!-- Acciones -->
          <div class="flex items-center justify-end gap-3 pb-6">
            <Button v-if="store.actual.estado === 'completado' || store.actual.estado === 'validado'" variant="outline"
              class="gap-2" @click="generarYDescargarPdf">
              <FileDown class="h-4 w-4" />
              {{ store.actual.archivo_pdf ? 'Descargar PDF' : 'Generar e imprimir PDF' }}
            </Button>
            <Button
              v-if="puedeValidar"
              :disabled="validando"
              class="gap-2 bg-emerald-600 hover:bg-emerald-700 text-white"
              @click="validarDesde">
              <Loader2 v-if="validando" class="h-4 w-4 animate-spin" />
              <BadgeCheck v-else class="h-4 w-4" />
              Validar resultado
            </Button>
            <Button v-if="esEditable" :disabled="store.saving" class="gap-2" @click="guardar">
              <Loader2 v-if="store.saving" class="h-4 w-4 animate-spin" />
              <Save v-else class="h-4 w-4" />
              Guardar resultados
            </Button>
          </div>
        </template>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>