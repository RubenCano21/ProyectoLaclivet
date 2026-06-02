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
  password: string
  password2: string
  first_name: string
  last_name: string
  telefono: string
  direccion: string
  fecha_nacimiento: string
  rol_id: string
  is_active: boolean
  is_staff: boolean
}

const emptyForm = (): LocalForm => ({
  email: '',
  password: '',
  password2: '',
  first_name: '',
  last_name: '',
  telefono: '',
  direccion: '',
  fecha_nacimiento: '',
  rol_id: '',
  is_active: true,
  is_staff: false,
})

const form = ref<LocalForm>(emptyForm())
const roles = computed(() => rolesStore.roles)

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
    password: '',
    password2: '',
    first_name: u.first_name ?? '',
    last_name: u.last_name ?? '',
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
    form.value = emptyForm()
    if (props.usuario) loadForEdit(props.usuario.id)
  },
)

function close() {
  emit('update:open', false)
}

async function handleSubmit() {
  formError.value = null

  if (!isEdit.value && form.value.password !== form.value.password2) {
    formError.value = 'Las contraseñas no coinciden'
    return
  }

  saving.value = true

  if (isEdit.value && props.usuario) {
    const payload: AdminActualizarForm = {
      email: form.value.email,
      first_name: form.value.first_name,
      last_name: form.value.last_name || undefined,
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

  const payload: RegisterForm = {
    email: form.value.email,
    password: form.value.password,
    password2: form.value.password2,
    first_name: form.value.first_name,
    last_name: form.value.last_name || undefined,
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
              <h2 class="text-lg font-bold text-mineral-green-950">
                {{ isEdit ? 'Editar usuario' : 'Nuevo usuario' }}
              </h2>
              <p class="mt-0.5 text-sm text-muted-foreground">
                {{ isEdit
                  ? 'Modifica los datos del usuario.'
                  : 'Completa el formulario para registrar un nuevo usuario.' }}
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
            <div v-if="!isEdit" class="grid grid-cols-2 gap-4">
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

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
