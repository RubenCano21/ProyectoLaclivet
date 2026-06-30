<!-- src/views/muestras/MuestraFormModal.vue -->
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useMuestrasStore, type MuestraForm } from '@/stores/muestras'
import { pacienteService } from '@/services/pacienteService'
import type { Muestra } from '@/models/muestra'
import type { Paciente } from '@/models/paciente'

import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import { Loader2, AlertCircle, FlaskConical, Search, ChevronsUpDown, X } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  muestra?: Muestra | null
  // ── Props opcionales para el sub-flujo de solicitudes ─────────────────────
  // Cuando se llama desde NuevaSolicitudModal, el paciente ya está elegido.
  pacientePreseleccionado?: { id: number; nombre: string } | null
  // Texto adicional en el título, p.ej. "Muestra para: Hemograma (1/2)"
  tituloContexto?: string
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'saved'): void
}>()

const store   = useMuestrasStore()
const isEdit  = computed(() => !!props.muestra)
// Modo embed: paciente ya viene fijado desde fuera
const esEmbed = computed(() => !!props.pacientePreseleccionado && !props.muestra)

// ── Constantes ────────────────────────────────────────────────────────────────
const ESTADOS = [
  { value: 'pendiente',  label: 'Pendiente' },
  { value: 'en_proceso', label: 'En proceso' },
  { value: 'completada', label: 'Completada' },
  { value: 'rechazada',  label: 'Rechazada' },
]

const TIPOS = [
  { value: 'sangre',  label: 'Sangre' },
  { value: 'orina',   label: 'Orina' },
  { value: 'heces',   label: 'Heces' },
  { value: 'tejido',  label: 'Tejido' },
  { value: 'otro',    label: 'Otro' },
]

// ── Formulario ────────────────────────────────────────────────────────────────
const defaultForm = (): MuestraForm => ({
  paciente:        null,
  tipo:            '',
  estado:          'pendiente',
  fecha_recepcion: new Date().toISOString().slice(0, 10),
  observaciones:   '',
})

const form      = ref<MuestraForm>(defaultForm())
const formError = ref<string | null>(null)

// ── Selector de paciente (solo cuando NO viene preseleccionado) ────────────────
const pacientes            = ref<Paciente[]>([])
const pacienteSearch       = ref('')
const pacienteDropdownOpen = ref(false)
const selectedPaciente     = ref<Paciente | null>(null)
const loadingPacientes     = ref(false)

const filteredPacientes = computed(() => {
  const q = pacienteSearch.value.trim().toLowerCase()
  if (!q) return pacientes.value
  return pacientes.value.filter(p =>
    p.nombre.toLowerCase().includes(q) ||
    p.propietario_nombre?.toLowerCase().includes(q) ||
    String(p.id).includes(q),
  )
})

async function loadPacientes() {
  loadingPacientes.value = true
  try {
    const { data } = await pacienteService.getAll(1)
    pacientes.value = data.resultados ?? data
  } catch {
    pacientes.value = []
  } finally {
    loadingPacientes.value = false
  }
}

function selectPaciente(p: Paciente) {
  selectedPaciente.value = p
  form.value.paciente = p.id
  pacienteSearch.value = ''
  pacienteDropdownOpen.value = false
}

function clearPaciente() {
  selectedPaciente.value = null
  form.value.paciente = null
}

// ── Sincronización al abrir ───────────────────────────────────────────────────
watch(
  () => [props.open, props.muestra, props.pacientePreseleccionado],
  async () => {
    if (!props.open) return
    formError.value = null
    pacienteDropdownOpen.value = false
    pacienteSearch.value = ''

    if (props.muestra) {
      // Modo edición
      form.value = {
        paciente:        props.muestra.paciente,
        tipo:            props.muestra.tipo ?? '',
        estado:          props.muestra.estado,
        fecha_recepcion: props.muestra.fecha_recepcion ?? new Date().toISOString().slice(0, 10),
        observaciones:   props.muestra.observaciones ?? '',
      }
    } else {
      form.value = defaultForm()
      selectedPaciente.value = null
    }

    if (esEmbed.value && props.pacientePreseleccionado) {
      // Modo sub-flujo: fijar paciente directamente, no cargar lista
      form.value.paciente = props.pacientePreseleccionado.id
      selectedPaciente.value = {
        id: props.pacientePreseleccionado.id,
        nombre: props.pacientePreseleccionado.nombre,
      } as Paciente
    } else {
      // Modo normal: cargar lista de pacientes
      await loadPacientes()
      if (props.muestra) {
        selectedPaciente.value =
          pacientes.value.find(p => p.id === props.muestra!.paciente) ?? null
      }
    }
  },
  { immediate: true },
)

// ── Acciones ──────────────────────────────────────────────────────────────────
function close() {
  emit('update:open', false)
}

async function handleSubmit() {
  formError.value = null

  if (!form.value.paciente) {
    formError.value = 'Debes seleccionar el paciente'
    return
  }
  if (!form.value.tipo) {
    formError.value = 'El tipo de muestra es requerido'
    return
  }

  const res = isEdit.value && props.muestra
    ? await store.update(props.muestra.id, form.value)
    : await store.create(form.value)

  if (res.ok) {
    emit('saved')
    close()
  } else {
    formError.value = res.error ?? 'Error al guardar la muestra'
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="(v) => emit('update:open', v)">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <FlaskConical class="h-5 w-5 text-primary" />
          <span>{{ isEdit ? 'Editar muestra' : 'Nueva muestra' }}</span>
        </DialogTitle>
        <!-- Contexto del examen cuando viene del sub-flujo -->
        <p v-if="tituloContexto" class="text-sm text-muted-foreground mt-0.5 flex items-center gap-1.5">
          <FlaskConical class="h-3.5 w-3.5 text-amber-500" />
          {{ tituloContexto }}
        </p>
      </DialogHeader>

      <!-- Error global -->
      <div
        v-if="formError"
        class="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600"
      >
        <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
        {{ formError }}
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">

        <!-- Código: solo en edición -->
        <div v-if="isEdit && muestra" class="space-y-1.5">
          <label class="text-sm font-medium text-muted-foreground">Código</label>
          <div class="flex items-center gap-2 rounded-md border bg-muted/40 px-3 py-2 text-sm font-mono font-medium">
            <FlaskConical class="h-3.5 w-3.5 text-muted-foreground" />
            {{ muestra.codigo }}
          </div>
        </div>
        <div v-else class="rounded-md border border-dashed border-muted-foreground/30 bg-muted/20 px-3 py-2 text-xs text-muted-foreground">
          El código se generará automáticamente al guardar (formato: MU-YYYYMMDD-NNNN).
        </div>

        <!-- ── Paciente ─────────────────────────────────────────────────────── -->
        <div class="space-y-1.5">
          <label class="text-sm font-medium">
            Paciente <span class="text-red-500">*</span>
          </label>

          <!-- Modo embed: paciente fijo, solo lectura -->
          <div
            v-if="esEmbed && selectedPaciente"
            class="flex items-center gap-2 rounded-md border bg-muted/40 px-3 py-2 text-sm"
          >
            <FlaskConical class="h-3.5 w-3.5 text-muted-foreground" />
            <span class="font-medium">{{ selectedPaciente.nombre }}</span>
            <span class="text-xs text-muted-foreground ml-auto">Asignado desde la solicitud</span>
          </div>

          <!-- Modo normal: selector interactivo -->
          <template v-else>
            <!-- Paciente ya elegido -->
            <div
              v-if="selectedPaciente"
              class="flex items-center justify-between rounded-md border bg-muted/40 px-3 py-2 text-sm"
            >
              <span>
                <span class="font-medium">{{ selectedPaciente.nombre }}</span>
                <span v-if="selectedPaciente.propietario_nombre" class="ml-1 text-muted-foreground">
                  — {{ selectedPaciente.propietario_nombre }}
                </span>
              </span>
              <button type="button" @click="clearPaciente" class="ml-2 text-muted-foreground hover:text-foreground">
                <X class="h-4 w-4" />
              </button>
            </div>

            <!-- Buscador -->
            <div v-else class="relative">
              <button
                type="button"
                class="flex w-full items-center justify-between rounded-md border bg-background px-3 py-2 text-sm shadow-sm hover:bg-muted/30"
                @click="pacienteDropdownOpen = !pacienteDropdownOpen"
              >
                <span class="text-muted-foreground">Seleccionar paciente…</span>
                <ChevronsUpDown class="h-4 w-4 text-muted-foreground" />
              </button>

              <div v-if="pacienteDropdownOpen" class="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-md">
                <div class="p-2">
                  <div class="relative">
                    <Search class="absolute left-2 top-2 h-4 w-4 text-muted-foreground" />
                    <Input
                      v-model="pacienteSearch"
                      class="pl-7"
                      placeholder="Buscar por nombre o propietario…"
                      autofocus
                    />
                  </div>
                </div>
                <ul class="max-h-48 overflow-y-auto pb-1">
                  <li v-if="loadingPacientes" class="px-3 py-2 text-sm text-muted-foreground">Cargando…</li>
                  <li v-else-if="filteredPacientes.length === 0" class="px-3 py-2 text-sm text-muted-foreground">Sin resultados</li>
                  <li
                    v-for="p in filteredPacientes"
                    :key="p.id"
                    class="cursor-pointer px-3 py-2 text-sm hover:bg-muted"
                    @click="selectPaciente(p)"
                  >
                    <span class="font-medium">{{ p.nombre }}</span>
                    <span v-if="p.propietario_nombre" class="ml-1 text-muted-foreground text-xs">
                      — {{ p.propietario_nombre }}
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </template>
        </div>

        <!-- Tipo + Estado -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="space-y-1.5">
            <label class="text-sm font-medium">Tipo <span class="text-red-500">*</span></label>
            <Select v-model="form.tipo">
              <SelectTrigger><SelectValue placeholder="Seleccionar tipo…" /></SelectTrigger>
              <SelectContent>
                <SelectItem v-for="t in TIPOS" :key="t.value" :value="t.value">{{ t.label }}</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium">Estado</label>
            <Select v-model="form.estado">
              <SelectTrigger><SelectValue placeholder="Seleccionar estado…" /></SelectTrigger>
              <SelectContent>
                <SelectItem v-for="e in ESTADOS" :key="e.value" :value="e.value">{{ e.label }}</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- Fecha recepción -->
        <div class="space-y-1.5">
          <label class="text-sm font-medium">Fecha de recepción</label>
          <Input type="date" v-model="form.fecha_recepcion" />
        </div>

        <!-- Observaciones -->
        <div class="space-y-1.5">
          <label class="text-sm font-medium">Observaciones</label>
          <Textarea v-model="form.observaciones" placeholder="Observaciones adicionales…" :rows="3" />
        </div>

        <DialogFooter class="pt-2">
          <Button type="button" variant="outline" @click="close">
            {{ esEmbed ? 'Omitir esta muestra' : 'Cancelar' }}
          </Button>
          <Button type="submit" :disabled="store.saving" class="gap-2">
            <Loader2 v-if="store.saving" class="h-4 w-4 animate-spin" />
            {{ isEdit ? 'Guardar cambios' : 'Registrar muestra' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>