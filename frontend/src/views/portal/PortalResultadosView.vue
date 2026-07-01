<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { portalService } from '@/services/portalService'

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
  Loader2, AlertCircle, FileDown, ClipboardCheck, Search,
} from 'lucide-vue-next'

interface Resultado {
  id: number
  estado: string
  examen_nombre: string | null
  solicitud_codigo: string | null
  fecha_solicitud: string | null
  fecha_resultado: string | null
  paciente: { nombre: string; especie_nombre: string } | null
  archivo_pdf: string | null
}

const resultados = ref<Resultado[]>([])
const loading   = ref(false)
const error     = ref<string | null>(null)
const search    = ref('')

function formatFecha(f: string | null) {
  if (!f) return '—'
  return new Date(f).toLocaleDateString('es-BO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

const filtered = () => {
  const q = search.value.trim().toLowerCase()
  if (!q) return resultados.value
  return resultados.value.filter(r =>
    r.examen_nombre?.toLowerCase().includes(q) ||
    r.paciente?.nombre?.toLowerCase().includes(q) ||
    r.solicitud_codigo?.toLowerCase().includes(q),
  )
}

function descargarPdf(url: string) {
  window.open(url, '_blank')
}

const ESTADO_COLOR: Record<string, string> = {
  completado: 'bg-green-100 text-green-700',
  validado: 'bg-emerald-100 text-emerald-700',
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await portalService.getMisResultados()
    resultados.value = Array.isArray(data) ? data : (data.resultados ?? [])
  } catch {
    error.value = 'No se pudo cargar los resultados.'
  } finally {
    loading.value = false
  }
})
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
            <BreadcrumbItem><BreadcrumbLink href="/mis-mascotas">Portal</BreadcrumbLink></BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem><BreadcrumbPage>Mis Resultados</BreadcrumbPage></BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6 max-w-3xl">
        <!-- Título -->
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-green-500/10 text-green-600">
            <ClipboardCheck class="h-5 w-5" />
          </div>
          <div>
            <h1 class="text-2xl font-bold leading-tight">Mis Resultados</h1>
            <p class="text-sm text-muted-foreground">Resultados de exámenes completados de tus mascotas</p>
          </div>
        </div>

        <!-- Buscador -->
        <div class="relative max-w-sm">
          <Search class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
          <Input v-model="search" placeholder="Buscar por examen, mascota o código…" class="pl-9" />
        </div>

        <!-- Cargando -->
        <div v-if="loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando resultados…</span>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" /> {{ error }}
        </div>

        <!-- Sin resultados -->
        <div v-else-if="filtered().length === 0" class="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground">
          <ClipboardCheck class="h-12 w-12 opacity-20" />
          <p class="text-sm">{{ search ? 'Sin resultados para tu búsqueda.' : 'Aún no hay resultados disponibles.' }}</p>
        </div>

        <!-- Lista de resultados -->
        <div v-else class="space-y-3">
          <div
            v-for="r in filtered()"
            :key="r.id"
            class="rounded-xl border bg-white p-4 shadow-xs flex items-start justify-between gap-4"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap mb-1">
                <p class="font-semibold">{{ r.examen_nombre || 'Examen' }}</p>
                <span 
                    :class="ESTADO_COLOR[r.estado] || 'bg-gray-100 text-gray-600'"
                  class="text-xs px-2 py-0.5 rounded-full font-medium capitalize">
                  {{ r.estado }}
                </span>
              </div>
              <p class="text-sm text-muted-foreground">
                Mascota: <span class="text-foreground">{{ r.paciente?.nombre || '—' }}</span>
                <template v-if="r.paciente?.especie_nombre"> · {{ r.paciente.especie_nombre }}</template>
              </p>
              <p class="text-xs text-muted-foreground mt-0.5">
                Solicitud: {{ r.solicitud_codigo || '—' }}
                <template v-if="r.fecha_resultado"> · {{ formatFecha(r.fecha_resultado) }}</template>
              </p>
            </div>
            <div class="shrink-0">
              <Button
                v-if="r.archivo_pdf"
                size="sm"
                variant="outline"
                class="gap-2"
                @click="descargarPdf(r.archivo_pdf!)"
              >
                <FileDown class="h-4 w-4" /> Descargar PDF
              </Button>
              <span v-else class="text-xs text-muted-foreground">PDF no disponible</span>
            </div>
          </div>
        </div>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
