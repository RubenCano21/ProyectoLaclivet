<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { examenService, type CatalogoExamen, type Examen } from '@/services/catalogoService'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Plus, Pencil, Trash2, Check, X,
  Loader2, AlertCircle, FlaskConical, BookOpen,
} from 'lucide-vue-next'

// ── Props ──────────────────────────────────────────────────────────────────────
const props = defineProps<{
  examenes: Examen[]
  selectedCat: CatalogoExamen | null
  selectedExId: number | null
  countParametros: (id: number) => number
}>()

// ── Emits ──────────────────────────────────────────────────────────────────────
const emit = defineEmits<{
  (e: 'select', id: number): void
  (e: 'created', ex: Examen): void
  (e: 'updated', ex: Examen): void
  (e: 'deleted', id: number): void
}>()

// ── Estado local ───────────────────────────────────────────────────────────────
const error  = ref<string | null>(null)
const saving = ref(false)

// add
const showAdd      = ref(false)
const addNombre    = ref('')
const addCategoria = ref('')
const addDesc      = ref('')

// edit
const editId       = ref<number | null>(null)
const editNombre   = ref('')
const editCategoria = ref('')
const editDesc     = ref('')

// delete
const deleteId     = ref<number | null>(null)

// ── Agregar ────────────────────────────────────────────────────────────────────
async function openAdd() {
  showAdd.value    = true
  addNombre.value  = ''; addCategoria.value = ''; addDesc.value = ''
  error.value      = null
  await nextTick()
  document.getElementById('add-ex-nombre')?.focus()
}

async function create() {
  const nombre = addNombre.value.trim()
  if (!nombre || !props.selectedCat) return
  saving.value = true; error.value = null
  try {
    const res = await examenService.create({
      nombre_examen: nombre,
      categoria:     addCategoria.value.trim() || null,
      descripcion:   addDesc.value.trim()      || null,
      catalogo:      props.selectedCat.id,
    })
    emit('created', res.data)
    showAdd.value = false
  } catch { error.value = 'No se pudo crear el examen.' }
  finally   { saving.value = false }
}

// ── Editar ─────────────────────────────────────────────────────────────────────
function startEdit(ex: Examen) {
  editId.value        = ex.id
  editNombre.value    = ex.nombre_examen
  editCategoria.value = ex.categoria  ?? ''
  editDesc.value      = ex.descripcion ?? ''
  error.value         = null
  deleteId.value      = null
}
function cancelEdit() { editId.value = null }

async function save() {
  const nombre = editNombre.value.trim()
  if (!nombre || !props.selectedCat) return
  saving.value = true; error.value = null
  try {
    const res = await examenService.update(editId.value!, {
      nombre_examen: nombre,
      categoria:     editCategoria.value.trim() || null,
      descripcion:   editDesc.value.trim()      || null,
      catalogo:      props.selectedCat.id,
    })
    emit('updated', res.data)
    cancelEdit()
  } catch { error.value = 'No se pudo guardar.' }
  finally   { saving.value = false }
}

// ── Eliminar ───────────────────────────────────────────────────────────────────
async function confirmDelete(id: number) {
  error.value = null
  try {
    await examenService.delete(id)
    emit('deleted', id)
    deleteId.value = null
  } catch { error.value = 'No se pudo eliminar. Puede tener parámetros asociados.' }
}
</script>

<template>
  <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
      <div class="flex items-center gap-2">
        <FlaskConical class="h-4 w-4 text-primary" />
        <span class="font-semibold text-sm">
          Exámenes
          <span v-if="selectedCat" class="font-normal text-muted-foreground">
            — {{ selectedCat.nombre }}
          </span>
        </span>
        <Badge variant="secondary">{{ examenes.length }}</Badge>
      </div>
      <Button v-if="selectedCat" size="sm" variant="ghost" class="gap-1 h-7 text-xs" @click="openAdd">
        <Plus class="h-3.5 w-3.5" /> Nuevo
      </Button>
    </div>

    <!-- Sin catálogo seleccionado -->
    <div v-if="!selectedCat" class="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground">
      <BookOpen class="h-10 w-10 opacity-20" />
      <p class="text-sm">Selecciona un catálogo.</p>
    </div>

    <template v-else>
      <!-- Error -->
      <div v-if="error" class="mx-3 mt-2 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
        <AlertCircle class="h-3.5 w-3.5 shrink-0" />{{ error }}
        <button class="ml-auto" @click="error = null"><X class="h-3 w-3" /></button>
      </div>

      <!-- Formulario agregar -->
      <div v-if="showAdd" class="px-3 pt-3 pb-2 space-y-2 border-b">
        <Input
          id="add-ex-nombre"
          v-model="addNombre"
          placeholder="Nombre del examen *"
          class="h-8 text-sm"
          @keyup.escape="showAdd = false"
        />
        <Input v-model="addCategoria" placeholder="Categoría (opcional)"  class="h-8 text-sm" />
        <Input v-model="addDesc"      placeholder="Descripción (opcional)" class="h-8 text-sm" />
        <div class="flex gap-2 justify-end">
          <Button size="sm" class="h-7 px-3 text-xs" :disabled="saving" @click="create">
            <Loader2 v-if="saving" class="h-3.5 w-3.5 animate-spin mr-1" />
            <Check  v-else         class="h-3.5 w-3.5 mr-1" />
            Guardar
          </Button>
          <Button size="sm" variant="ghost" class="h-7 px-3 text-xs" @click="showAdd = false">
            Cancelar
          </Button>
        </div>
      </div>

      <!-- Lista -->
      <ul class="py-1">
        <li
          v-if="examenes.length === 0"
          class="px-4 py-8 text-center text-sm text-muted-foreground"
        >
          Sin exámenes en <strong>{{ selectedCat.nombre }}</strong>.
        </li>

        <li
          v-for="ex in examenes"
          :key="ex.id"
          class="group relative cursor-pointer px-3 py-2 transition-colors"
          :class="selectedExId === ex.id
            ? 'bg-primary/10 border-l-2 border-primary'
            : 'hover:bg-muted/40 border-l-2 border-transparent'"
          @click="emit('select', ex.id)"
        >
          <!-- Edición -->
          <div v-if="editId === ex.id" class="space-y-1.5" @click.stop>
            <Input
              v-model="editNombre"
              placeholder="Nombre *"
              class="h-7 text-sm"
              autofocus
              @keyup.escape="cancelEdit"
            />
            <Input v-model="editCategoria" placeholder="Categoría"   class="h-7 text-sm" />
            <Input v-model="editDesc"      placeholder="Descripción" class="h-7 text-sm" />
            <div class="flex gap-1 justify-end">
              <button
                class="rounded px-2 py-1 text-xs bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-1"
                :disabled="saving"
                @click.stop="save"
              >
                <Loader2 v-if="saving" class="h-3 w-3 animate-spin" />
                <Check   v-else        class="h-3 w-3" />
                Guardar
              </button>
              <button
                class="rounded px-2 py-1 text-xs bg-muted hover:bg-muted/70"
                @click.stop="cancelEdit"
              >
                Cancelar
              </button>
            </div>
          </div>

          <!-- Confirmación borrado -->
          <div v-else-if="deleteId === ex.id" class="flex items-center gap-2" @click.stop>
            <span class="flex-1 text-xs text-red-600 font-medium">
              ¿Eliminar «{{ ex.nombre_examen }}»?
            </span>
            <button
              class="shrink-0 rounded p-1 bg-red-500 text-white hover:bg-red-600"
              @click.stop="confirmDelete(ex.id)"
            >
              <Check class="h-3.5 w-3.5" />
            </button>
            <button
              class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted"
              @click.stop="deleteId = null"
            >
              <X class="h-3.5 w-3.5" />
            </button>
          </div>

          <!-- Normal -->
          <div v-else class="flex items-center gap-2">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate">{{ ex.nombre_examen }}</p>
              <p v-if="ex.categoria" class="text-xs text-muted-foreground truncate">{{ ex.categoria }}</p>
            </div>
            <Badge variant="outline" class="text-xs px-1.5 py-0 shrink-0">
              {{ countParametros(ex.id) }}
            </Badge>
            <div class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0">
              <button
                class="rounded p-1 text-muted-foreground hover:text-primary hover:bg-primary/10"
                title="Editar"
                @click.stop="startEdit(ex)"
              >
                <Pencil class="h-3.5 w-3.5" />
              </button>
              <button
                class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50"
                title="Eliminar"
                @click.stop="deleteId = ex.id; error = null"
              >
                <Trash2 class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </li>
      </ul>
    </template>
  </div>
</template>