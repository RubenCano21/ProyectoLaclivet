<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { catalogoService, type CatalogoExamen } from '@/services/catalogoService'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Plus, Pencil, Trash2, Check, X,
  Loader2, AlertCircle, BookOpen,
} from 'lucide-vue-next'

// ── Props ──────────────────────────────────────────────────────────────────────
const props = defineProps<{
  catalogos: CatalogoExamen[]
  selectedCatId: number | null
  countExamenes: (id: number) => number
}>()

// ── Emits ──────────────────────────────────────────────────────────────────────
const emit = defineEmits<{
  (e: 'select', id: number): void
  (e: 'created', cat: CatalogoExamen): void
  (e: 'updated', cat: CatalogoExamen): void
  (e: 'deleted', id: number): void
}>()

// ── Estado local ───────────────────────────────────────────────────────────────
const error   = ref<string | null>(null)
const saving  = ref(false)

// add
const showAdd    = ref(false)
const addNombre  = ref('')
const addArea    = ref('')
const addPrecio  = ref('')

// edit
const editId     = ref<number | null>(null)
const editNombre = ref('')
const editArea   = ref('')
const editPrecio = ref('')

// delete
const deleteId   = ref<number | null>(null)

// ── Agregar ────────────────────────────────────────────────────────────────────
async function openAdd() {
  showAdd.value  = true
  addNombre.value = ''; addArea.value = ''; addPrecio.value = ''
  error.value    = null
  await nextTick()
  document.getElementById('add-cat-nombre')?.focus()
}

async function create() {
  const nombre = addNombre.value.trim()
  if (!nombre) return
  saving.value = true; error.value = null
  try {
    const res = await catalogoService.create({
      nombre,
      area:   addArea.value.trim()   || null,
      precio: addPrecio.value.trim() || null,
    })
    emit('created', res.data)
    showAdd.value = false
  } catch { error.value = 'No se pudo crear el catálogo.' }
  finally   { saving.value = false }
}

// ── Editar ─────────────────────────────────────────────────────────────────────
function startEdit(c: CatalogoExamen) {
  editId.value     = c.id
  editNombre.value = c.nombre
  editArea.value   = c.area   ?? ''
  editPrecio.value = c.precio ?? ''
  error.value      = null
  deleteId.value   = null
}
function cancelEdit() { editId.value = null }

async function save() {
  const nombre = editNombre.value.trim()
  if (!nombre) return
  saving.value = true; error.value = null
  try {
    const res = await catalogoService.update(editId.value!, {
      nombre,
      area:   editArea.value.trim()   || null,
      precio: editPrecio.value.trim() || null,
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
    await catalogoService.delete(id)
    emit('deleted', id)
    deleteId.value = null
  } catch { error.value = 'No se pudo eliminar. Puede tener exámenes asociados.' }
}
</script>

<template>
  <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
      <div class="flex items-center gap-2">
        <BookOpen class="h-4 w-4 text-primary" />
        <span class="font-semibold text-sm">Catálogos</span>
        <Badge variant="secondary">{{ catalogos.length }}</Badge>
      </div>
      <Button size="sm" variant="ghost" class="gap-1 h-7 text-xs" @click="openAdd">
        <Plus class="h-3.5 w-3.5" /> Nuevo
      </Button>
    </div>

    <!-- Error -->
    <div v-if="error" class="mx-3 mt-2 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
      <AlertCircle class="h-3.5 w-3.5 shrink-0" />
      {{ error }}
      <button class="ml-auto" @click="error = null"><X class="h-3 w-3" /></button>
    </div>

    <!-- Formulario agregar -->
    <div v-if="showAdd" class="px-3 pt-3 pb-2 space-y-2 border-b">
      <Input
        id="add-cat-nombre"
        v-model="addNombre"
        placeholder="Nombre del catálogo *"
        class="h-8 text-sm"
        @keyup.escape="showAdd = false"
      />
      <div class="flex gap-2">
        <Input v-model="addArea"   placeholder="Área (ej. Hematología)" class="h-8 text-sm" />
        <Input v-model="addPrecio" placeholder="Precio (Bs.)"           class="h-8 text-sm w-28" />
      </div>
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
        v-if="catalogos.length === 0"
        class="px-4 py-6 text-center text-sm text-muted-foreground"
      >
        Sin catálogos.
      </li>

      <li
        v-for="cat in catalogos"
        :key="cat.id"
        class="group relative cursor-pointer px-3 py-2 transition-colors"
        :class="selectedCatId === cat.id
          ? 'bg-primary/10 border-l-2 border-primary'
          : 'hover:bg-muted/40 border-l-2 border-transparent'"
        @click="emit('select', cat.id)"
      >
        <!-- Edición -->
        <div v-if="editId === cat.id" class="space-y-1.5" @click.stop>
          <Input
            v-model="editNombre"
            placeholder="Nombre *"
            class="h-7 text-sm"
            autofocus
            @keyup.escape="cancelEdit"
          />
          <div class="flex gap-1.5">
            <Input v-model="editArea"   placeholder="Área"   class="h-7 text-sm" />
            <Input v-model="editPrecio" placeholder="Precio" class="h-7 text-sm w-24" />
          </div>
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
        <div v-else-if="deleteId === cat.id" class="flex items-center gap-2" @click.stop>
          <span class="flex-1 text-xs text-red-600 font-medium">
            ¿Eliminar «{{ cat.nombre }}»?
          </span>
          <button
            class="shrink-0 rounded p-1 bg-red-500 text-white hover:bg-red-600"
            @click.stop="confirmDelete(cat.id)"
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
            <p class="text-sm font-medium truncate">{{ cat.nombre }}</p>
            <p class="text-xs text-muted-foreground truncate">
              <span v-if="cat.area">{{ cat.area }}</span>
              <span v-if="cat.area && cat.precio"> · </span>
              <span v-if="cat.precio">Bs. {{ cat.precio }}</span>
            </p>
          </div>
          <Badge variant="outline" class="text-xs px-1.5 py-0 shrink-0">
            {{ countExamenes(cat.id) }}
          </Badge>
          <div
            class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
          >
            <button
              class="rounded p-1 text-muted-foreground hover:text-primary hover:bg-primary/10"
              title="Editar"
              @click.stop="startEdit(cat)"
            >
              <Pencil class="h-3.5 w-3.5" />
            </button>
            <button
              class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50"
              title="Eliminar"
              @click.stop="deleteId = cat.id; error = null"
            >
              <Trash2 class="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>