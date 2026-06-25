<!-- src/components/muestra/MuestraFormModal.vue -->
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useMuestrasStore, type MuestraForm } from '@/stores/muestras'
import type { Muestra } from '@/models/muestra'

import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import { Loader2, AlertCircle, FlaskConical } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  muestra?: Muestra | null   // si viene, es edición; si no, es creación
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'saved'): void
}>()

const store = useMuestrasStore()

const isEdit = computed(() => !!props.muestra)

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

const defaultForm = (): MuestraForm => ({
  codigo:          '',
  paciente:        undefined as any,
  tipo:            '',
  estado:          'pendiente',
  fecha_recepcion: new Date().toISOString().slice(0, 10),
  observaciones:   '',
})

const form = ref<MuestraForm>(defaultForm())
const formError = ref<string | null>(null)

// Sincroniza el formulario cuando se abre el modal o cambia la muestra a editar
watch(
  () => [props.open, props.muestra],
  () => {
    if (!props.open) return
    formError.value = null
    form.value = props.muestra
      ? {
          codigo:          props.muestra.codigo,
          paciente:        props.muestra.paciente,
          tipo:            props.muestra.tipo,
          estado:          props.muestra.estado,
          fecha_recepcion: props.muestra.fecha_recepcion,
          observaciones:   props.muestra.observaciones ?? '',
        }
      : defaultForm()
  },
  { immediate: true },
)

function close() {
  emit('update:open', false)
}

async function handleSubmit() {
  formError.value = null

  if (!form.value.codigo.trim()) {
    formError.value = 'El código es requerido'
    return
  }
  if (!form.value.paciente) {
    formError.value = 'Debes indicar el paciente'
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
          {{ isEdit ? 'Editar muestra' : 'Nueva muestra' }}
        </DialogTitle>
      </DialogHeader>

      <!-- Error -->
      <div v-if="formError" class="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600">
        <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
        {{ formError }}
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">

        <!-- Código -->
        <div class="space-y-1.5">
          <label class="text-sm font-medium">Código <span class="text-red-500">*</span></label>
          <Input v-model="form.codigo" placeholder="Ej: MU-0001" />
        </div>

        <!-- Paciente -->
        <div class="space-y-1.5">
          <label class="text-sm font-medium">Paciente (ID) <span class="text-red-500">*</span></label>
          <Input v-model.number="form.paciente" type="number" placeholder="ID del paciente" />
          <!--
            Si tienes un listado de pacientes ya cargado (ej. en otro store),
            reemplaza este Input por un Select como el de abajo:

            <Select v-model="form.paciente">
              <SelectTrigger><SelectValue placeholder="Seleccionar paciente…" /></SelectTrigger>
              <SelectContent>
                <SelectItem v-for="p in pacientes" :key="p.id" :value="p.id">
                  {{ p.nombre }}
                </SelectItem>
              </SelectContent>
            </Select>
          -->
        </div>

        <!-- Tipo + Estado -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div class="space-y-1.5">
            <label class="text-sm font-medium">Tipo <span class="text-red-500">*</span></label>
            <Select v-model="form.tipo">
              <SelectTrigger><SelectValue placeholder="Seleccionar tipo…" /></SelectTrigger>
              <SelectContent>
                <SelectItem v-for="t in TIPOS" :key="t.value" :value="t.value">
                  {{ t.label }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium">Estado</label>
            <Select v-model="form.estado">
              <SelectTrigger><SelectValue placeholder="Seleccionar estado…" /></SelectTrigger>
              <SelectContent>
                <SelectItem v-for="e in ESTADOS" :key="e.value" :value="e.value">
                  {{ e.label }}
                </SelectItem>
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
          <Textarea v-model?="form.observaciones ?? '-'" placeholder="Observaciones adicionales…" rows="3" />
        </div>

        <DialogFooter class="pt-2">
          <Button type="button" variant="outline" @click="close">
            Cancelar
          </Button>
          <Button type="submit" :disabled="store.saving" class="gap-2">
            <Loader2 v-if="store.saving" class="h-4 w-4 animate-spin" />
            {{ isEdit ? 'Guardar cambios' : 'Crear muestra' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>