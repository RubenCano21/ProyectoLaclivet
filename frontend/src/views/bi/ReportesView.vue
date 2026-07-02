<script setup lang="ts">
import { ref, computed } from 'vue'
import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbPage, BreadcrumbSeparator, BreadcrumbLink,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from '@/components/ui/table'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Checkbox } from '@/components/ui/checkbox'

import {
  FileDown, Search, FlaskConical, ClipboardList, Microscope,
  AlertCircle, RefreshCw,
} from 'lucide-vue-next'

import {
  biService,
  type FiltrosReporte,
  type ReporteMuestra,
  type ReporteSolicitud,
  type ReporteExamen,
} from '@/services/biService'

// ── Tipos ─────────────────────────────────────────────────────────────────────
type TipoReporte = 'muestras' | 'solicitudes' | 'examenes'

interface ColDef { key: string; label: string; default: boolean }

// ── Definición de columnas por tipo ──────────────────────────────────────────
const COLS: Record<TipoReporte, ColDef[]> = {
  muestras: [
    { key: 'codigo',           label: 'Código',           default: true  },
    { key: 'tipo_muestra',     label: 'Tipo de muestra',  default: true  },
    { key: 'estado',           label: 'Estado',           default: true  },
    { key: 'fecha_recepcion',  label: 'Fecha Recepción',  default: true  },
    { key: 'paciente',         label: 'Paciente',         default: true  },
    { key: 'especie',          label: 'Especie',          default: true  },
    { key: 'solicitud_codigo', label: 'Solicitud',        default: false },
    { key: 'observaciones',    label: 'Observaciones',    default: false },
  ],
  solicitudes: [
    { key: 'codigo',             label: 'Código',          default: true  },
    { key: 'estado',             label: 'Estado',          default: true  },
    { key: 'fecha_solicitud',    label: 'Fecha',           default: true  },
    { key: 'paciente',           label: 'Paciente',        default: true  },
    { key: 'especie',            label: 'Especie',         default: true  },
    { key: 'medico_veterinario', label: 'Médico Vet.',     default: true  },
    { key: 'examenes',           label: 'Exámenes',        default: true  },
    { key: 'monto_total',        label: 'Monto (Bs.)',     default: true  },
    { key: 'metodo_pago',        label: 'Método de Pago',  default: false },
  ],
  examenes: [
    { key: 'id',              label: '#',                 default: false },
    { key: 'examen',          label: 'Examen',            default: true  },
    { key: 'catalogo',        label: 'Catálogo',          default: true  },
    { key: 'estado',          label: 'Estado',            default: true  },
    { key: 'fecha_resultado', label: 'Fecha Resultado',   default: true  },
    { key: 'paciente',        label: 'Paciente',          default: true  },
    { key: 'especie',         label: 'Especie',           default: true  },
    { key: 'veterinario',     label: 'Veterinario Resp.', default: true  },
    { key: 'observaciones',   label: 'Observaciones',     default: false },
  ],
}

// ── Estado global ─────────────────────────────────────────────────────────────
const tipoReporte = ref<TipoReporte>('muestras')

const colsActivas = ref<Record<TipoReporte, Set<string>>>({
  muestras:    new Set(COLS.muestras.filter(c => c.default).map(c => c.key)),
  solicitudes: new Set(COLS.solicitudes.filter(c => c.default).map(c => c.key)),
  examenes:    new Set(COLS.examenes.filter(c => c.default).map(c => c.key)),
})

const colsActivasActual = computed(() => colsActivas.value[tipoReporte.value])
const colDefsActual     = computed(() => COLS[tipoReporte.value])
const nColsActivas      = computed(() => colsActivasActual.value.size)

function hasCol(key: string) { return colsActivasActual.value.has(key) }

function toggleCol(key: string) {
  const set = new Set(colsActivas.value[tipoReporte.value])
  if (set.has(key)) {
    if (set.size === 1) return
    set.delete(key)
  } else {
    set.add(key)
  }
  colsActivas.value = { ...colsActivas.value, [tipoReporte.value]: set }
}

// ── Filtros ───────────────────────────────────────────────────────────────────
const fechaInicio  = ref('')
const fechaFin     = ref('')
const filtroEstado = ref('')
const filtroTipo   = ref('')

// ── Estado tabla ──────────────────────────────────────────────────────────────
const loading        = ref(false)
const loadingPdf     = ref(false)
const error          = ref<string | null>(null)
const totalRegistros = ref(0)
const buscado        = ref(false)

const resultadosMuestras    = ref<ReporteMuestra[]>([])
const resultadosSolicitudes = ref<ReporteSolicitud[]>([])
const resultadosExamenes    = ref<ReporteExamen[]>([])

// ── Opciones estado ───────────────────────────────────────────────────────────
const estadosMuestra   = [
  { value: '', label: 'Todos' }, { value: 'pendiente', label: 'Pendiente' },
  { value: 'en_proceso', label: 'En proceso' }, { value: 'completada', label: 'Completada' },
  { value: 'rechazada', label: 'Rechazada' },
]
const estadosSolicitud = [
  { value: '', label: 'Todos' }, { value: 'pendiente', label: 'Pendiente' },
  { value: 'en_proceso', label: 'En proceso' }, { value: 'completado', label: 'Completado' },
  { value: 'cancelado', label: 'Cancelado' },
]
const estadosExamen    = [
  { value: '', label: 'Todos' }, { value: 'pendiente', label: 'Pendiente' },
  { value: 'en_proceso', label: 'En proceso' }, { value: 'completado', label: 'Completado' },
  { value: 'validado', label: 'Validado' },
]
const estadosActivos = computed(() =>
  tipoReporte.value === 'muestras' ? estadosMuestra
  : tipoReporte.value === 'solicitudes' ? estadosSolicitud
  : estadosExamen
)

// ── Helpers ───────────────────────────────────────────────────────────────────
function badgeVariant(estado: string): 'default' | 'secondary' | 'destructive' | 'outline' {
  const m: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
    pendiente: 'secondary', en_proceso: 'outline',
    completada: 'default',  completado: 'default',
    validado: 'default',    rechazada: 'destructive', cancelado: 'destructive',
  }
  return m[estado] ?? 'secondary'
}
function estadoLabel(e: string) { return e.replace('_', ' ').replace(/^\w/, c => c.toUpperCase()) }

function buildFiltros(): FiltrosReporte {
  return {
    fecha_inicio: fechaInicio.value  || undefined,
    fecha_fin:    fechaFin.value     || undefined,
    estado:       filtroEstado.value || undefined,
    tipo_muestra: tipoReporte.value === 'muestras' ? filtroTipo.value || undefined : undefined,
    columnas:     [...colsActivasActual.value].join(','),
  }
}

// ── Acciones ──────────────────────────────────────────────────────────────────
async function buscar() {
  loading.value = true; error.value = null; buscado.value = true
  try {
    const f = buildFiltros()
    if (tipoReporte.value === 'muestras') {
      const { data } = await biService.getReporteMuestras(f)
      resultadosMuestras.value = data.resultados; totalRegistros.value = data.total
    } else if (tipoReporte.value === 'solicitudes') {
      const { data } = await biService.getReporteSolicitudes(f)
      resultadosSolicitudes.value = data.resultados; totalRegistros.value = data.total
    } else {
      const { data } = await biService.getReporteExamenes(f)
      resultadosExamenes.value = data.resultados; totalRegistros.value = data.total
    }
  } catch { error.value = 'Error al cargar el reporte. Verifique los filtros e intente nuevamente.' }
  finally { loading.value = false }
}

async function descargarPdf() {
  loadingPdf.value = true
  try {
    const { data } = await biService.descargarPdf(tipoReporte.value, buildFiltros())
    const url = URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))
    const a = document.createElement('a')
    a.href = url
    a.download = `reporte_${tipoReporte.value}_${new Date().toISOString().slice(0, 10)}.pdf`
    a.click(); URL.revokeObjectURL(url)
  } catch { error.value = 'Error al generar el PDF.' }
  finally { loadingPdf.value = false }
}

function limpiarFiltros() {
  fechaInicio.value = ''; fechaFin.value = ''; filtroEstado.value = ''; filtroTipo.value = ''
  resultadosMuestras.value = []; resultadosSolicitudes.value = []; resultadosExamenes.value = []
  totalRegistros.value = 0; buscado.value = false; error.value = null
}

function cambiarTipo(tipo: TipoReporte) {
  tipoReporte.value = tipo; filtroEstado.value = ''; filtroTipo.value = ''; limpiarFiltros()
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
            <BreadcrumbItem><BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink></BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem><BreadcrumbPage>Reportes</BreadcrumbPage></BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <div class="flex flex-col gap-6 p-6">

        <!-- Título -->
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold tracking-tight">Reportes Dinámicos</h1>
            <p class="text-sm text-muted-foreground mt-0.5">
              Filtra, elige columnas desde la cabecera y exporta en PDF
            </p>
          </div>
          <Button variant="outline" size="sm" :disabled="!buscado || loadingPdf" class="gap-2" @click="descargarPdf">
            <RefreshCw v-if="loadingPdf" class="h-4 w-4 animate-spin" />
            <FileDown v-else class="h-4 w-4" />
            Descargar PDF
          </Button>
        </div>

        <!-- Tipo de reporte -->
        <div class="grid grid-cols-3 gap-3">
          <button
            v-for="tab in [
              { key: 'muestras',    label: 'Muestras',    icon: FlaskConical  },
              { key: 'solicitudes', label: 'Solicitudes', icon: ClipboardList },
              { key: 'examenes',    label: 'Exámenes',    icon: Microscope    },
            ]"
            :key="tab.key"
            :class="[
              'flex items-center gap-2 rounded-lg border px-4 py-3 text-sm font-medium transition-colors',
              tipoReporte === tab.key
                ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                : 'border-border bg-card text-muted-foreground hover:bg-muted hover:text-foreground',
            ]"
            @click="cambiarTipo(tab.key as TipoReporte)"
          >
            <component :is="tab.icon" class="h-4 w-4" />
            {{ tab.label }}
          </button>
        </div>

        <!-- Filtros -->
        <div class="rounded-xl border bg-card p-5 shadow-sm">
          <h2 class="text-sm font-semibold mb-4">Filtros</h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div class="flex flex-col gap-1.5">
              <Label for="fecha-inicio">Fecha inicio</Label>
              <Input id="fecha-inicio" v-model="fechaInicio" type="date" />
            </div>
            <div class="flex flex-col gap-1.5">
              <Label for="fecha-fin">Fecha fin</Label>
              <Input id="fecha-fin" v-model="fechaFin" type="date" />
            </div>
            <div class="flex flex-col gap-1.5">
              <Label>Estado</Label>
              <Select
                :model-value="filtroEstado || '_all_'"
                @update:model-value="(v) => filtroEstado = String(v ?? '') === '_all_' ? '' : String(v ?? '')"
              >
                <SelectTrigger><SelectValue placeholder="Todos los estados" /></SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="opt in estadosActivos" :key="opt.value || '_all_'" :value="opt.value || '_all_'">
                    {{ opt.label }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div v-if="tipoReporte === 'muestras'" class="flex flex-col gap-1.5">
              <Label for="tipo-muestra">Tipo de muestra</Label>
              <Input id="tipo-muestra" v-model="filtroTipo" placeholder="Ej: Sangre, Orina…" />
            </div>
          </div>
          <div class="flex items-center gap-3 mt-4">
            <Button :disabled="loading" class="gap-2" @click="buscar">
              <RefreshCw v-if="loading" class="h-4 w-4 animate-spin" />
              <Search v-else class="h-4 w-4" />
              {{ loading ? 'Buscando…' : 'Generar Reporte' }}
            </Button>
            <Button variant="ghost" :disabled="loading" @click="limpiarFiltros">Limpiar filtros</Button>
            <span v-if="buscado && !loading" class="ml-auto text-sm text-muted-foreground">
              {{ totalRegistros }} resultado{{ totalRegistros !== 1 ? 's' : '' }}
              &nbsp;·&nbsp;
              <span class="font-medium">{{ nColsActivas }}/{{ colDefsActual.length }} columnas</span>
            </span>
          </div>
        </div>

        <!-- Error -->
        <div v-if="error" class="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          <AlertCircle class="h-4 w-4 shrink-0" />{{ error }}
        </div>

        <!-- Skeletons -->
        <div v-if="loading" class="space-y-2">
          <Skeleton v-for="i in 6" :key="i" class="h-10 w-full rounded" />
        </div>

        <!-- ─────────────────────────────── TABLA MUESTRAS ─────────────────────────────── -->
        <div v-else-if="buscado && tipoReporte === 'muestras'" class="rounded-xl border bg-card overflow-x-auto shadow-sm">
          <p class="px-4 pt-3 pb-1 text-xs text-muted-foreground">
            Marca o desmarca las columnas en la cabecera para personalizar el reporte
          </p>
          <Table>
            <TableHeader>
              <TableRow class="bg-muted/40 hover:bg-muted/40">
                <TableHead
                  v-for="col in COLS.muestras" :key="col.key"
                  :class="['transition-all duration-150', hasCol(col.key) ? 'min-w-25' : 'w-10 px-2']"
                >
                  <label class="flex cursor-pointer select-none items-center gap-1.5 group">
                    <Checkbox
                      :checked="hasCol(col.key)"
                      :disabled="hasCol(col.key) && nColsActivas === 1"
                      class="h-3.5 w-3.5 shrink-0"
                      @update:checked="() => toggleCol(col.key)"
                    />
                    <span v-show="hasCol(col.key)" class="whitespace-nowrap text-xs font-semibold uppercase tracking-wide">
                      {{ col.label }}
                    </span>
                  </label>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="resultadosMuestras.length === 0">
                <TableCell :colspan="COLS.muestras.length" class="text-center py-10 text-muted-foreground text-sm">
                  Sin resultados para los filtros aplicados.
                </TableCell>
              </TableRow>
              <TableRow v-for="m in resultadosMuestras" :key="m.id" class="hover:bg-muted/30 transition-colors">
                <TableCell v-show="hasCol('codigo')" class="font-mono font-medium">{{ m.codigo }}</TableCell>
                <TableCell v-show="hasCol('tipo_muestra')">{{ m.tipo_muestra }}</TableCell>
                <TableCell v-show="hasCol('estado')">
                  <Badge :variant="badgeVariant(m.estado)">{{ estadoLabel(m.estado) }}</Badge>
                </TableCell>
                <TableCell v-show="hasCol('fecha_recepcion')">
                  {{ m.fecha_recepcion ? new Date(m.fecha_recepcion + 'T00:00:00').toLocaleDateString('es-BO') : '—' }}
                </TableCell>
                <TableCell v-show="hasCol('paciente')">{{ m.paciente }}</TableCell>
                <TableCell v-show="hasCol('especie')">
                  <Badge v-if="m.especie !== '—'" variant="outline" class="text-xs">{{ m.especie }}</Badge>
                  <span v-else class="text-muted-foreground">—</span>
                </TableCell>
                <TableCell v-show="hasCol('solicitud_codigo')" class="font-mono text-xs">{{ m.solicitud_codigo }}</TableCell>
                <TableCell v-show="hasCol('observaciones')" class="max-w-xs truncate text-xs text-muted-foreground">{{ m.observaciones || '—' }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <!-- ─────────────────────────────── TABLA SOLICITUDES ─────────────────────────────── -->
        <div v-else-if="buscado && tipoReporte === 'solicitudes'" class="rounded-xl border bg-card overflow-x-auto shadow-sm">
          <p class="px-4 pt-3 pb-1 text-xs text-muted-foreground">
            Marca o desmarca las columnas en la cabecera para personalizar el reporte
          </p>
          <Table>
            <TableHeader>
              <TableRow class="bg-muted/40 hover:bg-muted/40">
                <TableHead
                  v-for="col in COLS.solicitudes" :key="col.key"
                  :class="['transition-all duration-150', hasCol(col.key) ? 'min-w-25' : 'w-10 px-2']"
                >
                  <label class="flex cursor-pointer select-none items-center gap-1.5">
                    <Checkbox
                      :checked="hasCol(col.key)"
                      :disabled="hasCol(col.key) && nColsActivas === 1"
                      class="h-3.5 w-3.5 shrink-0"
                      @update:checked="() => toggleCol(col.key)"
                    />
                    <span v-show="hasCol(col.key)" class="whitespace-nowrap text-xs font-semibold uppercase tracking-wide">
                      {{ col.label }}
                    </span>
                  </label>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="resultadosSolicitudes.length === 0">
                <TableCell :colspan="COLS.solicitudes.length" class="text-center py-10 text-muted-foreground text-sm">
                  Sin resultados para los filtros aplicados.
                </TableCell>
              </TableRow>
              <TableRow v-for="s in resultadosSolicitudes" :key="s.id" class="hover:bg-muted/30 transition-colors">
                <TableCell v-show="hasCol('codigo')" class="font-mono font-medium">{{ s.codigo }}</TableCell>
                <TableCell v-show="hasCol('estado')">
                  <Badge :variant="badgeVariant(s.estado)">{{ estadoLabel(s.estado) }}</Badge>
                </TableCell>
                <TableCell v-show="hasCol('fecha_solicitud')">{{ new Date(s.fecha_solicitud).toLocaleDateString('es-BO') }}</TableCell>
                <TableCell v-show="hasCol('paciente')">{{ s.paciente }}</TableCell>
                <TableCell v-show="hasCol('especie')">
                  <Badge v-if="s.especie !== '—'" variant="outline" class="text-xs">{{ s.especie }}</Badge>
                  <span v-else class="text-muted-foreground">—</span>
                </TableCell>
                <TableCell v-show="hasCol('medico_veterinario')">{{ s.medico_veterinario }}</TableCell>
                <TableCell v-show="hasCol('examenes')" class="max-w-xs text-xs">
                  <span v-if="s.examenes.length">{{ s.examenes.join(', ') }}</span>
                  <span v-else class="text-muted-foreground">—</span>
                </TableCell>
                <TableCell v-show="hasCol('monto_total')" class="font-medium">
                  {{ s.monto_total != null ? `Bs. ${s.monto_total.toFixed(2)}` : '—' }}
                </TableCell>
                <TableCell v-show="hasCol('metodo_pago')">{{ s.metodo_pago ?? '—' }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <!-- ─────────────────────────────── TABLA EXÁMENES ─────────────────────────────── -->
        <div v-else-if="buscado && tipoReporte === 'examenes'" class="rounded-xl border bg-card overflow-x-auto shadow-sm">
          <p class="px-4 pt-3 pb-1 text-xs text-muted-foreground">
            Marca o desmarca las columnas en la cabecera para personalizar el reporte
          </p>
          <Table>
            <TableHeader>
              <TableRow class="bg-muted/40 hover:bg-muted/40">
                <TableHead
                  v-for="col in COLS.examenes" :key="col.key"
                  :class="['transition-all duration-150', hasCol(col.key) ? 'min-w-25' : 'w-10 px-2']"
                >
                  <label class="flex cursor-pointer select-none items-center gap-1.5">
                    <Checkbox
                      :checked="hasCol(col.key)"
                      :disabled="hasCol(col.key) && nColsActivas === 1"
                      class="h-3.5 w-3.5 shrink-0"
                      @update:checked="() => toggleCol(col.key)"
                    />
                    <span v-show="hasCol(col.key)" class="whitespace-nowrap text-xs font-semibold uppercase tracking-wide">
                      {{ col.label }}
                    </span>
                  </label>
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-if="resultadosExamenes.length === 0">
                <TableCell :colspan="COLS.examenes.length" class="text-center py-10 text-muted-foreground text-sm">
                  Sin resultados para los filtros aplicados.
                </TableCell>
              </TableRow>
              <TableRow v-for="e in resultadosExamenes" :key="e.id" class="hover:bg-muted/30 transition-colors">
                <TableCell v-show="hasCol('id')" class="text-xs text-muted-foreground">{{ e.id }}</TableCell>
                <TableCell v-show="hasCol('examen')" class="font-medium">{{ e.examen }}</TableCell>
                <TableCell v-show="hasCol('catalogo')" class="text-sm text-muted-foreground">{{ e.catalogo }}</TableCell>
                <TableCell v-show="hasCol('estado')">
                  <Badge :variant="badgeVariant(e.estado)">{{ estadoLabel(e.estado) }}</Badge>
                </TableCell>
                <TableCell v-show="hasCol('fecha_resultado')">
                  {{ e.fecha_resultado ? new Date(e.fecha_resultado).toLocaleDateString('es-BO') : '—' }}
                </TableCell>
                <TableCell v-show="hasCol('paciente')">{{ e.paciente }}</TableCell>
                <TableCell v-show="hasCol('especie')">
                  <Badge v-if="e.especie !== '—'" variant="outline" class="text-xs">{{ e.especie }}</Badge>
                  <span v-else class="text-muted-foreground">—</span>
                </TableCell>
                <TableCell v-show="hasCol('veterinario')">{{ e.veterinario }}</TableCell>
                <TableCell v-show="hasCol('observaciones')" class="max-w-xs truncate text-xs text-muted-foreground">{{ e.observaciones || '—' }}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>

        <!-- Estado inicial -->
        <div v-else-if="!buscado" class="flex flex-col items-center justify-center rounded-xl border border-dashed bg-muted/20 py-16 text-center">
          <Search class="h-10 w-10 text-muted-foreground/40 mb-3" />
          <p class="text-sm font-medium text-muted-foreground">Aplica los filtros y presiona <strong>Generar Reporte</strong></p>
          <p class="text-xs text-muted-foreground mt-1">Podrás elegir columnas directamente desde la cabecera de la tabla</p>
        </div>

      </div>
    </SidebarInset>
  </SidebarProvider>
</template>
