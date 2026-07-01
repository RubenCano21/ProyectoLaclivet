<script setup lang="ts">
import { useResultadosStore } from '@/stores/resultados'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from '@/components/ui/dialog'

import {
  Search, Loader2, AlertCircle, ClipboardCheck, ChevronLeft, ChevronRight,
  Eye, BadgeCheck, FlaskConical, FileDown, CheckCircle2,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const store = useResultadosStore()

const search = ref('')
const estadoFiltro = ref<string>('completado')

const confirmOpen = ref(false)
const idAValidar = ref<number | null>(null)
const validandoId = ref<number | null>(null)
const errorValidacion = ref<string | null>(null)

function verDetalle(id: number) {
  router.push({ name: 'captura-resultados', params: { id } })
}

function abrirConfirmar(id: number) {
  idAValidar.value = id
  errorValidacion.value = null
  confirmOpen.value = true
}

async function confirmarValidacion() {
  if (!idAValidar.value) return
  validandoId.value = idAValidar.value
  errorValidacion.value = null
  confirmOpen.value = false
  const result = await store.validar(idAValidar.value)
  validandoId.value = null
  if (!result.ok) errorValidacion.value = result.error ?? 'Error al validar'
}

function descargarPdf(url: string) {
  window.open(url, '_blank')
}

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return store.items
  return store.items.filter(o =>
    o.examen_nombre?.toLowerCase().includes(q) ||
    o.solicitud_codigo?.toLowerCase().includes(q) ||
    o.paciente?.nombre?.toLowerCase().includes(q),
  )
})

const ESTADO_BADGE: Record<string, string> = {
  pendiente: 'bg-amber-50 text-amber-700 border-amber-200',
  en_proceso: 'bg-blue-50 text-blue-700 border-blue-200',
  completado: 'bg-green-50 text-green-700 border-green-200',
  validado: 'bg-emerald-50 text-emerald-700 border-emerald-200',
}

function titleCase(s: string | undefined | null) {
  if (!s) return '—'
  return s.replace('_', ' ').replace(/^\w/, c => c.toUpperCase())
}

function formatFecha(f: string | null) {
  if (!f) return '—'
  return new Date(f).toLocaleDateString('es-BO', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function goToPage(page: number) {
  router.replace({ query: { ...route.query, page: String(page) } })
}

watch(
  [() => route.query.page, estadoFiltro],
  ([pageParam]) => {
    const page = Number(pageParam) || 1
    const estado = estadoFiltro.value === 'all' ? '' : estadoFiltro.value
    store.fetchAll(page, estado)
  },
  { immediate: true },
)
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
            <BreadcrumbItem><BreadcrumbLink href="/dashboard">Inicio</BreadcrumbLink></BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem><BreadcrumbLink href="/resultados">Resultados</BreadcrumbLink></BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem><BreadcrumbPage>Validación</BreadcrumbPage></BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6">

        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600">
            <ClipboardCheck class="h-5 w-5" />
          </div>
          <div>
            <h1 class="text-2xl font-bold leading-tight">Validación de Resultados</h1>
            <p class="text-sm text-muted-foreground">Revisa y valida los exámenes completados por el laboratorio</p>
          </div>
        </div>

        <div
          v-if="errorValidacion"
          class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
          <AlertCircle class="h-4 w-4 shrink-0" />{{ errorValidacion }}
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <div class="relative max-w-sm flex-1">
            <Search class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
            <Input v-model="search" placeholder="Buscar por examen, código, paciente…" class="pl-9" />
          </div>
          <Select v-model="estadoFiltro">
            <SelectTrigger class="w-52">
              <SelectValue placeholder="Estado" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="completado">Pendientes de validar</SelectItem>
              <SelectItem value="validado">Ya validados</SelectItem>
              <SelectItem value="all">Todos</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div v-if="store.loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando…</span>
        </div>

        <div
          v-else-if="store.error"
          class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
          <AlertCircle class="h-4 w-4 shrink-0" />{{ store.error }}
        </div>

        <div v-else class="rounded-xl border bg-white shadow-xs overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b bg-muted/40">
                  <th class="px-4 py-3 text-left font-semibold">Solicitud</th>
                  <th class="px-4 py-3 text-left font-semibold">Paciente</th>
                  <th class="px-4 py-3 text-left font-semibold">Examen</th>
                  <th class="px-4 py-3 text-left font-semibold">Fecha resultado</th>
                  <th class="px-4 py-3 text-left font-semibold">Realizado por</th>
                  <th class="px-4 py-3 text-left font-semibold">Estado</th>
                  <th class="px-4 py-3 text-center font-semibold w-40">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filtered.length === 0">
                  <td colspan="7" class="px-4 py-14 text-center text-muted-foreground">
                    <CheckCircle2 class="h-8 w-8 mx-auto mb-2 text-emerald-400 opacity-60" />
                    <p class="font-medium">
                      {{ estadoFiltro === 'completado' ? 'No hay resultados pendientes de validar' : 'No hay registros en este estado' }}
                    </p>
                  </td>
                </tr>

                <tr
                  v-for="o in filtered"
                  :key="o.id"
                  class="border-b last:border-0 hover:bg-muted/20 transition-colors">

                  <td class="px-4 py-3 font-medium text-primary">{{ o.solicitud_codigo || '—' }}</td>

                  <td class="px-4 py-3">
                    <p class="font-medium">{{ o.paciente?.nombre || '—' }}</p>
                    <p class="text-xs text-muted-foreground">
                      {{ o.paciente?.especie || '' }}
                    </p>
                  </td>

                  <td class="px-4 py-3">
                    <p>{{ o.examen_nombre }}</p>
                    <span v-if="o.muestra" class="inline-flex items-center gap-1 text-xs text-muted-foreground mt-0.5">
                      <FlaskConical class="h-3 w-3" /> {{ o.muestra.codigo }}
                    </span>
                  </td>

                  <td class="px-4 py-3 text-xs text-muted-foreground whitespace-nowrap">
                    {{ formatFecha(o.fecha_resultado) }}
                  </td>

                  <td class="px-4 py-3 text-sm">
                    {{ (o.veterinario_nombre as any)?.nombre_completo ?? o.veterinario_nombre ?? '—' }}
                  </td>

                  <td class="px-4 py-3">
                    <span :class="`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${ESTADO_BADGE[o.estado]}`">
                      {{ titleCase(o.estado) }}
                    </span>
                  </td>

                  <td class="px-4 py-3">
                    <div class="flex items-center justify-center gap-1.5 flex-wrap">
                      <Button size="sm" variant="outline" class="h-7 gap-1 text-xs" @click="verDetalle(o.id)">
                        <Eye class="h-3.5 w-3.5" /> Ver
                      </Button>

                      <Button
                        v-if="o.estado === 'completado'"
                        size="sm"
                        class="h-7 gap-1 text-xs bg-emerald-600 hover:bg-emerald-700 text-white"
                        :disabled="validandoId === o.id"
                        @click="abrirConfirmar(o.id)">
                        <Loader2 v-if="validandoId === o.id" class="h-3.5 w-3.5 animate-spin" />
                        <BadgeCheck v-else class="h-3.5 w-3.5" />
                        Validar
                      </Button>

                      <Button
                        v-if="o.archivo_pdf"
                        size="sm"
                        variant="outline"
                        class="h-7 gap-1 text-xs"
                        @click="descargarPdf(o.archivo_pdf!)">
                        <FileDown class="h-3.5 w-3.5" /> PDF
                      </Button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="store.paginas > 1" class="flex items-center justify-between px-4 py-3 border-t bg-muted/20">
            <span class="text-sm text-muted-foreground">
              Página {{ store.paginaActual }} de {{ store.paginas }} — {{ store.total }} registros
            </span>
            <div class="flex items-center gap-1">
              <Button variant="outline" size="sm" :disabled="store.paginaActual <= 1" @click="goToPage(store.paginaActual - 1)">
                <ChevronLeft class="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" :disabled="store.paginaActual >= store.paginas" @click="goToPage(store.paginaActual + 1)">
                <ChevronRight class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>

  <!-- Confirmación -->
  <Dialog :open="confirmOpen" @update:open="confirmOpen = $event">
    <DialogContent>
      <DialogHeader>
        <DialogTitle>¿Validar este resultado?</DialogTitle>
        <DialogDescription>
          Al validar, el resultado quedará marcado como <strong>Validado</strong> y no podrá
          revertirse. Esta acción queda registrada con tu nombre.
        </DialogDescription>
      </DialogHeader>
      <DialogFooter class="gap-2">
        <Button variant="outline" @click="confirmOpen = false">Cancelar</Button>
        <Button class="bg-emerald-600 hover:bg-emerald-700 text-white" @click="confirmarValidacion">
          Sí, validar
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>
