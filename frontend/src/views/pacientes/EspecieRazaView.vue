<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { especieService, razaService } from '@/services/pacienteService'
import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Plus, Pencil, Trash2, Check, X,
  Loader2, AlertCircle, PawPrint, Tag,
} from 'lucide-vue-next'
import type { Especie } from '@/models/especie'
import type { Raza } from '@/models/raza'

// ── Estado global ─────────────────────────────────────────────────────────────
const loading     = ref(true)
const globalError = ref<string | null>(null)

// ── Especies ──────────────────────────────────────────────────────────────────
const especies           = ref<Especie[]>([])
const selectedEspecieId  = ref<number | null>(null)
const editEspecieId      = ref<number | null>(null)
const editEspecieNombre  = ref('')
const deleteEspecieId    = ref<number | null>(null)
const especieError       = ref<string | null>(null)
const especieSaving      = ref(false)
const showAddEspecie     = ref(false)
const newEspecieNombre   = ref('')
const addEspecieInput    = ref<InstanceType<typeof Input> | null>(null)

const selectedEspecie = computed(() =>
  especies.value.find(e => e.id === selectedEspecieId.value) ?? null,
)

function countRazas(especieId: number) {
  return razas.value.filter(r => r.especie === especieId).length
}

// ── Razas ─────────────────────────────────────────────────────────────────────
const razas          = ref<Raza[]>([])
const editRazaId     = ref<number | null>(null)
const editRazaNombre = ref('')
const deleteRazaId   = ref<number | null>(null)
const razaError      = ref<string | null>(null)
const razaSaving     = ref(false)
const showAddRaza    = ref(false)
const newRazaNombre  = ref('')
const addRazaInput   = ref<InstanceType<typeof Input> | null>(null)

const razasDeEspecie = computed(() =>
  razas.value.filter(r => r.especie === selectedEspecieId.value),
)

// ── Carga inicial ─────────────────────────────────────────────────────────────
async function loadAll() {
  loading.value = true
  globalError.value = null
  try {
    const [re, rr] = await Promise.all([especieService.getAll(), razaService.getAll()])
    especies.value = (re.data as any).resultados ?? (re.data as any).results ?? re.data
    razas.value    = (rr.data as any).resultados ?? (rr.data as any).results ?? rr.data
    if (especies.value.length && !selectedEspecieId.value) {
      selectedEspecieId.value = especies.value[0].id
    }
  } catch {
    globalError.value = 'Error al cargar los datos. Verifica la conexión con el servidor.'
  } finally {
    loading.value = false
  }
}

// ── CRUD Especies ──────────────────────────────────────────────────────────────
function selectEspecie(id: number) {
  selectedEspecieId.value = id
  // Resetear estados de razas al cambiar especie
  editRazaId.value  = null
  deleteRazaId.value = null
  showAddRaza.value  = false
  newRazaNombre.value = ''
  razaError.value    = null
}

function startEditEspecie(e: Especie) {
  editEspecieId.value     = e.id
  editEspecieNombre.value = e.nombre
  especieError.value      = null
  deleteEspecieId.value   = null
}

function cancelEditEspecie() {
  editEspecieId.value    = null
  editEspecieNombre.value = ''
}

async function saveEspecie() {
  const nombre = editEspecieNombre.value.trim()
  if (!nombre) return
  especieSaving.value = true
  especieError.value  = null
  try {
    const res = await especieService.update(editEspecieId.value!, { nombre })
    const idx = especies.value.findIndex(e => e.id === editEspecieId.value)
    if (idx !== -1) especies.value[idx] = res.data
    cancelEditEspecie()
  } catch {
    especieError.value = 'No se pudo guardar. Intenta de nuevo.'
  } finally {
    especieSaving.value = false
  }
}

async function openAddEspecie() {
  showAddEspecie.value  = true
  newEspecieNombre.value = ''
  especieError.value    = null
  await nextTick()
  addEspecieInput.value?.$el?.focus()
}

async function createEspecie() {
  const nombre = newEspecieNombre.value.trim()
  if (!nombre) return
  especieSaving.value = true
  especieError.value  = null
  try {
    const res = await especieService.create({ nombre })
    especies.value.push(res.data)
    selectedEspecieId.value = res.data.id
    showAddEspecie.value    = false
    newEspecieNombre.value  = ''
  } catch {
    especieError.value = 'No se pudo crear la especie.'
  } finally {
    especieSaving.value = false
  }
}

async function confirmDeleteEspecie(id: number) {
  especieError.value = null
  try {
    await especieService.delete(id)
    razas.value    = razas.value.filter(r => r.especie !== id)
    especies.value = especies.value.filter(e => e.id !== id)
    if (selectedEspecieId.value === id) {
      selectedEspecieId.value = especies.value[0]?.id ?? null
    }
    deleteEspecieId.value = null
  } catch {
    especieError.value = 'No se pudo eliminar. Puede que tenga pacientes asociados.'
    deleteEspecieId.value = null
  }
}

// ── CRUD Razas ────────────────────────────────────────────────────────────────
function startEditRaza(r: Raza) {
  editRazaId.value     = r.id
  editRazaNombre.value = r.nombre
  razaError.value      = null
  deleteRazaId.value   = null
}

function cancelEditRaza() {
  editRazaId.value    = null
  editRazaNombre.value = ''
}

async function saveRaza() {
  const nombre = editRazaNombre.value.trim()
  if (!nombre || !selectedEspecieId.value) return
  razaSaving.value = true
  razaError.value  = null
  try {
    const res = await razaService.update(editRazaId.value!, { nombre, especie: selectedEspecieId.value })
    const idx = razas.value.findIndex(r => r.id === editRazaId.value)
    if (idx !== -1) razas.value[idx] = res.data
    cancelEditRaza()
  } catch {
    razaError.value = 'No se pudo guardar. Intenta de nuevo.'
  } finally {
    razaSaving.value = false
  }
}

async function openAddRaza() {
  showAddRaza.value  = true
  newRazaNombre.value = ''
  razaError.value    = null
  await nextTick()
  addRazaInput.value?.$el?.focus()
}

async function createRaza() {
  const nombre = newRazaNombre.value.trim()
  if (!nombre || !selectedEspecieId.value) return
  razaSaving.value = true
  razaError.value  = null
  try {
    const res = await razaService.create({ nombre, especie: selectedEspecieId.value })
    razas.value.push(res.data)
    showAddRaza.value   = false
    newRazaNombre.value = ''
  } catch {
    razaError.value = 'No se pudo crear la raza.'
  } finally {
    razaSaving.value = false
  }
}

async function confirmDeleteRaza(id: number) {
  razaError.value = null
  try {
    await razaService.delete(id)
    razas.value       = razas.value.filter(r => r.id !== id)
    deleteRazaId.value = null
  } catch {
    razaError.value    = 'No se pudo eliminar. Puede que tenga pacientes asociados.'
    deleteRazaId.value = null
  }
}

onMounted(loadAll)
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
              <BreadcrumbPage>Especies &amp; Razas</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6">

        <!-- Título -->
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <PawPrint class="h-5 w-5" />
          </div>
          <div>
            <h1 class="text-2xl font-bold leading-tight">Gestión de Especies &amp; Razas</h1>
            <p class="text-sm text-muted-foreground">
              Gestiona las especies y sus razas en un solo lugar.
            </p>
          </div>
        </div>

        <!-- Error global -->
        <div v-if="globalError" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ globalError }}
        </div>

        <!-- Skeleton de carga -->
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-[280px_1fr] gap-4">
          <div class="rounded-xl border bg-white p-4 space-y-3">
            <Skeleton class="h-6 w-32" />
            <Skeleton class="h-10 w-full" v-for="n in 4" :key="n" />
          </div>
          <div class="rounded-xl border bg-white p-4 space-y-3">
            <Skeleton class="h-6 w-40" />
            <Skeleton class="h-10 w-full" v-for="n in 5" :key="n" />
          </div>
        </div>

        <!-- Contenido principal (dos columnas) -->
        <div v-else class="grid grid-cols-1 md:grid-cols-[300px_1fr] gap-4 items-start">

          <!-- ─── Panel Izquierdo: Especies ───────────────────────────────── -->
          <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

            <!-- Cabecera del panel -->
            <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
              <div class="flex items-center gap-2">
                <PawPrint class="h-4 w-4 text-primary" />
                <span class="font-semibold text-sm">Especies</span>
                <Badge variant="secondary">{{ especies.length }}</Badge>
              </div>
              <Button size="sm" variant="ghost" class="gap-1 h-7 text-xs" @click="openAddEspecie">
                <Plus class="h-3.5 w-3.5" />
                Nueva
              </Button>
            </div>

            <!-- Error de especie -->
            <div v-if="especieError" class="mx-3 mt-2 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
              <AlertCircle class="h-3.5 w-3.5 shrink-0" />
              {{ especieError }}
              <button class="ml-auto" @click="especieError = null"><X class="h-3 w-3" /></button>
            </div>

            <!-- Formulario nueva especie -->
            <div v-if="showAddEspecie" class="px-3 pt-3 pb-1">
              <div class="flex gap-2">
                <Input
                  ref="addEspecieInput"
                  v-model="newEspecieNombre"
                  placeholder="Nombre de la especie"
                  class="h-8 text-sm"
                  @keyup.enter="createEspecie"
                  @keyup.escape="showAddEspecie = false"
                />
                <Button size="sm" class="h-8 px-2" :disabled="especieSaving" @click="createEspecie">
                  <Loader2 v-if="especieSaving" class="h-3.5 w-3.5 animate-spin" />
                  <Check v-else class="h-3.5 w-3.5" />
                </Button>
                <Button size="sm" variant="ghost" class="h-8 px-2" @click="showAddEspecie = false">
                  <X class="h-3.5 w-3.5" />
                </Button>
              </div>
            </div>

            <!-- Lista de especies -->
            <ul class="py-1">
              <li
                v-if="especies.length === 0"
                class="px-4 py-6 text-center text-sm text-muted-foreground"
              >
                Sin especies. Agrega una.
              </li>

              <li
                v-for="esp in especies"
                :key="esp.id"
                @click="selectEspecie(esp.id)"
                class="group relative cursor-pointer px-3 py-2 transition-colors"
                :class="selectedEspecieId === esp.id
                  ? 'bg-primary/10 border-l-2 border-primary'
                  : 'hover:bg-muted/40 border-l-2 border-transparent'"
              >
                <!-- Modo edición -->
                <div v-if="editEspecieId === esp.id" class="flex gap-2" @click.stop>
                  <Input
                    v-model="editEspecieNombre"
                    class="h-7 text-sm"
                    @keyup.enter="saveEspecie"
                    @keyup.escape="cancelEditEspecie"
                    autofocus
                  />
                  <button
                    class="shrink-0 rounded p-1 text-green-600 hover:bg-green-50"
                    :disabled="especieSaving"
                    @click.stop="saveEspecie"
                    title="Guardar"
                  >
                    <Loader2 v-if="especieSaving" class="h-3.5 w-3.5 animate-spin" />
                    <Check v-else class="h-3.5 w-3.5" />
                  </button>
                  <button
                    class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted"
                    @click.stop="cancelEditEspecie"
                    title="Cancelar"
                  >
                    <X class="h-3.5 w-3.5" />
                  </button>
                </div>

                <!-- Modo confirmación de borrado -->
                <div v-else-if="deleteEspecieId === esp.id" class="flex items-center gap-2" @click.stop>
                  <span class="flex-1 text-sm text-red-600 font-medium">¿Eliminar «{{ esp.nombre }}»?</span>
                  <button
                    class="shrink-0 rounded p-1 bg-red-500 text-white hover:bg-red-600"
                    @click.stop="confirmDeleteEspecie(esp.id)"
                    title="Confirmar"
                  >
                    <Check class="h-3.5 w-3.5" />
                  </button>
                  <button
                    class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted"
                    @click.stop="deleteEspecieId = null"
                    title="Cancelar"
                  >
                    <X class="h-3.5 w-3.5" />
                  </button>
                </div>

                <!-- Vista normal -->
                <div v-else class="flex items-center gap-2">
                  <span class="flex-1 text-sm font-medium truncate">{{ esp.nombre }}</span>
                  <Badge variant="outline" class="text-xs px-1.5 py-0 shrink-0">
                    {{ countRazas(esp.id) }}
                  </Badge>
                  <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    <button
                      class="rounded p-1 text-muted-foreground hover:text-primary hover:bg-primary/10"
                      @click.stop="startEditEspecie(esp)"
                      title="Editar"
                    >
                      <Pencil class="h-3.5 w-3.5" />
                    </button>
                    <button
                      class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50"
                      @click.stop="deleteEspecieId = esp.id; especieError = null"
                      title="Eliminar"
                    >
                      <Trash2 class="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              </li>
            </ul>
          </div>

          <!-- ─── Panel Derecho: Razas ────────────────────────────────────── -->
          <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

            <!-- Cabecera del panel -->
            <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
              <div class="flex items-center gap-2">
                <Tag class="h-4 w-4 text-primary" />
                <span class="font-semibold text-sm">
                  Razas
                  <span v-if="selectedEspecie" class="font-normal text-muted-foreground">
                    — {{ selectedEspecie.nombre }}
                  </span>
                </span>
                <Badge variant="secondary">{{ razasDeEspecie.length }}</Badge>
              </div>
              <Button
                v-if="selectedEspecie"
                size="sm"
                variant="ghost"
                class="gap-1 h-7 text-xs"
                @click="openAddRaza"
              >
                <Plus class="h-3.5 w-3.5" />
                Nueva
              </Button>
            </div>

            <!-- Sin especie seleccionada -->
            <div v-if="!selectedEspecie" class="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground">
              <PawPrint class="h-10 w-10 opacity-20" />
              <p class="text-sm">Selecciona una especie para ver sus razas.</p>
            </div>

            <template v-else>
              <!-- Error de raza -->
              <div v-if="razaError" class="mx-3 mt-2 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
                <AlertCircle class="h-3.5 w-3.5 shrink-0" />
                {{ razaError }}
                <button class="ml-auto" @click="razaError = null"><X class="h-3 w-3" /></button>
              </div>

              <!-- Formulario nueva raza -->
              <div v-if="showAddRaza" class="px-3 pt-3 pb-1">
                <div class="flex gap-2">
                  <Input
                    ref="addRazaInput"
                    v-model="newRazaNombre"
                    :placeholder="`Nombre de la raza (${selectedEspecie.nombre})`"
                    class="h-8 text-sm"
                    @keyup.enter="createRaza"
                    @keyup.escape="showAddRaza = false"
                  />
                  <Button size="sm" class="h-8 px-2" :disabled="razaSaving" @click="createRaza">
                    <Loader2 v-if="razaSaving" class="h-3.5 w-3.5 animate-spin" />
                    <Check v-else class="h-3.5 w-3.5" />
                  </Button>
                  <Button size="sm" variant="ghost" class="h-8 px-2" @click="showAddRaza = false">
                    <X class="h-3.5 w-3.5" />
                  </Button>
                </div>
              </div>

              <!-- Lista de razas -->
              <ul class="py-1 divide-y divide-border/50">
                <li
                  v-if="razasDeEspecie.length === 0"
                  class="px-4 py-8 text-center text-sm text-muted-foreground"
                >
                  Sin razas registradas para <strong>{{ selectedEspecie.nombre }}</strong>. Agrega la primera.
                </li>

                <li
                  v-for="raza in razasDeEspecie"
                  :key="raza.id"
                  class="group px-4 py-2.5 hover:bg-muted/30 transition-colors"
                >
                  <!-- Modo edición -->
                  <div v-if="editRazaId === raza.id" class="flex gap-2">
                    <Input
                      v-model="editRazaNombre"
                      class="h-7 text-sm"
                      @keyup.enter="saveRaza"
                      @keyup.escape="cancelEditRaza"
                      autofocus
                    />
                    <button
                      class="shrink-0 rounded p-1 text-green-600 hover:bg-green-50"
                      :disabled="razaSaving"
                      @click="saveRaza"
                      title="Guardar"
                    >
                      <Loader2 v-if="razaSaving" class="h-3.5 w-3.5 animate-spin" />
                      <Check v-else class="h-3.5 w-3.5" />
                    </button>
                    <button
                      class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted"
                      @click="cancelEditRaza"
                      title="Cancelar"
                    >
                      <X class="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <!-- Modo confirmación de borrado -->
                  <div v-else-if="deleteRazaId === raza.id" class="flex items-center gap-2">
                    <span class="flex-1 text-sm text-red-600 font-medium">¿Eliminar «{{ raza.nombre }}»?</span>
                    <button
                      class="shrink-0 rounded p-1 bg-red-500 text-white hover:bg-red-600"
                      @click="confirmDeleteRaza(raza.id)"
                      title="Confirmar"
                    >
                      <Check class="h-3.5 w-3.5" />
                    </button>
                    <button
                      class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted"
                      @click="deleteRazaId = null"
                      title="Cancelar"
                    >
                      <X class="h-3.5 w-3.5" />
                    </button>
                  </div>

                  <!-- Vista normal -->
                  <div v-else class="flex items-center gap-2">
                    <span class="flex-1 text-sm">{{ raza.nombre }}</span>
                    <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        class="rounded p-1 text-muted-foreground hover:text-primary hover:bg-primary/10"
                        @click="startEditRaza(raza)"
                        title="Editar"
                      >
                        <Pencil class="h-3.5 w-3.5" />
                      </button>
                      <button
                        class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50"
                        @click="deleteRazaId = raza.id; razaError = null"
                        title="Eliminar"
                      >
                        <Trash2 class="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                </li>
              </ul>
            </template>
          </div>

        </div>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
