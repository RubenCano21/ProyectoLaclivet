<script setup lang="ts">
import { ref, nextTick } from 'vue'
import {
  valorReferenciaService,
  SEXO_LABELS,
  type SexoReferencia, type ValorReferencia,
} from '@/services/catalogoService'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Plus, Pencil, Trash2, Check, X, Loader2, AlertCircle, Ruler } from 'lucide-vue-next'

// ── Props ──────────────────────────────────────────────────────────────────────
const props = defineProps<{
  parametroId: number
  valores: ValorReferencia[]
}>()

// ── Emits ──────────────────────────────────────────────────────────────────────
const emit = defineEmits<{
  (e: 'created', val: ValorReferencia): void
  (e: 'updated', val: ValorReferencia): void
  (e: 'deleted', id: number): void
}>()

// ── Opciones estáticas ─────────────────────────────────────────────────────────
// SEXO_LABELS viene del service — derivamos el array de opciones de él
const sexoOptions = Object.entries(SEXO_LABELS) as [SexoReferencia, string][]

// ── Estado local ───────────────────────────────────────────────────────────────
const error  = ref<string | null>(null)
const saving = ref(false)

// add
const showAdd    = ref(false)
const addMin     = ref('')
const addMax     = ref('')
const addEspecie = ref('')
const addSexo    = ref<SexoReferencia>('A')
const addTexto   = ref('')

// edit
const editId      = ref<number | null>(null)
const editMin     = ref('')
const editMax     = ref('')
const editEspecie = ref('')
const editSexo    = ref<SexoReferencia>('A')
const editTexto   = ref('')

// delete
const deleteId    = ref<number | null>(null)

// ── Agregar ────────────────────────────────────────────────────────────────────
async function openAdd() {
  showAdd.value    = true
  addMin.value     = ''; addMax.value = ''; addEspecie.value = ''
  addSexo.value    = 'A'; addTexto.value = ''
  error.value      = null
  await nextTick()
  document.getElementById(`add-val-especie-${props.parametroId}`)?.focus()
}

async function create() {
  saving.value = true; error.value = null
  try {
    const res = await valorReferenciaService.create({
      valor_min:        addMin.value.trim()     || null,
      valor_max:        addMax.value.trim()     || null,
      especie:          addEspecie.value.trim() || null,
      sexo:             addSexo.value,
      texto_referencia: addTexto.value.trim()   || null,
      parametro:        props.parametroId,
    })
    emit('created', res.data)
    showAdd.value = false
  } catch { error.value = 'No se pudo crear el valor.' }
  finally   { saving.value = false }
}

// ── Editar ─────────────────────────────────────────────────────────────────────
function startEdit(v: ValorReferencia) {
  editId.value      = v.id
  editMin.value     = v.valor_min         ?? ''
  editMax.value     = v.valor_max         ?? ''
  editEspecie.value = v.especie           ?? ''
  editSexo.value    = v.sexo              ?? 'A'
  editTexto.value   = v.texto_referencia  ?? ''
  error.value       = null
  deleteId.value    = null
}
function cancelEdit() { editId.value = null }

async function save() {
  saving.value = true; error.value = null
  try {
    const res = await valorReferenciaService.update(editId.value!, {
      valor_min:        editMin.value.trim()     || null,
      valor_max:        editMax.value.trim()     || null,
      especie:          editEspecie.value.trim() || null,
      sexo:             editSexo.value,
      texto_referencia: editTexto.value.trim()   || null,
      parametro:        props.parametroId,
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
    await valorReferenciaService.delete(id)
    emit('deleted', id)
    deleteId.value = null
  } catch { error.value = 'No se pudo eliminar.' }
}
</script>

<template>
  <div class="bg-muted/20 border-t border-border/40 px-4 pb-2 pt-1">

    <!-- Error -->
    <div
      v-if="error"
      class="mt-1 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs text-red-600"
    >
      <AlertCircle class="h-3.5 w-3.5 shrink-0" />{{ error }}
      <button class="ml-auto" @click="error = null"><X class="h-3 w-3" /></button>
    </div>

    <!-- Lista de valores -->
    <ul class="mt-1 space-y-1">
      <li
        v-if="valores.length === 0 && !showAdd"
        class="text-xs text-muted-foreground py-1 italic"
      >
        Sin valores de referencia.
      </li>

      <li v-for="val in valores" :key="val.id">

        <!-- Edición -->
        <div v-if="editId === val.id" class="space-y-1.5 py-1">
          <div class="flex flex-wrap gap-1.5 items-center">
            <Input
              v-model="editEspecie"
              placeholder="Especie"
              class="h-7 text-xs w-24"
              autofocus
            />
            <select v-model="editSexo" class="h-7 text-xs border rounded-md px-1.5 bg-background">
              <option v-for="[value, label] in sexoOptions" :key="value" :value="value">{{ label }}</option>
            </select>
            <Input v-model="editMin" placeholder="Mín" class="h-7 text-xs w-14" />
            <Input v-model="editMax" placeholder="Máx" class="h-7 text-xs w-14" />
          </div>
          <div class="flex gap-1.5">
            <Input v-model="editTexto" placeholder="Texto referencia" class="h-7 text-xs flex-1" />
            <button
              class="rounded px-1.5 py-1 text-xs bg-primary text-primary-foreground flex items-center gap-0.5"
              :disabled="saving"
              @click="save"
            >
              <Loader2 v-if="saving" class="h-3 w-3 animate-spin" />
              <Check   v-else        class="h-3 w-3" />
            </button>
            <button class="rounded px-1.5 py-1 text-xs bg-muted" @click="cancelEdit">
              <X class="h-3 w-3" />
            </button>
          </div>
        </div>

        <!-- Confirmación borrado -->
        <div v-else-if="deleteId === val.id" class="flex items-center gap-1.5 py-1">
          <span class="flex-1 text-xs text-red-600">¿Eliminar valor?</span>
          <button
            class="rounded p-1 bg-red-500 text-white hover:bg-red-600"
            @click="confirmDelete(val.id)"
          >
            <Check class="h-3 w-3" />
          </button>
          <button class="rounded p-1 bg-muted" @click="deleteId = null">
            <X class="h-3 w-3" />
          </button>
        </div>

        <!-- Normal -->
        <div
          v-else
          class="group/val flex items-center gap-2 rounded px-1 py-0.5 hover:bg-background/60 transition-colors"
        >
          <Ruler class="h-3 w-3 text-muted-foreground shrink-0" />
          <span class="flex-1 text-xs">
            <span v-if="val.especie" class="font-medium">{{ val.especie }}</span>
            <span v-if="val.sexo && val.sexo !== 'A'" class="text-muted-foreground"> ({{ SEXO_LABELS[val.sexo] }})</span>
            <span v-if="val.especie">: </span>
            <template v-if="val.texto_referencia">{{ val.texto_referencia }}</template>
            <template v-else>{{ val.valor_min ?? '—' }} – {{ val.valor_max ?? '—' }}</template>
          </span>
          <div class="flex gap-0.5 opacity-0 group-hover/val:opacity-100 transition-opacity">
            <button
              class="rounded p-0.5 text-muted-foreground hover:text-primary hover:bg-primary/10"
              @click="startEdit(val)"
            >
              <Pencil class="h-3 w-3" />
            </button>
            <button
              class="rounded p-0.5 text-muted-foreground hover:text-red-500 hover:bg-red-50"
              @click="deleteId = val.id; error = null"
            >
              <Trash2 class="h-3 w-3" />
            </button>
          </div>
        </div>
      </li>
    </ul>

    <!-- Formulario agregar valor -->
    <div v-if="showAdd" class="mt-2 space-y-1.5">
      <div class="flex flex-wrap gap-1.5">
        <Input
          :id="`add-val-especie-${parametroId}`"
          v-model="addEspecie"
          placeholder="Especie"
          class="h-7 text-xs w-24"
          @keyup.escape="showAdd = false"
        />
        <select v-model="addSexo" class="h-7 text-xs border rounded-md px-1.5 bg-background">
          <option v-for="[value, label] in sexoOptions" :key="value" :value="value">{{ label }}</option>
        </select>
        <Input v-model="addMin" placeholder="Mín" class="h-7 text-xs w-14" />
        <Input v-model="addMax" placeholder="Máx" class="h-7 text-xs w-14" />
      </div>
      <Input v-model="addTexto" placeholder="Texto referencia (ej: '-a +') — alternativo a Mín/Máx" class="h-7 text-xs w-full" />
      <div class="flex gap-1.5">
        <Button size="sm" class="h-6 px-2 text-xs" :disabled="saving" @click="create">
          <Loader2 v-if="saving" class="h-3 w-3 animate-spin mr-1" />Guardar
        </Button>
        <Button size="sm" variant="ghost" class="h-6 px-2 text-xs" @click="showAdd = false">
          Cancelar
        </Button>
      </div>
    </div>

    <!-- Botón agregar valor -->
    <button
      v-if="!showAdd"
      class="mt-1.5 flex items-center gap-1 text-xs text-muted-foreground hover:text-primary transition-colors"
      @click.stop="openAdd"
    >
      <Plus class="h-3 w-3" /> Agregar valor de referencia
    </button>
  </div>
</template>