<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  especieService, razaService, propietarioService,
  pacienteService, antecedenteService,
  type HistorialResponse,
} from '@/services/pacienteService'
import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Loader2, PawPrint, AlertCircle, ArrowLeft,
  Plus, Trash2, Check, X, ClipboardList, History, Stethoscope,
  ChevronDown, User, Phone, Mail, MapPin,
} from 'lucide-vue-next'
import type { Especie } from '@/models/especie'
import type { Raza } from '@/models/raza'
import type { Propietario } from '@/stores/propietarios'

const route  = useRoute()
const router = useRouter()
const pacienteId = computed(() => Number(route.params.id))

// ── Tabs ──────────────────────────────────────────────────────────────────────
type Tab = 'datos' | 'antecedentes' | 'historial'
const activeTab = ref<Tab>('datos')

// ── Catálogos ─────────────────────────────────────────────────────────────────
const especies     = ref<Especie[]>([])
const todasRazas   = ref<Raza[]>([])
const propietarios = ref<Propietario[]>([])

// ── Historial (datos del paciente + antecedentes + solicitudes) ───────────────
const historial    = ref<HistorialResponse | null>(null)
const loadingMain  = ref(true)
const globalError  = ref<string | null>(null)

const paciente     = computed(() => historial.value?.paciente ?? null)
const antecedentes = computed(() => historial.value?.antecedentes ?? [])
const solicitudes  = computed(() => historial.value?.solicitudes ?? [])

// Propietario completo seleccionado (para el panel de datos)
const propietarioActivo = computed(() => {
  if (!paciente.value?.propietario) return null
  return propietarios.value.find(p => p.id === paciente.value!.propietario) ?? null
})

function iniciales(nombre?: string, apellido?: string) {
  return `${nombre?.[0] ?? ''}${apellido?.[0] ?? ''}`.toUpperCase() || '?'
}

// ── Formulario edición ────────────────────────────────────────────────────────
const editEspecieId = ref('')
const editForm = ref({
  nombre:           '',
  sexo:             '',
  tamanio:          '',
  color:            '',
  fecha_nacimiento: '',
  propietario:      '',
  raza:             '',
})

function prefillForm() {
  const p = paciente.value
  if (!p) return
  editForm.value.nombre           = p.nombre
  editForm.value.sexo             = p.sexo ?? ''
  editForm.value.tamanio          = p.tamanio ?? ''
  editForm.value.color            = p.color ?? ''
  editForm.value.fecha_nacimiento = p.fecha_nacimiento ?? ''
  editForm.value.propietario      = p.propietario ? String(p.propietario) : ''
  editForm.value.raza             = p.raza ? String(p.raza) : ''
  const razaActual = todasRazas.value.find(r => r.id === p.raza)
  editEspecieId.value = razaActual ? String(razaActual.especie) : ''
}

async function loadHistorial() {
  loadingMain.value = true
  globalError.value = null
  try {
    const res = await pacienteService.getHistorial(pacienteId.value)
    historial.value = res.data as HistorialResponse
    prefillForm()
  } catch {
    globalError.value = 'No se pudo cargar el paciente'
  } finally {
    loadingMain.value = false
  }
}

onMounted(async () => {
  try {
    const [re, rr, rp] = await Promise.all([
      especieService.getAll(),
      razaService.getAll(),
      propietarioService.getAll(),
    ])
    especies.value     = (re.data as any).resultados ?? (re.data as any).results ?? re.data
    todasRazas.value   = (rr.data as any).resultados ?? (rr.data as any).results ?? rr.data
    propietarios.value = (rp.data as any).resultados ?? (rp.data as any).results ?? rp.data
  } catch {
    globalError.value = 'Error al cargar catálogos'
  }
  await loadHistorial()
})

// ── Antecedentes ──────────────────────────────────────────────────────────────
const showAddAntecedente       = ref(false)
const newAntecedente           = ref({ tipo: 'otro', descripcion: '' })
const antecedenteSaving        = ref(false)
const antecedenteError         = ref<string | null>(null)
const confirmDeleteAntecedenteId = ref<number | null>(null)

const TIPO_LABELS: Record<string, string> = {
  enfermedad_cronica: 'Enfermedad crónica',
  cirugia:            'Cirugía previa',
  alergia:            'Alergia',
  vacuna:             'Vacuna',
  medicamento:        'Medicamento habitual',
  otro:               'Otro',
}

const TIPO_VARIANTS: Record<string, string> = {
  enfermedad_cronica: 'destructive',
  cirugia:            'secondary',
  alergia:            'destructive',
  vacuna:             'default',
  medicamento:        'secondary',
  otro:               'outline',
}

async function handleAddAntecedente() {
  antecedenteError.value = null
  if (!newAntecedente.value.descripcion.trim()) {
    antecedenteError.value = 'La descripción es requerida'
    return
  }
  antecedenteSaving.value = true
  try {
    await antecedenteService.create({
      paciente:    pacienteId.value,
      tipo:        newAntecedente.value.tipo,
      descripcion: newAntecedente.value.descripcion.trim(),
    })
    newAntecedente.value = { tipo: 'otro', descripcion: '' }
    showAddAntecedente.value = false
    await loadHistorial()
  } catch {
    antecedenteError.value = 'Error al guardar el antecedente'
  } finally {
    antecedenteSaving.value = false
  }
}

async function handleDeleteAntecedente(id: number) {
  antecedenteError.value = null
  try {
    await antecedenteService.delete(id)
    confirmDeleteAntecedenteId.value = null
    await loadHistorial()
  } catch {
    antecedenteError.value = 'Error al eliminar el antecedente'
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatFechaHora(dt: string) {
  return new Date(dt).toLocaleString('es-BO', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function formatFecha(dt: string) {
  return new Date(dt).toLocaleDateString('es-BO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

const ESTADO_VARIANT: Record<string, string> = {
  pendiente:  'secondary',
  en_proceso: 'default',
  completada: 'outline',
  cancelada:  'destructive',
}

// ── Timeline expandible (estilo Angular) ──────────────────────────────────────
const historialAbierto = ref<number | null>(null)
function toggleHistorial(id: number) {
  historialAbierto.value = historialAbierto.value === id ? null : id
}
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
              <BreadcrumbLink href="/pacientes">Pacientes</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{{ paciente?.nombre ?? `#${pacienteId}` }}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <!-- Cargando -->
      <div v-if="loadingMain" class="flex items-center justify-center py-24 gap-3 text-muted-foreground">
        <Loader2 class="h-5 w-5 animate-spin" />
        <span class="text-sm">Cargando paciente…</span>
      </div>

      <!-- Error fatal -->
      <div v-else-if="globalError && !historial" class="p-6">
        <div class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-md">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ globalError }}
          <Button variant="ghost" size="sm" class="ml-auto" @click="router.push('/pacientes')">
            <ArrowLeft class="h-4 w-4" />
          </Button>
        </div>
      </div>

      <main v-else class="flex flex-1 flex-col gap-0">

        <!-- Botón volver -->
        <div class="px-6 pt-5">
          <button
            @click="router.push('/pacientes')"
            class="flex items-center gap-2 text-muted-foreground hover:text-foreground text-sm mb-4 transition-colors"
          >
            <ArrowLeft class="h-4 w-4" />
            Volver a la lista
          </button>
        </div>

        <!-- Tabs -->
        <div class="px-6">
          <div class="flex gap-1 border-b pb-0">
            <button
              v-for="tab in ([
                { id: 'datos',         label: 'Datos',         icon: PawPrint },
                { id: 'antecedentes',  label: 'Antecedentes',  icon: ClipboardList },
                { id: 'historial',     label: 'Historial',     icon: History },
              ] as const)"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'flex items-center gap-1.5 rounded-t-md px-3 py-2 text-sm font-medium transition-colors border-b-2',
                activeTab === tab.id
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground',
              ]"
            >
              <component :is="tab.icon" class="h-4 w-4" />
              {{ tab.label }}
              <Badge
                v-if="tab.id === 'antecedentes' && antecedentes.length"
                variant="secondary"
                class="ml-0.5 h-4 min-w-4 px-1 text-[10px]"
              >
                {{ antecedentes.length }}
              </Badge>
              <Badge
                v-if="tab.id === 'historial' && solicitudes.length"
                variant="secondary"
                class="ml-0.5 h-4 min-w-4 px-1 text-[10px]"
              >
                {{ solicitudes.length }}
              </Badge>
            </button>
          </div>
        </div>

        <!-- ── Tab: DATOS (estilo Angular: 2 paneles) ───────────────────────── -->
        <div v-if="activeTab === 'datos'" class="p-6 space-y-6">

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

            

            <!-- ── PANEL DERECHO: Propietario ─────────────────────────────── -->
            <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

              <div class="flex items-center gap-2 px-5 py-4 border-b">
                <User class="h-4 w-4 text-muted-foreground" />
                <h2 class="text-sm font-semibold text-foreground">Propietario</h2>
              </div>

              <template v-if="propietarioActivo">
                <div class="flex items-center gap-4 px-5 py-5 border-b">
                  <div class="w-14 h-14 bg-teal-100 rounded-full flex items-center justify-center text-teal-700 text-xl font-bold shrink-0">
                    {{ iniciales(propietarioActivo.usuario?.first_name, propietarioActivo.usuario?.last_name) }}
                  </div>
                  <div>
                    <p class="text-lg font-semibold text-foreground">
                      {{ propietarioActivo.usuario?.first_name }} {{ propietarioActivo.usuario?.last_name }}
                    </p>
                    <p class="text-sm text-muted-foreground">CI: {{ propietarioActivo.usuario?.ci }}</p>
                  </div>
                </div>

                <div class="divide-y">
                  <div class="flex px-5 py-3.5 items-center gap-2">
                    <Phone class="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span class="text-sm font-medium text-muted-foreground w-32 shrink-0">Teléfono</span>
                    <span class="text-sm text-foreground">{{ propietarioActivo.usuario?.telefono || '—' }}</span>
                  </div>
                  <div class="flex px-5 py-3.5 items-center gap-2">
                    <Mail class="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span class="text-sm font-medium text-muted-foreground w-32 shrink-0">Correo</span>
                    <span class="text-sm text-foreground">{{ propietarioActivo.usuario?.email || '—' }}</span>
                  </div>
                  <div class="flex px-5 py-3.5 items-center gap-2">
                    <MapPin class="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span class="text-sm font-medium text-muted-foreground w-32 shrink-0">Dirección</span>
                    <span class="text-sm text-foreground">{{ propietarioActivo.usuario?.direccion || '—' }}</span>
                  </div>
                </div>
              </template>

              <div v-else class="px-5 py-10 text-center text-sm text-muted-foreground">
                Sin propietario asignado
              </div>
            </div>

            <!-- ── PANEL IZQUIERDO: Paciente (avatar + datos) ────────────── -->
            <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

              <div class="flex items-center gap-2 px-5 py-4 border-b">
                <PawPrint class="h-4 w-4 text-muted-foreground" />
                <h2 class="text-sm font-semibold text-foreground">Paciente</h2>
              </div>

              <div class="flex items-center gap-4 px-5 py-5 border-b">
                <div class="w-14 h-14 bg-primary/10 rounded-full flex items-center justify-center text-primary text-xl font-bold shrink-0">
                  {{ iniciales(paciente?.nombre) }}
                </div>
                <div>
                  <p class="text-lg font-semibold text-foreground">{{ paciente?.nombre }}</p>
                  <p class="text-sm text-muted-foreground">
                    {{ paciente?.especie_nombre }} · {{ paciente?.raza_nombre }}
                  </p>
                </div>
              </div>

              <div class="divide-y">
                <div class="flex px-5 py-3.5">
                  <span class="text-sm font-medium text-muted-foreground w-36 shrink-0">Sexo</span>
                  <span class="text-sm text-foreground capitalize">{{ paciente?.sexo || '—' }}</span>
                </div>
                <div class="flex px-5 py-3.5">
                  <span class="text-sm font-medium text-muted-foreground w-36 shrink-0">Tamaño</span>
                  <span class="text-sm text-foreground capitalize">{{ paciente?.tamanio || '—' }}</span>
                </div>
                <div class="flex px-5 py-3.5">
                  <span class="text-sm font-medium text-muted-foreground w-36 shrink-0">Color</span>
                  <span class="text-sm text-foreground">{{ paciente?.color || '—' }}</span>
                </div>
                <div class="flex px-5 py-3.5">
                  <span class="text-sm font-medium text-muted-foreground w-36 shrink-0">F. nacimiento</span>
                  <span class="text-sm text-foreground">
                    {{ paciente?.fecha_nacimiento ? formatFecha(paciente.fecha_nacimiento) : '—' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Tab: ANTECEDENTES (sin cambios de formato) ────────────────── -->
        <div v-else-if="activeTab === 'antecedentes'" class="p-6">
          <div class="mx-auto max-w-3xl space-y-4">

            <div v-if="antecedenteError" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              <AlertCircle class="h-4 w-4 shrink-0" />
              {{ antecedenteError }}
              <button class="ml-auto" @click="antecedenteError = null"><X class="h-4 w-4" /></button>
            </div>

            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold">Antecedentes clínicos</h2>
                <p class="text-sm text-muted-foreground">
                  {{ antecedentes.length }} registro{{ antecedentes.length !== 1 ? 's' : '' }}
                </p>
              </div>
              <Button size="sm" class="gap-1.5" @click="showAddAntecedente = !showAddAntecedente">
                <Plus class="h-4 w-4" />
                Agregar
              </Button>
            </div>

            <div v-if="showAddAntecedente" class="rounded-xl border bg-white p-4 shadow-xs space-y-3">
              <h3 class="text-sm font-semibold">Nuevo antecedente</h3>
              <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div class="space-y-1.5">
                  <label class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Tipo</label>
                  <Select v-model="newAntecedente.tipo">
                    <SelectTrigger>
                      <SelectValue placeholder="Tipo…" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem v-for="(label, key) in TIPO_LABELS" :key="key" :value="key">
                        {{ label }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div class="sm:col-span-1 space-y-1.5 sm:col-start-1 row-start-2">
                  <label class="text-xs font-medium text-muted-foreground uppercase tracking-wide">Descripción</label>
                  <Input
                    v-model="newAntecedente.descripcion"
                    placeholder="Descripción del antecedente…"
                    @keydown.enter.prevent="handleAddAntecedente"
                  />
                </div>
              </div>
              <div class="flex items-center justify-end gap-2 pt-1">
                <Button variant="outline" size="sm" @click="showAddAntecedente = false; antecedenteError = null">
                  Cancelar
                </Button>
                <Button size="sm" :disabled="antecedenteSaving" class="gap-1.5" @click="handleAddAntecedente">
                  <Loader2 v-if="antecedenteSaving" class="h-4 w-4 animate-spin" />
                  Guardar
                </Button>
              </div>
            </div>

            <div class="rounded-xl border bg-white shadow-xs overflow-hidden">
              <div v-if="antecedentes.length === 0" class="px-4 py-10 text-center text-sm text-muted-foreground">
                No hay antecedentes registrados para este paciente.
              </div>
              <table v-else class="w-full text-sm">
                <thead>
                  <tr class="border-b bg-muted/40">
                    <th class="px-4 py-3 text-left font-semibold">Tipo</th>
                    <th class="px-4 py-3 text-left font-semibold">Descripción</th>
                    <th class="px-4 py-3 text-left font-semibold">Registrado</th>
                    <th class="px-4 py-3 text-center font-semibold w-20">Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="a in antecedentes"
                    :key="a.id"
                    class="border-b last:border-0 hover:bg-muted/20 transition-colors"
                  >
                    <td class="px-4 py-3">
                      <Badge :variant="(TIPO_VARIANTS[a.tipo] ?? 'outline') as any" class="whitespace-nowrap">
                        {{ a.tipo_display ?? TIPO_LABELS[a.tipo] ?? a.tipo }}
                      </Badge>
                    </td>
                    <td class="px-4 py-3 text-muted-foreground max-w-xs">{{ a.descripcion }}</td>
                    <td class="px-4 py-3 text-muted-foreground whitespace-nowrap">
                      {{ formatFechaHora(a.fecha_registro) }}
                    </td>
                    <td class="px-4 py-3">
                      <div v-if="confirmDeleteAntecedenteId !== a.id" class="flex justify-center">
                        <button
                          @click="confirmDeleteAntecedenteId = a.id"
                          class="p-1.5 rounded-md text-red-500 hover:bg-red-50 transition-colors"
                          title="Eliminar"
                        >
                          <Trash2 class="h-4 w-4" />
                        </button>
                      </div>
                      <div v-else class="flex items-center justify-center gap-1">
                        <button
                          @click="handleDeleteAntecedente(a.id)"
                          class="p-1.5 rounded-md bg-red-500 text-white hover:bg-red-600 transition-colors"
                          title="Confirmar"
                        >
                          <Check class="h-4 w-4" />
                        </button>
                        <button
                          @click="confirmDeleteAntecedenteId = null"
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
        </div>

        <!-- ── Tab: HISTORIAL (timeline expandible estilo Angular) ────────── -->
        <div v-else-if="activeTab === 'historial'" class="p-6">
          <div class="mx-auto max-w-4xl">

            <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

              <!-- Header historial -->
              <div class="flex items-center gap-3 px-5 py-4 border-b">
                <History class="h-4 w-4 text-muted-foreground" />
                <h2 class="text-sm font-semibold text-foreground">
                  Historial de solicitudes — {{ paciente?.nombre }}
                </h2>
                <Badge variant="secondary" class="text-[10px]">
                  {{ historial?.total_visitas ?? 0 }} visita{{ (historial?.total_visitas ?? 0) !== 1 ? 's' : '' }}
                </Badge>
              </div>

              <!-- Vacío -->
              <div v-if="solicitudes.length === 0" class="py-12 text-center text-muted-foreground">
                <ClipboardList class="w-10 h-10 mx-auto mb-3 text-muted-foreground/30" />
                <p class="text-sm">Sin solicitudes registradas para {{ paciente?.nombre }}</p>
                <p class="text-xs mt-1 text-muted-foreground/60">El historial se genera al registrar una solicitud de examen</p>
              </div>

              <!-- Timeline de solicitudes -->
              <div v-else class="divide-y">
                <div v-for="s in solicitudes" :key="s.id" class="px-5 py-4">

                  <!-- Fila resumen (siempre visible) -->
                  <div
                    @click="toggleHistorial(s.id)"
                    class="flex items-center gap-4 cursor-pointer group"
                  >
                    <!-- Dot timeline -->
                    <div class="w-3 h-3 rounded-full bg-primary shrink-0 ring-2 ring-primary/20"></div>

                    <!-- Código + fecha + estado -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-3 flex-wrap">
                        <span class="text-sm font-semibold text-foreground">{{ s.codigo }}</span>
                        <span class="text-sm text-muted-foreground">{{ formatFechaHora(s.fecha_solicitud) }}</span>
                        <Badge :variant="(ESTADO_VARIANT[s.estado] ?? 'outline') as any" class="capitalize text-[10px]">
                          {{ s.estado.replace('_', ' ') }}
                        </Badge>
                      </div>
                      <div class="flex items-center gap-4 mt-1 text-xs text-muted-foreground flex-wrap">
                        <span v-if="s.medico_veterinario" class="flex items-center gap-1">
                          <Stethoscope class="h-3 w-3" />
                          Dr. {{ s.medico_veterinario }}
                        </span>
                        <span v-if="s.examenes.length">
                          {{ s.examenes.length }} examen{{ s.examenes.length !== 1 ? 'es' : '' }}
                        </span>
                      </div>
                    </div>

                    <!-- Chevron -->
                    <ChevronDown
                      :class="['h-4 w-4 text-muted-foreground transition-transform shrink-0', historialAbierto === s.id ? 'rotate-180' : '']"
                    />
                  </div>

                  <!-- Detalle expandible -->
                  <div v-if="historialAbierto === s.id" class="mt-4 ml-7 grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3 text-sm border-t pt-4">

                    <div v-if="s.observaciones" class="md:col-span-2">
                      <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Observaciones</p>
                      <p class="text-foreground italic">"{{ s.observaciones }}"</p>
                    </div>

                    <div v-if="s.examenes.length" class="md:col-span-2">
                      <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1.5">Exámenes</p>
                      <div class="flex flex-wrap gap-2">
                        <div
                          v-for="(ex, i) in s.examenes"
                          :key="i"
                          class="rounded-md border bg-muted/40 px-2.5 py-1 text-xs"
                        >
                          {{ ex.examen ?? '—' }}
                          <span class="ml-1 text-muted-foreground">Bs {{ ex.precio_aplicado }}</span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <p class="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Fecha de solicitud</p>
                      <p class="text-muted-foreground text-xs">{{ formatFechaHora(s.fecha_solicitud) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>
</template>