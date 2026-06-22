<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useUsuariosStore, type RegisterForm, type AdminActualizarForm, type Usuario } from '@/stores/usuarios'
import { useRolesPermisosStore } from '@/stores/rolesPermisos'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import { AlertCircle, Loader2, X } from 'lucide-vue-next'

const props = defineProps<{
  open: boolean
  usuario?: Usuario | null
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  'saved': []
}>()

const store = useUsuariosStore()
const rolesStore = useRolesPermisosStore()
const formError = ref<string | null>(null)
const saving = ref(false)

const isEdit = computed(() => !!props.usuario)

interface LocalForm {
  email: string
  first_name: string
  last_name: string
  ci: string
  telefono: string
  direccion: string
  fecha_nacimiento: string
  rol_id: string
  is_active: boolean
  is_staff: boolean
}

const emptyForm = (): LocalForm => ({
  email: '',
  first_name: '',
  last_name: '',
  ci: '',
  telefono: '',
  direccion: '',
  fecha_nacimiento: '',
  rol_id: '',
  is_active: true,
  is_staff: false,
})

const form = ref<LocalForm>(emptyForm())
const roles = computed(() => rolesStore.roles)

const errors = ref({
  first_name: '',
  last_name: '',
  email: '',
  ci: '',
  telefono: '',
  direccion: '',
  fecha_nacimiento: '',
})

function validarForm(): boolean {
  let valido = true
  errors.value = {
    first_name: '', last_name: '', email: '', ci: '',
    telefono: '', direccion: '', fecha_nacimiento: '',
  }

  // Nombre
  if (!form.value.first_name.trim()) {
    errors.value.first_name = 'El nombre es requerido'
    valido = false
  } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(form.value.first_name)) {
    errors.value.first_name = 'El nombre solo puede contener letras'
    valido = false
  }

  // Apellido
  if (!form.value.last_name.trim()) {
    errors.value.last_name = 'El apellido es requerido'
    valido = false
  } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(form.value.last_name)) {
    errors.value.last_name = 'El apellido solo puede contener letras'
    valido = false
  }

  // CI
  if (!form.value.ci.trim()) {
    errors.value.ci = 'El CI es requerido'
    valido = false
  } else if (!/^\d{5,10}$/.test(form.value.ci)) {
    errors.value.ci = 'El CI debe contener solo números (5 a 10 dígitos)'
    valido = false
  }

  // Teléfono
  if (form.value.telefono && !/^\d{7,8}$/.test(form.value.telefono)) {
    errors.value.telefono = 'El teléfono debe tener 7 u 8 dígitos numéricos'
    valido = false
  }

  // Dirección
  if (form.value.direccion && form.value.direccion.trim().length < 5) {
    errors.value.direccion = 'La dirección debe tener al menos 5 caracteres'
    valido = false
  }

  // Fecha de nacimiento
  if (form.value.fecha_nacimiento) {
    const hoy = new Date()
    const nacimiento = new Date(form.value.fecha_nacimiento + 'T00:00:00')
    if (nacimiento > hoy) {
      errors.value.fecha_nacimiento = 'La fecha de nacimiento no puede ser futura'
      valido = false
    }
  }

  return valido
}

onMounted(() => {
  if (rolesStore.roles.length === 0) rolesStore.fetchAll()
})

async function loadForEdit(id: number) {
  const res = await store.fetchById(id)
  if (!res.ok || !res.data) {
    formError.value = res.error ?? 'No se pudo cargar el usuario'
    return
  }
  const u = res.data
  form.value = {
    email: u.email ?? '',
    first_name: u.first_name ?? '',
    last_name: u.last_name ?? '',
    ci: u.ci ?? '',
    telefono: u.telefono ?? '',
    direccion: u.direccion ?? '',
    fecha_nacimiento: u.fecha_nacimiento ?? '',
    rol_id: u.rol?.id ? String(u.rol.id) : '',
    is_active: u.is_active,
    is_staff: u.is_staff,
  }
}

watch(
  () => props.open,
  (val) => {
    if (!val) return
    formError.value = null
    errors.value = { first_name: '', last_name: '', email: '', ci: '', telefono: '', direccion: '', fecha_nacimiento: '' }
    form.value = emptyForm()
    if (props.usuario) loadForEdit(props.usuario.id)
  },
)

function close() {
  emit('update:open', false)
}

async function handleSubmit() {
  formError.value = null
  if (!validarForm()) return

  saving.value = true

  if (isEdit.value && props.usuario) {
    const payload: AdminActualizarForm = {
      email: form.value.email,
      first_name: form.value.first_name,
      last_name: form.value.last_name || undefined,
      ci: form.value.ci || null,
      telefono: form.value.telefono || null,
      direccion: form.value.direccion || null,
      fecha_nacimiento: form.value.fecha_nacimiento || null,
      rol_id: form.value.rol_id ? Number(form.value.rol_id) : null,
      is_active: form.value.is_active,
      is_staff: form.value.is_staff,
    }
    const result = await store.update(props.usuario.id, payload)
    saving.value = false
    if (result.ok) {
      emit('saved')
      close()
    } else {
      formError.value = result.error ?? 'Error al actualizar usuario'
    }
    return
  }

  // Registro — sin contraseña, el backend genera primer_apellido.ci
  const payload: RegisterForm = {
    email: form.value.email,
    first_name: form.value.first_name,
    last_name: form.value.last_name || undefined,
    ci: form.value.ci || null,
    telefono: form.value.telefono || null,
    direccion: form.value.direccion || null,
    fecha_nacimiento: form.value.fecha_nacimiento || null,
    rol_id: form.value.rol_id ? Number(form.value.rol_id) : null,
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
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center p-4" @mousedown.self="close">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />

        <div class="relative z-10 w-full max-w-lg rounded-2xl bg-white shadow-2xl max-h-[90vh] overflow-y-auto">

          <!-- Header -->
          <div class="flex items-start justify-between border-b px-6 py-5">
            <div>
              <h2 class="text-lg font-bold text-mineral-green-950">
                {{ isEdit ? 'Editar usuario' : 'Nuevo usuario' }}
              </h2>
              <p class="mt-0.5 text-sm text-muted-foreground">
                {{ isEdit
                  ? 'Modifica los datos del usuario.'
                  : 'Completa el formulario para registrar un nuevo usuario.' }}
              </p>
            </div>
            <button type="button" @click="close"
              class="ml-4 rounded-lg p-1.5 text-muted-foreground hover:bg-accent hover:text-foreground transition-colors">
              <X class="h-5 w-5" />
            </button>
          </div>

          <!-- Form -->
          <form @submit.prevent="handleSubmit" class="px-6 py-5 space-y-4">

            <!-- Nombre + Apellido -->
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">
                  Nombre <span class="text-red-500">*</span>
                </label>
                <Input v-model="form.first_name" placeholder="Juan" maxlength="50" />
                <p v-if="errors.first_name" class="text-xs text-red-500">{{ errors.first_name }}</p>
              </div>
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">
                  Apellido <span class="text-red-500">*</span>
                </label>
                <Input v-model="form.last_name" placeholder="Pérez" maxlength="50" />
                <p v-if="errors.last_name" class="text-xs text-red-500">{{ errors.last_name }}</p>
              </div>
            </div>

            <!-- CI -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">
                CI <span class="text-red-500">*</span>
              </label>
              <Input v-model="form.ci" placeholder="Ej: 12345678" maxlength="10"
                @input="form.ci = form.ci.replace(/\D/g, '')" />
              <p v-if="errors.ci" class="text-xs text-red-500">{{ errors.ci }}</p>
            </div>

            <!-- Correo -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">
                Correo electrónico <span class="text-red-500">*</span>
              </label>
              <Input v-model="form.email" type="email" placeholder="juan@correo.com" required />
            </div>

            <!-- Aviso contraseña automática (solo creación) -->
            <div v-if="!isEdit" class="rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-700">
              La contraseña inicial será:
              <strong>
                {{ form.last_name ? form.last_name.trim().split(' ')[0].toLowerCase() : 'apellido' }}.{{ form.ci || 'ci'
                }}
              </strong>
              — actualiza desde tu perfil.
            </div>

            <!-- Teléfono + Fecha de nacimiento -->
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">Teléfono</label>
                <Input v-model="form.telefono" type="tel" placeholder="Ej: 70012345" maxlength="8"
                  @input="form.telefono = form.telefono.replace(/\D/g, '')" />
                <p v-if="errors.telefono" class="text-xs text-red-500">{{ errors.telefono }}</p>
              </div>
              <div class="space-y-1.5">
                <label class="block text-sm font-medium text-mineral-green-800">Fecha de nacimiento</label>
                <Input v-model="form.fecha_nacimiento" type="date" :max="new Date().toISOString().split('T')[0]" />
                <p v-if="errors.fecha_nacimiento" class="text-xs text-red-500">{{ errors.fecha_nacimiento }}</p>
              </div>
            </div>

            <!-- Dirección -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Dirección</label>
              <Input v-model="form.direccion" placeholder="Calle, barrio, ciudad" maxlength="100" />
              <p v-if="errors.direccion" class="text-xs text-red-500">{{ errors.direccion }}</p>
            </div>

            <!-- Rol -->
            <div class="space-y-1.5">
              <label class="block text-sm font-medium text-mineral-green-800">Rol</label>
              <Select v-model="form.rol_id">
                <SelectTrigger class="w-full">
                  <SelectValue placeholder="Selecciona un rol (opcional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="r in roles" :key="r.id" :value="String(r.id)">
                    {{ r.nombre }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <!-- Estados (solo edición) -->
            <div v-if="isEdit" class="grid grid-cols-2 gap-4">
              <label class="flex items-center gap-2 text-sm font-medium text-mineral-green-800">
                <input type="checkbox" v-model="form.is_active" class="h-4 w-4 rounded border-mineral-green-300" />
                Activo
              </label>
              <label class="flex items-center gap-2 text-sm font-medium text-mineral-green-800">
                <input type="checkbox" v-model="form.is_staff" class="h-4 w-4 rounded border-mineral-green-300" />
                Administrador
              </label>
            </div>

            <!-- Error del servidor -->
            <Transition name="fade">
              <div v-if="formError" class="flex items-start gap-2 rounded-xl border border-red-200
                    bg-red-50 px-4 py-3 text-sm text-red-600">
                <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
                <span>{{ formError }}</span>
              </div>
            </Transition>

            <!-- Footer -->
            <div class="flex justify-end gap-3 pt-2 border-t mt-2">
              <Button type="button" variant="outline" @click="close">Cancelar</Button>
              <Button type="submit" :disabled="saving"
                class="bg-mineral-green-600 hover:bg-mineral-green-700 text-white min-w-32">
                <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
                {{ saving
                  ? (isEdit ? 'Guardando…' : 'Registrando…')
                  : (isEdit ? 'Guardar cambios' : 'Registrar usuario') }}
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>