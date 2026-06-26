<script setup lang="ts">
import { ref, nextTick } from 'vue'
import {
  parametroService,
  TIPO_DATO_LABELS,
  type TipoDatoParametro,
  type Examen, type Parametro, type ValorReferencia,
} from '@/services/catalogoService'
import ValoresReferencia from './ValoresReferencia.vue'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Plus, Pencil, Trash2, Check, X,
  Loader2, AlertCircle, FlaskConical, SlidersHorizontal,
  ChevronDown, ChevronRight,
} from 'lucide-vue-next'

// ── Props ──────────────────────────────────────────────────────────────────────
const props = defineProps<{
  parametros: Parametro[]
  valores: ValorReferencia[]
  selectedEx: Examen | null
  countValores: (id: number) => number
}>()

// ── Emits ──────────────────────────────────────────────────────────────────────
const emit = defineEmits<{
  (e: 'created', par: Parametro): void
  (e: 'updated', par: Parametro): void
  (e: 'deleted', id: number): void
  (e: 'valor-created', val: ValorReferencia): void
  (e: 'valor-updated', val: ValorReferencia): void
  (e: 'valor-deleted', id: number): void
}>()

// ── Opciones estáticas ─────────────────────────────────────────────────────────
// Derivadas de los tipos del service para mantener una única fuente de verdad
const tipoDatoOptions = Object.entries(TIPO_DATO_LABELS) as [TipoDatoParametro, string][]

// ── Estado local ───────────────────────────────────────────────────────────────
const error  = ref<string | null>(null)
const saving = ref(false)

// add
const showAdd      = ref(false)
const addNombre    = ref('')
const addUnidad    = ref('')
const addGrupo     = ref('')
const addOrden     = ref('')
const addTipoDato  = ref<TipoDatoParametro>('NUM')
const addOpciones  = ref('')

// edit
const editId       = ref<number | null>(null)
const editNombre   = ref('')
const editUnidad   = ref('')
const editGrupo    = ref('')
const editOrden    = ref('')
const editTipoDato = ref<TipoDatoParametro>('NUM')
const editOpciones = ref('')

// delete
const deleteId   = ref<number | null>(null)

// expand
const expandedIds = ref<Set<number>>(new Set())

// ── Helpers ────────────────────────────────────────────────────────────────────
function valoresDelPar(id: number) {
  return props.valores.filter(v => v.parametro === id)
}

function togglePar(id: number) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

// ── Agregar ────────────────────────────────────────────────────────────────────
async function openAdd() {
  showAdd.value     = true
  addNombre.value   = ''; addUnidad.value  = ''
  addGrupo.value    = ''; addOrden.value   = ''
  addTipoDato.value = 'NUM'; addOpciones.value = ''
  error.value       = null
  await nextTick()
  document.getElementById('add-par-nombre')?.focus()
}

async function create() {
  const nombre = addNombre.value.trim()
  if (!nombre || !props.selectedEx) return
  saving.value = true; error.value = null
  try {
    const payload: Record<string, unknown> = {
      nombre_parametro:   nombre,
      unidad_medida:      addUnidad.value.trim()  || null,
      grupo:              addGrupo.value.trim()   || null,
      tipo_dato:          addTipoDato.value,
      opciones_seleccion: addTipoDato.value === 'SEL' ? addOpciones.value.trim() : '',
      examen:             props.selectedEx.id,
    }
    if (addOrden.value.trim()) payload.orden = Number(addOrden.value)
    const res = await parametroService.create(payload as any)
    emit('created', res.data)
    showAdd.value = false
  } catch { error.value = 'No se pudo crear el parámetro.' }
  finally   { saving.value = false }
}

// ── Editar ─────────────────────────────────────────────────────────────────────
function startEdit(p: Parametro) {
  editId.value        = p.id
  editNombre.value    = p.nombre_parametro
  editUnidad.value    = p.unidad_medida   ?? ''
  editGrupo.value     = p.grupo           ?? ''
  editOrden.value     = p.orden != null   ? String(p.orden) : ''
  editTipoDato.value  = p.tipo_dato       ?? 'NUM'
  // opciones_seleccion es string en ParametroForm (no string[] — opciones[] es read-only del backend)
  editOpciones.value  = p.opciones_seleccion ?? ''
  error.value         = null
  deleteId.value      = null
}
function cancelEdit() { editId.value = null }

async function save() {
  const nombre = editNombre.value.trim()
  if (!nombre || !props.selectedEx) return
  saving.value = true; error.value = null
  try {
    const payload: Record<string, unknown> = {
      nombre_parametro:   nombre,
      unidad_medida:      editUnidad.value.trim()  || null,
      grupo:              editGrupo.value.trim()   || null,
      tipo_dato:          editTipoDato.value,
      opciones_seleccion: editTipoDato.value === 'SEL' ? editOpciones.value.trim() : '',
      examen:             props.selectedEx.id,
    }
    if (editOrden.value.trim()) payload.orden = Number(editOrden.value)
    const res = await parametroService.update(editId.value!, payload as any)
    emit('updated', res.data)
    cancelEdit()
  } catch { error.value = 'No se pudo guardar.' }
  finally   { saving.value = false }
}

// ── Eliminar ───────────────────────────────────────────────────────────────────
async function confirmDelete(id: number) {
  error.value = null
  try {
    await parametroService.delete(id)
    expandedIds.value.delete(id)
    emit('deleted', id)
    deleteId.value = null
  } catch { error.value = 'No se pudo eliminar.' }
}
</script>

<template>
  <div class="rounded-xl border bg-white shadow-xs overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
      <div class="flex items-center gap-2">
        <SlidersHorizontal class="h-4 w-4 text-primary" />
        <span class="font-semibold text-sm">
          Parámetros
          <span v-if="selectedEx" class="font-normal text-muted-foreground">
            — {{ selectedEx.nombre_examen }}
          </span>
        </span>
        <Badge variant="secondary">{{ parametros.length }}</Badge>
      </div>
      <Button v-if="selectedEx" size="sm" variant="ghost" class="gap-1 h-7 text-xs" @click="openAdd">
        <Plus class="h-3.5 w-3.5" /> Nuevo
      </Button>
    </div>

    <!-- Sin examen seleccionado -->
    <div v-if="!selectedEx" class="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground">
      <FlaskConical class="h-10 w-10 opacity-20" />
      <p class="text-sm">Selecciona un examen.</p>
    </div>

    <template v-else>
      <!-- Error -->
      <div v-if="error" class="mx-3 mt-2 flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
        <AlertCircle class="h-3.5 w-3.5 shrink-0" />{{ error }}
        <button class="ml-auto" @click="error = null"><X class="h-3 w-3" /></button>
      </div>

      <!-- Formulario agregar -->
      <div v-if="showAdd" class="px-3 pt-3 pb-2 space-y-2 border-b">
        <div class="flex gap-2">
          <Input
            id="add-par-nombre"
            v-model="addNombre"
            placeholder="Nombre del parámetro *"
            class="h-8 text-sm"
            @keyup.escape="showAdd = false"
          />
          <Input v-model="addUnidad" placeholder="Unidad" class="h-8 text-sm w-24" />
        </div>
        <div class="flex gap-2">
          <Input v-model="addGrupo" placeholder="Grupo (ej. Eritrograma)" class="h-8 text-sm" />
          <Input v-model="addOrden" type="number" placeholder="Orden" class="h-8 text-sm w-20" />
        </div>
        <div class="flex gap-2 items-center">
          <select v-model="addTipoDato" class="h-8 text-sm border rounded-md px-2 flex-1 bg-background">
            <option v-for="[value, label] in tipoDatoOptions" :key="value" :value="value">{{ label }}</option>
          </select>
          <Input
            v-if="addTipoDato === 'SEL'"
            v-model="addOpciones"
            placeholder="Opciones: -,+,++"
            class="h-8 text-sm flex-1"
          />
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

      <!-- Lista parámetros -->
      <ul class="py-1 divide-y divide-border/40">
        <li
          v-if="parametros.length === 0"
          class="px-4 py-8 text-center text-sm text-muted-foreground"
        >
          Sin parámetros en <strong>{{ selectedEx.nombre_examen }}</strong>.
        </li>

        <li v-for="par in parametros" :key="par.id" class="group">

          <!-- Edición del parámetro -->
          <div v-if="editId === par.id" class="px-3 py-2 space-y-1.5">
            <div class="flex gap-2">
              <Input
                v-model="editNombre"
                placeholder="Nombre *"
                class="h-7 text-sm"
                autofocus
                @keyup.escape="cancelEdit"
              />
              <Input v-model="editUnidad" placeholder="Unidad" class="h-7 text-sm w-20" />
            </div>
            <div class="flex gap-2">
              <Input v-model="editGrupo" placeholder="Grupo" class="h-7 text-sm" />
              <Input v-model="editOrden" type="number" placeholder="Orden" class="h-7 text-sm w-16" />
            </div>
            <div class="flex gap-2 items-center">
              <select v-model="editTipoDato" class="h-7 text-sm border rounded-md px-2 flex-1 bg-background">
                <option v-for="[value, label] in tipoDatoOptions" :key="value" :value="value">{{ label }}</option>
              </select>
              <Input
                v-if="editTipoDato === 'SEL'"
                v-model="editOpciones"
                placeholder="Opciones: -,+,++"
                class="h-7 text-sm flex-1"
              />
            </div>
            <div class="flex gap-1 justify-end">
              <button
                class="rounded px-2 py-1 text-xs bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-1"
                :disabled="saving"
                @click="save"
              >
                <Loader2 v-if="saving" class="h-3 w-3 animate-spin" />
                <Check   v-else        class="h-3 w-3" />
                Guardar
              </button>
              <button
                class="rounded px-2 py-1 text-xs bg-muted hover:bg-muted/70"
                @click="cancelEdit"
              >
                Cancelar
              </button>
            </div>
          </div>

          <!-- Confirmación borrado parámetro -->
          <div v-else-if="deleteId === par.id" class="px-3 py-2 flex items-center gap-2">
            <span class="flex-1 text-xs text-red-600 font-medium">
              ¿Eliminar «{{ par.nombre_parametro }}»?
            </span>
            <button
              class="shrink-0 rounded p-1 bg-red-500 text-white hover:bg-red-600"
              @click="confirmDelete(par.id)"
            >
              <Check class="h-3.5 w-3.5" />
            </button>
            <button
              class="shrink-0 rounded p-1 text-muted-foreground hover:bg-muted"
              @click="deleteId = null"
            >
              <X class="h-3.5 w-3.5" />
            </button>
          </div>

          <!-- Vista normal -->
          <div v-else>
            <!-- Fila del parámetro -->
            <div
              class="flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-muted/30 transition-colors"
              @click="togglePar(par.id)"
            >
              <component
                :is="expandedIds.has(par.id) ? ChevronDown : ChevronRight"
                class="h-3.5 w-3.5 text-muted-foreground shrink-0"
              />
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium truncate">{{ par.nombre_parametro }}</p>
                <p v-if="par.unidad_medida" class="text-xs text-muted-foreground">
                  {{ par.unidad_medida }}
                </p>
                <p v-if="par.grupo" class="text-xs text-primary/70 truncate">{{ par.grupo }}</p>
              </div>
              <Badge variant="outline" class="text-xs px-1.5 py-0 shrink-0">
                {{ countValores(par.id) }}
              </Badge>
              <div
                class="flex gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity shrink-0"
                @click.stop
              >
                <button
                  class="rounded p-1 text-muted-foreground hover:text-primary hover:bg-primary/10"
                  title="Editar"
                  @click="startEdit(par)"
                >
                  <Pencil class="h-3.5 w-3.5" />
                </button>
                <button
                  class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50"
                  title="Eliminar"
                  @click="deleteId = par.id; error = null"
                >
                  <Trash2 class="h-3.5 w-3.5" />
                </button>
              </div>
            </div>

            <!-- Valores de referencia (expandido) -->
            <ValoresReferencia
              v-if="expandedIds.has(par.id)"
              :parametro-id="par.id"
              :valores="valoresDelPar(par.id)"
              @created="emit('valor-created', $event)"
              @updated="emit('valor-updated', $event)"
              @deleted="emit('valor-deleted', $event)"
            />
          </div>
        </li>
      </ul>
    </template>
  </div>
</template>