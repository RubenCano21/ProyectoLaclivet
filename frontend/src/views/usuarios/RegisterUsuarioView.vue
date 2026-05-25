<script setup lang="ts">
import { ref, watch } from 'vue'
import { useUsuariosStore, type RegisterForm } from '@/stores/usuarios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { AlertCircle, Loader2, X } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'saved': []
}>()

const store = useUsuariosStore()
const formError = ref<string | null>(null)
const saving = ref(false)

interface LocalForm {
  username: string
  email: string
  password: string
  password2: string
  first_name: string
  last_name: string
  telefono: string
  direccion: string
  fecha_nacimiento: string
}

const emptyForm = (): LocalForm => ({
  username: '',
  email: '',
  password: '',
  password2: '',
  first_name: '',
  last_name: '',
  telefono: '',
  direccion: '',
  fecha_nacimiento: '',
})

const form = ref<LocalForm>(emptyForm())

watch(
  () => props.open,
  (val) => {
    if (!val) return
    formError.value = null
    form.value = emptyForm()
  },
)

function close() {
  emit('update:open', false)
}

async function handleSubmit() {
  formError.value = null

  if (form.value.password !== form.value.password2) {
    formError.value = 'Las contraseñas no coinciden'
    return
  }

  saving.value = true
  const payload: RegisterForm = {
    username: form.value.username,
    email: form.value.email,
    password: form.value.password,
    password2: form.value.password2,
    first_name: form.value.first_name,
    last_name: form.value.last_name || undefined,
    telefono: form.value.telefono || null,
    direccion: form.value.direccion || null,
    fecha_nacimiento: form.value.fecha_nacimiento || null,
  }
  const result = await store.register(payload)
  saving.value = false

  if (result.ok) {
    emit('saved')
    close()
  } else {
    formError.value = result.error ?? 'Error al registrar usuario'
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
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />

        <!-- Modal -->
        <div class="relative z-10 w-full max-w-lg rounded-2xl bg-white shadow-2xl max-h-[90vh] overflow-y-auto">

          <!-- Header -->
          <div class="flex items-start justify-between border-b px-6 py-5">
            <div>
              <h2 class="text-lg font-bold text-mineral-green-950">Nuevo usuario</h2>
              <p class="mt-0.5 text-sm text-muted-foreground">
                Completa el formulario para registrar un nuevo usuario.
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

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="px-6 py-5 space-y-4">

            <!-- Username -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">
                Nombre de usuario <span class="text-red-500">*</span>
              </label>
              <Input v-model="form.username" placeholder="Ej: juan123" required maxlength="150" />
            </div>

            <!-- Nombre + Apellido -->
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">
                  Nombre <span class="text-red-500">*</span>
                </label>
                <Input v-model="form.first_name" placeholder="Juan" required maxlength="50" />
              </div>
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">Apellido</label>
                <Input v-model="form.last_name" placeholder="Pérez" maxlength="50" />
              </div>
            </div>

            <!-- Correo -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">
                Correo electrónico <span class="text-red-500">*</span>
              </label>
              <Input v-model="form.email" type="email" placeholder="juan@correo.com" required />
            </div>

            <!-- Contraseña -->
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">
                  Contraseña <span class="text-red-500">*</span>
                </label>
                <Input v-model="form.password" type="password" placeholder="••••••••" required />
              </div>
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">
                  Confirmar contraseña <span class="text-red-500">*</span>
                </label>
                <Input v-model="form.password2" type="password" placeholder="••••••••" required />
              </div>
            </div>

            <!-- Teléfono -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Teléfono</label>
              <Input v-model="form.telefono" type="tel" placeholder="Ej: 70012345" maxlength="15" />
            </div>

            <!-- Dirección -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Dirección</label>
              <Input v-model="form.direccion" placeholder="Calle, barrio, ciudad" maxlength="100" />
            </div>

            <!-- Fecha de nacimiento -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Fecha de nacimiento</label>
              <Input v-model="form.fecha_nacimiento" type="date" />
            </div>

            <!-- Error del servidor -->
            <Transition name="fade">
              <div
                v-if="formError"
                class="flex items-start gap-2 rounded-xl border border-red-200 
                    bg-red-50 px-4 py-3 text-sm text-red-600"
              >
                <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
                <span>{{ formError }}</span>
              </div>
            </Transition>

            <!-- Footer -->
            <div class="flex justify-end gap-3 pt-2 border-t mt-2">
              <Button type="button" variant="outline" @click="close">Cancelar</Button>
              <Button
                type="submit"
                :disabled="saving"
                class="bg-mineral-green-600 hover:bg-mineral-green-700 text-white min-w-32"
              >
                <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
                {{ saving ? 'Registrando…' : 'Registrar usuario' }}
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
