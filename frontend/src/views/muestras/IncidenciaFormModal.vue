<!-- src/views/muestras/IncidenciaFormModal.vue -->
<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useIncidenciasStore, type IncidenciaForm } from '@/stores/incidencias'
import { muestraService } from '@/services/muestraService'
import type { IncidenciaMuestra } from '@/models/muestra'
import type { Muestra } from '@/models/muestra'

import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import { Loader2, AlertCircle, AlertTriangle } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  incidencia?: IncidenciaMuestra | null
}>()

const emit = defineEmits<{
  (e: 'update:open', value: boolean): void
  (e: 'saved'): void
}>()

const store = useIncidenciasStore()
const isEdit = computed(() => !!props.incidencia)

const defaultForm = (): IncidenciaForm => ({ muestra: 0, descripcion: '' })
const form = ref<IncidenciaForm>(defaultForm())
const formError = ref<string | null>(null)

const muestras = ref<Muestra[]>([])
const loadingMuestras = ref(false)

async function loadMuestras() {
  loadingMuestras.value = true
  try {
    const { data } = await muestraService.getAll(1)
    muestras.value = data.resultados ?? data
  } catch {
    muestras.value = []
  } finally {
    loadingMuestras.value = false
  }
}

watch(
  () => props.open,
  async (open) => {
    if (!open) return
    formError.value = null
    await loadMuestras()

    if (props.incidencia) {
      form.value = {
        muestra: props.incidencia.muestra,
        descripcion: props.incidencia.descripcion ?? '',
      }
    } else {
      form.value = defaultForm()
    }
  },
  { immediate: true },
)

function close() {
  emit('update:open', false)
}

async function handleSubmit() {
  formError.value = null

  if (!form.value.muestra) {
    formError.value = 'Debes seleccionar la muestra'
    return
  }
  if (!form.value.descripcion.trim()) {
    formError.value = 'La descripción es requerida'
    return
  }

  const res = isEdit.value && props.incidencia
    ? await store.update(props.incidencia.id, form.value)
    : await store.create(form.value)

  if (res.ok) {
    emit('saved')
    close()
  } else {
    formError.value = res.error ?? 'Error al guardar la incidencia'
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="(v) => emit('update:open', v)">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle class="flex items-center gap-2">
          <AlertTriangle class="h-5 w-5 text-amber-500" />
          <span>{{ isEdit ? 'Editar incidencia' : 'Nueva incidencia' }}</span>
        </DialogTitle>
      </DialogHeader>

      <div
        v-if="formError"
        class="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-600"
      >
        <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
        {{ formError }}
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium">Muestra <span class="text-red-500">*</span></label>
          <Select :model-value="form.muestra ? String(form.muestra) : ''" @update:model-value="(v) => form.muestra = Number(v)">
            <SelectTrigger>
              <SelectValue :placeholder="loadingMuestras ? 'Cargando…' : 'Seleccionar muestra…'" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem v-for="m in muestras" :key="m.id" :value="String(m.id)">{{ m.codigo }}</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div class="space-y-1.5">
          <label class="text-sm font-medium">Descripción <span class="text-red-500">*</span></label>
          <Textarea v-model="form.descripcion" placeholder="Describe la incidencia…" :rows="4" />
        </div>

        <DialogFooter class="pt-2">
          <Button type="button" variant="outline" @click="close">Cancelar</Button>
          <Button type="submit" :disabled="store.saving" class="gap-2">
            <Loader2 v-if="store.saving" class="h-4 w-4 animate-spin" />
            {{ isEdit ? 'Guardar cambios' : 'Registrar incidencia' }}
          </Button>
        </DialogFooter>
      </form>
    </DialogContent>
  </Dialog>
</template>
