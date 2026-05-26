<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import {
  catalogoService, examenService, parametroService, valorReferenciaService,
  type CatalogoExamen, type Examen, type Parametro, type ValorReferencia,
} from '@/services/catalogoService'
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
  Loader2, AlertCircle, FlaskConical, BookOpen, SlidersHorizontal, Ruler,
  ChevronDown, ChevronRight,
} from 'lucide-vue-next'

// ── Carga ──────────────────────────────────────────────────────────────────────
const loading     = ref(true)
const globalError = ref<string | null>(null)

// ── CatalogoExamen ─────────────────────────────────────────────────────────────
const catalogos       = ref<CatalogoExamen[]>([])
const selectedCatId   = ref<number | null>(null)
const catError        = ref<string | null>(null)
const catSaving       = ref(false)

// add form
const showAddCat      = ref(false)
const addCatNombre    = ref('')
const addCatArea      = ref('')
const addCatPrecio    = ref('')

// edit
const editCatId       = ref<number | null>(null)
const editCatNombre   = ref('')
const editCatArea     = ref('')
const editCatPrecio   = ref('')
const deleteCatId     = ref<number | null>(null)

const selectedCat = computed(() => catalogos.value.find(c => c.id === selectedCatId.value) ?? null)
const countExamenes = (id: number) => examenes.value.filter(e => e.catalogo === id).length

// ── Examen ─────────────────────────────────────────────────────────────────────
const examenes        = ref<Examen[]>([])
const selectedExId    = ref<number | null>(null)
const exError         = ref<string | null>(null)
const exSaving        = ref(false)

const showAddEx       = ref(false)
const addExNombre     = ref('')
const addExCategoria  = ref('')
const addExDesc       = ref('')

const editExId        = ref<number | null>(null)
const editExNombre    = ref('')
const editExCategoria = ref('')
const editExDesc      = ref('')
const deleteExId      = ref<number | null>(null)

const selectedEx      = computed(() => examenes.value.find(e => e.id === selectedExId.value) ?? null)
const examenesDelCat  = computed(() => examenes.value.filter(e => e.catalogo === selectedCatId.value))
const countParametros = (id: number) => parametros.value.filter(p => p.examen === id).length

// ── Parametro ──────────────────────────────────────────────────────────────────
const parametros       = ref<Parametro[]>([])
const selectedParId    = ref<number | null>(null)
const parError         = ref<string | null>(null)
const parSaving        = ref(false)

const showAddPar       = ref(false)
const addParNombre     = ref('')
const addParUnidad     = ref('')

const editParId        = ref<number | null>(null)
const editParNombre    = ref('')
const editParUnidad    = ref('')
const deleteParId      = ref<number | null>(null)

const parametrosDelEx  = computed(() => parametros.value.filter(p => p.examen === selectedExId.value))
const countValores     = (id: number) => valores.value.filter(v => v.parametro === id).length

// ── ValorReferencia ────────────────────────────────────────────────────────────
const valores          = ref<ValorReferencia[]>([])
const valError         = ref<string | null>(null)
const valSaving        = ref(false)

const showAddVal       = ref(false)
const addValMin        = ref('')
const addValMax        = ref('')
const addValEspecie    = ref('')

const editValId        = ref<number | null>(null)
const editValMin       = ref('')
const editValMax       = ref('')
const editValEspecie   = ref('')
const deleteValId      = ref<number | null>(null)

const expandedParIds   = ref<Set<number>>(new Set())
const valoresDelPar    = (id: number) => valores.value.filter(v => v.parametro === id)

function togglePar(id: number) {
  if (expandedParIds.value.has(id)) {
    expandedParIds.value.delete(id)
    if (selectedParId.value === id) {
      selectedParId.value = null
      showAddVal.value = false
    }
  } else {
    expandedParIds.value.add(id)
    selectedParId.value = id
  }
}

// ── Carga inicial ──────────────────────────────────────────────────────────────
async function loadAll() {
  loading.value = true
  globalError.value = null
  try {
    const [rc, re, rp, rv] = await Promise.all([
      catalogoService.getAll(),
      examenService.getAll(),
      parametroService.getAll(),
      valorReferenciaService.getAll(),
    ])
    catalogos.value  = (rc.data as any).resultados ?? (rc.data as any).results ?? rc.data
    examenes.value   = (re.data as any).resultados ?? (re.data as any).results ?? re.data
    parametros.value = (rp.data as any).resultados ?? (rp.data as any).results ?? rp.data
    valores.value    = (rv.data as any).resultados ?? (rv.data as any).results ?? rv.data
    if (catalogos.value.length && !selectedCatId.value) {
      selectedCatId.value = catalogos.value[0].id
    }
  } catch {
    globalError.value = 'Error al cargar los datos. Verifica la conexión con el servidor.'
  } finally {
    loading.value = false
  }
}

// ── CRUD CatalogoExamen ────────────────────────────────────────────────────────
function selectCat(id: number) {
  selectedCatId.value = id
  selectedExId.value  = null
  selectedParId.value = null
  showAddEx.value     = false
  showAddPar.value    = false
  showAddVal.value    = false
  editExId.value      = null
  deleteExId.value    = null
  exError.value       = null
}

function startEditCat(c: CatalogoExamen) {
  editCatId.value     = c.id
  editCatNombre.value = c.nombre
  editCatArea.value   = c.area ?? ''
  editCatPrecio.value = c.precio ?? ''
  catError.value      = null
  deleteCatId.value   = null
}
function cancelEditCat() { editCatId.value = null }

async function saveCat() {
  const nombre = editCatNombre.value.trim()
  if (!nombre) return
  catSaving.value = true; catError.value = null
  try {
    const res = await catalogoService.update(editCatId.value!, {
      nombre,
      area: editCatArea.value.trim() || null,
      precio: editCatPrecio.value.trim() || null,
    })
    const idx = catalogos.value.findIndex(c => c.id === editCatId.value)
    if (idx !== -1) catalogos.value[idx] = res.data
    cancelEditCat()
  } catch { catError.value = 'No se pudo guardar.' }
  finally   { catSaving.value = false }
}

async function openAddCat() {
  showAddCat.value  = true
  addCatNombre.value = ''; addCatArea.value = ''; addCatPrecio.value = ''
  catError.value    = null
  await nextTick()
  document.getElementById('add-cat-nombre')?.focus()
}

async function createCat() {
  const nombre = addCatNombre.value.trim()
  if (!nombre) return
  catSaving.value = true; catError.value = null
  try {
    const res = await catalogoService.create({
      nombre,
      area: addCatArea.value.trim() || null,
      precio: addCatPrecio.value.trim() || null,
    })
    catalogos.value.push(res.data)
    selectedCatId.value = res.data.id
    showAddCat.value    = false
  } catch { catError.value = 'No se pudo crear el catálogo.' }
  finally   { catSaving.value = false }
}

async function confirmDeleteCat(id: number) {
  catError.value = null
  try {
    await catalogoService.delete(id)
    examenes.value  = examenes.value.filter(e => e.catalogo !== id)
    catalogos.value = catalogos.value.filter(c => c.id !== id)
    if (selectedCatId.value === id) {
      selectedCatId.value = catalogos.value[0]?.id ?? null
      selectedExId.value  = null
    }
    deleteCatId.value = null
  } catch { catError.value = 'No se pudo eliminar. Puede tener exámenes asociados.' }
}

// ── CRUD Examen ────────────────────────────────────────────────────────────────
function selectEx(id: number) {
  selectedExId.value  = id
  selectedParId.value = null
  showAddPar.value    = false
  showAddVal.value    = false
  editParId.value     = null
  deleteParId.value   = null
  parError.value      = null
  expandedParIds.value.clear()
}

function startEditEx(e: Examen) {
  editExId.value       = e.id
  editExNombre.value   = e.nombre_examen
  editExCategoria.value = e.categoria ?? ''
  editExDesc.value     = e.descripcion ?? ''
  exError.value        = null
  deleteExId.value     = null
}
function cancelEditEx() { editExId.value = null }

async function saveEx() {
  const nombre = editExNombre.value.trim()
  if (!nombre || !selectedCatId.value) return
  exSaving.value = true; exError.value = null
  try {
    const res = await examenService.update(editExId.value!, {
      nombre_examen: nombre,
      categoria: editExCategoria.value.trim() || null,
      descripcion: editExDesc.value.trim() || null,
      catalogo: selectedCatId.value,
    })
    const idx = examenes.value.findIndex(e => e.id === editExId.value)
    if (idx !== -1) examenes.value[idx] = res.data
    cancelEditEx()
  } catch { exError.value = 'No se pudo guardar.' }
  finally   { exSaving.value = false }
}

async function openAddEx() {
  showAddEx.value     = true
  addExNombre.value   = ''; addExCategoria.value = ''; addExDesc.value = ''
  exError.value       = null
  await nextTick()
  document.getElementById('add-ex-nombre')?.focus()
}

async function createEx() {
  const nombre = addExNombre.value.trim()
  if (!nombre || !selectedCatId.value) return
  exSaving.value = true; exError.value = null
  try {
    const res = await examenService.create({
      nombre_examen: nombre,
      categoria: addExCategoria.value.trim() || null,
      descripcion: addExDesc.value.trim() || null,
      catalogo: selectedCatId.value,
    })
    examenes.value.push(res.data)
    selectedExId.value = res.data.id
    showAddEx.value    = false
  } catch { exError.value = 'No se pudo crear el examen.' }
  finally   { exSaving.value = false }
}

async function confirmDeleteEx(id: number) {
  exError.value = null
  try {
    await examenService.delete(id)
    parametros.value = parametros.value.filter(p => p.examen !== id)
    examenes.value   = examenes.value.filter(e => e.id !== id)
    if (selectedExId.value === id) {
      selectedExId.value = null; selectedParId.value = null
    }
    deleteExId.value = null
  } catch { exError.value = 'No se pudo eliminar. Puede tener parámetros asociados.' }
}

// ── CRUD Parametro ─────────────────────────────────────────────────────────────
function startEditPar(p: Parametro) {
  editParId.value     = p.id
  editParNombre.value = p.nombre_parametro
  editParUnidad.value = p.unidad_medida ?? ''
  parError.value      = null
  deleteParId.value   = null
}
function cancelEditPar() { editParId.value = null }

async function savePar() {
  const nombre = editParNombre.value.trim()
  if (!nombre || !selectedExId.value) return
  parSaving.value = true; parError.value = null
  try {
    const res = await parametroService.update(editParId.value!, {
      nombre_parametro: nombre,
      unidad_medida: editParUnidad.value.trim() || null,
      examen: selectedExId.value,
    })
    const idx = parametros.value.findIndex(p => p.id === editParId.value)
    if (idx !== -1) parametros.value[idx] = res.data
    cancelEditPar()
  } catch { parError.value = 'No se pudo guardar.' }
  finally   { parSaving.value = false }
}

async function openAddPar() {
  showAddPar.value    = true
  addParNombre.value  = ''; addParUnidad.value = ''
  parError.value      = null
  await nextTick()
  document.getElementById('add-par-nombre')?.focus()
}

async function createPar() {
  const nombre = addParNombre.value.trim()
  if (!nombre || !selectedExId.value) return
  parSaving.value = true; parError.value = null
  try {
    const res = await parametroService.create({
      nombre_parametro: nombre,
      unidad_medida: addParUnidad.value.trim() || null,
      examen: selectedExId.value,
    })
    parametros.value.push(res.data)
    showAddPar.value = false
  } catch { parError.value = 'No se pudo crear el parámetro.' }
  finally   { parSaving.value = false }
}

async function confirmDeletePar(id: number) {
  parError.value = null
  try {
    await parametroService.delete(id)
    valores.value    = valores.value.filter(v => v.parametro !== id)
    parametros.value = parametros.value.filter(p => p.id !== id)
    if (selectedParId.value === id) selectedParId.value = null
    expandedParIds.value.delete(id)
    deleteParId.value = null
  } catch { parError.value = 'No se pudo eliminar.' }
}

// ── CRUD ValorReferencia ───────────────────────────────────────────────────────
async function openAddVal(parId: number) {
  selectedParId.value = parId
  expandedParIds.value.add(parId)
  showAddVal.value    = true
  addValMin.value     = ''; addValMax.value = ''; addValEspecie.value = ''
  valError.value      = null
  await nextTick()
  document.getElementById(`add-val-especie-${parId}`)?.focus()
}

function startEditVal(v: ValorReferencia) {
  editValId.value      = v.id
  editValMin.value     = v.valor_min ?? ''
  editValMax.value     = v.valor_max ?? ''
  editValEspecie.value = v.especie ?? ''
  valError.value       = null
  deleteValId.value    = null
}
function cancelEditVal() { editValId.value = null }

async function saveVal() {
  if (!selectedParId.value) return
  valSaving.value = true; valError.value = null
  try {
    const res = await valorReferenciaService.update(editValId.value!, {
      valor_min: editValMin.value.trim() || null,
      valor_max: editValMax.value.trim() || null,
      especie: editValEspecie.value.trim() || null,
      parametro: selectedParId.value,
    })
    const idx = valores.value.findIndex(v => v.id === editValId.value)
    if (idx !== -1) valores.value[idx] = res.data
    cancelEditVal()
  } catch { valError.value = 'No se pudo guardar.' }
  finally   { valSaving.value = false }
}

async function createVal() {
  if (!selectedParId.value) return
  valSaving.value = true; valError.value = null
  try {
    const res = await valorReferenciaService.create({
      valor_min: addValMin.value.trim() || null,
      valor_max: addValMax.value.trim() || null,
      especie: addValEspecie.value.trim() || null,
      parametro: selectedParId.value,
    })
    valores.value.push(res.data)
    showAddVal.value = false
  } catch { valError.value = 'No se pudo crear el valor.' }
  finally   { valSaving.value = false }
}

async function confirmDeleteVal(id: number) {
  valError.value = null
  try {
    await valorReferenciaService.delete(id)
    valores.value  = valores.value.filter(v => v.id !== id)
    deleteValId.value = null
  } catch { valError.value = 'No se pudo eliminar.' }
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
              <BreadcrumbPage>Catálogo de Exámenes</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6">

        <!-- Título -->
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <BookOpen class="h-5 w-5" />
          </div>
          <div>
            <h1 class="text-2xl font-bold leading-tight">Catálogo de Exámenes</h1>
            <p class="text-sm text-muted-foreground">
              Gestiona catálogos, exámenes, parámetros y valores de referencia.
            </p>
          </div>
        </div>

        <!-- Error global -->
        <div v-if="globalError" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ globalError }}
        </div>

        <!-- Skeleton -->
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="rounded-xl border bg-white p-4 space-y-3" v-for="n in 3" :key="n">
            <Skeleton class="h-6 w-32" />
            <Skeleton class="h-10 w-full" v-for="i in 4" :key="i" />
          </div>
        </div>

        <!-- Contenido principal — 3 columnas -->
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">

          <!-- ═══════════════════════════════════════════════════════════════
               COL 1 — Catálogos
          ══════════════════════════════════════════════════════════════════ -->
          <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

            <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
              <div class="flex items-center gap-2">
                <BookOpen class="h-4 w-4 text-primary" />
                <span class="font-semibold text-sm">Catálogos</span>
                <Badge variant="secondary">{{ catalogos.length }}</Badge>
              </div>
              <Button size="sm" variant="ghost" class="gap-1 h-7 text-xs" @click="openAddCat">
                <Plus class="h-3.5 w-3.5" /> Nuevo
              </Button>
            </div>

            <!-- Error catálogo -->
            <div v-if="catError" class="mx-3 mt-2 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
              <AlertCircle class="h-3.5 w-3.5 shrink-0" />
              {{ catError }}
              <button class="ml-auto" @click="catError = null"><X class="h-3 w-3" /></button>
            </div>

            <!-- Formulario agregar catálogo -->
            <div v-if="showAddCat" class="px-3 pt-3 pb-2 space-y-2 border-b">
              <Input id="add-cat-nombre" v-model="addCatNombre" placeholder="Nombre del catálogo *" class="h-8 text-sm" @keyup.escape="showAddCat = false" />
              <div class="flex gap-2">
                <Input v-model="addCatArea" placeholder="Área (ej. Hematología)" class="h-8 text-sm" />
                <Input v-model="addCatPrecio" placeholder="Precio (Bs.)" class="h-8 text-sm w-28" />
              </div>
              <div class="flex gap-2 justify-end">
                <Button size="sm" class="h-7 px-3 text-xs" :disabled="catSaving" @click="createCat">
                  <Loader2 v-if="catSaving" class="h-3.5 w-3.5 animate-spin mr-1" />
                  <Check v-else class="h-3.5 w-3.5 mr-1" />
                  Guardar
                </Button>
                <Button size="sm" variant="ghost" class="h-7 px-3 text-xs" @click="showAddCat = false">Cancelar</Button>
              </div>
            </div>

            <!-- Lista catálogos -->
            <ul class="py-1">
              <li v-if="catalogos.length === 0" class="px-4 py-6 text-center text-sm text-muted-foreground">Sin catálogos.</li>

              <li
                v-for="cat in catalogos"
                :key="cat.id"
                @click="selectCat(cat.id)"
                class="group relative cursor-pointer px-3 py-2 transition-colors"
                :class="selectedCatId === cat.id
                  ? 'bg-primary/10 border-l-2 border-primary'
                  : 'hover:bg-muted/40 border-l-2 border-transparent'"
              >
                <!-- Edición -->
                <div v-if="editCatId === cat.id" class="space-y-1.5" @click.stop>
                  <Input v-model="editCatNombre" placeholder="Nombre *" class="h-7 text-sm" autofocus @keyup.escape="cancelEditCat" />
                  <div class="flex gap-1.5">
                    <Input v-model="editCatArea" placeholder="Área" class="h-7 text-sm" />
                    <Input v-model="editCatPrecio" placeholder="Precio" class="h-7 text-sm w-24" />
                  </div>
                  <div class="flex gap-1 justify-end">
                    <button class="rounded px-2 py-1 text-xs bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-1" :disabled="catSaving" @click.stop="saveCat">
                      <Loader2 v-if="catSaving" class="h-3 w-3 animate-spin" /><Check v-else class="h-3 w-3" /> Guardar
                    </button>
                    <button class="rounded px-2 py-1 text-xs bg-muted hover:bg-muted/70" @click.stop="cancelEditCat">Cancelar</button>
                  </div>
                </div>

                <!-- Confirmación borrado -->
                <div v-else-if="deleteCatId === cat.id" class="flex items-center gap-2" @click.stop>
                  <span class="flex-1 text-xs text-red-600 font-medium">¿Eliminar «{{ cat.nombre }}»?</span>
                  <button class="shrink-0 rounded p-1 bg-red-500 text-white hover:bg-red-600" @click.stop="confirmDeleteCat(cat.id)"><Check class="h-3.5 w-3.5" /></button>
                  <button class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted" @click.stop="deleteCatId = null"><X class="h-3.5 w-3.5" /></button>
                </div>

                <!-- Normal -->
                <div v-else class="flex items-center gap-2">
                  <div class="flex-1 min-w-0">
                    <p class="text-sm font-medium truncate">{{ cat.nombre }}</p>
                    <p class="text-xs text-muted-foreground truncate">
                      <span v-if="cat.area">{{ cat.area }}</span>
                      <span v-if="cat.area && cat.precio"> · </span>
                      <span v-if="cat.precio">Bs. {{ cat.precio }}</span>
                    </p>
                  </div>
                  <Badge variant="outline" class="text-xs px-1.5 py-0 shrink-0">{{ countExamenes(cat.id) }}</Badge>
                  <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                    <button class="rounded p-1 text-muted-foreground hover:text-primary hover:bg-primary/10" @click.stop="startEditCat(cat)" title="Editar"><Pencil class="h-3.5 w-3.5" /></button>
                    <button class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50" @click.stop="deleteCatId = cat.id; catError = null" title="Eliminar"><Trash2 class="h-3.5 w-3.5" /></button>
                  </div>
                </div>
              </li>
            </ul>
          </div>

          <!-- ═══════════════════════════════════════════════════════════════
               COL 2 — Exámenes
          ══════════════════════════════════════════════════════════════════ -->
          <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

            <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
              <div class="flex items-center gap-2">
                <FlaskConical class="h-4 w-4 text-primary" />
                <span class="font-semibold text-sm">
                  Exámenes
                  <span v-if="selectedCat" class="font-normal text-muted-foreground">— {{ selectedCat.nombre }}</span>
                </span>
                <Badge variant="secondary">{{ examenesDelCat.length }}</Badge>
              </div>
              <Button v-if="selectedCat" size="sm" variant="ghost" class="gap-1 h-7 text-xs" @click="openAddEx">
                <Plus class="h-3.5 w-3.5" /> Nuevo
              </Button>
            </div>

            <div v-if="!selectedCat" class="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground">
              <BookOpen class="h-10 w-10 opacity-20" />
              <p class="text-sm">Selecciona un catálogo.</p>
            </div>

            <template v-else>
              <!-- Error examen -->
              <div v-if="exError" class="mx-3 mt-2 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
                <AlertCircle class="h-3.5 w-3.5 shrink-0" />{{ exError }}
                <button class="ml-auto" @click="exError = null"><X class="h-3 w-3" /></button>
              </div>

              <!-- Formulario agregar examen -->
              <div v-if="showAddEx" class="px-3 pt-3 pb-2 space-y-2 border-b">
                <Input id="add-ex-nombre" v-model="addExNombre" placeholder="Nombre del examen *" class="h-8 text-sm" @keyup.escape="showAddEx = false" />
                <Input v-model="addExCategoria" placeholder="Categoría (opcional)" class="h-8 text-sm" />
                <Input v-model="addExDesc" placeholder="Descripción (opcional)" class="h-8 text-sm" />
                <div class="flex gap-2 justify-end">
                  <Button size="sm" class="h-7 px-3 text-xs" :disabled="exSaving" @click="createEx">
                    <Loader2 v-if="exSaving" class="h-3.5 w-3.5 animate-spin mr-1" /><Check v-else class="h-3.5 w-3.5 mr-1" />Guardar
                  </Button>
                  <Button size="sm" variant="ghost" class="h-7 px-3 text-xs" @click="showAddEx = false">Cancelar</Button>
                </div>
              </div>

              <!-- Lista exámenes -->
              <ul class="py-1">
                <li v-if="examenesDelCat.length === 0" class="px-4 py-8 text-center text-sm text-muted-foreground">
                  Sin exámenes en <strong>{{ selectedCat.nombre }}</strong>.
                </li>

                <li
                  v-for="ex in examenesDelCat"
                  :key="ex.id"
                  @click="selectEx(ex.id)"
                  class="group relative cursor-pointer px-3 py-2 transition-colors"
                  :class="selectedExId === ex.id
                    ? 'bg-primary/10 border-l-2 border-primary'
                    : 'hover:bg-muted/40 border-l-2 border-transparent'"
                >
                  <!-- Edición -->
                  <div v-if="editExId === ex.id" class="space-y-1.5" @click.stop>
                    <Input v-model="editExNombre" placeholder="Nombre *" class="h-7 text-sm" autofocus @keyup.escape="cancelEditEx" />
                    <Input v-model="editExCategoria" placeholder="Categoría" class="h-7 text-sm" />
                    <Input v-model="editExDesc" placeholder="Descripción" class="h-7 text-sm" />
                    <div class="flex gap-1 justify-end">
                      <button class="rounded px-2 py-1 text-xs bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-1" :disabled="exSaving" @click.stop="saveEx">
                        <Loader2 v-if="exSaving" class="h-3 w-3 animate-spin" /><Check v-else class="h-3 w-3" /> Guardar
                      </button>
                      <button class="rounded px-2 py-1 text-xs bg-muted hover:bg-muted/70" @click.stop="cancelEditEx">Cancelar</button>
                    </div>
                  </div>

                  <!-- Confirmación borrado -->
                  <div v-else-if="deleteExId === ex.id" class="flex items-center gap-2" @click.stop>
                    <span class="flex-1 text-xs text-red-600 font-medium">¿Eliminar «{{ ex.nombre_examen }}»?</span>
                    <button class="shrink-0 rounded p-1 bg-red-500 text-white hover:bg-red-600" @click.stop="confirmDeleteEx(ex.id)"><Check class="h-3.5 w-3.5" /></button>
                    <button class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted" @click.stop="deleteExId = null"><X class="h-3.5 w-3.5" /></button>
                  </div>

                  <!-- Normal -->
                  <div v-else class="flex items-center gap-2">
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium truncate">{{ ex.nombre_examen }}</p>
                      <p v-if="ex.categoria" class="text-xs text-muted-foreground truncate">{{ ex.categoria }}</p>
                    </div>
                    <Badge variant="outline" class="text-xs px-1.5 py-0 shrink-0">{{ countParametros(ex.id) }}</Badge>
                    <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
                      <button class="rounded p-1 text-muted-foreground hover:text-primary hover:bg-primary/10" @click.stop="startEditEx(ex)" title="Editar"><Pencil class="h-3.5 w-3.5" /></button>
                      <button class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50" @click.stop="deleteExId = ex.id; exError = null" title="Eliminar"><Trash2 class="h-3.5 w-3.5" /></button>
                    </div>
                  </div>
                </li>
              </ul>
            </template>
          </div>

          <!-- ═══════════════════════════════════════════════════════════════
               COL 3 — Parámetros & Valores de Referencia
          ══════════════════════════════════════════════════════════════════ -->
          <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

            <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
              <div class="flex items-center gap-2">
                <SlidersHorizontal class="h-4 w-4 text-primary" />
                <span class="font-semibold text-sm">
                  Parámetros
                  <span v-if="selectedEx" class="font-normal text-muted-foreground">— {{ selectedEx.nombre_examen }}</span>
                </span>
                <Badge variant="secondary">{{ parametrosDelEx.length }}</Badge>
              </div>
              <Button v-if="selectedEx" size="sm" variant="ghost" class="gap-1 h-7 text-xs" @click="openAddPar">
                <Plus class="h-3.5 w-3.5" /> Nuevo
              </Button>
            </div>

            <div v-if="!selectedEx" class="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground">
              <FlaskConical class="h-10 w-10 opacity-20" />
              <p class="text-sm">Selecciona un examen.</p>
            </div>

            <template v-else>
              <!-- Error parámetro -->
              <div v-if="parError" class="mx-3 mt-2 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
                <AlertCircle class="h-3.5 w-3.5 shrink-0" />{{ parError }}
                <button class="ml-auto" @click="parError = null"><X class="h-3 w-3" /></button>
              </div>

              <!-- Formulario agregar parámetro -->
              <div v-if="showAddPar" class="px-3 pt-3 pb-2 space-y-2 border-b">
                <div class="flex gap-2">
                  <Input id="add-par-nombre" v-model="addParNombre" placeholder="Nombre del parámetro *" class="h-8 text-sm" @keyup.escape="showAddPar = false" />
                  <Input v-model="addParUnidad" placeholder="Unidad" class="h-8 text-sm w-28" />
                </div>
                <div class="flex gap-2 justify-end">
                  <Button size="sm" class="h-7 px-3 text-xs" :disabled="parSaving" @click="createPar">
                    <Loader2 v-if="parSaving" class="h-3.5 w-3.5 animate-spin mr-1" /><Check v-else class="h-3.5 w-3.5 mr-1" />Guardar
                  </Button>
                  <Button size="sm" variant="ghost" class="h-7 px-3 text-xs" @click="showAddPar = false">Cancelar</Button>
                </div>
              </div>

              <!-- Lista parámetros -->
              <ul class="py-1 divide-y divide-border/40">
                <li v-if="parametrosDelEx.length === 0" class="px-4 py-8 text-center text-sm text-muted-foreground">
                  Sin parámetros en <strong>{{ selectedEx.nombre_examen }}</strong>.
                </li>

                <li v-for="par in parametrosDelEx" :key="par.id" class="group">

                  <!-- Edición del parámetro -->
                  <div v-if="editParId === par.id" class="px-3 py-2 space-y-1.5">
                    <div class="flex gap-2">
                      <Input v-model="editParNombre" placeholder="Nombre *" class="h-7 text-sm" autofocus @keyup.escape="cancelEditPar" />
                      <Input v-model="editParUnidad" placeholder="Unidad" class="h-7 text-sm w-24" />
                    </div>
                    <div class="flex gap-1 justify-end">
                      <button class="rounded px-2 py-1 text-xs bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-1" :disabled="parSaving" @click="savePar">
                        <Loader2 v-if="parSaving" class="h-3 w-3 animate-spin" /><Check v-else class="h-3 w-3" /> Guardar
                      </button>
                      <button class="rounded px-2 py-1 text-xs bg-muted hover:bg-muted/70" @click="cancelEditPar">Cancelar</button>
                    </div>
                  </div>

                  <!-- Confirmación borrado parámetro -->
                  <div v-else-if="deleteParId === par.id" class="px-3 py-2 flex items-center gap-2">
                    <span class="flex-1 text-xs text-red-600 font-medium">¿Eliminar «{{ par.nombre_parametro }}»?</span>
                    <button class="shrink-0 rounded p-1 bg-red-500 text-white hover:bg-red-600" @click="confirmDeletePar(par.id)"><Check class="h-3.5 w-3.5" /></button>
                    <button class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted" @click="deleteParId = null"><X class="h-3.5 w-3.5" /></button>
                  </div>

                  <!-- Vista normal parámetro -->
                  <div v-else>
                    <div
                      class="flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-muted/30 transition-colors"
                      @click="togglePar(par.id)"
                    >
                      <component :is="expandedParIds.has(par.id) ? ChevronDown : ChevronRight" class="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                      <div class="flex-1 min-w-0">
                        <p class="text-sm font-medium truncate">{{ par.nombre_parametro }}</p>
                        <p v-if="par.unidad_medida" class="text-xs text-muted-foreground">{{ par.unidad_medida }}</p>
                      </div>
                      <Badge variant="outline" class="text-xs px-1.5 py-0 shrink-0">{{ countValores(par.id) }}</Badge>
                      <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" @click.stop>
                        <button class="rounded p-1 text-muted-foreground hover:text-primary hover:bg-primary/10" @click="startEditPar(par)" title="Editar"><Pencil class="h-3.5 w-3.5" /></button>
                        <button class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50" @click="deleteParId = par.id; parError = null" title="Eliminar"><Trash2 class="h-3.5 w-3.5" /></button>
                      </div>
                    </div>

                    <!-- Valores de referencia (expandido) -->
                    <div v-if="expandedParIds.has(par.id)" class="bg-muted/20 border-t border-border/40 px-4 pb-2 pt-1">

                      <!-- Error valor -->
                      <div v-if="valError && selectedParId === par.id" class="mt-1 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs text-red-600">
                        <AlertCircle class="h-3.5 w-3.5 shrink-0" />{{ valError }}
                        <button class="ml-auto" @click="valError = null"><X class="h-3 w-3" /></button>
                      </div>

                      <!-- Lista valores -->
                      <ul class="mt-1 space-y-1">
                        <li v-if="valoresDelPar(par.id).length === 0 && !(showAddVal && selectedParId === par.id)"
                          class="text-xs text-muted-foreground py-1 italic">
                          Sin valores de referencia.
                        </li>

                        <li v-for="val in valoresDelPar(par.id)" :key="val.id">
                          <!-- Edición valor -->
                          <div v-if="editValId === val.id" class="flex flex-wrap gap-1.5 items-center py-1">
                            <Input v-model="editValEspecie" placeholder="Especie" class="h-7 text-xs w-24" autofocus />
                            <Input v-model="editValMin" placeholder="Mín" class="h-7 text-xs w-16" />
                            <Input v-model="editValMax" placeholder="Máx" class="h-7 text-xs w-16" />
                            <button class="rounded px-1.5 py-1 text-xs bg-primary text-primary-foreground flex items-center gap-0.5" :disabled="valSaving" @click="saveVal">
                              <Loader2 v-if="valSaving" class="h-3 w-3 animate-spin" /><Check v-else class="h-3 w-3" />
                            </button>
                            <button class="rounded px-1.5 py-1 text-xs bg-muted" @click="cancelEditVal"><X class="h-3 w-3" /></button>
                          </div>

                          <!-- Confirmación borrado valor -->
                          <div v-else-if="deleteValId === val.id" class="flex items-center gap-1.5 py-1">
                            <span class="flex-1 text-xs text-red-600">¿Eliminar valor?</span>
                            <button class="rounded p-1 bg-red-500 text-white hover:bg-red-600" @click="confirmDeleteVal(val.id)"><Check class="h-3 w-3" /></button>
                            <button class="rounded p-1 bg-muted" @click="deleteValId = null"><X class="h-3 w-3" /></button>
                          </div>

                          <!-- Normal valor -->
                          <div v-else class="group/val flex items-center gap-2 rounded px-1 py-0.5 hover:bg-background/60 transition-colors">
                            <Ruler class="h-3 w-3 text-muted-foreground shrink-0" />
                            <span class="flex-1 text-xs">
                              <span v-if="val.especie" class="font-medium">{{ val.especie }}: </span>
                              {{ val.valor_min ?? '—' }} – {{ val.valor_max ?? '—' }}
                            </span>
                            <div class="flex gap-0.5 opacity-0 group-hover/val:opacity-100 transition-opacity">
                              <button class="rounded p-0.5 text-muted-foreground hover:text-primary hover:bg-primary/10" @click="startEditVal(val); selectedParId = par.id"><Pencil class="h-3 w-3" /></button>
                              <button class="rounded p-0.5 text-muted-foreground hover:text-red-500 hover:bg-red-50" @click="deleteValId = val.id; valError = null"><Trash2 class="h-3 w-3" /></button>
                            </div>
                          </div>
                        </li>
                      </ul>

                      <!-- Formulario agregar valor -->
                      <div v-if="showAddVal && selectedParId === par.id" class="mt-2 space-y-1.5">
                        <div class="flex flex-wrap gap-1.5">
                          <Input :id="`add-val-especie-${par.id}`" v-model="addValEspecie" placeholder="Especie" class="h-7 text-xs w-28" @keyup.escape="showAddVal = false" />
                          <Input v-model="addValMin" placeholder="Mín" class="h-7 text-xs w-16" />
                          <Input v-model="addValMax" placeholder="Máx" class="h-7 text-xs w-16" />
                        </div>
                        <div class="flex gap-1.5">
                          <Button size="sm" class="h-6 px-2 text-xs" :disabled="valSaving" @click="createVal">
                            <Loader2 v-if="valSaving" class="h-3 w-3 animate-spin mr-1" />Guardar
                          </Button>
                          <Button size="sm" variant="ghost" class="h-6 px-2 text-xs" @click="showAddVal = false">Cancelar</Button>
                        </div>
                      </div>

                      <!-- Botón agregar valor -->
                      <button
                        v-if="!(showAddVal && selectedParId === par.id)"
                        class="mt-1.5 flex items-center gap-1 text-xs text-muted-foreground hover:text-primary transition-colors"
                        @click.stop="openAddVal(par.id)"
                      >
                        <Plus class="h-3 w-3" /> Agregar valor de referencia
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
