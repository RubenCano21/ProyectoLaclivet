<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler,
} from 'chart.js'
import { Line, Bar, Doughnut } from 'vue-chartjs'

import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbPage, BreadcrumbSeparator, BreadcrumbLink,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'

import {
  FlaskConical, PawPrint, ClipboardList,
  TrendingUp, TrendingDown, Minus, RefreshCw,
  AlertCircle, BarChart3,
} from 'lucide-vue-next'

import { biService, type BiResumen, type BiSerie } from '@/services/biService'

// ── Registro de Chart.js ──────────────────────────────────────────────────────
ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler,
)

// ── Estado ────────────────────────────────────────────────────────────────────
const loading = ref(true)
const error   = ref<string | null>(null)

const resumen           = ref<BiResumen | null>(null)
const muestrasMes       = ref<BiSerie | null>(null)
const solicitudesMes    = ref<BiSerie | null>(null)
const ingresosMes       = ref<BiSerie | null>(null)
const solicitudesEstado = ref<BiSerie | null>(null)
const tiposMuestra      = ref<BiSerie | null>(null)
const muestrasEstado    = ref<BiSerie | null>(null)
const especies          = ref<BiSerie | null>(null)
const examenesTop       = ref<BiSerie | null>(null)

// ── Paletas ───────────────────────────────────────────────────────────────────
const PALETTE = ['#6366f1','#22d3ee','#f59e0b','#10b981','#ef4444','#8b5cf6','#ec4899','#14b8a6']
const PALETTE_ALPHA = (hex: string, a = 0.15) => hex + Math.round(a * 255).toString(16).padStart(2, '0')

// ── Opciones base ─────────────────────────────────────────────────────────────
const baseOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
}

// ── Datos de gráficas ─────────────────────────────────────────────────────────
const trendData = computed(() => {
  if (!muestrasMes.value || !solicitudesMes.value) return null
  const labels = muestrasMes.value.labels.map(l => {
    const [y, m] = l.split('-')
    return new Date(+y, +m - 1).toLocaleDateString('es-BO', { month: 'short', year: '2-digit' })
  })
  return {
    labels,
    datasets: [
      {
        label: 'Muestras',
        data: muestrasMes.value.datos,
        borderColor: '#6366f1',
        backgroundColor: PALETTE_ALPHA('#6366f1'),
        fill: true,
        tension: 0.4,
        pointRadius: 4,
      },
      {
        label: 'Solicitudes',
        data: solicitudesMes.value.datos,
        borderColor: '#22d3ee',
        backgroundColor: PALETTE_ALPHA('#22d3ee'),
        fill: true,
        tension: 0.4,
        pointRadius: 4,
      },
    ],
  }
})

const trendOpts = {
  ...baseOpts,
  plugins: {
    legend: { display: true, position: 'top' as const },
  },
  scales: {
    y: { beginAtZero: true, ticks: { stepSize: 1 } },
  },
}

const ingresosData = computed(() => {
  if (!ingresosMes.value) return null
  const labels = ingresosMes.value.labels.map(l => {
    const [y, m] = l.split('-')
    return new Date(+y, +m - 1).toLocaleDateString('es-BO', { month: 'short', year: '2-digit' })
  })
  return {
    labels,
    datasets: [{
      label: 'Ingresos (Bs.)',
      data: ingresosMes.value.datos,
      borderColor: '#10b981',
      backgroundColor: PALETTE_ALPHA('#10b981'),
      fill: true,
      tension: 0.4,
      pointRadius: 4,
    }],
  }
})

const ingresosOpts = {
  ...baseOpts,
  plugins: { legend: { display: false } },
  scales: {
    y: { beginAtZero: true },
  },
}

const donutOpts = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: true, position: 'right' as const },
  },
  cutout: '65%',
}

const makePie = (serie: BiSerie | null) => {
  if (!serie) return null
  return {
    labels: serie.labels,
    datasets: [{
      data: serie.datos,
      backgroundColor: PALETTE.slice(0, serie.labels.length),
      borderWidth: 2,
      borderColor: '#fff',
    }],
  }
}

const solEstadoData    = computed(() => makePie(solicitudesEstado.value))
const tiposData        = computed(() => makePie(tiposMuestra.value))
const muestrasEstData  = computed(() => makePie(muestrasEstado.value))
const especiesData     = computed(() => makePie(especies.value))

const examenesData = computed(() => {
  if (!examenesTop.value) return null
  return {
    labels: examenesTop.value.labels,
    datasets: [{
      label: 'Solicitudes',
      data: examenesTop.value.datos,
      backgroundColor: PALETTE,
      borderRadius: 6,
    }],
  }
})

const examenesOpts = {
  ...baseOpts,
  indexAxis: 'y' as const,
  plugins: { legend: { display: false } },
  scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } },
}

// ── Tendencia KPI ─────────────────────────────────────────────────────────────
function tendencia(actual: number, anterior: number) {
  if (anterior === 0) return actual > 0 ? 'up' : 'neutral'
  return actual >= anterior ? 'up' : 'down'
}
function variacion(actual: number, anterior: number): string {
  if (anterior === 0) return '—'
  const pct = ((actual - anterior) / anterior) * 100
  return `${pct > 0 ? '+' : ''}${pct.toFixed(1)}%`
}

// ── Carga ─────────────────────────────────────────────────────────────────────
async function loadBI() {
  loading.value = true
  error.value   = null
  try {
    const [r0, r1, r2, r3, r4, r5, r6, r7, r8] = await Promise.all([
      biService.getResumen(),
      biService.getMuestrasPorMes(),
      biService.getSolicitudesPorMes(),
      biService.getIngresosPorMes(),
      biService.getSolicitudesEstado(),
      biService.getTiposMuestra(),
      biService.getMuestrasEstado(),
      biService.getEspecies(),
      biService.getExamenesTop(),
    ])
    resumen.value           = r0.data
    muestrasMes.value       = r1.data
    solicitudesMes.value    = r2.data
    ingresosMes.value       = r3.data
    solicitudesEstado.value = r4.data
    tiposMuestra.value      = r5.data
    muestrasEstado.value    = r6.data
    especies.value          = r7.data
    examenesTop.value       = r8.data
  } catch {
    error.value = 'No se pudo cargar la información del módulo BI.'
  } finally {
    loading.value = false
  }
}

onMounted(loadBI)
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
            <BreadcrumbItem><BreadcrumbLink href="/dashboard">Inicio</BreadcrumbLink></BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem><BreadcrumbPage>Business Intelligence</BreadcrumbPage></BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
        <div class="ml-auto">
          <Button variant="outline" size="sm" class="gap-1.5" :disabled="loading" @click="loadBI">
            <RefreshCw class="h-3.5 w-3.5" :class="{ 'animate-spin': loading }" />
            Actualizar
          </Button>
        </div>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6 bg-muted/20 min-h-screen">

        <!-- Título -->
        <div>
          <h1 class="text-2xl font-bold flex items-center gap-2">
            <BarChart3 class="h-6 w-6 text-primary" />
            Business Intelligence
          </h1>
          <p class="text-sm text-muted-foreground mt-0.5">
            Indicadores clave y análisis de tendencias del laboratorio
          </p>
        </div>

        <!-- Error -->
        <div v-if="error" class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" /> {{ error }}
        </div>

        <!-- ── KPI Cards ─────────────────────────────────────────────────── -->
        <div class="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-4">

          <!-- Muestras totales -->
          <div class="rounded-xl border bg-white p-4 shadow-xs col-span-1">
            <div class="flex items-center justify-between mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                <FlaskConical class="h-5 w-5" />
              </div>
              <template v-if="resumen">
                <TrendingUp v-if="tendencia(resumen.muestras_este_mes, resumen.muestras_mes_anterior) === 'up'" class="h-4 w-4 text-emerald-500" />
                <TrendingDown v-else-if="tendencia(resumen.muestras_este_mes, resumen.muestras_mes_anterior) === 'down'" class="h-4 w-4 text-red-500" />
                <Minus v-else class="h-4 w-4 text-muted-foreground" />
              </template>
            </div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold">{{ resumen?.total_muestras ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Total muestras</p>
            <p v-if="resumen && !loading" class="text-xs mt-1 font-medium"
               :class="tendencia(resumen.muestras_este_mes, resumen.muestras_mes_anterior) === 'up' ? 'text-emerald-600' : 'text-red-500'">
              {{ variacion(resumen.muestras_este_mes, resumen.muestras_mes_anterior) }} vs mes ant.
            </p>
          </div>

          <!-- Solicitudes -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex items-center justify-between mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-50 text-cyan-600">
                <ClipboardList class="h-5 w-5" />
              </div>
              <template v-if="resumen">
                <TrendingUp v-if="tendencia(resumen.solicitudes_este_mes, resumen.solicitudes_mes_anterior) === 'up'" class="h-4 w-4 text-emerald-500" />
                <TrendingDown v-else class="h-4 w-4 text-red-500" />
              </template>
            </div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold">{{ resumen?.total_solicitudes ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Total solicitudes</p>
            <p v-if="resumen && !loading" class="text-xs mt-1 font-medium"
               :class="tendencia(resumen.solicitudes_este_mes, resumen.solicitudes_mes_anterior) === 'up' ? 'text-emerald-600' : 'text-red-500'">
              {{ variacion(resumen.solicitudes_este_mes, resumen.solicitudes_mes_anterior) }} vs mes ant.
            </p>
          </div>

          <!-- Pacientes -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex items-center justify-between mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-50 text-violet-600">
                <PawPrint class="h-5 w-5" />
              </div>
            </div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold">{{ resumen?.total_pacientes ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Pacientes registrados</p>
          </div>

          <!-- Ingresos -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex items-center justify-between mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600">
                <TrendingUp class="h-5 w-5" />
              </div>
            </div>
            <Skeleton v-if="loading" class="h-7 w-20 mb-1" />
            <p v-else class="text-2xl font-bold">Bs. {{ resumen?.total_ingresos.toLocaleString('es-BO') ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Ingresos totales</p>
          </div>

          <!-- Sol. pendientes -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex items-center justify-between mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50 text-amber-600">
                <ClipboardList class="h-5 w-5" />
              </div>
            </div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold text-amber-600">{{ resumen?.solicitudes_pendientes ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Sol. pendientes</p>
          </div>

          <!-- Muestras pendientes -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex items-center justify-between mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-orange-50 text-orange-600">
                <FlaskConical class="h-5 w-5" />
              </div>
            </div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold text-orange-600">{{ resumen?.muestras_pendientes ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Muestras pendientes</p>
          </div>

        </div>

        <!-- ── Tendencia Muestras + Solicitudes ──────────────────────────── -->
        <div class="rounded-xl border bg-white p-5 shadow-xs">
          <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
            <TrendingUp class="h-4 w-4 text-primary" />
            Tendencia — Muestras y Solicitudes (últimos 6 meses)
          </h2>
          <div class="h-64 relative">
            <Skeleton v-if="loading || !trendData" class="absolute inset-0 rounded-lg" />
            <Line v-else-if="trendData" :data="trendData" :options="trendOpts" />
          </div>
        </div>

        <!-- ── Fila: Tipos de muestra + Estado muestras + Estado solicitudes ── -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm">Tipos de muestra</h2>
            <div class="h-52 relative">
              <Skeleton v-if="loading || !tiposData" class="absolute inset-0 rounded-lg" />
              <Doughnut v-else-if="tiposData" :data="tiposData" :options="donutOpts" />
              <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
            </div>
          </div>

          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm">Estado de muestras</h2>
            <div class="h-52 relative">
              <Skeleton v-if="loading || !muestrasEstData" class="absolute inset-0 rounded-lg" />
              <Doughnut v-else-if="muestrasEstData" :data="muestrasEstData" :options="donutOpts" />
              <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
            </div>
          </div>

          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm">Estado de solicitudes</h2>
            <div class="h-52 relative">
              <Skeleton v-if="loading || !solEstadoData" class="absolute inset-0 rounded-lg" />
              <Doughnut v-else-if="solEstadoData" :data="solEstadoData" :options="donutOpts" />
              <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
            </div>
          </div>

        </div>

        <!-- ── Fila: Top Exámenes + Especies ─────────────────────────────── -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">

          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
              <BarChart3 class="h-4 w-4 text-primary" />
              Top exámenes solicitados
            </h2>
            <div class="h-64 relative">
              <Skeleton v-if="loading || !examenesData" class="absolute inset-0 rounded-lg" />
              <Bar v-else-if="examenesData" :data="examenesData" :options="examenesOpts" />
              <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
            </div>
          </div>

          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
              <PawPrint class="h-4 w-4 text-primary" />
              Distribución por especie
            </h2>
            <div class="h-64 relative">
              <Skeleton v-if="loading || !especiesData" class="absolute inset-0 rounded-lg" />
              <Doughnut v-else-if="especiesData" :data="especiesData" :options="{ ...donutOpts, cutout: '55%' }" />
              <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
            </div>
          </div>

        </div>

        <!-- ── Ingresos por mes ───────────────────────────────────────────── -->
        <div class="rounded-xl border bg-white p-5 shadow-xs">
          <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
            <TrendingUp class="h-4 w-4 text-emerald-600" />
            Ingresos por mes (Bs.) — últimos 6 meses
          </h2>
          <div class="h-52 relative">
            <Skeleton v-if="loading || !ingresosData" class="absolute inset-0 rounded-lg" />
            <Line v-else-if="ingresosData" :data="ingresosData" :options="ingresosOpts" />
          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>
</template>

