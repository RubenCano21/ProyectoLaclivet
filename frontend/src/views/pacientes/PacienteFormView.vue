<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { watchDebounced } from '@vueuse/core'
import {especieService, razaService, pacienteService
} from '@/services/pacienteService'
import { usePropietariosStore, type Propietario } from '@/stores/propietarios'
import {Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  Search, Loader2, AlertCircle, UserPlus, PawPrint, User,
} from 'lucide-vue-next'
import PropietarioForm from './PropietarioForm.vue'
import type { Especie } from '@/models/especie.ts'
import type { Paciente } from '@/models/paciente.ts'
import type { Raza } from '@/models/raza.ts'

const props = defineProps<{
  open: boolean
  paciente?: Paciente | null // null/undefined = modo crear
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'saved'): void
}>()

const propietariosStore = usePropietariosStore()

type Step = 'propietario' | 'paciente'
const step = ref<Step>('paciente')
const isEdit = computed(() => !!props.paciente?.id)

// ── Catálogos especie/raza (sólo del paciente) ──────────────────
const especies   = ref<Especie[]>([])
const todasRazas = ref<Raza[]>([])
const loadingCatalogos = ref(false)
let catalogosCargados = false

async function cargarCatalogos() {
  if (catalogosCargados) return
  loadingCatalogos.value = true
  try {
    const [re, rr] = await Promise.all([especieService.getAll(), razaService.getAll()])
    especies.value   = (re.data as any).resultados ?? (re.data as any).results ?? re.data
    todasRazas.value = (rr.data as any).resultados ?? (rr.data as any).results ?? rr.data
    catalogosCargados = true
  } catch {
    globalError.value = 'Error al cargar catálogos'
  } finally {
    loadingCatalogos.value = false
  }
}

// ── Paso 1: buscar propietario (usa el store) ───────────────────
const buscarPropietario = ref('')
const propietarioSeleccionado = ref<Propietario | null>(null)

watchDebounced(
  buscarPropietario,
  (q) => {
    if (step.value === 'propietario') {
      propietariosStore.fetchAll(1, q)
    }
  },
  { debounce: 300 },
)

/*const propietariosFiltrados = computed(() => {
  const lista = propietariosStore.items
  const q = buscarPropietario.value.trim().toLowerCase()
  if (!q) return lista
  return lista.filter((p: Propietario) =>
    `${p.nombre} ${p.apellido}`.toLowerCase().includes(q) ||
    p.ci.toLowerCase().includes(q) ||
    (p.telefono ?? '').toLowerCase().includes(q),
  )
})*/

function elegirPropietario(p: Propietario) {
  propietarioSeleccionado.value = p
  form.value.propietario = String(p.id)
  step.value = 'paciente'
}

// ── Sub-modal: registrar propietario nuevo ───────────────────────
const showPropietarioModal = ref(false)

function abrirNuevoPropietario() {
  emit('update:open', false)

  nextTick(() => {
    showPropietarioModal.value = true
  })
}

// Cuando PropietarioModal emite 'saved', el store ya tiene el nuevo registro.
// Lo identificamos por CI (lo más confiable) o, si no, tomamos el último creado.
async function onPropietarioGuardado() {
  const creado = propietariosStore.items[0]
  showPropietarioModal.value = false

  emit('update:open', true)
  await nextTick()
  if (creado) elegirPropietario(creado)
}

// ── Paso 2: datos del paciente ───────────────────────────────────
const especieId = ref('')
const form = ref({
  nombre: '', sexo: '', tamanio: '', color: '',
  fecha_nacimiento: '', propietario: '', raza: '',
})

const razasFiltradas = computed(() =>
  todasRazas.value.filter(r => String(r.especie) === especieId.value),
)
function onEspecieChange() { form.value.raza = '' }

const saving = ref(false)
const errorPaciente = ref<string | null>(null)
const globalError = ref<string | null>(null)

function resetTodo() {
  step.value = isEdit.value ? 'paciente' : 'propietario'
  buscarPropietario.value = ''
  propietarioSeleccionado.value = null
  errorPaciente.value = null
  globalError.value = null
  especieId.value = ''
  form.value = { nombre: '', sexo: '', tamanio: '', color: '', fecha_nacimiento: '', propietario: '', raza: '' }
}

function prefillEdicion() {
  const p = props.paciente
  if (!p) return
  form.value.nombre           = p.nombre
  form.value.sexo             = p.sexo ?? ''
  form.value.tamanio          = p.tamanio ?? ''
  form.value.color            = p.color ?? ''
  form.value.fecha_nacimiento = p.fecha_nacimiento ?? ''
  form.value.propietario      = p.propietario ? String(p.propietario) : ''
  form.value.raza             = p.raza ? String(p.raza) : ''
  const razaActual = todasRazas.value.find(r => r.id === p.raza)
  especieId.value = razaActual ? String(razaActual.especie) : ''
  propietarioSeleccionado.value =
    propietariosStore.items.find((pr: Propietario) => pr.id === p.propietario) ?? null
}

const reabriendoTrasPropietario = ref(false)

watch(() => props.open, async (isOpen) => {
  if (!isOpen) return
  if (reabriendoTrasPropietario.value){
    reabriendoTrasPropietario.value = false
    return
  }
  resetTodo()
  if (!propietariosStore.items.length) {
    await propietariosStore.fetchAll()
  }
  await cargarCatalogos()
  await nextTick()
  if (isEdit.value) prefillEdicion()
})

function volverAElegirPropietario() {
  step.value = 'propietario'
}

async function handleGuardarPaciente() {
  errorPaciente.value = null
  if (!form.value.nombre.trim()) {
    errorPaciente.value = 'El nombre del paciente es requerido'
    return
  }
  if (!form.value.propietario) {
    errorPaciente.value = 'Debes seleccionar un propietario'
    return
  }
  saving.value = true
  try {
    const payload = {
      nombre:           form.value.nombre.trim(),
      sexo:             form.value.sexo || '',
      tamanio:          form.value.tamanio || '',
      color:            form.value.color.trim(),
      fecha_nacimiento: form.value.fecha_nacimiento || null,
      propietario:      Number(form.value.propietario),
      raza:             form.value.raza ? Number(form.value.raza) : (null as any),
    }
    if (isEdit.value && props.paciente) {
      await pacienteService.patch(props.paciente.id, payload as any)
    } else {
      await pacienteService.create(payload as any)
    }
    emit('saved')
    emit('update:open', false)
  } catch (e: any) {
    const data = e.response?.data
    errorPaciente.value = data && typeof data === 'object'
      ? Object.entries(data).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : v}`).join(' | ')
      : 'Error al guardar el paciente'
  } finally {
    saving.value = false
  }
}

function close() {
  emit('update:open', false)
}
</script>

<template>
  <Dialog :open="open" @update:open="(v) => emit('update:open', v)">
    <DialogContent class="sm:max-w-lg max-h-[90vh] overflow-y-auto">

      <!-- ════════ PASO 1: Elegir propietario ════════ -->
      <template v-if="step === 'propietario'">
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2">
            <User class="h-5 w-5 text-primary" />
            ¿Quién es el propietario?
          </DialogTitle>
          <DialogDescription>
            Busca al propietario por nombre, apellido o CI. Si aún no está registrado, puedes crearlo aquí mismo.
          </DialogDescription>
        </DialogHeader>

        <div class="space-y-3">
          <div class="relative">
            <Search class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
            <Input v-model="buscarPropietario" placeholder="Buscar por nombre, apellido o CI…" class="pl-9" autofocus />
          </div>

          <div v-if="propietariosStore.loading" class="flex items-center justify-center gap-2 py-8 text-muted-foreground">
            <Loader2 class="h-4 w-4 animate-spin" />
            <span class="text-sm">Cargando…</span>
          </div>

          <div v-else class="max-h-72 overflow-y-auto rounded-lg border divide-y">
            <button
              v-for="p in propietariosStore.items"
  :key="p.id"
  type="button"
  @click="elegirPropietario(p)"
              class="w-full flex items-center justify-between px-3 py-2.5 text-left hover:bg-muted/40 transition-colors"
            >
              <div>
                <p class="text-sm font-medium">{{ p.usuario?.first_name }} {{ p.usuario?.last_name }}</p>
                <p class="text-xs text-muted-foreground">
                  CI: {{ p.usuario?.ci }}<span v-if="p.usuario?.telefono"> · {{ p.usuario.telefono }}</span>
                </p>
              </div>
            </button>

            <div v-if="propietariosStore.total != 0" class="px-3 py-6 text-center text-sm text-muted-foreground">
              No se encontró ningún propietario{{ buscarPropietario ? ` para "${buscarPropietario}"` : '' }}.
            </div>
          </div>

          <Button type="button" variant="outline" class="w-full gap-2" @click="abrirNuevoPropietario">
            <UserPlus class="h-4 w-4" />
            Registrar nuevo propietario{{ buscarPropietario ? `: "${buscarPropietario}"` : '' }}
          </Button>
        </div>
      </template>

      <!-- ════════ PASO 2: Datos del paciente ════════ -->
      <template v-else>
        <DialogHeader>
          <DialogTitle class="flex items-center gap-2">
            <PawPrint class="h-5 w-5 text-primary" />
            {{ isEdit ? 'Editar paciente' : 'Nuevo paciente' }}
          </DialogTitle>
          <DialogDescription>
            {{ isEdit ? 'Actualiza los datos del paciente.' : 'Completa los datos del paciente.' }}
          </DialogDescription>
        </DialogHeader>

        <!-- Propietario elegido -->
        <div class="flex items-center justify-between rounded-lg border bg-muted/30 px-3 py-2">
          <div class="flex items-center gap-2 text-sm">
            <User class="h-4 w-4 text-muted-foreground" />
            <span v-if="propietarioSeleccionado" class="font-medium">
              {{ propietarioSeleccionado.usuario?.first_name }} {{ propietarioSeleccionado.usuario?.last_name }}
              <span class="text-muted-foreground font-normal">· CI {{ propietarioSeleccionado.usuario?.ci }}</span>
            </span>
            <span v-else class="text-muted-foreground">Sin propietario seleccionado</span>
          </div>
          <Button type="button" variant="ghost" size="sm" @click="volverAElegirPropietario">Cambiar</Button>
        </div>

        <div v-if="errorPaciente" class="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
          <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
          {{ errorPaciente }}
        </div>

        <div class="space-y-3">
          <div class="space-y-1.5">
            <label class="text-sm font-medium">Nombre <span class="text-red-500">*</span></label>
            <Input v-model="form.nombre" placeholder="Ej: Max" autofocus />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Especie</label>
              <Select v-model="especieId" @update:model-value="onEspecieChange">
                <SelectTrigger><SelectValue placeholder="Seleccionar…" /></SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="e in especies" :key="e.id" :value="String(e.id)">{{ e.nombre }}</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Raza</label>
              <Select v-model="form.raza" :disabled="!especieId || razasFiltradas.length === 0">
                <SelectTrigger><SelectValue placeholder="Seleccionar…" /></SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="r in razasFiltradas" :key="r.id" :value="String(r.id)">{{ r.nombre }}</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Sexo</label>
              <Select v-model="form.sexo">
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
              <Select v-model="form.tamanio">
                <SelectTrigger><SelectValue placeholder="Seleccionar…" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="pequeño">Pequeño</SelectItem>
                  <SelectItem value="mediano">Mediano</SelectItem>
                  <SelectItem value="grande">Grande</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Color</label>
              <Input v-model="form.color" placeholder="Ej: café, negro…" />
            </div>
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Fecha de nacimiento</label>
              <Input type="date" v-model="form.fecha_nacimiento" />
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 pt-3 border-t">
          <Button type="button" variant="outline" @click="close">Cancelar</Button>
          <Button type="button" :disabled="saving" class="gap-2" @click="handleGuardarPaciente">
            <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
            {{ isEdit ? 'Guardar cambios' : 'Registrar paciente' }}
          </Button>
        </div>
      </template>

    </DialogContent>
  </Dialog>

  <!-- Sub-modal: registrar propietario (el que ya tienes) -->
  <PropietarioForm
    v-model:open="showPropietarioModal"
    @saved="onPropietarioGuardado"
  />
</template>