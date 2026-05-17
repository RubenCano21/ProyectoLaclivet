<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppSidebar from '@/components/AppSidebar.vue'
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
  AlertCircle, Users, X, Check,
} from 'lucide-vue-next'
import { useUsuariosStore, type Usuario } from '@/stores/usuarios'

const store = useUsuariosStore()

// ── Búsqueda ────────────────────────────────────────────────────────────────
const search = ref('')
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return store.items
  return store.items.filter(p =>
    p.first_name.toLowerCase().includes(q) ||
    p.last_name.toLowerCase().includes(q) ||
    p.email.toLowerCase().includes(q) ||
    p.is_staff.toString().includes(q),
  )
})

// ── Modal ────────────────────────────────────────────────────────────────────
const modalOpen = ref(false)
const editingUsuario = ref<Usuario | null>(null)

function openCreate() {
  editingUsuario.value = null
  modalOpen.value = true
}

function openEdit(p: Usuario) {
  editingUsuario.value = p
  modalOpen.value = true
}

// ── Eliminar ─────────────────────────────────────────────────────────────────
const confirmDeleteId = ref<number | null>(null)

async function handleDelete(id: number) {
  await store.remove(id)
  confirmDeleteId.value = null
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
              <BreadcrumbPage>Usuarios</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <!-- Contenido principal -->
      <main class="flex flex-1 flex-col gap-6 p-6">

        <!-- Título + botón nuevo -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-mineral-green-100 text-mineral-green-700">
              <Users class="h-5 w-5" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-mineral-green-950 leading-tight">Gestion de Usuarios</h1>
              <p class="text-sm text-muted-foreground">
                {{ store.items.length }} registrado{{ store.items.length !== 1 ? 's' : '' }}
              </p>
            </div>
          </div>
          <Button @click="openCreate" class="bg-mineral-green-600 hover:bg-mineral-green-700 text-white gap-2">
            <Plus class="h-4 w-4" />
            Nuevo usuario
          </Button>
        </div>

        <!-- Buscador -->
        <div class="relative max-w-sm">
          <Search class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
          <Input
            v-model="search"
            placeholder="Buscar por nombre, CI, correo…"
            class="pl-9"
          />
        </div>

        <!-- Estado de carga -->
        <div v-if="store.loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando usuarios…</span>
        </div>

        <!-- Error al cargar -->
        <div v-else-if="store.error" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ store.error }}
        </div>

        <!-- Tabla -->
        <div v-else class="rounded-xl border bg-white shadow-xs overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b bg-mineral-green-50/60">
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-28">CI</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-36">Nombre</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-36">Apellido</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800">Correo</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-32">Teléfono</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-40">Dirección</th>
                  <th class="px-4 py-3 text-center font-semibold text-mineral-green-800 w-28">Acciones</th>
                </tr>
              </thead>
              <tbody>
                <!-- Sin resultados -->
                <tr v-if="filtered.length === 0">
                  <td colspan="7" class="px-4 py-12 text-center text-muted-foreground">
                    {{ search ? 'Sin resultados para tu búsqueda.' : 'No hay usuarios registrados.' }}
                  </td>
                </tr>

                <tr
                  v-for="p in filtered"
                  :key="p.id"
                  class="border-b last:border-0 hover:bg-mineral-green-50/40 transition-colors"
                >
                  <td class="px-4 py-3 font-medium text-mineral-green-950">{{ p.first_name }}</td>
                  <td class="px-4 py-3 text-mineral-green-800">{{ p.last_name }}</td>
                  <td class="px-4 py-3 text-mineral-green-700">{{ p.email }}</td>
                  <td class="px-4 py-3 text-mineral-green-700">{{ p.is_staff }}</td>
                  <td class="px-4 py-3">
                    <!-- Acciones normales -->
                    <div v-if="confirmDeleteId !== p.id" class="flex items-center justify-center gap-1">
                      <button
                        @click="openEdit(p)"
                        class="p-1.5 rounded-md text-mineral-green-600 hover:bg-mineral-green-100 transition-colors"
                        title="Editar"
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

                    <!-- Confirmación de eliminación -->
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
        </div>
      </main>

    </SidebarInset>
  </SidebarProvider>

  <!-- Modal crear / editar -->
  <RegisterUsuarioView
    v-model:open="modalOpen"
    :usuario="editingUsuario"
  />
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
