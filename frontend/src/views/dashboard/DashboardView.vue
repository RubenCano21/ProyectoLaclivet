<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import { Breadcrumb, BreadcrumbItem, BreadcrumbList, BreadcrumbPage } from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Users, PawPrint, FlaskConical, BookOpen,
  SoapDispenserDroplet, ClipboardList, ArrowRight, Loader2,
  TrendingUp, AlertCircle,
} from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { pacienteService, propietarioService } from '@/services/pacienteService'
import { catalogoService, examenService } from '@/services/catalogoService'
import { solicitudService } from '@/services/solicitudService'
import { muestraService } from '@/services/muestraService'
import api from '@/services/apiClient'

const router  = useRouter()
const auth    = useAuthStore()
const loading = ref(true)
const error   = ref<string | null>(null)

const nombreUsuario = computed(() => {
  if (!auth.user) return 'Usuario'
  return auth.user.first_name?.trim() || auth.user.username
})

// ── Stats ──────────────────────────────────────────────────────────────────────
interface Stat {
  label: string
  value: number | null
  icon: any
  color: string
  bg: string
  href: string
  sub?: string
}

const stats = ref<Stat[]>([
  { label: 'Pacientes',    value: null, icon: PawPrint,        color: 'text-violet-600',  bg: 'bg-violet-50',  href: '/pacientes' },
  { label: 'Propietarios', value: null, icon: Users,           color: 'text-blue-600',    bg: 'bg-blue-50',    href: '/propietarios' },
  { label: 'Solicitudes',  value: null, icon: ClipboardList,   color: 'text-amber-600',   bg: 'bg-amber-50',   href: '/solicitudes', sub: 'pendientes' },
  { label: 'Exámenes',     value: null, icon: FlaskConical,    color: 'text-emerald-600', bg: 'bg-emerald-50', href: '/solicitudes/catalogo' },
  { label: 'Catálogos',    value: null, icon: BookOpen,        color: 'text-pink-600',    bg: 'bg-pink-50',    href: '/solicitudes/catalogo' },
  { label: 'Muestras',     value: null, icon: SoapDispenserDroplet, color: 'text-cyan-600', bg: 'bg-cyan-50', href: '/muestras/incidencias' },
  { label: 'Usuarios',     value: null, icon: Users,           color: 'text-slate-600',   bg: 'bg-slate-50',   href: '/usuarios' },
])

// ── Solicitudes recientes ──────────────────────────────────────────────────────
interface SolicitudReciente {
  id: number
  codigo: string
  estado: string
  paciente_nombre: string | null
  propietario_nombre: string | null
  fecha_solicitud: string
}
const recientes = ref<SolicitudReciente[]>([])

const estadoColor: Record<string, string> = {
  pendiente:  'bg-amber-100 text-amber-700',
  en_proceso: 'bg-blue-100 text-blue-700',
  completado: 'bg-green-100 text-green-700',
  cancelado:  'bg-red-100 text-red-700',
}

function formatFecha(iso: string) {
  return new Date(iso).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' })
}

// ── Carga ──────────────────────────────────────────────────────────────────────
async function loadDashboard() {
  loading.value = true
  error.value   = null
  try {
    const [rPac, rProp, rSol, rEx, rCat, rMue, rUsr] = await Promise.all([
      pacienteService.getAll(),
      propietarioService.getAll(),
      solicitudService.getAll(1),
      examenService.getAll(),
      catalogoService.getAll(),
      muestraService.getAll(1),
      api.get('/usuarios/'),
    ])

    const totals = [rPac, rProp, rSol, rEx, rCat, rMue, rUsr].map(
      r => (r.data as any).total ?? (r.data as any).count ?? (Array.isArray(r.data) ? r.data.length : 0)
    )
    totals.forEach((v, i) => { stats.value[i].value = v })

    // Solicitudes pendientes como subtítulo
    const solData = (rSol.data as any).resultados ?? (rSol.data as any).results ?? []
    recientes.value = solData.slice(0, 5).map((s: any) => ({
      id:             s.id,
      codigo:         s.codigo,
      estado:         s.estado,
      paciente_nombre: s.paciente_nombre,
      propietario_nombre: s.propietario_nombre,
      fecha_solicitud: s.fecha_solicitud,
    }))
  } catch {
    error.value = 'No se pudo cargar la información del dashboard.'
  } finally {
    loading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>

      <header class="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger class="-ml-1" />
        <Separator orientation="vertical" class="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>Dashboard</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6">

        <!-- Bienvenida -->
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold leading-tight">
              Bienvenido, {{ nombreUsuario }} 👋
            </h1>
            <p class="text-sm text-muted-foreground mt-0.5">
              Resumen general del sistema LACLIVET
            </p>
          </div>
          <button
            class="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-primary transition-colors"
            @click="loadDashboard"
          >
            <Loader2 v-if="loading" class="h-3.5 w-3.5 animate-spin" />
            <TrendingUp v-else class="h-3.5 w-3.5" />
            Actualizar
          </button>
        </div>

        <!-- Error -->
        <div v-if="error" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" />{{ error }}
        </div>

        <!-- Tarjetas de estadísticas -->
        <div class="grid grid-cols-3 sm:grid-cols-4 lg:grid-cols-7 gap-3">
          <div
            v-for="stat in stats"
            :key="stat.label"
            class="group rounded-xl border bg-white shadow-xs p-3 cursor-pointer hover:shadow-md hover:border-primary/30 transition-all"
            @click="router.push(stat.href)"
          >
            <div class="flex items-start justify-between">
              <div :class="['flex h-8 w-8 items-center justify-center rounded-lg', stat.bg, stat.color]">
                <component :is="stat.icon" class="h-4 w-4" />
              </div>
              <ArrowRight class="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <div class="mt-2">
              <Skeleton v-if="loading" class="h-6 w-10 mb-1" />
              <p v-else class="text-xl font-bold leading-none">
                {{ stat.value ?? '—' }}
              </p>
              <p class="text-xs text-muted-foreground mt-1">{{ stat.label }}</p>
            </div>
          </div>
        </div>

        <!-- Solicitudes recientes -->
        <div class="rounded-xl border bg-white shadow-xs overflow-hidden">
          <div class="flex items-center justify-between px-5 py-3 border-b bg-muted/30">
            <div class="flex items-center gap-2">
              <ClipboardList class="h-4 w-4 text-primary" />
              <span class="font-semibold text-sm">Solicitudes recientes</span>
            </div>
            <button
              class="text-xs text-primary hover:underline flex items-center gap-1"
              @click="router.push('/solicitudes')"
            >
              Nueva <ArrowRight class="h-3.5 w-3.5" />
            </button>
          </div>

          <!-- Skeleton -->
          <div v-if="loading" class="divide-y">
            <div v-for="n in 4" :key="n" class="flex items-center gap-3 px-5 py-3">
              <Skeleton class="h-4 w-28" />
              <Skeleton class="h-5 w-20 rounded-full" />
              <Skeleton class="h-4 w-24 ml-auto" />
            </div>
          </div>

          <!-- Sin datos -->
          <div v-else-if="recientes.length === 0" class="flex flex-col items-center justify-center py-12 gap-2 text-muted-foreground">
            <ClipboardList class="h-10 w-10 opacity-20" />
            <p class="text-sm">No hay solicitudes registradas.</p>
          </div>

          <!-- Tabla -->
          <table v-else class="w-full text-sm">
            <thead class="border-b bg-muted/10">
              <tr>
                <th class="text-left px-5 py-2 text-xs font-medium text-muted-foreground">Código</th>
                <th class="text-left px-4 py-2 text-xs font-medium text-muted-foreground">Paciente</th>
                <th class="text-left px-4 py-2 text-xs font-medium text-muted-foreground">Propietario</th>
                <th class="text-left px-4 py-2 text-xs font-medium text-muted-foreground">Estado</th>
                <th class="text-right px-5 py-2 text-xs font-medium text-muted-foreground">Fecha</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border/40">
              <tr
                v-for="sol in recientes"
                :key="sol.id"
                class="hover:bg-muted/20 transition-colors cursor-pointer"
                @click="router.push({ name: 'solicitud-detalle', params: { id: sol.id } })"
              >
                <td class="px-5 py-2.5 font-mono text-xs font-medium">{{ sol.codigo }}</td>
                <td class="px-4 py-2.5 text-sm">{{ sol.paciente_nombre ?? '—' }}</td>
                <td class="px-4 py-2.5 text-sm text-muted-foreground">{{ sol.propietario_nombre ?? '—' }}</td>
                <td class="px-4 py-2.5">
                  <Badge
                    class="text-xs capitalize"
                    :class="estadoColor[sol.estado] ?? 'bg-gray-100 text-gray-600'"
                  >
                    {{ sol.estado.replace('_', ' ') }}
                  </Badge>
                </td>
                <td class="px-5 py-2.5 text-xs text-muted-foreground text-right">
                  {{ formatFecha(sol.fecha_solicitud) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
