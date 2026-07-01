<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { portalService } from '@/services/portalService'

import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import {
  Loader2, AlertCircle, ArrowLeft,
  Stethoscope, FileText, FlaskConical, ChevronDown, ChevronRight,
} from 'lucide-vue-next'

interface PacienteResumen {
  id: number
  nombre: string
  sexo: string | null
  tamanio: string | null
  color: string | null
  fecha_nacimiento: string | null
  raza_nombre: string | null
  especie_nombre: string | null
}

interface Antecedente {
  id: number
  tipo: string
  descripcion: string
}

interface Examen {
  examen: string | null
  precio_aplicado: number | null
}

interface Solicitud {
  id: number
  codigo: string
  fecha_solicitud: string
  estado: string
  medico_veterinario: string | null
  examenes: Examen[]
}

interface Historial {
  paciente: PacienteResumen
  antecedentes: Antecedente[]
  solicitudes: Solicitud[]
}

const route    = useRoute()
const router   = useRouter()
const id       = computed(() => Number(route.params.id))

const historial = ref<Historial | null>(null)
const loading   = ref(false)
const error     = ref<string | null>(null)
const expanded  = ref<Set<number>>(new Set())

function toggleSolicitud(solicitudId: number) {
  if (expanded.value.has(solicitudId)) {
    expanded.value.delete(solicitudId)
  } else {
    expanded.value.add(solicitudId)
  }
}

function formatFecha(f: string | null | undefined) {
  if (!f) return '—'
  return new Date(f).toLocaleDateString('es-BO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

const paciente = computed(() => historial.value?.paciente)

const ESTADO_LABEL: Record<string, string> = {
  pendiente: 'Pendiente',
  en_proceso: 'En proceso',
  completado: 'Completado',
  validado: 'Validado',
}
const ESTADO_COLOR: Record<string, string> = {
  pendiente: 'bg-amber-100 text-amber-700',
  en_proceso: 'bg-blue-100 text-blue-700',
  completado: 'bg-green-100 text-green-700',
  validado: 'bg-emerald-100 text-emerald-700',
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await portalService.getHistorialMascota(id.value)
    historial.value = data
  } catch {
    error.value = 'No se pudo cargar el historial de esta mascota.'
  } finally {
    loading.value = false
  }
})
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
            <BreadcrumbItem><BreadcrumbLink href="/mis-mascotas">Mis Mascotas</BreadcrumbLink></BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>{{ paciente?.nombre || '…' }}</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6 max-w-3xl">
        <Button
          variant="ghost"
          size="sm"
          class="w-fit gap-2 -ml-2"
          @click="router.push({ name: 'portal-mascotas' })">
          <ArrowLeft class="h-4 w-4" /> Volver a Mis Mascotas
        </Button>

        <!-- Cargando -->
        <div v-if="loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando historial…</span>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" /> {{ error }}
        </div>

        <template v-else-if="historial">
          <!-- Datos del paciente -->
          <div class="rounded-xl border bg-white p-5 shadow-xs">
            <div class="flex items-center gap-4">
              <div class="flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary text-2xl font-bold">
                {{ paciente?.nombre?.[0]?.toUpperCase() }}
              </div>
              <div>
                <h1 class="text-xl font-bold">{{ paciente?.nombre }}</h1>
                <p class="text-sm text-muted-foreground">
                  {{ paciente?.especie_nombre }}
                  <template v-if="paciente?.raza_nombre"> · {{ paciente.raza_nombre }}</template>
                  <template v-if="paciente?.sexo"> · {{ paciente.sexo }}</template>
                </p>
              </div>
            </div>
            <div class="grid grid-cols-3 gap-4 mt-4 text-sm border-t pt-4">
              <div>
                <p class="text-xs text-muted-foreground">Color</p>
                <p class="font-medium">{{ paciente?.color || '—' }}</p>
              </div>
              <div>
                <p class="text-xs text-muted-foreground">Tamaño</p>
                <p class="font-medium capitalize">{{ paciente?.tamanio || '—' }}</p>
              </div>
              <div>
                <p class="text-xs text-muted-foreground">Fecha nacimiento</p>
                <p class="font-medium">{{ formatFecha(paciente?.fecha_nacimiento) }}</p>
              </div>
            </div>
          </div>

          <!-- Antecedentes -->
          <div v-if="historial.antecedentes?.length" class="rounded-xl border bg-white shadow-xs overflow-hidden">
            <div class="flex items-center gap-2 px-4 py-3 border-b bg-muted/30 text-sm font-semibold">
              <FileText class="h-4 w-4 text-muted-foreground" /> Antecedentes médicos
            </div>
            <ul class="divide-y text-sm">
              <li v-for="a in historial.antecedentes" :key="a.id" class="px-4 py-3">
                <span class="inline-block text-xs font-medium bg-muted px-2 py-0.5 rounded-full mr-2 capitalize">
                  {{ a.tipo }}
                </span>
                {{ a.descripcion }}
              </li>
            </ul>
          </div>

          <!-- Historial de solicitudes -->
          <div>
            <h2 class="text-sm font-semibold mb-3 flex items-center gap-2">
              <Stethoscope class="h-4 w-4 text-muted-foreground" /> Historial de exámenes
            </h2>

            <div v-if="!historial.solicitudes?.length" class="text-sm text-muted-foreground py-6 text-center">
              No hay solicitudes de examen registradas.
            </div>

            <div v-else class="space-y-2">
              <div
                v-for="s in historial.solicitudes"
                :key="s.id"
                class="rounded-xl border bg-white shadow-xs overflow-hidden"
              >
                <!-- Cabecera colapsable -->
                <button
                  class="w-full flex items-center justify-between px-4 py-3 text-sm hover:bg-muted/20 transition-colors"
                  @click="toggleSolicitud(s.id)"
                >
                  <div class="flex items-center gap-3">
                    <FlaskConical class="h-4 w-4 text-muted-foreground shrink-0" />
                    <div class="text-left">
                      <p class="font-medium">{{ s.codigo }}</p>
                      <p class="text-xs text-muted-foreground">{{ formatFecha(s.fecha_solicitud) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center gap-2">
                    <span 
                        :class="ESTADO_COLOR[s.estado] || 'bg-gray-100 text-gray-600'"
                      class="text-xs px-2 py-0.5 rounded-full font-medium">
                      {{ ESTADO_LABEL[s.estado] || s.estado }}
                    </span>
                    <component 
                        :is="expanded.has(s.id) ? ChevronDown : ChevronRight"
                      class="h-4 w-4 text-muted-foreground" />
                  </div>
                </button>

                <!-- Detalle expandido -->
                <div v-if="expanded.has(s.id)" class="border-t px-4 py-3 text-sm space-y-2">
                  <p v-if="s.medico_veterinario" class="text-muted-foreground">
                    Veterinario: <span class="text-foreground font-medium">{{ s.medico_veterinario }}</span>
                  </p>
                  <ul v-if="s.examenes?.length" class="space-y-1">
                    <li v-for="(e, idx) in s.examenes" :key="idx" class="flex justify-between">
                      <span>{{ e.examen }}</span>
                      <span class="text-muted-foreground">Bs. {{ e.precio_aplicado ?? '—' }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </template>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
