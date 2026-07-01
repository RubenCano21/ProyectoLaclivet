<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { solicitudFlujoService, type SolicitudCompleta } from '@/services/solicitudService'

import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { CalendarDays, ChevronLeft, ChevronRight, Loader2, AlertCircle, RotateCcw } from 'lucide-vue-next'

// ─── Types ───────────────────────────────────────────────────────────────────

type Vista = 'mes' | 'semana' | 'dia'

interface DiaCalendario {
  fecha: Date
  esHoy: boolean
  esMesActual: boolean
  esFinDeSemana: boolean
  solicitudes: SolicitudCompleta[]
}

interface MiniDia {
  fecha: Date
  esHoy: boolean
  esMesActual: boolean
  esSeleccionado: boolean
  tieneEventos: boolean
}

// ─── State ────────────────────────────────────────────────────────────────────

const router = useRouter()
const vista = ref<Vista>('mes')
const hoy = new Date()
const cursor = ref(new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate()))

// Mes que muestra el mini-calendario del panel lateral. Se mantiene
// sincronizado con `cursor` cuando el usuario navega desde el calendario
// principal, pero también se puede mover de forma independiente con sus
// propias flechas sin afectar la vista principal hasta que se elige un día.
const miniMes = ref(new Date(cursor.value.getFullYear(), cursor.value.getMonth(), 1))

const solicitudes = ref<SolicitudCompleta[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

// ─── Helpers de fecha ────────────────────────────────────────────────────────
//
// Usamos componentes de fecha LOCALES (no toISOString) para evitar que las
// solicitudes se agrupen en el día equivocado en zonas horarias distintas a
// UTC (p.ej. Bolivia, UTC-4).

function isoDate(d: Date) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function esHoy(d: Date) {
  return isoDate(d) === isoDate(hoy)
}

function esFinDeSemana(d: Date) {
  const day = d.getDay()
  return day === 0 || day === 6
}

function startOfWeek(d: Date) {
  const day = d.getDay()          // 0=dom ... 6=sab
  const diff = (day + 6) % 7      // lunes = 0
  const lunes = new Date(d)
  lunes.setDate(d.getDate() - diff)
  return lunes
}

function addDays(d: Date, n: number) {
  const r = new Date(d)
  r.setDate(r.getDate() + n)
  return r
}

// Genera las semanas (5 o 6) necesarias para cubrir un mes completo,
// comenzando en lunes. Se reutiliza tanto para el grid grande como el mini.
function semanasDelMes(año: number, mes: number): Date[][] {
  const primerDia = new Date(año, mes, 1)
  const ultimoDiaNum = new Date(año, mes + 1, 0).getDate()
  const lunes = startOfWeek(primerDia)

  const semanas: Date[][] = []
  let dia = new Date(lunes)
  let cubrioUltimoDia = false

  while (!cubrioUltimoDia) {
    const semana: Date[] = []
    for (let d = 0; d < 7; d++) {
      const actual = new Date(dia)
      semana.push(actual)
      if (actual.getFullYear() === año && actual.getMonth() === mes && actual.getDate() === ultimoDiaNum) {
        cubrioUltimoDia = true
      }
      dia = addDays(dia, 1)
    }
    semanas.push(semana)
  }
  return semanas
}

const MESES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
               'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
const DIAS_CORTOS = ['Lun','Mar','Mié','Jue','Vie','Sáb','Dom']
const DIAS_INICIAL = ['L','M','X','J','V','S','D']

// ─── Estados: colores, etiquetas y orden ──────────────────────────────────────

const ESTADOS = ['pendiente', 'en_proceso', 'completado', 'cancelado'] as const

const ESTADO_LABEL: Record<string, string> = {
  pendiente:  'Pendiente',
  en_proceso: 'En proceso',
  completado: 'Completado',
  cancelado:  'Cancelado',
}

const ESTADO_COLOR: Record<string, string> = {
  pendiente:   'bg-amber-50 text-amber-800 border-l-amber-400',
  en_proceso:  'bg-blue-50 text-blue-800 border-l-blue-400',
  completado:  'bg-green-50 text-green-800 border-l-green-400',
  cancelado:   'bg-red-50 text-red-800 border-l-red-400',
}

const ESTADO_DOT: Record<string, string> = {
  pendiente:  'bg-amber-400',
  en_proceso: 'bg-blue-500',
  completado: 'bg-green-500',
  cancelado:  'bg-red-500',
}

// ─── Rango de fechas según vista ──────────────────────────────────────────────

const rango = computed(() => {
  if (vista.value === 'mes') {
    const desde = new Date(cursor.value.getFullYear(), cursor.value.getMonth(), 1)
    const hasta = new Date(cursor.value.getFullYear(), cursor.value.getMonth() + 1, 0)
    return { desde, hasta }
  }
  if (vista.value === 'semana') {
    const desde = startOfWeek(cursor.value)
    const hasta = addDays(desde, 6)
    return { desde, hasta }
  }
  return { desde: cursor.value, hasta: cursor.value }
})

// ─── Título del encabezado ────────────────────────────────────────────────────

const titulo = computed(() => {
  const c = cursor.value
  if (vista.value === 'mes') return `${MESES[c.getMonth()]} ${c.getFullYear()}`
  if (vista.value === 'semana') {
    const lunes = startOfWeek(c)
    const domingo = addDays(lunes, 6)
    if (lunes.getMonth() === domingo.getMonth())
      return `${lunes.getDate()} – ${domingo.getDate()} de ${MESES[lunes.getMonth()]} ${lunes.getFullYear()}`
    return `${lunes.getDate()} ${MESES[lunes.getMonth()]} – ${domingo.getDate()} ${MESES[domingo.getMonth()]} ${lunes.getFullYear()}`
  }
  return `${c.getDate()} de ${MESES[c.getMonth()]} de ${c.getFullYear()}`
})

const etiquetaPeriodo = computed(() => {
  if (vista.value === 'mes') return 'este mes'
  if (vista.value === 'semana') return 'esta semana'
  return 'este día'
})

// ─── Navegación (calendario principal) ────────────────────────────────────────

function prev() {
  const c = new Date(cursor.value)
  if (vista.value === 'mes')    c.setMonth(c.getMonth() - 1)
  if (vista.value === 'semana') c.setDate(c.getDate() - 7)
  if (vista.value === 'dia')    c.setDate(c.getDate() - 1)
  cursor.value = c
}

function next() {
  const c = new Date(cursor.value)
  if (vista.value === 'mes')    c.setMonth(c.getMonth() + 1)
  if (vista.value === 'semana') c.setDate(c.getDate() + 7)
  if (vista.value === 'dia')    c.setDate(c.getDate() + 1)
  cursor.value = c
}

function irHoy() {
  cursor.value = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate())
}

function irDia(d: Date) {
  cursor.value = new Date(d)
  vista.value = 'dia'
}

// ─── Navegación (mini-calendario) ─────────────────────────────────────────────

function miniPrev() {
  const m = new Date(miniMes.value)
  m.setMonth(m.getMonth() - 1)
  miniMes.value = m
}

function miniNext() {
  const m = new Date(miniMes.value)
  m.setMonth(m.getMonth() + 1)
  miniMes.value = m
}

function miniSeleccionar(d: Date) {
  // Selecciona el día en el calendario principal sin forzar un cambio de
  // vista (respeta si el usuario está en mes/semana/día).
  cursor.value = new Date(d.getFullYear(), d.getMonth(), d.getDate())
}

// Si el usuario navega el calendario principal (prev/next/hoy), el
// mini-calendario sigue el mismo mes automáticamente.
watch(cursor, (nuevo) => {
  if (nuevo.getFullYear() !== miniMes.value.getFullYear() || nuevo.getMonth() !== miniMes.value.getMonth()) {
    miniMes.value = new Date(nuevo.getFullYear(), nuevo.getMonth(), 1)
  }
})

// ─── Carga de datos ───────────────────────────────────────────────────────────

async function cargar() {
  loading.value = true
  error.value = null
  try {
    const { data } = await solicitudFlujoService.getAgenda(
      isoDate(rango.value.desde),
      isoDate(rango.value.hasta),
    )
    solicitudes.value = Array.isArray(data) ? data : (data as { resultados: SolicitudCompleta[] }).resultados ?? []
  } catch {
    error.value = 'No se pudieron cargar las solicitudes'
  } finally {
    loading.value = false
  }
}

watch([vista, cursor], cargar, { immediate: true })

// ─── Agrupación de solicitudes por fecha ──────────────────────────────────────

const solicitudesPorFecha = computed(() => {
  const map = new Map<string, SolicitudCompleta[]>()
  for (const s of solicitudes.value) {
    if (!s.fecha_solicitud) continue
    const key = isoDate(new Date(s.fecha_solicitud))
    if (!map.has(key)) map.set(key, [])
    map.get(key)!.push(s)
  }
  for (const arr of map.values()) {
    arr.sort((a, b) => new Date(a.fecha_solicitud!).getTime() - new Date(b.fecha_solicitud!).getTime())
  }
  return map
})

function solicitudesDel(d: Date) {
  return solicitudesPorFecha.value.get(isoDate(d)) ?? []
}

// ─── Resumen por estado (para la leyenda) ─────────────────────────────────────

const conteoPorEstado = computed(() => {
  const c: Record<string, number> = { pendiente: 0, en_proceso: 0, completado: 0, cancelado: 0 }
  for (const s of solicitudes.value) c[s.estado] = (c[s.estado] ?? 0) + 1
  return c
})

function verSolicitud(id: number) {
  router.push({ name: 'solicitud-detalle', params: { id } })
}

// ─── Vista Mes (grid grande) ───────────────────────────────────────────────────

const gridMes = computed((): DiaCalendario[][] => {
  const año = cursor.value.getFullYear()
  const mes = cursor.value.getMonth()
  return semanasDelMes(año, mes).map(semana =>
    semana.map(actual => ({
      fecha: actual,
      esHoy: esHoy(actual),
      esMesActual: actual.getMonth() === mes,
      esFinDeSemana: esFinDeSemana(actual),
      solicitudes: solicitudesDel(actual),
    }))
  )
})

// ─── Mini-calendario (panel lateral) ───────────────────────────────────────────

const gridMini = computed((): MiniDia[][] => {
  const año = miniMes.value.getFullYear()
  const mes = miniMes.value.getMonth()
  return semanasDelMes(año, mes).map(semana =>
    semana.map(actual => ({
      fecha: actual,
      esHoy: esHoy(actual),
      esMesActual: actual.getMonth() === mes,
      esSeleccionado: isoDate(actual) === isoDate(cursor.value),
      tieneEventos: solicitudesDel(actual).length > 0,
    }))
  )
})

// ─── Vista Semana ─────────────────────────────────────────────────────────────

const diasSemana = computed((): DiaCalendario[] => {
  const lunes = startOfWeek(cursor.value)
  return Array.from({ length: 7 }, (_, i) => {
    const d = addDays(lunes, i)
    return { fecha: d, esHoy: esHoy(d), esMesActual: true, esFinDeSemana: esFinDeSemana(d), solicitudes: solicitudesDel(d) }
  })
})

// ─── Vista Día ────────────────────────────────────────────────────────────────

const solicitudesDia = computed(() => solicitudesDel(cursor.value))

function nombresOcultos(celda: DiaCalendario) {
  return celda.solicitudes.slice(3).map(s => s.paciente_nombre || s.codigo).join(', ')
}
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
            <BreadcrumbItem><BreadcrumbLink href="/dashboard">Inicio</BreadcrumbLink></BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem><BreadcrumbPage>Agenda</BreadcrumbPage></BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-4 p-6">

        <div class="flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <CalendarDays class="h-5 w-5" />
            </div>
            <div>
              <h1 class="text-2xl font-bold leading-tight">Agenda</h1>
              <p class="text-sm text-muted-foreground">Solicitudes de examen por fecha</p>
            </div>
          </div>

          <div class="flex items-center gap-2 rounded-lg border bg-muted/30 p-1">
            <button
              v-for="v in (['dia', 'semana', 'mes'] as const)"
              :key="v"
              type="button"
              :class="['px-3 py-1.5 rounded-md text-sm font-medium transition-colors',
                vista === v ? 'bg-white shadow-sm text-foreground' : 'text-muted-foreground hover:text-foreground']"
              @click="vista = v">
              {{ v === 'dia' ? 'Día' : v === 'semana' ? 'Semana' : 'Mes' }}
            </button>
          </div>
        </div>

        <!-- Cuerpo: panel lateral + calendario -->
        <div class="flex flex-col lg:flex-row items-start gap-5">

          <!-- Panel lateral: mini-calendario + leyenda + resumen -->
          <aside class="w-full lg:w-56 shrink-0 lg:sticky lg:top-6 space-y-4">

            <!-- Mini-calendario de navegación rápida -->
            <div class="rounded-xl border bg-white shadow-xs p-3">
              <div class="flex items-center justify-between mb-2 px-0.5">
                <button
                  type="button"
                  class="h-6 w-6 flex items-center justify-center rounded hover:bg-slate-100 text-muted-foreground transition-colors"
                  aria-label="Mes anterior en mini-calendario"
                  @click="miniPrev">
                  <ChevronLeft class="h-3.5 w-3.5" />
                </button>
                <p class="text-xs font-semibold capitalize">{{ MESES[miniMes.getMonth()] }} {{ miniMes.getFullYear() }}</p>
                <button
                  type="button"
                  class="h-6 w-6 flex items-center justify-center rounded hover:bg-slate-100 text-muted-foreground transition-colors"
                  aria-label="Mes siguiente en mini-calendario"
                  @click="miniNext">
                  <ChevronRight class="h-3.5 w-3.5" />
                </button>
              </div>

              <div class="mini-grid mb-1">
                <span
                  v-for="d in DIAS_INICIAL"
                  :key="d"
                  class="text-[10px] text-center text-muted-foreground/50 font-medium">
                  {{ d }}
                </span>
              </div>

              <div v-for="(semana, si) in gridMini" :key="si" class="mini-grid mb-0.5">
                <button
                  v-for="dia in semana"
                  :key="isoDate(dia.fecha)"
                  type="button"
                  :class="['relative h-7 w-7 mx-auto flex items-center justify-center rounded-full text-[11px] transition-colors',
                    dia.esSeleccionado ? 'bg-primary text-primary-foreground font-semibold' :
                    dia.esHoy ? 'text-primary font-semibold ring-1 ring-inset ring-primary/40' : '',
                    !dia.esMesActual ? 'text-muted-foreground/30 hover:bg-slate-50' :
                      (!dia.esSeleccionado ? 'text-foreground hover:bg-slate-100' : '')]"
                  @click="miniSeleccionar(dia.fecha)">
                  {{ dia.fecha.getDate() }}
                  <span
                    v-if="dia.tieneEventos && !dia.esSeleccionado"
                    class="absolute bottom-0.5 h-1 w-1 rounded-full bg-primary/70" />
                </button>
              </div>
            </div>

            <!-- Leyenda + resumen -->
            <div class="rounded-xl border bg-white shadow-xs p-4 space-y-4">
              <div>
                <h3 class="text-xs font-semibold text-muted-foreground uppercase tracking-wide mb-3">Estados</h3>
                <ul class="space-y-2.5">
                  <li v-for="estado in ESTADOS" :key="estado" class="flex items-center justify-between gap-2">
                    <span class="flex items-center gap-2 text-sm text-foreground">
                      <span :class="['h-2.5 w-2.5 rounded-full shrink-0', ESTADO_DOT[estado]]" />
                      {{ ESTADO_LABEL[estado] }}
                    </span>
                    <span class="text-xs font-medium text-muted-foreground bg-muted rounded-full px-2 py-0.5 min-w-6 text-center">
                      {{ conteoPorEstado[estado] }}
                    </span>
                  </li>
                </ul>
              </div>

              <Separator />

              <div>
                <p class="text-xs text-muted-foreground uppercase tracking-wide">Total</p>
                <p class="text-2xl font-bold leading-tight mt-0.5">{{ solicitudes.length }}</p>
                <p class="text-xs text-muted-foreground">solicitud{{ solicitudes.length !== 1 ? 'es' : '' }} {{ etiquetaPeriodo }}</p>
              </div>
            </div>
          </aside>

          <!-- Columna principal: navegación + calendario -->
          <div class="flex-1 min-w-0 w-full space-y-4">

            <div class="flex items-center gap-3">
              <Button variant="outline" size="sm" @click="irHoy">Hoy</Button>
              <div class="flex items-center gap-1">
                <Button variant="ghost" size="icon" class="h-8 w-8" aria-label="Periodo anterior" @click="prev">
                  <ChevronLeft class="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" class="h-8 w-8" aria-label="Periodo siguiente" @click="next">
                  <ChevronRight class="h-4 w-4" />
                </Button>
              </div>
              <h2 class="text-lg font-semibold">{{ titulo }}</h2>

              <div v-if="loading" class="flex items-center gap-1.5 text-sm text-muted-foreground ml-2">
                <Loader2 class="h-3.5 w-3.5 animate-spin" /> Cargando…
              </div>
            </div>

            <div v-if="error" class="flex items-center justify-between gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              <span class="flex items-center gap-2"><AlertCircle class="h-4 w-4 shrink-0" /> {{ error }}</span>
              <button
                type="button"
                class="flex items-center gap-1 rounded-md border border-red-300 px-2 py-1 text-xs font-medium hover:bg-red-100 transition-colors"
                @click="cargar">
                <RotateCcw class="h-3 w-3" /> Reintentar
              </button>
            </div>

            <!-- VISTA MES -->
            <div v-if="vista === 'mes'" class="rounded-xl border bg-white shadow-sm overflow-hidden">
              <div class="cal-grid border-b bg-slate-50/80">
                <div
                  v-for="(dia, i) in DIAS_CORTOS"
                  :key="dia"
                  :class="['py-2.5 text-center text-[11px] font-semibold uppercase tracking-wider',
                    i >= 5 ? 'text-muted-foreground/60' : 'text-muted-foreground']">
                  {{ dia }}
                </div>
              </div>

              <div v-for="(semana, si) in gridMes" :key="si" class="cal-grid divide-x divide-slate-100">
                <div
                  v-for="celda in semana"
                  :key="isoDate(celda.fecha)"
                  :class="['min-h-32 p-2 border-b border-slate-100 relative transition-colors group',
                    celda.esFinDeSemana ? 'bg-slate-50/50' : 'bg-white',
                    !celda.esMesActual ? 'bg-slate-50/40' : '',
                    'hover:bg-slate-50']">

                  <div v-if="celda.esHoy" class="absolute inset-x-0 top-0 h-0.5 bg-primary" />

                  <div class="flex items-center justify-between mb-1.5">
                    <button
                      type="button"
                      :class="['text-xs font-semibold w-6 h-6 rounded-full flex items-center justify-center transition-colors hover:bg-slate-200/70',
                        celda.esHoy ? 'bg-primary text-primary-foreground hover:bg-primary/90' : '',
                        !celda.esMesActual ? 'text-muted-foreground/40' : 'text-foreground']"
                      @click="irDia(celda.fecha)">
                      {{ celda.fecha.getDate() }}
                    </button>
                    <span
                      v-if="celda.solicitudes.length > 0"
                      class="text-[10px] font-medium text-muted-foreground/70">
                      {{ celda.solicitudes.length }}
                    </span>
                  </div>

                  <div class="space-y-1">
                    <button
                      v-for="s in celda.solicitudes.slice(0, 3)"
                      :key="s.id"
                      type="button"
                      :class="['w-full text-left text-[11px] leading-tight px-1.5 py-1 rounded-sm border-l-2 truncate transition-shadow hover:shadow-sm',
                        ESTADO_COLOR[s.estado] ?? 'bg-gray-50 text-gray-700 border-l-gray-300']"
                      @click.stop="verSolicitud(s.id)">
                      <span class="font-medium">{{ s.paciente_nombre || s.codigo }}</span>
                    </button>
                    <button
                      v-if="celda.solicitudes.length > 3"
                      type="button"
                      :title="nombresOcultos(celda)"
                      class="w-full text-left text-[11px] px-1.5 py-0.5 rounded-sm text-muted-foreground hover:text-foreground hover:bg-slate-100 transition-colors"
                      @click.stop="irDia(celda.fecha)">
                      +{{ celda.solicitudes.length - 3 }} más
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- VISTA SEMANA -->
            <div v-else-if="vista === 'semana'" class="rounded-xl border bg-white shadow-sm overflow-hidden">
              <div class="cal-grid divide-x divide-slate-100">
                <div
                  v-for="dia in diasSemana"
                  :key="isoDate(dia.fecha)"
                  :class="['flex flex-col min-h-120', dia.esFinDeSemana ? 'bg-slate-50/50' : '']">

                  <div
                    :class="['p-3 border-b border-slate-100 text-center sticky top-0 bg-white z-10',
                    dia.esFinDeSemana ? 'bg-slate-50/80' : '']">
                    <div v-if="dia.esHoy" class="absolute inset-x-0 top-0 h-0.5 bg-primary" />
                    <p class="text-[11px] text-muted-foreground uppercase tracking-wider">
                      {{ DIAS_CORTOS[(dia.fecha.getDay() + 6) % 7] }}
                    </p>
                    <button
                      type="button"
                      :class="['mt-0.5 text-xl font-bold w-10 h-10 rounded-full flex items-center justify-center mx-auto transition-colors hover:bg-slate-200/70',
                        dia.esHoy ? 'bg-primary text-primary-foreground hover:bg-primary/90' : '']"
                      @click="irDia(dia.fecha)">
                      {{ dia.fecha.getDate() }}
                    </button>
                  </div>

                  <div class="flex-1 p-2 space-y-1.5 overflow-y-auto">
                    <div
                      v-if="dia.solicitudes.length === 0"
                      class="flex items-center justify-center h-full text-muted-foreground/40 text-xs">
                      Sin solicitudes
                    </div>
                    <button
                      v-for="s in dia.solicitudes"
                      :key="s.id"
                      type="button"
                      :class="['w-full text-left rounded-md border-l-2 p-2 text-xs transition-shadow hover:shadow-sm',
                        ESTADO_COLOR[s.estado] ?? 'bg-gray-50 text-gray-700 border-l-gray-300']"
                      @click="verSolicitud(s.id)">
                      <p class="font-semibold truncate">{{ s.paciente_nombre || '—' }}</p>
                      <p class="truncate opacity-80 mt-0.5">
                        {{ s.detalles.map(d => d.examen_nombre).filter(Boolean).join(', ') || s.codigo }}
                      </p>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- VISTA DÍA -->
            <div v-else class="rounded-xl border bg-white shadow-sm overflow-hidden">
              <div :class="['px-4 py-4 border-b relative', esHoy(cursor) ? 'bg-slate-50/80' : 'bg-slate-50/40']">
                <div v-if="esHoy(cursor)" class="absolute inset-x-0 top-0 h-0.5 bg-primary" />
                <p class="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                  {{ DIAS_CORTOS[(cursor.getDay() + 6) % 7] }}
                </p>
                <p class="text-3xl font-bold leading-none mt-0.5">
                  {{ cursor.getDate() }} <span class="text-lg font-normal text-muted-foreground">{{ MESES[cursor.getMonth()] }} {{ cursor.getFullYear() }}</span>
                </p>
              </div>

              <div v-if="!loading && solicitudesDia.length === 0" class="flex flex-col items-center justify-center py-20 text-muted-foreground gap-2">
                <CalendarDays class="h-10 w-10 opacity-30" />
                <p class="text-sm">No hay solicitudes para este día</p>
              </div>

              <div v-else class="divide-y divide-slate-100">
                <button
                  v-for="s in solicitudesDia"
                  :key="s.id"
                  type="button"
                  class="w-full text-left px-5 py-4 hover:bg-slate-50 transition-colors flex items-start gap-4"
                  @click="verSolicitud(s.id)">

                  <span :class="['mt-1.5 h-3 w-3 rounded-full shrink-0', ESTADO_DOT[s.estado] ?? 'bg-gray-400']" />

                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2 flex-wrap">
                      <p class="font-semibold text-sm">{{ s.paciente_nombre || '—' }}</p>
                      <span class="text-xs text-muted-foreground">· {{ s.codigo }}</span>
                      <span
                        :class="['inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
                          ESTADO_COLOR[s.estado] ?? 'bg-gray-100 text-gray-700 border-l-gray-300']">
                        {{ ESTADO_LABEL[s.estado] ?? s.estado }}
                      </span>
                    </div>
                    <p class="text-sm text-muted-foreground mt-0.5">
                      Médico: {{ s.medico_nombre || 'No asignado' }}
                    </p>
                    <div class="flex flex-wrap gap-1.5 mt-1.5">
                      <span
                        v-for="d in s.detalles"
                        :key="d.id"
                        class="inline-flex items-center rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                        {{ d.examen_nombre }}
                      </span>
                    </div>
                  </div>

                  <p class="text-xs text-muted-foreground whitespace-nowrap mt-0.5 shrink-0">
                    {{ new Date(s.fecha_solicitud!).toLocaleTimeString('es-BO', { hour: '2-digit', minute: '2-digit' }) }}
                  </p>
                </button>
              </div>
            </div>

          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>
</template>

<style scoped>
.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
}

.mini-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
}
</style>