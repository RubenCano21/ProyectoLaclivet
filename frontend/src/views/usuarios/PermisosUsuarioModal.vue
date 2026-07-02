<template>
  <Dialog :open="open" @update:open="$emit('update:open', $event)">
    <DialogContent class="max-w-xl max-h-[85vh] flex flex-col gap-0 p-0 overflow-hidden">

      <!-- Cabecera -->
      <div class="px-6 pt-6 pb-4 border-b border-mineral-green-100">
        <DialogTitle class="flex items-center gap-2 text-mineral-green-900 text-base font-semibold">
          <span class="flex h-7 w-7 items-center justify-center rounded-lg bg-mineral-green-100">
            <ShieldIcon class="h-4 w-4 text-mineral-green-600" />
          </span>
          {{ usuario?.first_name }} {{ usuario?.last_name }}
        </DialogTitle>
        <DialogDescription class="mt-1 text-xs text-mineral-green-500 pl-9">
          Rol: <span class="font-semibold text-mineral-green-700">{{ usuario?.rol?.nombre ?? 'Sin rol' }}</span>
          &nbsp;·&nbsp; Los permisos activos (incluyendo los del rol) pueden quitarse individualmente.
        </DialogDescription>
      </div>

      <!-- Cuerpo con scroll -->
      <div class="flex-1 overflow-y-auto px-6 py-4">
        <!-- Loading -->
        <div v-if="loading" class="flex justify-center py-16">
          <Loader2Icon class="h-6 w-6 animate-spin text-mineral-green-400" />
        </div>

        <!-- Sin permisos cargados -->
        <div v-else-if="store.permisos.length === 0" class="py-10 text-center text-sm text-mineral-green-400">
          No hay permisos configurados en el sistema.
        </div>

        <!-- Grupos de permisos -->
        <template v-else>
          <div
            v-for="(grupo, label) in permisosAgrupados"
            :key="label"
            class="mb-5"
          >
            <!-- Cabecera de grupo -->
            <div class="flex items-center gap-2 mb-3">
              <span class="flex h-6 w-6 items-center justify-center rounded-lg bg-mineral-green-100">
                <KeyRoundIcon class="h-3 w-3 text-mineral-green-600" />
              </span>
              <h4 class="text-sm font-semibold text-mineral-green-800">
                Privilegios de {{ (label as string).toLowerCase() }}
              </h4>
              <div class="flex-1 h-px bg-mineral-green-100" />
            </div>

            <!-- Filas -->
            <div class="rounded-xl border border-mineral-green-100 overflow-hidden">
              <div
                v-for="(permiso, idx) in grupo"
                :key="permiso.id"
                :class="[
                  'grid grid-cols-[160px_56px_1fr] items-center gap-3 px-4 py-3 transition-colors',
                  'hover:bg-mineral-green-50/60',
                  idx < grupo.length - 1 ? 'border-b border-mineral-green-100' : '',
                ]"
              >
                <span class="text-sm text-right text-mineral-green-600 font-medium leading-tight pr-1">
                  {{ permiso.nombre }}
                </span>
                <div class="flex justify-center">
                  <Switch
                    class="data-[state=checked]:bg-mineral-green-600"
                    :checked="activoSet.has(permiso.id)"
                    @update:checked="toggle(permiso.id, $event)"
                  />
                </div>
                <span class="text-xs text-mineral-green-400 leading-snug">
                  {{ permiso.descripcion }}
                </span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Footer -->
      <div class="px-6 py-4 border-t border-mineral-green-100 flex justify-end gap-2 bg-white">
        <Button variant="outline" @click="$emit('update:open', false)">Cancelar</Button>
        <Button
          class="bg-mineral-green-600 hover:bg-mineral-green-700 text-white"
          :disabled="loading || saving"
          @click="guardar"
        >
          <Loader2Icon v-if="saving" class="h-4 w-4 animate-spin mr-2" />
          Guardar permisos
        </Button>
      </div>

    </DialogContent>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { ShieldIcon, Loader2Icon, KeyRoundIcon } from 'lucide-vue-next'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { useRolesPermisosStore, type Permiso } from '@/stores/rolesPermisos'
import { useNotification } from '@/composables/useNotification'

interface UsuarioResumen {
  id: number
  first_name: string
  last_name: string
  rol: { id: number; nombre: string } | null
}

const props = defineProps<{
  open: boolean
  usuario: UsuarioResumen | null
}>()

const emit = defineEmits<{
  (e: 'update:open', val: boolean): void
}>()

const store = useRolesPermisosStore()
const { notify } = useNotification()

const loading = ref(false)
const saving = ref(false)

/**
 * Array of active permiso IDs. Using array (not Set) for reliable Vue reactivity.
 * Initialized with role permisos + extra permisos on load.
 */
const permisosMarcados = ref<number[]>([])
/** Computed Set for O(1) lookups in the template — derived from the reactive array. */
const activoSet = computed(() => new Set(permisosMarcados.value))
/** IDs that belong to the user's current role (to compute extras on save). */
const rolIds = ref<Set<number>>(new Set())

// ── Agrupar por la última palabra del código ──────────────────────────────────
const permisosAgrupados = computed(() => {
  const groups: Record<string, Permiso[]> = {}
  for (const p of store.permisos) {
    const parts = p.codigo.split('_')
    const raw = (parts.length > 1 ? parts[parts.length - 1] : 'general').toLowerCase()
    const norm = raw.endsWith('s') && raw.length > 2 ? raw.slice(0, -1) : raw
    const label = norm.charAt(0).toUpperCase() + norm.slice(1)
    if (!groups[label]) groups[label] = []
    groups[label].push(p)
  }
  return groups
})

function toggle(id: number, checked: boolean) {
  if (checked) {
    if (!permisosMarcados.value.includes(id)) {
      permisosMarcados.value = [...permisosMarcados.value, id]
    }
  } else {
    permisosMarcados.value = permisosMarcados.value.filter((x) => x !== id)
  }
}

async function cargar() {
  if (!props.usuario) return
  loading.value = true
  if (store.permisos.length === 0) await store.fetchAll()
  const result = await store.getPermisosExtraUsuario(props.usuario.id)
  if (result.ok) {
    const rolArr = (result.permisos_rol ?? []).map((p) => p.id)
    const extrasArr = (result.permisos_extra ?? []).map((p) => p.id)
    rolIds.value = new Set(rolArr)
    // Merge: role permisos + individual extras, deduplicated
    const merged = Array.from(new Set([...rolArr, ...extrasArr]))
    permisosMarcados.value = merged
  } else {
    notify('error', result.error ?? 'Error al cargar permisos')
  }
  loading.value = false
}

async function guardar() {
  if (!props.usuario) return
  saving.value = true
  // "Extras" = anything active that is NOT in the original role set
  const extrasFinales = permisosMarcados.value.filter((id) => !rolIds.value.has(id))
  const result = await store.setPermisosExtraUsuario(props.usuario.id, extrasFinales)
  saving.value = false
  if (result.ok) {
    notify('success', 'Permisos actualizados correctamente.')
    emit('update:open', false)
  } else {
    notify('error', result.error ?? 'Error al guardar permisos')
  }
}

watch(
  () => props.open,
  (val) => {
    if (val) cargar()
    else {
      permisosMarcados.value = []
      rolIds.value = new Set()
    }
  },
)
</script>
