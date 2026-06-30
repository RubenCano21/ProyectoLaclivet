<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Loader2, AlertCircle, FlaskConical, CheckCircle2,
  Search, CreditCard, Trash2, ChevronRight, ClipboardList,
} from 'lucide-vue-next'
import ComboboxBuscable from '@/components/common/ComboboxBuscable.vue'
import { useSolicitudesStore } from '@/stores/solicitudes'
import { useMuestrasStore } from '@/stores/muestras'
import { pacienteService } from '@/services/pacienteService'
import { medicoService } from '@/services/medicoService'
import { catalogoService, type CatalogoExamen } from '@/services/catalogoService'

// ── Props / Emits ──────────────────────────────────────────────────────────────
const props = defineProps<{ open: boolean }>()
const emit  = defineEmits<{ 'update:open': [value: boolean]; saved: [] }>()

const solicitudesStore = useSolicitudesStore()
const muestrasStore    = useMuestrasStore()

// ── Pasos del wizard ───────────────────────────────────────────────────────────
// 1 → Paciente + Médico   2 → Exámenes   3 → Muestras   4 → Cobro + Confirmar
const paso = ref(1)
const TOTAL_PASOS = 4

const tituloPaso: Record<number, string> = {
  1: 'Paciente',
  2: 'Exámenes',
  3: 'Muestras',
  4: 'Cobro',
}

// ── Paso 1: Paciente + Médico ──────────────────────────────────────────────────
const paciente          = ref<number | null>(null)
const pacienteNombre    = ref('')
const medicoVeterinario = ref<number | null>(null)
const observaciones     = ref('')

const _ultimaListaPacientes = ref<any[]>([])

const pacienteObj = computed(() =>
  paciente.value !== null
    ? { id: paciente.value, nombre: pacienteNombre.value || `Paciente #${paciente.value}` }
    : null,
)

watch(paciente, (id) => {
  if (!id) { pacienteNombre.value = ''; return }
  const found = _ultimaListaPacientes.value.find((p: any) => p.id === id)
  if (found) pacienteNombre.value = found.nombre ?? ''
})

async function fetchPacientes(search: string) {
  const { data } = await pacienteService.buscar(search)
  const lista = data.resultados ?? data.results ?? data
  _ultimaListaPacientes.value = lista
  return lista
}

async function fetchMedicos(search: string) {
  const { data } = await medicoService.buscar(search)
  return data.resultados ?? data.results ?? data
}

// ── Paso 2: Exámenes ───────────────────────────────────────────────────────────
interface ExamenDisponible {
  id: number
  nombre_examen: string
  catalogo: number
  catalogo_nombre?: string
  categoria?: string
  requiere_muestra?: boolean
}

interface ExamenSeleccionado {
  examen: ExamenDisponible
  precio: string
}

const examenesDisponibles = ref<ExamenDisponible[]>([])
const catalogos           = ref<CatalogoExamen[]>([])
const busqueda            = ref('')
const catalogoFiltroId    = ref<string>('todos')
const seleccionados       = ref<ExamenSeleccionado[]>([])
const cargandoExamenes    = ref(false)

const examenesFiltrados = computed(() => {
  let list = examenesDisponibles.value
  if (catalogoFiltroId.value !== 'todos')
    list = list.filter(e => e.catalogo === Number(catalogoFiltroId.value))
  if (busqueda.value.trim()) {
    const q = busqueda.value.toLowerCase()
    list = list.filter(e =>
      e.nombre_examen.toLowerCase().includes(q) ||
      (e.categoria ?? '').toLowerCase().includes(q),
    )
  }
  return list
})

const montoTotal = computed(() =>
  seleccionados.value.reduce((sum, s) => sum + (parseFloat(s.precio) || 0), 0).toFixed(2),
)

function toggleExamen(ex: ExamenDisponible) {
  const idx = seleccionados.value.findIndex(s => s.examen.id === ex.id)
  if (idx === -1) {
    const cat = catalogos.value.find(c => c.id === ex.catalogo)
    seleccionados.value.push({ examen: ex, precio: (cat as any)?.precio ?? '' })
    // Inicializar muestra vacía para este examen
    muestras.value.push({
      examen_id:       ex.id,
      examen_nombre:   ex.nombre_examen,
      tipo:            '',
      fecha_recepcion: new Date().toISOString().slice(0, 10),
      observaciones:   '',
    })
  } else {
    seleccionados.value.splice(idx, 1)
    muestras.value = muestras.value.filter(m => m.examen_id !== ex.id)
  }
}

function estaSeleccionado(id: number) {
  return seleccionados.value.some(s => s.examen.id === id)
}

function removeSeleccionado(id: number) {
  seleccionados.value = seleccionados.value.filter(s => s.examen.id !== id)
  muestras.value      = muestras.value.filter(m => m.examen_id !== id)
}

async function cargarExamenes() {
  cargandoExamenes.value = true
  try {
    const [re, rc] = await Promise.all([
      catalogoService.getExamenes(),
      catalogoService.getAll(),
    ])
    examenesDisponibles.value = re.data.resultados ?? re.data.results ?? re.data
    catalogos.value           = rc.data.resultados ?? rc.data.results ?? rc.data
  } finally {
    cargandoExamenes.value = false
  }
}

// ── Paso 3: Muestras ───────────────────────────────────────────────────────────
const TIPOS_MUESTRA = [
  { value: 'sangre', label: 'Sangre' },
  { value: 'orina',  label: 'Orina' },
  { value: 'heces',  label: 'Heces' },
  { value: 'tejido', label: 'Tejido' },
  { value: 'otro',   label: 'Otro' },
]

interface MuestraForm {
  examen_id:       number
  examen_nombre:   string
  tipo:            string
  fecha_recepcion: string
  observaciones:   string
}

const muestras = ref<MuestraForm[]>([])

// Cada examen seleccionado tiene exactamente una muestra (1:1 obligatorio)
// Validación del paso 3: todos los tipos deben estar completados
const paso3Valido = computed(() =>
  muestras.value.length > 0 && muestras.value.every(m => m.tipo !== ''),
)

// ── Paso 4: Cobro ──────────────────────────────────────────────────────────────
const incluirCobro = ref(true)
const metodoPago   = ref('')

// ── Estado UI global ───────────────────────────────────────────────────────────
const error        = ref<string | null>(null)
const mensajeExito = ref<string | null>(null)

// ── Validación por paso ────────────────────────────────────────────────────────
const pasoValido = computed(() => {
  if (paso.value === 1) return !!paciente.value
  if (paso.value === 2) return seleccionados.value.length > 0
  if (paso.value === 3) return paso3Valido.value
  return true
})

// ── Reset ──────────────────────────────────────────────────────────────────────
function resetForm() {
  paso.value              = 1
  paciente.value          = null
  pacienteNombre.value    = ''
  medicoVeterinario.value = null
  observaciones.value     = ''
  seleccionados.value     = []
  muestras.value          = []
  busqueda.value          = ''
  catalogoFiltroId.value  = 'todos'
  incluirCobro.value      = true
  metodoPago.value        = ''
  error.value             = null
  mensajeExito.value      = null
}

watch(() => props.open, (val) => {
  if (val) { resetForm(); cargarExamenes() }
})

// ── Submit ─────────────────────────────────────────────────────────────────────
async function guardar() {
  error.value = null

  // 1. Crear solicitud con exámenes
  const res = await solicitudesStore.crear({
    paciente:           paciente.value!,
    medico_veterinario: medicoVeterinario.value,
    examenes_ids:       seleccionados.value.map(s => s.examen.id),
    observaciones:      observaciones.value,
  })

  if (!res.ok) {
    error.value = res.error || 'No se pudo crear la solicitud.'
    return
  }

  // 2. Registrar cada muestra vinculada al paciente
  const erroresMuestra: string[] = []
  for (const m of muestras.value) {
    const rm = await muestrasStore.create({
      paciente:        paciente.value!,
      tipo:            m.tipo,
      estado:          'pendiente',
      fecha_recepcion: m.fecha_recepcion,
      observaciones:   m.observaciones,
    })
    if (!rm.ok) erroresMuestra.push(m.examen_nombre)
  }

  if (erroresMuestra.length > 0) {
    mensajeExito.value = `Solicitud creada. Error al registrar muestra(s) para: ${erroresMuestra.join(', ')}.`
  } else {
    mensajeExito.value = `Solicitud creada con ${muestras.value.length} muestra(s) registrada(s).`
  }

  emit('saved')
  setTimeout(() => emit('update:open', false), 1600)
}
</script>

<template>
  <Dialog :open="open" @update:open="(v) => emit('update:open', v)">
    <DialogContent class="sm:max-w-2xl max-h-[92vh] flex flex-col gap-0 p-0 overflow-hidden">

      <!-- ── Encabezado ─────────────────────────────────────────────────────── -->
      <DialogHeader class="px-6 pt-5 pb-4 border-b shrink-0">
        <DialogTitle class="text-base font-semibold">Nueva solicitud de examen</DialogTitle>

        <!-- Indicador de pasos -->
        <div class="flex items-center gap-1 mt-3">
          <template v-for="n in TOTAL_PASOS" :key="n">
            <button
              class="flex items-center gap-1.5 text-xs font-medium transition-colors"
              :class="n === paso
                ? 'text-primary'
                : n < paso ? 'text-green-600 cursor-pointer hover:text-green-700'
                           : 'text-muted-foreground cursor-default'"
              :disabled="n > paso"
              @click="n < paso && (paso = n)"
            >
              <span
                class="flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold shrink-0 transition-colors"
                :class="n < paso
                  ? 'bg-green-100 text-green-600'
                  : n === paso ? 'bg-primary text-primary-foreground'
                               : 'bg-muted text-muted-foreground'"
              >
                <CheckCircle2 v-if="n < paso" class="h-3 w-3" />
                <span v-else>{{ n }}</span>
              </span>
              {{ tituloPaso[n] }}
            </button>
            <ChevronRight v-if="n < TOTAL_PASOS" class="h-3 w-3 text-muted-foreground/40 shrink-0" />
          </template>
        </div>
      </DialogHeader>

      <!-- ── Cuerpo scrolleable ─────────────────────────────────────────────── -->
      <div class="flex-1 overflow-y-auto px-6 py-5 space-y-4">

        <!-- ════ PASO 1: Paciente + Médico ════ -->
        <template v-if="paso === 1">
          <div class="space-y-1.5">
            <Label>Paciente <span class="text-red-500">*</span></Label>
            <ComboboxBuscable
              v-model="paciente"
              :fetcher="fetchPacientes"
              :label-fn="(p: any) => `${p.nombre} (${p.raza_nombre || p.especie_nombre || 'Paciente'})`"
              placeholder="Buscar paciente…"
              empty-text="No se encontraron pacientes."
            />
          </div>

          <div class="space-y-1.5">
            <Label>
              Médico veterinario externo
              <span class="text-xs text-muted-foreground font-normal">(opcional)</span>
            </Label>
            <ComboboxBuscable
              v-model="medicoVeterinario"
              :fetcher="fetchMedicos"
              :label-fn="(m: any) => `Dr(a). ${m.usuario_first_name || m.nombre || ''} ${m.usuario_last_name || ''}`"
              placeholder="Buscar médico…"
              empty-text="No se encontraron médicos."
            />
          </div>

          <div class="space-y-1.5">
            <Label>
              Observaciones
              <span class="text-xs text-muted-foreground font-normal">(opcional)</span>
            </Label>
            <Textarea v-model="observaciones" rows="3" placeholder="Notas adicionales para el laboratorio…" />
          </div>
        </template>

        <!-- ════ PASO 2: Exámenes ════ -->
        <template v-if="paso === 2">
          <!-- Buscador + filtro -->
          <div class="flex gap-2">
            <div class="relative flex-1">
              <Search class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
              <Input v-model="busqueda" placeholder="Buscar examen…" class="h-8 text-sm pl-8" />
            </div>
            <Select v-model="catalogoFiltroId">
              <SelectTrigger class="h-8 text-xs w-44 shrink-0">
                <SelectValue placeholder="Todos los catálogos" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos los catálogos</SelectItem>
                <SelectItem v-for="c in catalogos" :key="c.id" :value="String(c.id)">
                  {{ c.nombre }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          <!-- Lista disponible -->
          <div class="rounded-lg border overflow-hidden">
            <div v-if="cargandoExamenes" class="flex justify-center items-center py-8 text-muted-foreground">
              <Loader2 class="h-5 w-5 animate-spin mr-2" /> Cargando…
            </div>
            <ul v-else class="max-h-52 overflow-y-auto divide-y">
              <li
                v-for="ex in examenesFiltrados" :key="ex.id"
                class="flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-muted/40 cursor-pointer transition-colors"
                :class="estaSeleccionado(ex.id) ? 'bg-primary/5' : ''"
                @click="toggleExamen(ex)"
              >
                <Checkbox :checked="estaSeleccionado(ex.id)" @update:checked="() => toggleExamen(ex)" />
                <span class="flex-1 font-medium">{{ ex.nombre_examen }}</span>
                <span class="text-xs text-muted-foreground shrink-0">
                  {{ ex.catalogo_nombre ?? catalogos.find(c => c.id === ex.catalogo)?.nombre ?? '' }}
                  <span v-if="ex.categoria"> · {{ ex.categoria }}</span>
                </span>
              </li>
              <li v-if="examenesFiltrados.length === 0" class="px-4 py-6 text-center text-sm text-muted-foreground">
                Sin resultados.
              </li>
            </ul>
          </div>

          <!-- Tabla seleccionados -->
          <div v-if="seleccionados.length > 0" class="space-y-2">
            <div class="flex items-center gap-2">
              <span class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Seleccionados</span>
              <Badge variant="secondary">{{ seleccionados.length }}</Badge>
            </div>
            <div class="rounded-lg border overflow-hidden">
              <table class="w-full text-sm">
                <thead class="bg-muted/30 border-b">
                  <tr>
                    <th class="text-left px-3 py-1.5 text-xs font-medium text-muted-foreground">Examen</th>
                    <th class="text-right px-3 py-1.5 text-xs font-medium text-muted-foreground w-28">Precio (Bs.)</th>
                    <th class="w-8"></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-border/40">
                  <tr v-for="s in seleccionados" :key="s.examen.id" class="hover:bg-muted/20">
                    <td class="px-3 py-1.5">
                      <p class="font-medium leading-tight">{{ s.examen.nombre_examen }}</p>
                      <p v-if="s.examen.categoria" class="text-xs text-muted-foreground">{{ s.examen.categoria }}</p>
                    </td>
                    <td class="px-3 py-1.5">
                      <Input v-model="s.precio" placeholder="0.00" class="h-7 text-sm text-right w-24 ml-auto" />
                    </td>
                    <td class="px-2 py-1.5">
                      <button
                        class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50 transition-colors"
                        @click="removeSeleccionado(s.examen.id)"
                      >
                        <Trash2 class="h-3.5 w-3.5" />
                      </button>
                    </td>
                  </tr>
                </tbody>
                <tfoot class="bg-muted/10 border-t">
                  <tr>
                    <td class="px-3 py-1.5 text-xs text-muted-foreground text-right font-medium">Total:</td>
                    <td class="px-3 py-1.5 text-right font-bold text-sm">Bs. {{ montoTotal }}</td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- Aviso trazabilidad -->
          <div class="flex items-start gap-2 rounded-lg border border-blue-100 bg-blue-50 px-3 py-2 text-sm text-blue-700">
            <FlaskConical class="h-4 w-4 shrink-0 mt-0.5" />
            <span>En el siguiente paso registrarás una muestra por cada examen para garantizar la trazabilidad.</span>
          </div>
        </template>

        <!-- ════ PASO 3: Muestras ════ -->
        <template v-if="paso === 3">
          <div class="flex items-start gap-2 rounded-lg border border-amber-100 bg-amber-50 px-3 py-2 text-sm text-amber-700 mb-1">
            <FlaskConical class="h-4 w-4 shrink-0 mt-0.5" />
            <span>
              Registra una muestra por cada examen solicitado. El tipo de muestra es obligatorio
              para poder procesar el análisis.
            </span>
          </div>

          <!-- Una tarjeta por examen -->
          <div
            v-for="(m) in muestras" :key="m.examen_id"
            class="rounded-lg border overflow-hidden"
            :class="m.tipo ? 'border-border' : 'border-red-200'"
          >
            <!-- Cabecera de la tarjeta -->
            <div
              class="flex items-center justify-between px-4 py-2.5 border-b text-sm font-medium"
              :class="m.tipo ? 'bg-muted/30' : 'bg-red-50'"
            >
              <div class="flex items-center gap-2">
                <FlaskConical class="h-4 w-4 text-primary shrink-0" />
                <span>{{ m.examen_nombre }}</span>
                <Badge v-if="!m.tipo" variant="destructive" class="text-[10px] h-4 px-1.5">
                  Tipo requerido
                </Badge>
              </div>
              <CheckCircle2 v-if="m.tipo" class="h-4 w-4 text-green-500 shrink-0" />
            </div>

            <!-- Campos de la muestra -->
            <div class="p-4 grid sm:grid-cols-2 gap-3">
              <!-- Tipo (obligatorio) -->
              <div class="space-y-1.5">
                <Label class="text-xs">
                  Tipo de muestra <span class="text-red-500">*</span>
                </Label>
                <Select v-model="m.tipo">
                  <SelectTrigger class="h-8 text-sm" :class="!m.tipo ? 'border-red-300' : ''">
                    <SelectValue placeholder="Seleccionar tipo…" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="t in TIPOS_MUESTRA" :key="t.value" :value="t.value">
                      {{ t.label }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <!-- Fecha de recepción -->
              <div class="space-y-1.5">
                <Label class="text-xs">Fecha de recepción</Label>
                <Input type="date" v-model="m.fecha_recepcion" class="h-8 text-sm" />
              </div>

              <!-- Observaciones (span completo) -->
              <div class="space-y-1.5 sm:col-span-2">
                <Label class="text-xs">
                  Observaciones de la muestra
                  <span class="text-muted-foreground font-normal">(opcional)</span>
                </Label>
                <Input
                  v-model="m.observaciones"
                  placeholder="Ej: muestra hemolizada, volumen insuficiente…"
                  class="h-8 text-sm"
                />
              </div>
            </div>
          </div>

          <!-- Progreso de completitud -->
          <div class="flex items-center gap-2 text-xs text-muted-foreground">
            <div class="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
              <div
                class="h-full rounded-full bg-primary transition-all"
                :style="`width: ${(muestras.filter(m => m.tipo).length / muestras.length) * 100}%`"
              />
            </div>
            <span class="shrink-0">
              {{ muestras.filter(m => m.tipo).length }}/{{ muestras.length }} completadas
            </span>
          </div>
        </template>

        <!-- ════ PASO 4: Cobro + Confirmar ════ -->
        <template v-if="paso === 4">

          <!-- Resumen de solicitud -->
          <div class="rounded-lg border bg-muted/20 divide-y overflow-hidden">
            <div class="px-4 py-2.5 flex items-center gap-2">
              <ClipboardList class="h-4 w-4 text-primary shrink-0" />
              <span class="text-xs font-semibold uppercase tracking-wide text-muted-foreground">Resumen</span>
            </div>
            <div class="px-4 py-3 text-sm space-y-1.5">
              <div class="flex justify-between">
                <span class="text-muted-foreground">Paciente</span>
                <strong>{{ pacienteObj?.nombre ?? `#${paciente}` }}</strong>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Exámenes</span>
                <strong>{{ seleccionados.length }}</strong>
              </div>
              <div class="flex justify-between">
                <span class="text-muted-foreground">Muestras registradas</span>
                <span class="flex items-center gap-1 text-green-600 font-medium">
                  <CheckCircle2 class="h-3.5 w-3.5" />
                  {{ muestras.length }}
                </span>
              </div>
              <div class="flex justify-between font-semibold pt-1 border-t">
                <span>Total</span>
                <span>Bs. {{ montoTotal }}</span>
              </div>
            </div>

            <!-- Lista de exámenes + muestra -->
            <div class="px-4 py-3 space-y-1">
              <p class="text-xs text-muted-foreground font-medium mb-2">Detalle por examen</p>
              <div
                v-for="s in seleccionados" :key="s.examen.id"
                class="flex items-center justify-between text-xs py-1"
              >
                <div class="flex items-center gap-1.5">
                  <FlaskConical class="h-3 w-3 text-muted-foreground" />
                  <span class="font-medium">{{ s.examen.nombre_examen }}</span>
                </div>
                <div class="flex items-center gap-2">
                  <span class="text-muted-foreground">
                    {{ muestras.find(m => m.examen_id === s.examen.id)?.tipo ?? '—' }}
                  </span>
                  <span class="font-mono">Bs. {{ s.precio || '0.00' }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Cobro -->
          <div class="rounded-lg border overflow-hidden">
            <div class="flex items-center justify-between px-4 py-2.5 border-b bg-muted/30">
              <div class="flex items-center gap-2 text-sm font-semibold">
                <CreditCard class="h-4 w-4 text-primary" />
                Cobro
              </div>
              <label class="flex items-center gap-1.5 text-xs text-muted-foreground cursor-pointer">
                <input type="checkbox" v-model="incluirCobro" class="rounded" />
                Incluir cobro
              </label>
            </div>

            <div v-if="incluirCobro" class="p-4 space-y-3">
              <div class="space-y-1.5">
                <Label class="text-xs">Método de pago</Label>
                <Select v-model="metodoPago">
                  <SelectTrigger class="h-9 text-sm">
                    <SelectValue placeholder="Seleccionar método" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="efectivo">Efectivo</SelectItem>
                    <SelectItem value="tarjeta">Tarjeta</SelectItem>
                    <SelectItem value="transferencia">Transferencia</SelectItem>
                    <SelectItem value="qr">QR</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-1">
                <Label class="text-xs">Monto total (Bs.)</Label>
                <div class="h-9 rounded-md border bg-muted/20 px-3 flex items-center text-sm font-mono font-semibold">
                  {{ montoTotal }}
                </div>
                <p class="text-xs text-muted-foreground">Calculado desde los precios del paso 2.</p>
              </div>
            </div>
            <div v-else class="px-4 py-4 text-center text-sm text-muted-foreground">
              No se registrará cobro para esta solicitud.
            </div>
          </div>

          <!-- Observaciones -->
          <div v-if="observaciones" class="rounded-lg border bg-muted/20 px-4 py-2.5 text-sm">
            <p class="text-xs text-muted-foreground font-medium mb-0.5">Observaciones</p>
            <p>{{ observaciones }}</p>
          </div>

          <!-- Error / Éxito -->
          <div v-if="error" class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
            <AlertCircle class="h-4 w-4 shrink-0" />{{ error }}
          </div>
          <div v-if="mensajeExito" class="flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700">
            <CheckCircle2 class="h-4 w-4 shrink-0" />{{ mensajeExito }}
          </div>
        </template>

      </div>

      <!-- ── Footer ─────────────────────────────────────────────────────────── -->
      <DialogFooter class="px-6 py-4 border-t shrink-0 flex justify-between sm:justify-between gap-2">
        <Button
          variant="outline"
          @click="paso > 1 ? paso-- : emit('update:open', false)"
        >
          {{ paso > 1 ? 'Atrás' : 'Cancelar' }}
        </Button>

        <Button
          v-if="paso < TOTAL_PASOS"
          :disabled="!pasoValido"
          @click="paso++"
        >
          Continuar
        </Button>
        <Button
          v-else
          :disabled="solicitudesStore.saving || !!mensajeExito"
          class="gap-2"
          @click="guardar"
        >
          <Loader2 v-if="solicitudesStore.saving" class="h-4 w-4 animate-spin" />
          Crear solicitud
        </Button>
      </DialogFooter>

    </DialogContent>
  </Dialog>
</template>