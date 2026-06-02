<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppSidebar from '@/components/layout/Sidebar.vue'
import {
  SidebarInset, SidebarProvider, SidebarTrigger,
} from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbPage, BreadcrumbSeparator, BreadcrumbLink,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Plus, Search, Pencil, Trash2, Loader2,
  AlertCircle, Stethoscope, X, Check, ChevronLeft, ChevronRight,
} from 'lucide-vue-next'
import { useMedicosStore, type Medico } from '@/stores/medicos'
import MedicoFormView from './MedicoFormView.vue'

const store = useMedicosStore()

const search = ref('')
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return store.items
  return store.items.filter(m =>
    m.nombre.toLowerCase().includes(q) ||
    m.apellido.toLowerCase().includes(q) ||
    (m.especialidad ?? '').toLowerCase().includes(q) ||
    (m.correo ?? '').toLowerCase().includes(q),
  )
})

const modalOpen = ref(false)
const editingMedico = ref<Medico | null>(null)

function openCreate() {
  editingMedico.value = null
  modalOpen.value = true
}

function openEdit(m: Medico) {
  editingMedico.value = m
  modalOpen.value = true
}

const confirmDeleteId = ref<number | null>(null)

async function handleDelete(id: number) {
  await store.remove(id)
  confirmDeleteId.value = null
}

function goToPage(page: number) {
  store.fetchAll(page)
}

function generoLabel(g: string | null): string {
  if (g === 'M') return 'Masculino'
  if (g === 'F') return 'Femenino'
  if (g === 'O') return 'Otro'
  return '—'
}

onMounted(() => store.fetchAll())
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
              <BreadcrumbPage>Médicos</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6">

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg
            bg-mineral-green-100 text-mineral-green-700">
              <Stethoscope class="h-5 w-5" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-mineral-green-950 leading-tight">Gestión de Médicos</h1>
              <p class="text-sm text-muted-foreground">
                {{ store.total }} registrado{{ store.total !== 1 ? 's' : '' }}
              </p>
            </div>
          </div>
          <Button @click="openCreate" class="bg-mineral-green-600 hover:bg-mineral-green-700 text-white gap-2">
            <Plus class="h-4 w-4" />
            Nuevo médico
          </Button>
        </div>

        <div class="relative max-w-sm">
          <Search class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
          <Input
            v-model="search"
            placeholder="Buscar por nombre, especialidad, correo…"
            class="pl-9"
          />
        </div>

        <div v-if="store.loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando médicos…</span>
        </div>

        <div v-else-if="store.error" class="flex items-center gap-2 rounded-xl border
        border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ store.error }}
        </div>

        <div v-else class="rounded-xl border bg-white shadow-xs overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b bg-mineral-green-50/60">
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-16">#</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-36">Nombre</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-36">Apellido</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-40">Especialidad</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-28">Género</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800">Correo</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-32">Teléfono</th>
                  <th class="px-4 py-3 text-center font-semibold text-mineral-green-800 w-28">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filtered.length === 0">
                  <td colspan="8" class="px-4 py-12 text-center text-muted-foreground">
                    {{ search ? 'Sin resultados para tu búsqueda.' : 'No hay médicos registrados.' }}
                  </td>
                </tr>

                <tr
                  v-for="(m, index) in filtered"
                  :key="m.id"
                  class="border-b last:border-0 hover:bg-mineral-green-50/40 transition-colors"
                >
                  <td class="px-4 py-3 font-medium text-mineral-green-950">{{ index + 1 }}</td>
                  <td class="px-4 py-3 text-mineral-green-800">{{ m.nombre }}</td>
                  <td class="px-4 py-3 text-mineral-green-800">{{ m.apellido }}</td>
                  <td class="px-4 py-3 text-mineral-green-700">{{ m.especialidad || '—' }}</td>
                  <td class="px-4 py-3 text-mineral-green-700">{{ generoLabel(m.genero) }}</td>
                  <td class="px-4 py-3 text-mineral-green-700">{{ m.correo || '—' }}</td>
                  <td class="px-4 py-3 text-mineral-green-700">{{ m.telefono || '—' }}</td>
                  <td class="px-4 py-3">
                    <div v-if="confirmDeleteId !== m.id" class="flex items-center justify-center gap-1">
                      <button
                        @click="openEdit(m)"
                        class="p-1.5 rounded-md text-mineral-green-600 hover:bg-mineral-green-100 transition-colors"
                        title="Editar"
                      >
                        <Pencil class="h-4 w-4" />
                      </button>
                      <button
                        @click="confirmDeleteId = m.id"
                        class="p-1.5 rounded-md text-red-500 hover:bg-red-50 transition-colors"
                        title="Eliminar"
                      >
                        <Trash2 class="h-4 w-4" />
                      </button>
                    </div>

                    <div v-else class="flex items-center justify-center gap-1">
                      <button
                        @click="handleDelete(m.id)"
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

          <div v-if="store.paginas > 1" class="flex items-center justify-between px-4 py-3 border-t bg-mineral-green-50/30">
            <span class="text-sm text-muted-foreground">
              Página {{ store.paginaActual }} de {{ store.paginas }} — {{ store.total }} registros
            </span>
            <div class="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                :disabled="store.paginaActual <= 1"
                @click="goToPage(store.paginaActual - 1)"
              >
                <ChevronLeft class="h-4 w-4" />
              </Button>
              <span class="px-2 text-sm font-medium">{{ store.paginaActual }}</span>
              <Button
                variant="outline"
                size="sm"
                :disabled="store.paginaActual >= store.paginas"
                @click="goToPage(store.paginaActual + 1)"
              >
                <ChevronRight class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </main>

    </SidebarInset>
  </SidebarProvider>

  <MedicoFormView
    v-model:open="modalOpen"
    :medico="editingMedico"
    @saved="store.fetchAll(store.paginaActual)"
  />
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
