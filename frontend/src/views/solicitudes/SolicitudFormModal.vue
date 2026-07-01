<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Checkbox } from '@/components/ui/checkbox'
import { Loader2, AlertCircle, FlaskConical, CheckCircle2 } from 'lucide-vue-next'
import ComboboxBuscable from '@/components/common/ComboboxBuscable.vue'
import { useSolicitudesStore } from '@/stores/solicitudes'
import { pacienteService } from '@/services/pacienteService'
import { medicoService } from '@/services/medicoService'
import { catalogoService } from '@/services/catalogoService'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ 'update:open': [value: boolean]; saved: [] }>()

const store = useSolicitudesStore()

const paciente = ref<number | null>(null)
const medicoVeterinario = ref<number | null>(null)
const observaciones = ref('')
const examenesSeleccionados = ref<number[]>([])
const examenesDisponibles = ref<Array<{ id: number; nombre_examen: string; catalogo_nombre: string; requiere_muestra?: boolean }>>([])
const error = ref<string | null>(null)
const mensajeExito = ref<string | null>(null)

async function fetchPacientes(search: string) {
  const { data } = await pacienteService.buscar(search)
  return data.resultados ?? data.results ?? data
}

async function fetchMedicos(search: string) {
  const { data } = await medicoService.buscar(search)
  return data.resultados ?? data.results ?? data
}

async function cargarExamenes() {
  const { data } = await catalogoService.getExamenes()
  examenesDisponibles.value = data.resultados ?? data.results ?? data
}

function toggleExamen(id: number) {
  const idx = examenesSeleccionados.value.indexOf(id)
  if (idx === -1) examenesSeleccionados.value.push(id)
  else examenesSeleccionados.value.splice(idx, 1)
}

const examenesConMuestra = computed(() =>
  examenesDisponibles.value.filter(
    e => examenesSeleccionados.value.includes(e.id) && e.requiere_muestra
  )
)

function resetForm() {
  paciente.value = null
  medicoVeterinario.value = null
  observaciones.value = ''
  examenesSeleccionados.value = []
  error.value = null
  mensajeExito.value = null
}

watch(() => props.open, (val) => {
  if (val) {
    resetForm()
    cargarExamenes()
  }
})

async function guardar() {
  error.value = null
  if (!paciente.value) {
    error.value = 'Selecciona un paciente.'
    return
  }
  if (examenesSeleccionados.value.length === 0) {
    error.value = 'Selecciona al menos un examen.'
    return
  }

  const res = await store.crear({
    paciente: paciente.value,
    medico_veterinario: medicoVeterinario.value,
    examenes_ids: examenesSeleccionados.value,
    observaciones: observaciones.value,
  })

  if (res.ok) {
    const cantidadMuestras = res.data?.muestras_generadas ?? 0
    mensajeExito.value = `Solicitud creada. ${cantidadMuestras} muestra(s) requerida(s).`
    emit('saved')
    setTimeout(() => emit('update:open', false), 1200)
  } else {
    error.value = res.error || 'No se pudo crear la solicitud.'
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="(v) => emit('update:open', v)">
    <DialogContent class="sm:max-w-lg max-h-[90vh] overflow-y-auto">
      <DialogHeader>
        <DialogTitle>Nueva solicitud de examen</DialogTitle>
      </DialogHeader>

      <div class="space-y-4 py-2">
        <div class="space-y-1.5">
          <Label>Paciente</Label>
          <ComboboxBuscable
            v-model="paciente"
            :fetcher="fetchPacientes"
            :label-fn="(p: any) => `${p.nombre} (${p.raza_nombre || p.especie_nombre || 'Paciente'})`"
            placeholder="Buscar paciente…"
            empty-text="No se encontraron pacientes."
          />
        </div>

        <div class="space-y-1.5">
          <Label>Médico veterinario externo (opcional)</Label>
          <ComboboxBuscable
            v-model="medicoVeterinario"
            :fetcher="fetchMedicos"
            :label-fn="(m: any) => `Dr(a). ${m.usuario_first_name || m.nombre || ''} ${m.usuario_last_name || ''}`"
            placeholder="Buscar médico…"
            empty-text="No se encontraron médicos."
          />
        </div>

        <div class="space-y-1.5">
          <Label>Exámenes a solicitar</Label>
          <div class="rounded-lg border max-h-56 overflow-y-auto divide-y">
            <label
              v-for="ex in examenesDisponibles"
              :key="ex.id"
              class="flex items-center gap-2 px-3 py-2 text-sm hover:bg-muted/40 cursor-pointer"
            >
              <Checkbox
                :checked="examenesSeleccionados.includes(ex.id)"
                @update:checked="() => toggleExamen(ex.id)"
              />
              <span class="flex-1">{{ ex.nombre_examen }}</span>
              <span class="text-xs text-muted-foreground">{{ ex.catalogo_nombre }}</span>
            </label>
            <div v-if="examenesDisponibles.length === 0" class="px-3 py-6 text-center text-sm text-muted-foreground">
              No hay exámenes en el catálogo.
            </div>
          </div>
        </div>

        <!-- Aviso de muestras requeridas -->
        <div
          v-if="examenesConMuestra.length > 0"
          class="flex items-start gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-700"
        >
          <FlaskConical class="h-4 w-4 shrink-0 mt-0.5" />
          <span>
            {{ examenesConMuestra.length }} examen(es) requerirán muestra:
            {{ examenesConMuestra.map(e => e.nombre_examen).join(', ') }}
          </span>
        </div>

        <div class="space-y-1.5">
          <Label>Observaciones</Label>
          <Textarea v-model="observaciones" rows="3" placeholder="Notas adicionales (opcional)" />
        </div>

        <div v-if="error" class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ error }}
        </div>

        <div v-if="mensajeExito" class="flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700">
          <CheckCircle2 class="h-4 w-4 shrink-0" />
          {{ mensajeExito }}
        </div>
      </div>

      <DialogFooter>
        <Button variant="outline" @click="emit('update:open', false)">Cancelar</Button>
        <Button class="gap-2" :disabled="store.saving" @click="guardar" >
          <Loader2 v-if="store.saving" class="h-4 w-4 animate-spin" />
          Crear solicitud
        </Button>
      </DialogFooter>
    </DialogContent>
  </Dialog>
</template>