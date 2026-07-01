<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMuestrasStore } from '@/stores/muestras'
import type { Muestra } from '@/models/muestra'
import MuestraFormModal from './MuestraFormModal.vue'
import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Breadcrumb, BreadcrumbItem, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator, BreadcrumbLink } from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  FlaskConical, Plus, Search, Pencil, Trash2, AlertCircle, ChevronLeft, ChevronRight,
} from 'lucide-vue-next'

const store = useMuestrasStore()

// ── Modal ──────────────────────────────────────────────────────────────────────
const modalOpen     = ref(false)
const muestraEditar = ref<Muestra | null>(null)

function abrirCrear() {
  muestraEditar.value = null
  modalOpen.value = true
}

function abrirEditar(m: Muestra) {
  muestraEditar.value = m
  modalOpen.value = true
}

async function onSaved() {
  await store.fetchAll(store.paginaActual, search.value)
}

// ── Búsqueda y paginación ──────────────────────────────────────────────────────
const search = ref('')
let searchTimeout: ReturnType<typeof setTimeout>

function onSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => store.fetchAll(1, search.value), 350)
}

function irPagina(p: number) {
  store.fetchAll(p, search.value)
}

// ── Eliminar ──────────────────────────────────────────────────────────────────
const eliminandoId = ref<number | null>(null)

async function confirmarEliminar(m: Muestra) {
  if (!confirm(`¿Eliminar la muestra ${m.codigo}?`)) return
  eliminandoId.value = m.id
  await store.remove(m.id)
  eliminandoId.value = null
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const estadoClases: Record<string, string> = {
  pendiente:  'bg-amber-100 text-amber-700',
  en_proceso: 'bg-blue-100 text-blue-700',
  completada: 'bg-green-100 text-green-700',
  rechazada:  'bg-red-100 text-red-700',
}

function formatFecha(fecha: string | null) {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(() => store.fetchAll())
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>

      <!-- Header -->
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
              <BreadcrumbPage>Muestras</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6">

        <!-- Cabecera -->
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold leading-tight flex items-center gap-2">
              <FlaskConical class="h-6 w-6 text-primary" />
              Muestras
            </h1>
            <p class="text-sm text-muted-foreground mt-0.5">Registro y trazabilidad de muestras de laboratorio</p>
          </div>
          <Button @click="abrirCrear" class="gap-2">
            <Plus class="h-4 w-4" /> Nueva muestra
          </Button>
        </div>

        <!-- Buscador -->
        <div class="relative max-w-sm">
          <Search class="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input v-model="search" @input="onSearch" placeholder="Buscar por código o paciente…" class="pl-9" />
        </div>

        <!-- Error -->
        <div v-if="store.error" class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" /> {{ store.error }}
        </div>

        <!-- Tabla -->
        <div class="rounded-xl border bg-white shadow-xs overflow-hidden">
          <table class="w-full text-sm">
            <thead class="border-b bg-muted/30">
              <tr>
                <th class="text-left px-5 py-3 text-xs font-medium text-muted-foreground">Código</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Paciente</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Tipo</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Estado</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Fecha recepción</th>
                <th class="text-left px-4 py-3 text-xs font-medium text-muted-foreground">Observaciones</th>
                <th class="px-5 py-3 text-xs font-medium text-muted-foreground text-right">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/40">

              <!-- Skeleton -->
              <template v-if="store.loading">
                <tr v-for="n in 5" :key="n">
                  <td class="px-5 py-3"><Skeleton class="h-4 w-32" /></td>
                  <td class="px-4 py-3"><Skeleton class="h-4 w-28" /></td>
                  <td class="px-4 py-3"><Skeleton class="h-4 w-20" /></td>
                  <td class="px-4 py-3"><Skeleton class="h-5 w-20 rounded-full" /></td>
                  <td class="px-4 py-3"><Skeleton class="h-4 w-24" /></td>
                  <td class="px-4 py-3"><Skeleton class="h-4 w-32" /></td>
                  <td class="px-5 py-3"><Skeleton class="h-7 w-16 ml-auto" /></td>
                </tr>
              </template>

              <!-- Sin datos -->
              <tr v-else-if="store.items.length === 0">
                <td colspan="7" class="px-5 py-12 text-center text-sm text-muted-foreground">
                  <FlaskConical class="h-10 w-10 mx-auto mb-2 opacity-20" />
                  No se encontraron muestras.
                </td>
              </tr>

              <!-- Filas -->
              <tr
                v-else
                v-for="m in store.items"
                :key="m.id"
                class="hover:bg-muted/20 transition-colors"
              >
                <td class="px-5 py-3 font-mono text-xs font-medium">{{ m.codigo }}</td>
                <td class="px-4 py-3 font-medium">{{ m.paciente_nombre ?? '—' }}</td>
                <td class="px-4 py-3 text-muted-foreground capitalize">{{ m.tipo_muestra ?? '—' }}</td>
                <td class="px-4 py-3">
                  <Badge
                    class="text-xs capitalize"
                    :class="estadoClases[m.estado] ?? 'bg-gray-100 text-gray-600'"
                  >
                    {{ m.estado.replace('_', ' ') }}
                  </Badge>
                </td>
                <td class="px-4 py-3 text-muted-foreground">{{ formatFecha(m.fecha_recepcion) }}</td>
                <td class="px-4 py-3 text-muted-foreground text-xs max-w-45 truncate">{{ m.observaciones ?? '—' }}</td>
                <td class="px-5 py-3">
                  <div class="flex items-center justify-end gap-1">
                    <Button size="icon" variant="ghost" class="h-7 w-7" @click="abrirEditar(m)">
                      <Pencil class="h-3.5 w-3.5" />
                    </Button>
                    <Button
                      size="icon" variant="ghost"
                      class="h-7 w-7 text-red-500 hover:text-red-600 hover:bg-red-50"
                      :disabled="eliminandoId === m.id"
                      @click="confirmarEliminar(m)"
                    >
                      <Trash2 class="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </td>
              </tr>

            </tbody>
          </table>
        </div>

        <!-- Paginación -->
        <div v-if="store.paginas > 1" class="flex items-center justify-between text-sm text-muted-foreground">
          <span>Página {{ store.paginaActual }} de {{ store.paginas }} · {{ store.total }} muestras</span>
          <div class="flex gap-1">
            <Button
              size="icon" variant="outline" class="h-8 w-8"
              :disabled="store.paginaActual <= 1 || store.loading"
              @click="irPagina(store.paginaActual - 1)"
            >
              <ChevronLeft class="h-4 w-4" />
            </Button>
            <Button
              size="icon" variant="outline" class="h-8 w-8"
              :disabled="store.paginaActual >= store.paginas || store.loading"
              @click="irPagina(store.paginaActual + 1)"
            >
              <ChevronRight class="h-4 w-4" />
            </Button>
          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>

  <!-- Modal -->
  <MuestraFormModal
    v-model:open="modalOpen"
    :muestra="muestraEditar"
    @saved="onSaved"
  />
</template>
