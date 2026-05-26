<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { pacienteService, type Paciente } from '@/services/pacienteService'
import { medicoService, type MedicoVeterinario } from '@/services/medicoService'
import { catalogoService, examenService, type CatalogoExamen, type Examen } from '@/services/catalogoService'
import { cobroService, solicitudService, detalleService } from '@/services/solicitudService'
import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from '@/components/ui/select'
import {
  FilePlus, AlertCircle, Loader2, Trash2, Plus,
  FlaskConical, BookOpen, CreditCard, CheckCircle2, Search,
} from 'lucide-vue-next'

const router = useRouter()

// ── Carga ──────────────────────────────────────────────────────────────────────
const loading    = ref(true)
const loadError  = ref<string | null>(null)
const submitting = ref(false)
const submitted  = ref(false)
const submitError = ref<string | null>(null)

// ── Datos para selects ─────────────────────────────────────────────────────────
const pacientes  = ref<Paciente[]>([])
const medicos    = ref<MedicoVeterinario[]>([])
const catalogos  = ref<CatalogoExamen[]>([])
const examenes   = ref<Examen[]>([])

// ── Búsqueda de exámenes ───────────────────────────────────────────────────────
const busquedaExamen    = ref('')
const catalogoFiltroId  = ref<string>('todos')

const examenesFiltrados = computed(() => {
  let list = examenes.value
  if (catalogoFiltroId.value !== 'todos') {
    list = list.filter(e => e.catalogo === Number(catalogoFiltroId.value))
  }
  if (busquedaExamen.value.trim()) {
    const q = busquedaExamen.value.toLowerCase()
    list = list.filter(e =>
      e.nombre_examen.toLowerCase().includes(q) ||
      (e.categoria ?? '').toLowerCase().includes(q),
    )
  }
  return list
})

// ── Formulario ─────────────────────────────────────────────────────────────────
function generarCodigo() {
  const now  = new Date()
  const date = now.toISOString().slice(0, 10).replace(/-/g, '')
  const rand = Math.floor(Math.random() * 9000 + 1000)
  return `SOL-${date}-${rand}`
}

const form = ref({
  codigo:      generarCodigo(),
  paciente:    '',
  medico:      '',
  estado:      'pendiente',
  observaciones: '',
  // cobro
  metodo_pago: '',
  incluir_cobro: true,
})

// Exámenes seleccionados
interface ExamenSeleccionado {
  examen: Examen
  precio: string
}
const seleccionados = ref<ExamenSeleccionado[]>([])

const montoTotal = computed(() =>
  seleccionados.value
    .reduce((sum, s) => sum + (parseFloat(s.precio) || 0), 0)
    .toFixed(2),
)

function addExamen(ex: Examen) {
  if (seleccionados.value.some(s => s.examen.id === ex.id)) return
  // Intentar obtener precio del catálogo
  const cat = catalogos.value.find(c => c.id === ex.catalogo)
  seleccionados.value.push({ examen: ex, precio: cat?.precio ?? '' })
}

function removeExamen(id: number) {
  seleccionados.value = seleccionados.value.filter(s => s.examen.id !== id)
}

// ── Carga inicial ──────────────────────────────────────────────────────────────
async function loadAll() {
  loading.value = true
  loadError.value = null
  try {
    const [rp, rm, rc, re] = await Promise.all([
      pacienteService.getAll(),
      medicoService.getAll(),
      catalogoService.getAll(),
      examenService.getAll(),
    ])
    pacientes.value = (rp.data as any).resultados ?? (rp.data as any).results ?? rp.data
    medicos.value   = (rm.data as any).resultados ?? (rm.data as any).results ?? rm.data
    catalogos.value = (rc.data as any).resultados ?? (rc.data as any).results ?? rc.data
    examenes.value  = (re.data as any).resultados ?? (re.data as any).results ?? re.data
  } catch {
    loadError.value = 'Error al cargar los datos. Verifica la conexión.'
  } finally {
    loading.value = false
  }
}

// ── Submit ─────────────────────────────────────────────────────────────────────
async function handleSubmit() {
  if (!form.value.codigo.trim()) {
    submitError.value = 'El código es obligatorio.'
    return
  }
  submitting.value = true
  submitError.value = null
  try {
    // 1. Crear cobro si corresponde
    let cobroId: number | null = null
    if (form.value.incluir_cobro && (form.value.metodo_pago || parseFloat(montoTotal.value) > 0)) {
      const resCobro = await cobroService.create({
        monto_total: parseFloat(montoTotal.value) > 0 ? montoTotal.value : null,
        metodo_pago: form.value.metodo_pago || null,
        fecha: new Date().toISOString(),
      })
      cobroId = resCobro.data.id
    }

    // 2. Crear solicitud
    const resSol = await solicitudService.create({
      codigo:              form.value.codigo.trim(),
      observaciones:       form.value.observaciones.trim() || null,
      estado:              form.value.estado,
      cobro:               cobroId,
      paciente:            form.value.paciente ? Number(form.value.paciente) : null,
      medico_veterinario:  form.value.medico ? Number(form.value.medico) : null,
    })
    const solicitudId: number = resSol.data.id

    // 3. Crear detalles
    await Promise.all(
      seleccionados.value.map(s =>
        detalleService.create({
          solicitud: solicitudId,
          examen: s.examen.id,
          precio_aplicado: s.precio.trim() || null,
        }),
      ),
    )

    submitted.value = true
  } catch (err: any) {
    const data = err?.response?.data
    if (data?.codigo) {
      submitError.value = `Código: ${data.codigo[0]}`
    } else {
      submitError.value = 'No se pudo crear la solicitud. Verifica los datos.'
    }
  } finally {
    submitting.value = false
  }
}

function nuevaSolicitud() {
  submitted.value = false
  form.value.codigo = generarCodigo()
  form.value.paciente = ''
  form.value.medico = ''
  form.value.estado = 'pendiente'
  form.value.observaciones = ''
  form.value.metodo_pago = ''
  form.value.incluir_cobro = true
  seleccionados.value = []
  submitError.value = null
}

onMounted(loadAll)
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
              <BreadcrumbLink href="/solicitudes/catalogo">Solicitudes</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Nueva Orden</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6 max-w-6xl mx-auto w-full">

        <!-- Título -->
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <FilePlus class="h-5 w-5" />
          </div>
          <div>
            <h1 class="text-2xl font-bold leading-tight">Nueva Orden de Examen</h1>
            <p class="text-sm text-muted-foreground">Registra una nueva solicitud de análisis clínico.</p>
          </div>
        </div>

        <!-- Error de carga -->
        <div v-if="loadError" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" />{{ loadError }}
        </div>

        <!-- Skeleton -->
        <div v-if="loading" class="grid md:grid-cols-2 gap-4">
          <div class="rounded-xl border bg-white p-5 space-y-3">
            <Skeleton class="h-5 w-40" />
            <Skeleton class="h-9 w-full" v-for="n in 4" :key="n" />
          </div>
          <div class="rounded-xl border bg-white p-5 space-y-3">
            <Skeleton class="h-5 w-40" />
            <Skeleton class="h-9 w-full" v-for="n in 3" :key="n" />
          </div>
        </div>

        <!-- ── Confirmación de éxito ──────────────────────────────────────── -->
        <div v-else-if="submitted" class="flex flex-col items-center justify-center gap-5 rounded-xl border bg-white py-20 shadow-xs">
          <div class="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 text-green-600">
            <CheckCircle2 class="h-9 w-9" />
          </div>
          <div class="text-center">
            <p class="text-lg font-semibold">¡Solicitud creada correctamente!</p>
            <p class="text-sm text-muted-foreground mt-1">La orden de examen ha sido registrada en el sistema.</p>
          </div>
          <div class="flex gap-3">
            <Button @click="nuevaSolicitud">Nueva Solicitud</Button>
            <Button variant="outline" @click="router.push('/dashboard')">Ir al Dashboard</Button>
          </div>
        </div>

        <!-- ── Formulario ─────────────────────────────────────────────────── -->
        <template v-else-if="!loading">
          <div class="grid md:grid-cols-[1fr_380px] gap-5 items-start">

            <!-- Columna izquierda -->
            <div class="flex flex-col gap-5">

              <!-- Sección: Datos de la solicitud -->
              <div class="rounded-xl border bg-white shadow-xs overflow-hidden">
                <div class="flex items-center gap-2 px-5 py-3 border-b bg-muted/30">
                  <FilePlus class="h-4 w-4 text-primary" />
                  <span class="font-semibold text-sm">Datos de la solicitud</span>
                </div>
                <div class="p-5 grid sm:grid-cols-2 gap-4">

                  <!-- Código -->
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Código <span class="text-red-500">*</span></label>
                    <div class="flex gap-2">
                      <Input v-model="form.codigo" placeholder="SOL-20240101-1234" class="h-9 text-sm font-mono" />
                      <Button size="sm" variant="outline" class="h-9 px-3 text-xs shrink-0" @click="form.codigo = generarCodigo()" title="Generar código">
                        ↻
                      </Button>
                    </div>
                  </div>

                  <!-- Estado -->
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Estado</label>
                    <Select v-model="form.estado">
                      <SelectTrigger class="h-9 text-sm">
                        <SelectValue placeholder="Selecciona estado" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pendiente">Pendiente</SelectItem>
                        <SelectItem value="en_proceso">En proceso</SelectItem>
                        <SelectItem value="completado">Completado</SelectItem>
                        <SelectItem value="cancelado">Cancelado</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <!-- Paciente -->
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Paciente</label>
                    <Select v-model="form.paciente">
                      <SelectTrigger class="h-9 text-sm">
                        <SelectValue placeholder="Selecciona paciente" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem v-for="p in pacientes" :key="p.id" :value="String(p.id)">
                          {{ p.nombre }}
                          <span class="text-muted-foreground text-xs ml-1">({{ p.propietario_nombre }})</span>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <!-- Médico -->
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Médico Veterinario</label>
                    <Select v-model="form.medico">
                      <SelectTrigger class="h-9 text-sm">
                        <SelectValue placeholder="Selecciona médico" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem v-for="m in medicos" :key="m.id" :value="String(m.id)">
                          Dr(a). {{ m.nombre }} {{ m.apellido }}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <!-- Observaciones -->
                  <div class="flex flex-col gap-1.5 sm:col-span-2">
                    <label class="text-xs font-medium text-muted-foreground">Observaciones</label>
                    <textarea
                      v-model="form.observaciones"
                      placeholder="Observaciones adicionales..."
                      rows="2"
                      class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
                    />
                  </div>
                </div>
              </div>

              <!-- Sección: Exámenes seleccionados -->
              <div class="rounded-xl border bg-white shadow-xs overflow-hidden">
                <div class="flex items-center justify-between px-5 py-3 border-b bg-muted/30">
                  <div class="flex items-center gap-2">
                    <FlaskConical class="h-4 w-4 text-primary" />
                    <span class="font-semibold text-sm">Exámenes solicitados</span>
                    <Badge variant="secondary">{{ seleccionados.length }}</Badge>
                  </div>
                </div>

                <div v-if="seleccionados.length === 0" class="flex flex-col items-center justify-center py-10 gap-2 text-muted-foreground">
                  <FlaskConical class="h-10 w-10 opacity-20" />
                  <p class="text-sm">Agrega exámenes desde el panel derecho.</p>
                </div>

                <table v-else class="w-full text-sm">
                  <thead class="border-b bg-muted/20">
                    <tr>
                      <th class="text-left px-4 py-2 text-xs font-medium text-muted-foreground">Examen</th>
                      <th class="text-left px-4 py-2 text-xs font-medium text-muted-foreground">Catálogo</th>
                      <th class="text-right px-4 py-2 text-xs font-medium text-muted-foreground w-28">Precio (Bs.)</th>
                      <th class="w-10"></th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-border/40">
                    <tr v-for="s in seleccionados" :key="s.examen.id" class="hover:bg-muted/20 transition-colors">
                      <td class="px-4 py-2">
                        <p class="font-medium">{{ s.examen.nombre_examen }}</p>
                        <p v-if="s.examen.categoria" class="text-xs text-muted-foreground">{{ s.examen.categoria }}</p>
                      </td>
                      <td class="px-4 py-2 text-xs text-muted-foreground">
                        {{ s.examen.catalogo_nombre ?? catalogos.find(c => c.id === s.examen.catalogo)?.nombre ?? '—' }}
                      </td>
                      <td class="px-4 py-2">
                        <Input
                          v-model="s.precio"
                          placeholder="0.00"
                          class="h-8 text-sm text-right w-24 ml-auto"
                        />
                      </td>
                      <td class="px-2 py-2">
                        <button class="rounded p-1 text-muted-foreground hover:text-red-500 hover:bg-red-50" @click="removeExamen(s.examen.id)">
                          <Trash2 class="h-4 w-4" />
                        </button>
                      </td>
                    </tr>
                  </tbody>
                  <tfoot class="border-t bg-muted/10">
                    <tr>
                      <td colspan="2" class="px-4 py-2 text-sm font-medium text-right text-muted-foreground">Total:</td>
                      <td class="px-4 py-2 text-right font-bold text-sm">Bs. {{ montoTotal }}</td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

            <!-- Columna derecha -->
            <div class="flex flex-col gap-5">

              <!-- Sección: Selector de exámenes -->
              <div class="rounded-xl border bg-white shadow-xs overflow-hidden">
                <div class="flex items-center gap-2 px-4 py-3 border-b bg-muted/30">
                  <BookOpen class="h-4 w-4 text-primary" />
                  <span class="font-semibold text-sm">Catálogo de Exámenes</span>
                </div>

                <div class="p-3 space-y-2 border-b">
                  <div class="relative">
                    <Search class="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
                    <Input
                      v-model="busquedaExamen"
                      placeholder="Buscar examen..."
                      class="h-8 text-sm pl-8"
                    />
                  </div>
                  <Select v-model="catalogoFiltroId">
                    <SelectTrigger class="h-8 text-xs">
                      <SelectValue placeholder="Todos los catálogos" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="todos">Todos los catálogos</SelectItem>
                      <SelectItem v-for="c in catalogos" :key="c.id" :value="String(c.id)">
                        {{ c.nombre }}
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <ul class="max-h-72 overflow-y-auto divide-y divide-border/40 py-1">
                  <li v-if="examenesFiltrados.length === 0" class="px-4 py-6 text-center text-sm text-muted-foreground">
                    Sin resultados.
                  </li>
                  <li
                    v-for="ex in examenesFiltrados"
                    :key="ex.id"
                    class="group flex items-center gap-2 px-3 py-2 hover:bg-muted/30 transition-colors cursor-pointer"
                    @click="addExamen(ex)"
                  >
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-medium truncate">{{ ex.nombre_examen }}</p>
                      <p class="text-xs text-muted-foreground truncate">
                        {{ catalogos.find(c => c.id === ex.catalogo)?.nombre ?? '' }}
                        <span v-if="ex.categoria"> · {{ ex.categoria }}</span>
                      </p>
                    </div>
                    <div class="shrink-0">
                      <span
                        v-if="seleccionados.some(s => s.examen.id === ex.id)"
                        class="text-xs text-green-600 font-medium flex items-center gap-0.5"
                      >
                        ✓ Agregado
                      </span>
                      <span v-else class="opacity-0 group-hover:opacity-100 transition-opacity">
                        <Plus class="h-4 w-4 text-primary" />
                      </span>
                    </div>
                  </li>
                </ul>
              </div>

              <!-- Sección: Cobro -->
              <div class="rounded-xl border bg-white shadow-xs overflow-hidden">
                <div class="flex items-center justify-between px-4 py-3 border-b bg-muted/30">
                  <div class="flex items-center gap-2">
                    <CreditCard class="h-4 w-4 text-primary" />
                    <span class="font-semibold text-sm">Cobro</span>
                  </div>
                  <label class="flex items-center gap-1.5 text-xs text-muted-foreground cursor-pointer">
                    <input type="checkbox" v-model="form.incluir_cobro" class="rounded" />
                    Incluir cobro
                  </label>
                </div>

                <div v-if="form.incluir_cobro" class="p-4 space-y-3">
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Método de Pago</label>
                    <Select v-model="form.metodo_pago">
                      <SelectTrigger class="h-9 text-sm">
                        <SelectValue placeholder="Seleccionar método" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="efectivo">Efectivo</SelectItem>
                        <SelectItem value="tarjeta">Tarjeta</SelectItem>
                        <SelectItem value="transferencia">Transferencia</SelectItem>
                        <SelectItem value="qr">QR</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Monto Total (Bs.)</label>
                    <div class="h-9 rounded-md border bg-muted/20 px-3 flex items-center text-sm font-mono font-semibold">
                      {{ montoTotal }}
                    </div>
                    <p class="text-xs text-muted-foreground">Calculado automáticamente.</p>
                  </div>
                </div>
                <div v-else class="px-4 py-5 text-center text-sm text-muted-foreground">
                  No se registrará cobro para esta solicitud.
                </div>
              </div>

              <!-- Error submit -->
              <div v-if="submitError" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                <AlertCircle class="h-4 w-4 shrink-0" />{{ submitError }}
              </div>

              <!-- Botón crear -->
              <Button class="w-full h-10" :disabled="submitting || !form.codigo.trim()" @click="handleSubmit">
                <Loader2 v-if="submitting" class="h-4 w-4 animate-spin mr-2" />
                <FilePlus v-else class="h-4 w-4 mr-2" />
                Crear Solicitud
              </Button>
            </div>

          </div>
        </template>

      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
