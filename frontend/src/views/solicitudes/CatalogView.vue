<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
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
import { Skeleton } from '@/components/ui/skeleton'
import { AlertCircle, BookOpen } from 'lucide-vue-next'

import CatalogoList  from './CatalogoList.vue'
import ExamenView    from './ExamenView.vue'
import ParametroView from './ParametroView.vue'

// ── Carga ──────────────────────────────────────────────────────────────────────
const loading     = ref(true)
const globalError = ref<string | null>(null)

// ── Estado global compartido ───────────────────────────────────────────────────
const catalogos  = ref<CatalogoExamen[]>([])
const examenes   = ref<Examen[]>([])
const parametros = ref<Parametro[]>([])
const valores    = ref<ValorReferencia[]>([])

const selectedCatId = ref<number | null>(null)
const selectedExId  = ref<number | null>(null)

// ── Derivados ──────────────────────────────────────────────────────────────────
const selectedCat    = computed(() => catalogos.value.find(c => c.id === selectedCatId.value) ?? null)
const selectedEx     = computed(() => examenes.value.find(e => e.id === selectedExId.value)   ?? null)
const examenesDelCat = computed(() => examenes.value.filter(e => e.catalogo === selectedCatId.value))
const parametrosDelEx = computed(() => parametros.value.filter(p => p.examen === selectedExId.value))

const countExamenes  = (id: number) => examenes.value.filter(e => e.catalogo === id).length
const countParametros = (id: number) => parametros.value.filter(p => p.examen === id).length
const countValores    = (id: number) => valores.value.filter(v => v.parametro === id).length

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

// ── Handlers de selección ──────────────────────────────────────────────────────
function handleSelectCat(id: number) {
  selectedCatId.value = id
  selectedExId.value  = null
}

function handleSelectEx(id: number) {
  selectedExId.value = id
}

// ── Handlers CatalogoList ──────────────────────────────────────────────────────
function onCatCreated(cat: CatalogoExamen) {
  catalogos.value.push(cat)
  selectedCatId.value = cat.id
  selectedExId.value  = null
}

function onCatUpdated(cat: CatalogoExamen) {
  const idx = catalogos.value.findIndex(c => c.id === cat.id)
  if (idx !== -1) catalogos.value[idx] = cat
}

function onCatDeleted(id: number) {
  examenes.value  = examenes.value.filter(e => e.catalogo !== id)
  catalogos.value = catalogos.value.filter(c => c.id !== id)
  if (selectedCatId.value === id) {
    selectedCatId.value = catalogos.value[0]?.id ?? null
    selectedExId.value  = null
  }
}

// ── Handlers ExamenList ────────────────────────────────────────────────────────
function onExCreated(ex: Examen) {
  examenes.value.push(ex)
  selectedExId.value = ex.id
}

function onExUpdated(ex: Examen) {
  const idx = examenes.value.findIndex(e => e.id === ex.id)
  if (idx !== -1) examenes.value[idx] = ex
}

function onExDeleted(id: number) {
  parametros.value = parametros.value.filter(p => p.examen !== id)
  examenes.value   = examenes.value.filter(e => e.id !== id)
  if (selectedExId.value === id) selectedExId.value = null
}

// ── Handlers ParametroList ────────────────────────────────────────────────────
function onParCreated(par: Parametro) {
  parametros.value.push(par)
}

function onParUpdated(par: Parametro) {
  const idx = parametros.value.findIndex(p => p.id === par.id)
  if (idx !== -1) parametros.value[idx] = par
}

function onParDeleted(id: number) {
  valores.value    = valores.value.filter(v => v.parametro !== id)
  parametros.value = parametros.value.filter(p => p.id !== id)
}

// ── Handlers ValoresReferencia (burbujeados desde ParametroList) ───────────────
function onValCreated(val: ValorReferencia) {
  valores.value.push(val)
}

function onValUpdated(val: ValorReferencia) {
  const idx = valores.value.findIndex(v => v.id === val.id)
  if (idx !== -1) valores.value[idx] = val
}

function onValDeleted(id: number) {
  valores.value = valores.value.filter(v => v.id !== id)
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
        <div
          v-if="globalError"
          class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
        >
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ globalError }}
        </div>

        <!-- Skeleton de carga -->
        <div v-if="loading" class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div
            v-for="n in 3"
            :key="n"
            class="rounded-xl border bg-white p-4 space-y-3"
          >
            <Skeleton class="h-6 w-32" />
            <Skeleton v-for="i in 4" :key="i" class="h-10 w-full" />
          </div>
        </div>

        <!-- Contenido principal — 3 columnas -->
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-4 items-start">

          <!-- Col 1 — Catálogos -->
          <CatalogoList
            :catalogos="catalogos"
            :selected-cat-id="selectedCatId"
            :count-examenes="countExamenes"
            @select="handleSelectCat"
            @created="onCatCreated"
            @updated="onCatUpdated"
            @deleted="onCatDeleted"
          />

          <!-- Col 2 — Exámenes -->
          <ExamenView
            :examenes="examenesDelCat"
            :selected-cat="selectedCat"
            :selected-ex-id="selectedExId"
            :count-parametros="countParametros"
            @select="handleSelectEx"
            @created="onExCreated"
            @updated="onExUpdated"
            @deleted="onExDeleted"
          />

          <!-- Col 3 — Parámetros + Valores de Referencia -->
          <ParametroView
            :parametros="parametrosDelEx"
            :valores="valores"
            :selected-ex="selectedEx"
            :count-valores="countValores"
            @created="onParCreated"
            @updated="onParUpdated"
            @deleted="onParDeleted"
            @valor-created="onValCreated"
            @valor-updated="onValUpdated"
            @valor-deleted="onValDeleted"
          />

        </div>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>