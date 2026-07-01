<script setup lang="ts">
import { useIncidenciasStore } from '@/stores/incidencias';
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

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
  Plus, Search, Pencil, Trash2, Loader2,
  AlertCircle, AlertTriangle, Check, X, ChevronLeft, ChevronRight,
} from 'lucide-vue-next'
import type { IncidenciaMuestra } from '@/models/muestra';
import IncidenciaFormModal from '@/views/muestras/IncidenciaFormModal.vue'

const router = useRouter();
const route = useRoute();
const store = useIncidenciasStore()

const confirmDeleteId = ref<number | null>(null)
const search = ref('')

// Modal
const modalOpen = ref(false)
const incidenciaEditando = ref<IncidenciaMuestra | null>(null)

function abrirNuevo() {
  incidenciaEditando.value = null
  modalOpen.value = true
}

function abrirEditar(i: IncidenciaMuestra) {
  incidenciaEditando.value = i
  modalOpen.value = true
}

function onSaved() {
  store.fetchAll(store.paginaActual)
}

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return store.items
  return store.items.filter((i: IncidenciaMuestra) =>
      i.muestra_codigo?.toLowerCase().includes(q) ||
      i.descripcion?.toLowerCase().includes(q),
  )
})

// ── Helpers ──────────────────────────────────────────────────────────────────
function formatFecha(fecha: string | null) {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleString('es-BO', {
    day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit',
  })
}

function goToPage(page: number) {
  router.replace({ query: { page: String(page) } })
}

async function handleDelete(id: number) {
  const res = await store.remove(id)
  confirmDeleteId.value = null
  if (!res.ok) {
    // El store ya expone `error`
  }
}

// Reacciona a cambios en ?page= (incluyendo el primer render y el botón Atrás del navegador)
watch(
  () => route.query.page,
  (pageParam) => {
    const page = Number(pageParam) || 1
    store.fetchAll(page)
  },
  { immediate: true },
)
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
              <BreadcrumbPage>Incidencias</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <!-- Contenido principal -->
      <main class="flex flex-1 flex-col gap-6 p-6">

        <!-- Título + botón nuevo -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-500/10 text-amber-600">
              <AlertTriangle class="h-5 w-5" />
            </div>
            <div>
              <h1 class="text-2xl font-bold leading-tight">Incidencias de Muestras</h1>
              <p class="text-sm text-muted-foreground">
                {{ store.total }} registrada{{ store.total !== 1 ? 's' : '' }}
              </p>
            </div>
          </div>
          <Button @click="abrirNuevo" class="gap-2">
            <Plus class="h-4 w-4" />
            Nueva Incidencia
          </Button>
        </div>

        <!-- Buscador -->
        <div class="relative max-w-sm">
          <Search class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
          <Input v-model="search" placeholder="Buscar por código de muestra o descripción…" class="pl-9" />
        </div>

        <!-- Cargando -->
        <div v-if="store.loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando incidencias…</span>
        </div>

        <!-- Error -->
        <div v-else-if="store.error" class="flex items-center gap-2 rounded-xl border border-red-200
        bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ store.error }}
        </div>

        <!-- Tabla -->
        <div v-else class="rounded-xl border bg-white shadow-xs overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b bg-muted/40">
                  <th class="px-4 py-3 text-left font-semibold">Muestra</th>
                  <th class="px-4 py-3 text-left font-semibold">Fecha registro</th>
                  <th class="px-4 py-3 text-left font-semibold">Descripción</th>
                  <th class="px-4 py-3 text-center font-semibold w-28">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filtered.length === 0">
                  <td colspan="4" class="px-4 py-12 text-center text-muted-foreground">
                    {{ search ? 'Sin resultados para tu búsqueda.' : 'No hay incidencias registradas.' }}
                  </td>
                </tr>
                <tr
                  v-for="i in filtered"
                  :key="i.id"
                  class="border-b last:border-0 hover:bg-muted/20 transition-colors"
                >
                  <td class="px-4 py-3 font-medium">{{ i.muestra_codigo || '—' }}</td>
                  <td class="px-4 py-3">{{ formatFecha(i.fecha_registro) }}</td>
                  <td class="px-4 py-3">{{ i.descripcion || '—' }}</td>
                  <td class="px-4 py-3">
                    <div v-if="confirmDeleteId !== i.id" class="flex items-center justify-center gap-1">
                      <button
                        @click="abrirEditar(i)"
                        class="p-1.5 rounded-md text-primary hover:bg-primary/10 transition-colors"
                        title="Editar"
                      >
                        <Pencil class="h-4 w-4" />
                      </button>
                      <button
                        @click="confirmDeleteId = i.id"
                        class="p-1.5 rounded-md text-red-500 hover:bg-red-50 transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 class="h-4 w-4" />
                      </button>
                    </div>
                    <div v-else class="flex items-center justify-center gap-1">
                      <button
                        @click="handleDelete(i.id)"
                        class="p-1.5 rounded-md bg-red-500 text-white hover:bg-red-600 transition-colors"
                        title="Confirmar eliminación"
                      >
                        <Check class="h-4 w-4" />
                      </button>
                      <button
                        @click="confirmDeleteId = null"
                        class="p-1.5 rounded-md text-muted-foreground hover:bg-accent transition-colors"
                        title="Cancelar"
                      >
                        <X class="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Paginación -->
          <div v-if="store.paginas > 1" class="flex items-center justify-between px-4 py-3 border-t bg-muted/20">
            <span class="text-sm text-muted-foreground">
              Página {{ store.paginaActual }} de {{ store.paginas }} — {{ store.total }} registros
            </span>
            <div class="flex items-center gap-1">
              <Button variant="outline" size="sm" :disabled="store.paginaActual <= 1" @click="goToPage(store.paginaActual - 1)">
                <ChevronLeft class="h-4 w-4" />
              </Button>
              <span class="px-2 text-sm font-medium">{{ store.paginaActual }}</span>
              <Button variant="outline" size="sm" :disabled="store.paginaActual >= store.paginas" @click="goToPage(store.paginaActual + 1)">
                <ChevronRight class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>

  <!-- Modal crear/editar -->
  <IncidenciaFormModal
    v-model:open="modalOpen"
    :incidencia="incidenciaEditando"
    @saved="onSaved"
  />
</template>
