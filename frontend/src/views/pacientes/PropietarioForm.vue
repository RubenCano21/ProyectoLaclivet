<script setup lang="ts">
import { ref, watch } from 'vue'
import { usePropietariosStore, type PropietarioForm, type Propietario } from '@/stores/propietarios'
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
  first_name: '',
  last_name: '',
  ci: '',
  email: '',
  telefono: '',
  direccion: '',
  fecha_nacimiento: '',
})

const form = ref<PropietarioForm>(emptyForm())

watch(
  () => props.open,
  (val) => {
    if (!val) return
    formError.value = null
    const u = props.propietario?.usuario
    form.value = u
      ? {
          first_name: u.first_name,
          last_name: u.last_name,
          ci: u.ci ?? '',
          email: u.email,
          telefono: u.telefono ?? '',
          direccion: u.direccion ?? '',
          fecha_nacimiento: u.fecha_nacimiento ?? '',
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
          {{ propietario
            ? 'Modifica los datos del propietario.'
            : 'Completa el formulario para registrar un nuevo propietario.' }}
        </DialogDescription>
      </DialogHeader>

      <form @submit.prevent="handleSubmit" class="space-y-4">

        <!-- Nombre + Apellido -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <label class="block text-sm font-medium">
              Nombre <span class="text-red-500">*</span>
            </label>
            <Input v-model="form.first_name" placeholder="Juan" required maxlength="50" />
          </div>
          <div class="space-y-1.5">
            <label class="block text-sm font-medium">
              Apellido <span class="text-red-500">*</span>
            </label>
            <Input v-model="form.last_name" placeholder="Pérez" required maxlength="50" />
          </div>
        </div>

        <!-- CI -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium">
            CI <span class="text-red-500">*</span>
          </label>
          <Input
            v-model="form.ci"
            placeholder="Ej: 12345678"
            required
            maxlength="10"
            @input="form.ci = form.ci.replace(/\D/g, '')"
          />
        </div>

        <!-- Correo -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium">
            Correo electrónico <span class="text-red-500">*</span>
          </label>
          <Input v-model="form.email" type="email" placeholder="juan@correo.com" required />
        </div>

        <!-- Teléfono + Fecha de nacimiento -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <label class="block text-sm font-medium">Teléfono</label>
            <Input
              v-model="form.telefono"
              type="tel"
              placeholder="Ej: 70012345"
              maxlength="8"
              @input="form.telefono = form.telefono.replace(/\D/g, '')"
            />
          </div>
          <div class="space-y-1.5">
            <label class="block text-sm font-medium">Fecha de nacimiento</label>
            <Input
              v-model="form.fecha_nacimiento"
              type="date"
              :max="new Date().toISOString().split('T')[0]"
            />
          </div>
        </div>

        <!-- Dirección -->
        <div class="space-y-1.5">
          <label class="block text-sm font-medium">Dirección</label>
          <Input
            v-model="form.direccion"
            placeholder="Calle, barrio, ciudad"
            maxlength="100"
          />
        </div>

        <!-- Aviso contraseña automática (solo creación) -->
        <div
          v-if="!propietario"
          class="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700"
        >
          🔑 Contraseña inicial:
          <strong>
            {{ form.last_name ? form.last_name.trim().split(' ')[0].toLowerCase() : 'apellido' }}.{{ form.ci || 'ci' }}
          </strong>
          — el propietario deberá cambiarla al ingresar.
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