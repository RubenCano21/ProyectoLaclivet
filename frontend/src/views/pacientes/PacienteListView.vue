<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { pacienteService, type Paciente } from '@/services/pacienteService'
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
  AlertCircle, PawPrint, Check, X, ChevronLeft, ChevronRight,
} from 'lucide-vue-next'

const router = useRouter()
const route  = useRoute()

// ── Estado ───────────────────────────────────────────────────────────────────
const pacientes       = ref<Paciente[]>([])
const loading         = ref(false)
const error           = ref<string | null>(null)
const total           = ref(0)
const paginas         = ref(1)
const paginaActual    = ref(1)
const confirmDeleteId = ref<number | null>(null)
const search          = ref('')

// ── Filtro ───────────────────────────────────────────────────────────────────
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return pacientes.value
  return pacientes.value.filter(p =>
    p.nombre.toLowerCase().includes(q) ||
    p.especie_nombre.toLowerCase().includes(q) ||
    p.raza_nombre.toLowerCase().includes(q) ||
    p.propietario_nombre.toLowerCase().includes(q),
  )
})

// ── Helpers ──────────────────────────────────────────────────────────────────
function titleCase(s: string) {
  return s.charAt(0).toUpperCase() + s.slice(1)
}
function formatFecha(fecha: string | null) {
  if (!fecha) return '—'
  return new Date(fecha + 'T00:00:00').toLocaleDateString('es-BO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

// ── Carga ────────────────────────────────────────────────────────────────────
async function loadPacientes(page = 1) {
  loading.value = true
  error.value = null
  try {
    const res = await pacienteService.getAll(page)
    const data = res.data
    pacientes.value  = data.resultados
    total.value      = data.total
    paginas.value    = data.paginas
    paginaActual.value = data.pagina_actual
  } catch (e: any) {
    error.value = e.response?.data?.detail ?? 'Error al cargar los pacientes'
  } finally {
    loading.value = false
  }
}

function goToPage(page: number) {
  router.replace({ query: { page: String(page) } })
}

async function handleDelete(id: number) {
  try {
    await pacienteService.delete(id)
    confirmDeleteId.value = null
    await loadPacientes(paginaActual.value)
  } catch {
    error.value = 'Error al eliminar el paciente'
  }
}

// Reacciona a cambios en ?page= (incluyendo el primer render y el botón Atrás del navegador)
watch(
  () => route.query.page,
  (pageParam) => {
    const page = Number(pageParam) || 1
    loadPacientes(page)
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
              <BreadcrumbPage>Pacientes</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <!-- Contenido principal -->
      <main class="flex flex-1 flex-col gap-6 p-6">

        <!-- Título + botón nuevo -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <PawPrint class="h-5 w-5" />
            </div>
            <div>
              <h1 class="text-2xl font-bold leading-tight">Gestión de Pacientes</h1>
              <p class="text-sm text-muted-foreground">
                {{ total }} registrado{{ total !== 1 ? 's' : '' }}
              </p>
            </div>
          </div>
          <Button @click="router.push('/pacientes/nuevo')" class="gap-2">
            <Plus class="h-4 w-4" />
            Nuevo paciente
          </Button>
        </div>

        <!-- Buscador -->
        <div class="relative max-w-sm">
          <Search class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
          <Input v-model="search" placeholder="Buscar por nombre, especie, raza…" class="pl-9" />
        </div>

        <!-- Cargando -->
        <div v-if="loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando pacientes…</span>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ error }}
        </div>

        <!-- Tabla -->
        <div v-else class="rounded-xl border bg-white shadow-xs overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b bg-muted/40">
                  <th class="px-4 py-3 text-left font-semibold">Nombre</th>
                  <th class="px-4 py-3 text-left font-semibold">Especie</th>
                  <th class="px-4 py-3 text-left font-semibold">Raza</th>
                  <th class="px-4 py-3 text-left font-semibold">Sexo</th>
                  <th class="px-4 py-3 text-left font-semibold">Fecha nac.</th>
                  <th class="px-4 py-3 text-left font-semibold">Propietario</th>
                  <th class="px-4 py-3 text-center font-semibold w-28">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filtered.length === 0">
                  <td colspan="7" class="px-4 py-12 text-center text-muted-foreground">
                    {{ search ? 'Sin resultados para tu búsqueda.' : 'No hay pacientes registrados.' }}
                  </td>
                </tr>
                <tr
                  v-for="p in filtered"
                  :key="p.id"
                  class="border-b last:border-0 hover:bg-muted/20 transition-colors"
                >
                  <td class="px-4 py-3 font-medium">{{ p.nombre }}</td>
                  <td class="px-4 py-3">{{ p.especie_nombre }}</td>
                  <td class="px-4 py-3">{{ p.raza_nombre }}</td>
                  <td class="px-4 py-3">{{ titleCase(p.sexo) }}</td>
                  <td class="px-4 py-3">{{ formatFecha(p.fecha_nacimiento) }}</td>
                  <td class="px-4 py-3">{{ p.propietario_nombre }}</td>
                  <td class="px-4 py-3">
                    <div v-if="confirmDeleteId !== p.id" class="flex items-center justify-center gap-1">
                      <button
                        @click="router.push(`/pacientes/${p.id}`)"
                        class="p-1.5 rounded-md text-primary hover:bg-primary/10 transition-colors"
                        title="Ver / Editar"
                      >
                        <Pencil class="h-4 w-4" />
                      </button>
                      <button
                        @click="confirmDeleteId = p.id"
                        class="p-1.5 rounded-md text-red-500 hover:bg-red-50 transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 class="h-4 w-4" />
                      </button>
                    </div>
                    <div v-else class="flex items-center justify-center gap-1">
                      <button
                        @click="handleDelete(p.id)"
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
          <div v-if="paginas > 1" class="flex items-center justify-between px-4 py-3 border-t bg-muted/20">
            <span class="text-sm text-muted-foreground">
              Página {{ paginaActual }} de {{ paginas }} — {{ total }} registros
            </span>
            <div class="flex items-center gap-1">
              <Button variant="outline" size="sm" :disabled="paginaActual <= 1" @click="goToPage(paginaActual - 1)">
                <ChevronLeft class="h-4 w-4" />
              </Button>
              <span class="px-2 text-sm font-medium">{{ paginaActual }}</span>
              <Button variant="outline" size="sm" :disabled="paginaActual >= paginas" @click="goToPage(paginaActual + 1)">
                <ChevronRight class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>
</template>

