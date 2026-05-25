<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  especieService, razaService, propietarioService, pacienteService,
  type Especie, type Raza, type Propietario,
} from '@/services/pacienteService'
import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import { Loader2, PawPrint, AlertCircle } from 'lucide-vue-next'

const router = useRouter()

// ── Catálogos ─────────────────────────────────────────────────────────────────
const especies     = ref<Especie[]>([])
const todasRazas   = ref<Raza[]>([])
const propietarios = ref<Propietario[]>([])
const loadingData  = ref(true)

// ── Formulario ────────────────────────────────────────────────────────────────
const especieId = ref('')
const form = ref({
  nombre: '',
  sexo: '',
  tamanio: '',
  color: '',
  fecha_nacimiento: '',
  propietario: '',
  raza: '',
})

const razasFiltradas = computed(() =>
  todasRazas.value.filter(r => String(r.especie) === especieId.value),
)

// ── Estado ────────────────────────────────────────────────────────────────────
const saving = ref(false)
const error  = ref<string | null>(null)

// ── Carga inicial ─────────────────────────────────────────────────────────────
onMounted(async () => {
  try {
    const [re, rr, rp] = await Promise.all([
      especieService.getAll(),
      razaService.getAll(),
      propietarioService.getAll(),
    ])
    especies.value     = (re.data as any).resultados ?? (re.data as any).results ?? re.data
    todasRazas.value   = (rr.data as any).resultados ?? (rr.data as any).results ?? rr.data
    propietarios.value = (rp.data as any).resultados ?? (rp.data as any).results ?? rp.data
  } catch {
    error.value = 'Error al cargar los datos del formulario'
  } finally {
    loadingData.value = false
  }
})

function onEspecieChange() {
  form.value.raza = ''
}

// ── Guardar ───────────────────────────────────────────────────────────────────
async function handleSubmit() {
  error.value = null
  if (!form.value.nombre.trim()) {
    error.value = 'El nombre del paciente es requerido'
    return
  }
  saving.value = true
  try {
    await pacienteService.create({
      nombre:           form.value.nombre.trim(),
      sexo:             form.value.sexo || '',
      tamanio:          form.value.tamanio || '',
      color:            form.value.color.trim(),
      fecha_nacimiento: form.value.fecha_nacimiento || null,
      propietario:      form.value.propietario ? Number(form.value.propietario) : (null as any),
      raza:             form.value.raza ? Number(form.value.raza) : (null as any),
    } as any)
    router.push('/pacientes')
  } catch (e: any) {
    const data = e.response?.data
    if (data && typeof data === 'object') {
      const msgs = Object.entries(data)
        .map(([k, v]) => `${k}: ${Array.isArray(v) ? (v as string[]).join(', ') : v}`)
        .join(' | ')
      error.value = msgs
    } else {
      error.value = 'Error al guardar el paciente'
    }
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>

      <!-- Header -->
      <header class="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger class="-ml-1" />
        <Separator orientation="vertical" class="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/dashboard">Inicio</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink href="/pacientes">Pacientes</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Nuevo paciente</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6">
        <div class="mx-auto w-full max-w-2xl space-y-6">

          <!-- Título -->
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <PawPrint class="h-5 w-5" />
            </div>
            <div>
              <h1 class="text-2xl font-bold leading-tight">Nuevo paciente</h1>
              <p class="text-sm text-muted-foreground">Registra un nuevo animal en el sistema</p>
            </div>
          </div>

          <!-- Error -->
          <div
            v-if="error"
            class="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
          >
            <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
            {{ error }}
          </div>

          <!-- Cargando catálogos -->
          <div v-if="loadingData" class="flex items-center gap-3 py-8 text-muted-foreground">
            <Loader2 class="h-5 w-5 animate-spin" />
            <span class="text-sm">Cargando catálogos…</span>
          </div>

          <!-- Formulario -->
          <form
            v-else
            @submit.prevent="handleSubmit"
            class="rounded-xl border bg-white p-6 shadow-xs space-y-5"
          >
            <!-- Nombre -->
            <div class="space-y-1.5">
              <label class="text-sm font-medium">
                Nombre <span class="text-red-500">*</span>
              </label>
              <Input v-model="form.nombre" placeholder="Ej: Max" autofocus />
            </div>

            <!-- Especie + Raza -->
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Especie</label>
                <Select v-model="especieId" @update:model-value="onEspecieChange">
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar especie…" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="e in especies" :key="e.id" :value="String(e.id)">
                      {{ e.nombre }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Raza</label>
                <Select v-model="form.raza" :disabled="!especieId || razasFiltradas.length === 0">
                  <SelectTrigger>
                    <SelectValue
                      :placeholder="!especieId ? 'Selecciona una especie primero' : 'Seleccionar raza…'"
                    />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="r in razasFiltradas" :key="r.id" :value="String(r.id)">
                      {{ r.nombre }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <!-- Sexo + Tamaño -->
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Sexo</label>
                <Select v-model="form.sexo">
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar…" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="macho">Macho</SelectItem>
                    <SelectItem value="hembra">Hembra</SelectItem>
                    <SelectItem value="desconocido">Desconocido</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Tamaño</label>
                <Select v-model="form.tamanio">
                  <SelectTrigger>
                    <SelectValue placeholder="Seleccionar…" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pequeño">Pequeño</SelectItem>
                    <SelectItem value="mediano">Mediano</SelectItem>
                    <SelectItem value="grande">Grande</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <!-- Color + Fecha nacimiento -->
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Color</label>
                <Input v-model="form.color" placeholder="Ej: café, negro y blanco…" />
              </div>
              <div class="space-y-1.5">
                <label class="text-sm font-medium">Fecha de nacimiento</label>
                <Input type="date" v-model="form.fecha_nacimiento" />
              </div>
            </div>

            <!-- Propietario -->
            <div class="space-y-1.5">
              <label class="text-sm font-medium">Propietario</label>
              <Select v-model="form.propietario">
                <SelectTrigger>
                  <SelectValue placeholder="Seleccionar propietario…" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="p in propietarios" :key="p.id" :value="String(p.id)">
                    {{ p.nombre }} {{ p.apellido }} — {{ p.ci }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <!-- Acciones -->
            <div class="flex items-center justify-end gap-3 pt-2 border-t">
              <Button type="button" variant="outline" @click="router.push('/pacientes')">
                Cancelar
              </Button>
              <Button type="submit" :disabled="saving" class="gap-2">
                <Loader2 v-if="saving" class="h-4 w-4 animate-spin" />
                Guardar paciente
              </Button>
            </div>
          </form>

        </div>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
