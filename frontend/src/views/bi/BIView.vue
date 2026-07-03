<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
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
  AlertCircle, BarChart3, Stethoscope, CreditCard,
  AlertTriangle, CheckCircle2, Info, Zap,
} from 'lucide-vue-next'

import {
  biService,
  type BiResumen, type BiSerie, type BiInsight,
} from '@/services/biService'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  BarElement, ArcElement, Title, Tooltip, Legend, Filler,
)

// ── Estado ────────────────────────────────────────────────────────────────────
const loading = ref(true)
const error   = ref<string | null>(null)
const meses   = ref<3 | 6 | 12>(6)

const resumen               = ref<BiResumen | null>(null)
const muestrasMes           = ref<BiSerie | null>(null)
const solicitudesMes        = ref<BiSerie | null>(null)
const ingresosMes           = ref<BiSerie | null>(null)
const solicitudesEstado     = ref<BiSerie | null>(null)
const tiposMuestra          = ref<BiSerie | null>(null)
const muestrasEstado        = ref<BiSerie | null>(null)
const especies              = ref<BiSerie | null>(null)
const examenesTop           = ref<BiSerie | null>(null)
const ingresosPago          = ref<BiSerie | null>(null)
const rendimientoVets       = ref<BiSerie | null>(null)
const pacientesActivos      = ref<BiSerie | null>(null)
const insights              = ref<BiInsight[]>([])

// ── Paletas ───────────────────────────────────────────────────────────────────
const PALETTE = ['#6366f1','#22d3ee','#f59e0b','#10b981','#ef4444','#8b5cf6','#ec4899','#14b8a6']
const PALETTE_ALPHA = (hex: string, a = 0.15) => hex + Math.round(a * 255).toString(16).padStart(2, '0')

const baseOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }

// ── Helpers labels ─────────────────────────────────────────────────────────────
function fmtMes(l: string) {
  const [y, m] = l.split('-')
  return new Date(+y, +m - 1).toLocaleDateString('es-BO', { month: 'short', year: '2-digit' })
}

// ── Gráficas tendencia ─────────────────────────────────────────────────────────
const trendData = computed(() => {
  if (!muestrasMes.value || !solicitudesMes.value) return null
  return {
    labels: muestrasMes.value.labels.map(fmtMes),
    datasets: [
      { label: 'Muestras', data: muestrasMes.value.datos, borderColor: '#6366f1', backgroundColor: PALETTE_ALPHA('#6366f1'), fill: true, tension: 0.4, pointRadius: 4 },
      { label: 'Solicitudes', data: solicitudesMes.value.datos, borderColor: '#22d3ee', backgroundColor: PALETTE_ALPHA('#22d3ee'), fill: true, tension: 0.4, pointRadius: 4 },
    ],
  }
})
const trendOpts = { ...baseOpts, plugins: { legend: { display: true, position: 'top' as const } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }

const ingresosData = computed(() => {
  if (!ingresosMes.value) return null
  return {
    labels: ingresosMes.value.labels.map(fmtMes),
    datasets: [{ label: 'Ingresos (Bs.)', data: ingresosMes.value.datos, borderColor: '#10b981', backgroundColor: PALETTE_ALPHA('#10b981'), fill: true, tension: 0.4, pointRadius: 4 }],
  }
})
const ingresosOpts = { ...baseOpts, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }

// ── Donuts ─────────────────────────────────────────────────────────────────────
const donutOpts = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: true, position: 'right' as const } }, cutout: '65%' }

const makePie = (serie: BiSerie | null) => {
  if (!serie) return null
  return { labels: serie.labels, datasets: [{ data: serie.datos, backgroundColor: PALETTE.slice(0, serie.labels.length), borderWidth: 2, borderColor: '#fff' }] }
}
const solEstadoData    = computed(() => makePie(solicitudesEstado.value))
const tiposData        = computed(() => makePie(tiposMuestra.value))
const muestrasEstData  = computed(() => makePie(muestrasEstado.value))
const especiesData     = computed(() => makePie(especies.value))
const ingresosPagoData = computed(() => makePie(ingresosPago.value))

// ── Barras horizontales ────────────────────────────────────────────────────────
const makeHBar = (serie: BiSerie | null, color: string) => {
  if (!serie) return null
  return { labels: serie.labels, datasets: [{ label: 'Total', data: serie.datos, backgroundColor: color, borderRadius: 6 }] }
}
const hBarOpts = { ...baseOpts, indexAxis: 'y' as const, scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } } }

const examenesData       = computed(() => {
  if (!examenesTop.value) return null
  return { labels: examenesTop.value.labels, datasets: [{ label: 'Solicitudes', data: examenesTop.value.datos, backgroundColor: PALETTE, borderRadius: 6 }] }
})
const rendimientoData    = computed(() => makeHBar(rendimientoVets.value, '#6366f1'))
const pacientesActivosData = computed(() => makeHBar(pacientesActivos.value, '#f59e0b'))

// ── KPI helpers ────────────────────────────────────────────────────────────────
function tendencia(actual: number, anterior: number) {
  if (anterior === 0) return actual > 0 ? 'up' : 'neutral'
  return actual >= anterior ? 'up' : 'down'
}
function variacion(actual: number, anterior: number): string {
  if (anterior === 0) return '—'
  const pct = ((actual - anterior) / anterior) * 100
  return `${pct > 0 ? '+' : ''}${pct.toFixed(1)}%`
}

// ── Insights helpers ───────────────────────────────────────────────────────────
const insightStyle: Record<string, { bg: string; border: string; text: string }> = {
  alerta:     { bg: 'bg-red-50',    border: 'border-red-200',    text: 'text-red-700' },
  advertencia:{ bg: 'bg-amber-50',  border: 'border-amber-200',  text: 'text-amber-700' },
  info:       { bg: 'bg-blue-50',   border: 'border-blue-200',   text: 'text-blue-700' },
  exito:      { bg: 'bg-emerald-50',border: 'border-emerald-200',text: 'text-emerald-700' },
}

// ── Carga ──────────────────────────────────────────────────────────────────────
async function loadBI() {
  loading.value = true
  error.value   = null
  const n = meses.value
  try {
    const [r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12] = await Promise.all([
      biService.getResumen(),
      biService.getMuestrasPorMes(n),
      biService.getSolicitudesPorMes(n),
      biService.getIngresosPorMes(n),
      biService.getSolicitudesEstado(),
      biService.getTiposMuestra(),
      biService.getMuestrasEstado(),
      biService.getEspecies(),
      biService.getExamenesTop(),
      biService.getIngresosPorMetodoPago(),
      biService.getRendimientoVeterinarios(),
      biService.getPacientesMasActivos(),
      biService.getInsights(),
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
    ingresosPago.value      = r9.data
    rendimientoVets.value   = r10.data
    pacientesActivos.value  = r11.data
    insights.value          = r12.data.insights
  } catch {
    error.value = 'No se pudo cargar la información del módulo BI.'
  } finally {
    loading.value = false
  }
}

watch(meses, loadBI)
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
        <div class="ml-auto flex items-center gap-2">
          <!-- Selector de rango -->
          <div class="flex items-center gap-1 rounded-lg border bg-white p-1 text-xs shadow-xs">
            <button
              v-for="n in [3, 6, 12]" :key="n"
              :class="['px-2.5 py-1 rounded-md font-medium transition-colors', meses === n ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:bg-muted']"
              @click="meses = n as 3 | 6 | 12"
            >{{ n }}m</button>
          </div>
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
            Indicadores clave, análisis de tendencias y asistente IA del laboratorio
          </p>
        </div>

        <!-- Error -->
        <div v-if="error" class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" /> {{ error }}
        </div>

        <!-- ── Insights automáticos ──────────────────────────────────────── -->
        <div v-if="!loading && insights.length" class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          <div
            v-for="(ins, i) in insights" :key="i"
            :class="['flex items-start gap-3 rounded-xl border p-4 shadow-xs', insightStyle[ins.tipo]?.bg, insightStyle[ins.tipo]?.border]"
          >
            <component
              :is="ins.tipo === 'alerta' ? AlertTriangle : ins.tipo === 'advertencia' ? AlertCircle : ins.tipo === 'info' ? Info : CheckCircle2"
              :class="['h-5 w-5 mt-0.5 shrink-0', insightStyle[ins.tipo]?.text]"
            />
            <div>
              <p :class="['text-sm font-semibold', insightStyle[ins.tipo]?.text]">{{ ins.titulo }}</p>
              <p class="text-xs mt-0.5 text-muted-foreground">{{ ins.mensaje }}</p>
            </div>
          </div>
        </div>

        <!-- ── KPI Cards ─────────────────────────────────────────────────── -->
        <div class="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-8 gap-3">

          <!-- Muestras totales -->
          <div class="rounded-xl border bg-white p-4 shadow-xs col-span-1">
            <div class="flex items-center justify-between mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600"><FlaskConical class="h-5 w-5" /></div>
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
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-cyan-50 text-cyan-600"><ClipboardList class="h-5 w-5" /></div>
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
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-50 text-violet-600 mb-2"><PawPrint class="h-5 w-5" /></div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold">{{ resumen?.total_pacientes ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Pacientes</p>
          </div>

          <!-- Ingresos -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex items-center justify-between mb-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-50 text-emerald-600"><TrendingUp class="h-5 w-5" /></div>
              <template v-if="resumen">
                <TrendingUp v-if="tendencia(resumen.ingresos_este_mes, resumen.ingresos_mes_anterior) === 'up'" class="h-4 w-4 text-emerald-500" />
                <TrendingDown v-else class="h-4 w-4 text-red-500" />
              </template>
            </div>
            <Skeleton v-if="loading" class="h-7 w-20 mb-1" />
            <p v-else class="text-xl font-bold">Bs. {{ resumen?.ingresos_este_mes.toLocaleString('es-BO') ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Ingresos este mes</p>
            <p v-if="resumen && !loading" class="text-xs mt-1 font-medium"
               :class="tendencia(resumen.ingresos_este_mes, resumen.ingresos_mes_anterior) === 'up' ? 'text-emerald-600' : 'text-red-500'">
              {{ variacion(resumen.ingresos_este_mes, resumen.ingresos_mes_anterior) }} vs mes ant.
            </p>
          </div>

          <!-- Sol. pendientes -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50 text-amber-600 mb-2"><ClipboardList class="h-5 w-5" /></div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold text-amber-600">{{ resumen?.solicitudes_pendientes ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Sol. pendientes</p>
          </div>

          <!-- Muestras pendientes -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-orange-50 text-orange-600 mb-2"><FlaskConical class="h-5 w-5" /></div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold text-orange-600">{{ resumen?.muestras_pendientes ?? '—' }}</p>
            <p class="text-xs text-muted-foreground">Muest. pendientes</p>
          </div>

          <!-- Tasa de rechazo -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50 text-red-600 mb-2"><AlertTriangle class="h-5 w-5" /></div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold" :class="(resumen?.tasa_rechazo ?? 0) > 10 ? 'text-red-600' : 'text-foreground'">
              {{ resumen?.tasa_rechazo ?? '—' }}%
            </p>
            <p class="text-xs text-muted-foreground">Tasa rechazo</p>
          </div>

          <!-- Parámetros fuera de rango -->
          <div class="rounded-xl border bg-white p-4 shadow-xs">
            <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-pink-50 text-pink-600 mb-2"><Zap class="h-5 w-5" /></div>
            <Skeleton v-if="loading" class="h-7 w-16 mb-1" />
            <p v-else class="text-2xl font-bold" :class="(resumen?.parametros_fuera_rango ?? 0) > 0 ? 'text-pink-600' : 'text-foreground'">
              {{ resumen?.parametros_fuera_rango ?? '—' }}
            </p>
            <p class="text-xs text-muted-foreground">Fuera de rango</p>
          </div>

        </div>

        <!-- ── Tendencia Muestras + Solicitudes ──────────────────────────── -->
        <div class="rounded-xl border bg-white p-5 shadow-xs">
          <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
            <TrendingUp class="h-4 w-4 text-primary" />
            Tendencia — Muestras y Solicitudes (últimos {{ meses }} meses)
          </h2>
          <div class="h-64 relative">
            <Skeleton v-if="loading || !trendData" class="absolute inset-0 rounded-lg" />
            <Line v-else-if="trendData" :data="trendData" :options="trendOpts" />
          </div>
        </div>

        <!-- ── Fila: Tipos + Estado muestras + Estado solicitudes ─────────── -->
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

        <!-- ── Fila: Top Exámenes + Distribución por especie ─────────────── -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
              <BarChart3 class="h-4 w-4 text-primary" />Top exámenes solicitados
            </h2>
            <div class="h-64 relative">
              <Skeleton v-if="loading || !examenesData" class="absolute inset-0 rounded-lg" />
              <Bar v-else-if="examenesData" :data="examenesData" :options="hBarOpts" />
              <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
            </div>
          </div>
          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
              <PawPrint class="h-4 w-4 text-primary" />Distribución por especie
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
            Ingresos por mes (Bs.) — últimos {{ meses }} meses
          </h2>
          <div class="h-52 relative">
            <Skeleton v-if="loading || !ingresosData" class="absolute inset-0 rounded-lg" />
            <Line v-else-if="ingresosData" :data="ingresosData" :options="ingresosOpts" />
          </div>
        </div>

        <!-- ── NUEVOS: Ingresos por método de pago + Rendimiento Veterinarios ── -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
              <CreditCard class="h-4 w-4 text-primary" />Ingresos por método de pago
            </h2>
            <div class="h-52 relative">
              <Skeleton v-if="loading || !ingresosPagoData" class="absolute inset-0 rounded-lg" />
              <Doughnut v-else-if="ingresosPagoData" :data="ingresosPagoData" :options="donutOpts" />
              <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
            </div>
          </div>
          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
              <Stethoscope class="h-4 w-4 text-primary" />Rendimiento de veterinarios
            </h2>
            <div class="h-52 relative">
              <Skeleton v-if="loading || !rendimientoData" class="absolute inset-0 rounded-lg" />
              <Bar v-else-if="rendimientoData" :data="rendimientoData" :options="hBarOpts" />
              <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
            </div>
          </div>
        </div>

        <!-- ── NUEVO: Pacientes más activos ──────────────────────────────── -->
        <div class="rounded-xl border bg-white p-5 shadow-xs">
          <h2 class="font-semibold mb-4 text-sm flex items-center gap-2">
            <PawPrint class="h-4 w-4 text-amber-500" />Pacientes más activos (top 8 por solicitudes)
          </h2>
          <div class="h-52 relative">
            <Skeleton v-if="loading || !pacientesActivosData" class="absolute inset-0 rounded-lg" />
            <Bar v-else-if="pacientesActivosData" :data="pacientesActivosData" :options="hBarOpts" />
            <div v-else class="flex items-center justify-center h-full text-xs text-muted-foreground">Sin datos</div>
          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>
</template>

