<script setup lang="ts">
import { ref, watch } from 'vue'
import { usePropietariosStore, type Propietario, type PropietarioForm } from '@/stores/propietarios'
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AlertCircle, Loader2 } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  propietario?: Propietario | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'saved': []
}>()

const store = usePropietariosStore()
const formError = ref<string | null>(null)

const emptyForm = (): PropietarioForm => ({
  ci: '', nombre: '', apellido: '', correo: '', telefono: '', direccion: '',
})

const form = ref<PropietarioForm>(emptyForm())

// Sincroniza el form cuando cambia el propietario (edición) o se abre para crear
watch(
  () => props.open,
  (val) => {
    if (!val) return
    formError.value = null
    form.value = props.propietario
      ? {
          ci: props.propietario.ci,
          nombre: props.propietario.nombre,
          apellido: props.propietario.apellido,
          correo: props.propietario.correo,
          telefono: props.propietario.telefono,
          direccion: props.propietario.direccion,
        }
      : emptyForm()
  },
)

function close() {
  emit('update:open', false)
}

async function handleSubmit() {
  formError.value = null
  const result = props.propietario
    ? await store.update(props.propietario.id, form.value)
    : await store.create(form.value)

  if (result.ok) {
    emit('saved')
    close()
  } else {
    formError.value = result.error ?? 'Error al guardar'
  }
}
</script>

<template>
  <Dialog :open="open" @update:open="(v) => emit('update:open', v)">
    <DialogContent class="sm:max-w-lg">
      <DialogHeader>
        <DialogTitle>
          {{ propietario ? 'Editar propietario' : 'Nuevo propietario' }}
        </DialogTitle>
        <DialogDescription>
          {{ propietario ? 'Modifica los datos del propietario.' : 'Completa el formulario para registrar un nuevo propietario.' }}
        </DialogDescription>
      </DialogHeader>

      <form @submit.prevent="handleSubmit" class="space-y-4">

        <!-- CI -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium">
            Cédula de identidad <span class="text-red-500">*</span>
          </label>
          <Input v-model="form.ci" placeholder="Ej: 12345678" required maxlength="10" />
        </div>

        <!-- Nombre + Apellido -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <label class="block text-sm font-medium">
              Nombre <span class="text-red-500">*</span>
            </label>
            <Input v-model="form.nombre" placeholder="Juan" required maxlength="50" />
          </div>
          <div class="space-y-1.5">
            <label class="block text-sm font-medium">
              Apellido <span class="text-red-500">*</span>
            </label>
            <Input v-model="form.apellido" placeholder="Pérez" required maxlength="50" />
          </div>
        </div>

        <!-- Correo -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium">
            Correo electrónico <span class="text-red-500">*</span>
          </label>
          <Input v-model="form.correo" type="email" placeholder="juan@correo.com" required />
        </div>

        <!-- Teléfono -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium">
            Teléfono <span class="text-red-500">*</span>
          </label>
          <Input v-model="form.telefono" type="tel" placeholder="Ej: 70012345" required maxlength="15" />
        </div>

        <!-- Dirección -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium">Dirección</label>
          <Input v-model="form.direccion" placeholder="Calle, barrio, ciudad" maxlength="100" />
        </div>

        <!-- Error del servidor -->
        <div
          v-if="formError"
          class="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
        >
          <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
          <span>{{ formError }}</span>
        </div>

        <!-- Footer -->
        <div class="flex justify-end gap-3 pt-2 border-t mt-2">
          <Button type="button" variant="outline" @click="close">Cancelar</Button>
          <Button type="submit" :disabled="store.saving" class="min-w-32">
            <Loader2 v-if="store.saving" class="h-4 w-4 animate-spin mr-1.5" />
            {{ store.saving ? 'Guardando…' : propietario ? 'Actualizar' : 'Crear propietario' }}
          </Button>
        </div>
      </form>
    </DialogContent>
  </Dialog>
</template>