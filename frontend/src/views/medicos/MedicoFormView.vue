<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useMedicosStore, type Medico, type MedicoForm } from '@/stores/medicos'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import { AlertCircle, Loader2, X } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  medico?: Medico | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'saved': []
}>()

const store = useMedicosStore()
const formError = ref<string | null>(null)
const saving = ref(false)

const isEdit = computed(() => !!props.medico)

interface LocalForm {
  nombre: string
  apellido: string
  especialidad: string
  genero: string
  correo: string
  telefono: string
  direccion: string
}

const emptyForm = (): LocalForm => ({
  nombre: '',
  apellido: '',
  especialidad: '',
  genero: '',
  correo: '',
  telefono: '',
  direccion: '',
})

const form = ref<LocalForm>(emptyForm())

watch(
  () => props.open,
  (val) => {
    if (!val) return
    formError.value = null
    if (props.medico) {
      const m = props.medico
      form.value = {
        nombre: m.nombre ?? '',
        apellido: m.apellido ?? '',
        especialidad: m.especialidad ?? '',
        genero: m.genero ?? '',
        correo: m.correo ?? '',
        telefono: m.telefono ?? '',
        direccion: m.direccion ?? '',
      }
    } else {
      form.value = emptyForm()
    }
  },
)

function close() {
  emit('update:open', false)
}

async function handleSubmit() {
  formError.value = null
  saving.value = true

  const payload: MedicoForm = {
    nombre: form.value.nombre,
    apellido: form.value.apellido,
    especialidad: form.value.especialidad || null,
    genero: (form.value.genero || null) as MedicoForm['genero'],
    correo: form.value.correo || null,
    telefono: form.value.telefono || null,
    direccion: form.value.direccion || null,
  }

  const result = isEdit.value && props.medico
    ? await store.update(props.medico.id, payload)
    : await store.create(payload)

  saving.value = false

  if (result.ok) {
    emit('saved')
    close()
  } else {
    formError.value = result.error ?? 'Error al guardar el médico'
  }
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex items-center justify-center p-4"
        @mousedown.self="close"
      >
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />

        <div class="relative z-10 w-full max-w-lg rounded-2xl bg-white shadow-2xl max-h-[90vh] overflow-y-auto">
          <div class="flex items-start justify-between border-b px-6 py-5">
            <div>
              <h2 class="text-lg font-bold text-mineral-green-950">
                {{ isEdit ? 'Editar médico' : 'Nuevo médico' }}
              </h2>
              <p class="mt-0.5 text-sm text-muted-foreground">
                {{ isEdit
                  ? 'Modifica los datos del médico veterinario.'
                  : 'Completa el formulario para registrar un nuevo médico veterinario.' }}
              </p>
            </div>
            <button
              type="button"
              @click="close"
              class="ml-4 rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            >
              <X class="h-5 w-5" />
            </button>
          </div>

          <form @submit.prevent="handleSubmit" class="px-6 py-5 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">
                  Nombre <span class="text-red-500">*</span>
                </label>
                <Input v-model="form.nombre" placeholder="Juan" required maxlength="100" />
              </div>
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">
                  Apellido <span class="text-red-500">*</span>
                </label>
                <Input v-model="form.apellido" placeholder="Pérez" required maxlength="100" />
              </div>
            </div>

            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Especialidad</label>
              <Input v-model="form.especialidad" placeholder="Ej: Cirugía, Dermatología…" maxlength="100" />
            </div>

            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Género</label>
              <Select v-model="form.genero">
                <SelectTrigger class="w-full">
                  <SelectValue placeholder="Selecciona un género (opcional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="M">Masculino</SelectItem>
                  <SelectItem value="F">Femenino</SelectItem>
                  <SelectItem value="O">Otro</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Correo electrónico</label>
              <Input v-model="form.correo" type="email" placeholder="medico@correo.com" maxlength="100" />
            </div>

            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Teléfono</label>
              <Input v-model="form.telefono" type="tel" placeholder="Ej: 70012345" maxlength="20" />
            </div>

            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Dirección</label>
              <Input v-model="form.direccion" placeholder="Calle, barrio, ciudad" maxlength="200" />
            </div>

            <Transition name="fade">
              <div
                v-if="formError"
                class="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
              >
                <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
                <span>{{ formError }}</span>
              </div>
            </Transition>

            <div class="flex justify-end gap-3 pt-2 border-t mt-2">
              <Button type="button" variant="outline" @click="close">Cancelar</Button>
              <Button
                type="submit"
                :disabled="saving"
                class="bg-mineral-green-600 hover:bg-mineral-green-700 text-white min-w-32"
              >
                <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
                {{ saving
                  ? (isEdit ? 'Guardando…' : 'Registrando…')
                  : (isEdit ? 'Guardar cambios' : 'Registrar médico') }}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.2s ease, opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
.modal-enter-from .relative {
  transform: scale(0.96) translateY(8px);
  opacity: 0;
}
.modal-leave-to .relative {
  transform: scale(0.96) translateY(8px);
  opacity: 0;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
