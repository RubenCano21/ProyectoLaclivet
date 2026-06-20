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
  Loader2, PawPrint, AlertCircle, Save, ArrowLeft,
  Plus, Trash2, Check, X, ClipboardList, History, Stethoscope,
} from 'lucide-vue-next'
import type { Especie } from '@/models/especie'
import type { Propietario } from '@/models/propietario'
import type { Raza } from '@/models/raza'

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
const saving      = ref(false)
const saveSuccess = ref(false)
const saveError   = ref<string | null>(null)

const razasFiltradas = computed(() =>
  todasRazas.value.filter(r => String(r.especie) === editEspecieId.value),
)

function onEspecieChange() {
  editForm.value.raza = ''
}

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
  // Determinar especie desde la raza actual
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

// ── Guardar datos del paciente ────────────────────────────────────────────────
async function handleSaveDatos() {
  saveError.value   = null
  saveSuccess.value = false
  if (!editForm.value.nombre.trim()) {
    saveError.value = 'El nombre es requerido'
    return
  }
  saving.value = true
  try {
    await pacienteService.patch(pacienteId.value, {
      nombre:           editForm.value.nombre.trim(),
      sexo:             editForm.value.sexo || '',
      tamanio:          editForm.value.tamanio || '',
      color:            editForm.value.color.trim(),
      fecha_nacimiento: editForm.value.fecha_nacimiento || null,
      propietario:      editForm.value.propietario ? Number(editForm.value.propietario) : (null as any),
      raza:             editForm.value.raza ? Number(editForm.value.raza) : (null as any),
    } as any)
    saveSuccess.value = true
    await loadHistorial()
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch (e: any) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      saveError.value = Object.entries(data)
        .map(([k, v]) => `${k}: ${Array.isArray(v) ? (v as string[]).join(', ') : v}`)
        .join(' | ')
    } else {
      saveError.value = 'Error al guardar'
    }
  } finally {
    saving.value = false
  }
}

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

const ESTADO_VARIANT: Record<string, string> = {
  pendiente:  'secondary',
  en_proceso: 'default',
  completada: 'outline',
  cancelada:  'destructive',
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

        <!-- Cabecera del paciente -->
        <div class="border-b bg-muted/20 px-6 py-5">
          <div class="flex items-center gap-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
              <PawPrint class="h-6 w-6" />
            </div>
            <div>
              <h1 class="text-xl font-bold leading-tight">{{ paciente?.nombre }}</h1>
              <p class="text-sm text-muted-foreground">
                {{ paciente?.especie_nombre }} · {{ paciente?.raza_nombre }}
                <span v-if="paciente?.propietario_nombre"> · {{ paciente?.propietario_nombre }}</span>
              </p>
            </div>
            <Button variant="outline" size="sm" class="ml-auto gap-1.5" @click="router.push('/pacientes')">
              <ArrowLeft class="h-4 w-4" />
              Volver
            </Button>
          </div>

          <!-- Tabs -->
          <div class="mt-4 flex gap-1">
            <button
              v-for="tab in ([
                { id: 'datos',         label: 'Datos',         icon: PawPrint },
                { id: 'antecedentes',  label: 'Antecedentes',  icon: ClipboardList },
                { id: 'historial',     label: 'Historial',     icon: History },
              ] as const)"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'bg-white shadow-sm text-primary border'
                  : 'text-muted-foreground hover:text-foreground hover:bg-white/60',
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

        <!-- ── Tab: DATOS ─────────────────────────────────────────────────── -->
        <div v-if="activeTab === 'datos'" class="p-6">
          <div class="mx-auto max-w-2xl space-y-5">

            <!-- Éxito guardado -->
            <div v-if="saveSuccess" class="flex items-center gap-2 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">
              <Check class="h-4 w-4 shrink-0" />
              Datos guardados correctamente
            </div>

            <!-- Error guardado -->
            <div v-if="saveError" class="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
              {{ saveError }}
            </div>

            <form @submit.prevent="handleSaveDatos" class="rounded-xl border bg-white p-6 shadow-xs space-y-5">

              <!-- Nombre -->
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Nombre <span class="text-red-500">*</span></label>
                <Input v-model="editForm.nombre" placeholder="Nombre del paciente" />
              </div>

              <!-- Especie + Raza -->
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div class="space-y-1.5">
                  <label class="text-sm font-medium">Especie</label>
                  <Select v-model="editEspecieId" @update:model-value="onEspecieChange">
                    <SelectTrigger>
                      <SelectValue placeholder="Seleccionar especie…" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem v-for="e in especies" :key="e.id" :value="String(e.id)">
                        {{ e.nombre }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div class="space-y-1.5">
                  <label class="text-sm font-medium">Raza</label>
                  <Select v-model="editForm.raza" :disabled="!editEspecieId || razasFiltradas.length === 0">
                    <SelectTrigger>
                      <SelectValue placeholder="Seleccionar raza…" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem v-for="r in razasFiltradas" :key="r.id" :value="String(r.id)">
                        {{ r.nombre }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <!-- Sexo + Tamaño -->
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div class="space-y-1.5">
                  <label class="text-sm font-medium">Sexo</label>
                  <Select v-model="editForm.sexo">
                    <SelectTrigger><SelectValue placeholder="Seleccionar…" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="macho">Macho</SelectItem>
                      <SelectItem value="hembra">Hembra</SelectItem>
                      <SelectItem value="desconocido">Desconocido</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div class="space-y-1.5">
                  <label class="text-sm font-medium">Tamaño</label>
                  <Select v-model="editForm.tamanio">
                    <SelectTrigger><SelectValue placeholder="Seleccionar…" /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pequeño">Pequeño</SelectItem>
                      <SelectItem value="mediano">Mediano</SelectItem>
                      <SelectItem value="grande">Grande</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <!-- Color + Fecha nacimiento -->
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div class="space-y-1.5">
                  <label class="text-sm font-medium">Color</label>
                  <Input v-model="editForm.color" placeholder="Ej: café, negro y blanco…" />
                </div>
                <div class="space-y-1.5">
                  <label class="text-sm font-medium">Fecha de nacimiento</label>
                  <Input type="date" v-model="editForm.fecha_nacimiento" />
                </div>
              </div>

              <!-- Propietario -->
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Propietario</label>
                <Select v-model="editForm.propietario">
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar propietario…" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="p in propietarios" :key="p.id" :value="String(p.id)">
                      {{ p.nombre }} {{ p.apellido }} — {{ p.ci }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <!-- Acciones -->
              <div class="flex items-center justify-end gap-3 pt-2 border-t">
                <Button type="button" variant="outline" @click="prefillForm">
                  Descartar cambios
                </Button>
                <Button type="submit" :disabled="saving" class="gap-2">
                  <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
                  <Save v-else class="h-4 w-4" />
                  Guardar cambios
                </Button>
              </div>
            </form>
          </div>
        </div>

        <!-- ── Tab: ANTECEDENTES ──────────────────────────────────────────── -->
        <div v-else-if="activeTab === 'antecedentes'" class="p-6">
          <div class="mx-auto max-w-3xl space-y-4">

            <!-- Error -->
            <div v-if="antecedenteError" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              <AlertCircle class="h-4 w-4 shrink-0" />
              {{ antecedenteError }}
              <button class="ml-auto" @click="antecedenteError = null"><X class="h-4 w-4" /></button>
            </div>

            <!-- Cabecera sección -->
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

            <!-- Formulario agregar -->
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

            <!-- Lista antecedentes -->
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

        <!-- ── Tab: HISTORIAL ────────────────────────────────────────────── -->
        <div v-else-if="activeTab === 'historial'" class="p-6">
          <div class="mx-auto max-w-4xl space-y-4">

            <div class="flex items-center justify-between">
              <div>
                <h2 class="text-base font-semibold">Historial de solicitudes</h2>
                <p class="text-sm text-muted-foreground">
                  {{ historial?.total_visitas ?? 0 }} visita{{ (historial?.total_visitas ?? 0) !== 1 ? 's' : '' }} registrada{{ (historial?.total_visitas ?? 0) !== 1 ? 's' : '' }}
                </p>
              </div>
            </div>

            <div v-if="solicitudes.length === 0" class="rounded-xl border bg-white p-10 text-center text-sm text-muted-foreground shadow-xs">
              No hay solicitudes registradas para este paciente.
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="s in solicitudes"
                :key="s.id"
                class="rounded-xl border bg-white p-4 shadow-xs space-y-3"
              >
                <!-- Cabecera solicitud -->
                <div class="flex items-start justify-between gap-4">
                  <div class="flex items-center gap-2">
                    <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                      <Stethoscope class="h-4 w-4" />
                    </div>
                    <div>
                      <span class="font-semibold text-sm">{{ s.codigo }}</span>
                      <p class="text-xs text-muted-foreground">{{ formatFechaHora(s.fecha_solicitud) }}</p>
                    </div>
                  </div>
                  <Badge :variant="(ESTADO_VARIANT[s.estado] ?? 'outline') as any" class="capitalize shrink-0">
                    {{ s.estado.replace('_', ' ') }}
                  </Badge>
                </div>

                <!-- Médico -->
                <p v-if="s.medico_veterinario" class="text-sm text-muted-foreground">
                  <span class="font-medium text-foreground">Médico:</span> {{ s.medico_veterinario }}
                </p>

                <!-- Observaciones -->
                <p v-if="s.observaciones" class="text-sm text-muted-foreground italic">
                  "{{ s.observaciones }}"
                </p>

                <!-- Exámenes -->
                <div v-if="s.examenes.length > 0">
                  <p class="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1.5">Exámenes</p>
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
              </div>
            </div>

          </div>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>
</template>

