<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { portalService } from '@/services/portalService'

import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Loader2, AlertCircle, PawPrint, ChevronRight } from 'lucide-vue-next'

interface Mascota {
  id: number
  nombre: string
  sexo: string
  tamanio: string | null
  color: string | null
  fecha_nacimiento: string | null
  raza_nombre: string | null
  especie_nombre: string | null
}

const router    = useRouter()
const authStore = useAuthStore()
const mascotas  = ref<Mascota[]>([])
const loading   = ref(false)
const error     = ref<string | null>(null)

function formatFecha(f: string | null) {
  if (!f) return '—'
  return new Date(f + 'T00:00:00').toLocaleDateString('es-BO', {
    day: '2-digit', month: 'short', year: 'numeric',
  })
}

onMounted(async () => {
  loading.value = true
  try {
    const { data } = await portalService.getMisMascotas()
    mascotas.value = data.resultados ?? data
  } catch {
    error.value = 'No se pudo cargar la lista de mascotas.'
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
            <BreadcrumbItem><BreadcrumbLink href="/mis-mascotas">Portal</BreadcrumbLink></BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem><BreadcrumbPage>Mis Mascotas</BreadcrumbPage></BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6 max-w-3xl">
        <!-- Bienvenida -->
        <div class="flex items-center gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <PawPrint class="h-5 w-5" />
          </div>
          <div>
            <h1 class="text-2xl font-bold leading-tight">Mis Mascotas</h1>
            <p class="text-sm text-muted-foreground">
              Bienvenido/a, {{ authStore.user?.first_name }}. Aquí están tus mascotas registradas.
            </p>
          </div>
        </div>

        <!-- Cargando -->
        <div v-if="loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando mascotas…</span>
        </div>

        <!-- Error -->
        <div v-else-if="error" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <AlertCircle class="h-4 w-4 shrink-0" /> {{ error }}
        </div>

        <!-- Lista -->
        <div v-else-if="mascotas.length === 0" class="flex flex-col items-center justify-center py-16 gap-3 text-muted-foreground">
          <PawPrint class="h-12 w-12 opacity-20" />
          <p class="text-sm">No tienes mascotas registradas todavía.</p>
        </div>

        <div v-else class="grid gap-3 sm:grid-cols-2">
          <button
            v-for="m in mascotas"
            :key="m.id"
            @click="router.push({ name: 'portal-mascota-detalle', params: { id: m.id } })"
            class="flex items-center gap-4 rounded-xl border bg-white p-4 shadow-xs hover:bg-muted/20 transition-colors text-left"
          >
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary text-lg font-bold">
              {{ m.nombre[0]?.toUpperCase() }}
            </div>
            <div class="flex-1 min-w-0">
              <p class="font-semibold truncate">{{ m.nombre }}</p>
              <p class="text-xs text-muted-foreground">
                {{ m.especie_nombre }}{{ m.raza_nombre ? ` · ${m.raza_nombre}` : '' }}
              </p>
              <p v-if="m.fecha_nacimiento" class="text-xs text-muted-foreground">
                Nac. {{ formatFecha(m.fecha_nacimiento) }}
              </p>
            </div>
            <ChevronRight class="h-4 w-4 text-muted-foreground shrink-0" />
          </button>
        </div>

        <!-- Acceso rápido a resultados -->
        <div class="rounded-xl border bg-white p-4 shadow-xs flex items-center justify-between">
          <div>
            <p class="font-medium text-sm">Resultados de exámenes</p>
            <p class="text-xs text-muted-foreground">Descarga los resultados de laboratorio de tus mascotas</p>
          </div>
          <Button variant="outline" size="sm" @click="router.push({ name: 'portal-resultados' })">
            Ver resultados
          </Button>
        </div>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
