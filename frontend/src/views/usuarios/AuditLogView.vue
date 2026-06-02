<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import AppSidebar from '@/components/layout/Sidebar.vue'
import {
  SidebarInset, SidebarProvider, SidebarTrigger,
} from '@/components/ui/sidebar'
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbList,
  BreadcrumbPage, BreadcrumbSeparator, BreadcrumbLink,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Search, Loader2, AlertCircle, ScrollText,
  ChevronLeft, ChevronRight, RefreshCw,
} from 'lucide-vue-next'
import { useBitacoraStore } from '@/stores/bitacora'

const store = useBitacoraStore()

const search = ref('')
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return store.items
  return store.items.filter(b =>
    (b.modulo ?? '').toLowerCase().includes(q) ||
    (b.accion_realizada ?? '').toLowerCase().includes(q) ||
    (b.usuario_email ?? '').toLowerCase().includes(q) ||
    (b.direccion_ip ?? '').toLowerCase().includes(q),
  )
})

function goToPage(page: number) {
  store.fetchAll(page)
}

function formatFecha(f: string): string {
  const d = new Date(f)
  return d.toLocaleString('es-BO', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
    hour12: false,
  })
}

function moduloBadge(m: string | null): string {
  const map: Record<string, string> = {
    usuarios: 'bg-blue-100 text-blue-800',
    auth: 'bg-purple-100 text-purple-800',
    pacientes: 'bg-emerald-100 text-emerald-800',
    medicos: 'bg-cyan-100 text-cyan-800',
    propietarios: 'bg-amber-100 text-amber-800',
    muestras: 'bg-fuchsia-100 text-fuchsia-800',
    resultados: 'bg-indigo-100 text-indigo-800',
  }
  return map[(m ?? '').toLowerCase()] ?? 'bg-slate-100 text-slate-800'
}

onMounted(() => store.fetchAll())
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
              <BreadcrumbLink href="/dashboard">Inicio</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Bitácora</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6">

        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg
            bg-mineral-green-100 text-mineral-green-700">
              <ScrollText class="h-5 w-5" />
            </div>
            <div>
              <h1 class="text-2xl font-bold text-mineral-green-950 leading-tight">Bitácora de Auditoría</h1>
              <p class="text-sm text-muted-foreground">
                {{ store.total }} registro{{ store.total !== 1 ? 's' : '' }}
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            class="gap-2"
            :disabled="store.loading"
            @click="store.fetchAll(store.paginaActual)"
          >
            <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': store.loading }" />
            Actualizar
          </Button>
        </div>

        <div class="relative max-w-sm">
          <Search class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
          <Input
            v-model="search"
            placeholder="Buscar por módulo, acción, usuario, IP…"
            class="pl-9"
          />
        </div>

        <div v-if="store.loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
          <Loader2 class="h-5 w-5 animate-spin" />
          <span class="text-sm">Cargando bitácora…</span>
        </div>

        <div v-else-if="store.error" class="flex items-center gap-2 rounded-xl border
        border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
          <AlertCircle class="h-4 w-4 shrink-0" />
          {{ store.error }}
        </div>

        <div v-else class="rounded-xl border bg-white shadow-xs overflow-hidden">
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="border-b bg-mineral-green-50/60">
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-44">Fecha</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-32">Módulo</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800">Acción</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-56">Usuario</th>
                  <th class="px-4 py-3 text-left font-semibold text-mineral-green-800 w-32">IP</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="filtered.length === 0">
                  <td colspan="5" class="px-4 py-12 text-center text-muted-foreground">
                    {{ search ? 'Sin resultados para tu búsqueda.' : 'No hay registros en la bitácora.' }}
                  </td>
                </tr>

                <tr
                  v-for="b in filtered"
                  :key="b.id"
                  class="border-b last:border-0 hover:bg-mineral-green-50/40 transition-colors"
                >
                  <td class="px-4 py-3 text-mineral-green-700 whitespace-nowrap">{{ formatFecha(b.fecha) }}</td>
                  <td class="px-4 py-3">
                    <span
                      v-if="b.modulo"
                      :class="['inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium', moduloBadge(b.modulo)]"
                    >
                      {{ b.modulo }}
                    </span>
                    <span v-else class="text-xs text-muted-foreground italic">—</span>
                  </td>
                  <td class="px-4 py-3 text-mineral-green-800">{{ b.accion_realizada || '—' }}</td>
                  <td class="px-4 py-3 text-mineral-green-700">
                    {{ b.usuario_email || (b.usuario ? `Usuario #${b.usuario}` : 'Sistema') }}
                  </td>
                  <td class="px-4 py-3 text-mineral-green-700 font-mono text-xs">{{ b.direccion_ip || '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div v-if="store.paginas > 1" class="flex items-center justify-between px-4 py-3 border-t bg-mineral-green-50/30">
            <span class="text-sm text-muted-foreground">
              Página {{ store.paginaActual }} de {{ store.paginas }} — {{ store.total }} registros
            </span>
            <div class="flex items-center gap-1">
              <Button
                variant="outline"
                size="sm"
                :disabled="store.paginaActual <= 1"
                @click="goToPage(store.paginaActual - 1)"
              >
                <ChevronLeft class="h-4 w-4" />
              </Button>
              <span class="px-2 text-sm font-medium">{{ store.paginaActual }}</span>
              <Button
                variant="outline"
                size="sm"
                :disabled="store.paginaActual >= store.paginas"
                @click="goToPage(store.paginaActual + 1)"
              >
                <ChevronRight class="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </main>

    </SidebarInset>
  </SidebarProvider>
</template>
