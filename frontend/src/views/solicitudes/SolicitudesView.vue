<script setup lang="ts">
import { useSolicitudesStore } from '@/stores/solicitudes'
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

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

import {
    Plus, Search, Loader2, AlertCircle, ClipboardList, ChevronLeft, ChevronRight, FlaskConical, Eye,
} from 'lucide-vue-next'
import NuevaSolicitudView from './NuevaSolicitudView.vue'

const router = useRouter()
const route = useRoute()
const store = useSolicitudesStore()

const search = ref('')
const estadoFiltro = ref<string>('')
const modalOpen = ref(false)

function abrirNueva() {
    modalOpen.value = true
}

function onSaved() {
    store.fetchAll(store.paginaActual, estadoFiltro.value)
}

function verDetalle(id: number) {
    router.push({ name: 'solicitud-detalle', params: { id } })
}

const filtered = computed(() => {
    const q = search.value.trim().toLowerCase()
    if (!q) return store.items
    return store.items.filter((s) =>
        s.codigo.toLowerCase().includes(q) ||
        s.paciente_nombre?.toLowerCase().includes(q) ||
        s.medico_nombre?.toLowerCase().includes(q),
    )
})

const ESTADO_BADGE: Record<string, string> = {
    pendiente: 'bg-amber-50 text-amber-700 border-amber-200',
    en_proceso: 'bg-blue-50 text-blue-700 border-blue-200',
    completado: 'bg-green-50 text-green-700 border-green-200',
    cancelado: 'bg-red-50 text-red-700 border-red-200',
}

function titleCase(s: string) {
    return s.replace('_', ' ').replace(/^\w/, c => c.toUpperCase())
}

function formatFecha(fecha: string) {
    return new Date(fecha).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' })
}

function goToPage(page: number) {
    router.replace({ query: { ...route.query, page: String(page) } })
}

function cantidadMuestrasPendientes(s: any) {
    return s.detalles?.filter((d: any) => d.muestra?.estado === 'pendiente').length || 0
}

watch(
    [() => route.query.page, estadoFiltro],
    ([pageParam]) => {
        const page = Number(pageParam) || 1
        const estado = estadoFiltro.value === 'all' ? '' : estadoFiltro.value
        store.fetchAll(page, estado)
    },
    { immediate: true },
)
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
                            <BreadcrumbPage>Solicitudes de Examen</BreadcrumbPage>
                        </BreadcrumbItem>
                    </BreadcrumbList>
                </Breadcrumb>
            </header>

            <main class="flex flex-1 flex-col gap-6 p-6">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                            <ClipboardList class="h-5 w-5" />
                        </div>
                        <div>
                            <h1 class="text-2xl font-bold leading-tight">Solicitudes de Examen</h1>
                            <p class="text-sm text-muted-foreground">
                                {{ store.total }} registrada{{ store.total !== 1 ? 's' : '' }}
                            </p>
                        </div>
                    </div>
                    <Button @click="abrirNueva" class="gap-2">
                        <Plus class="h-4 w-4" />
                        Nueva Solicitud
                    </Button>
                </div>

                <div class="flex items-center gap-3">
                    <div class="relative max-w-sm flex-1">
                        <Search
                            class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
                        <Input v-model="search" placeholder="Buscar por código, paciente, médico…" class="pl-9" />
                    </div>
                    <Select v-model="estadoFiltro">
                        <SelectTrigger class="w-48">
                            <SelectValue placeholder="Todos los estados" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Todos los estados</SelectItem>
                            <SelectItem value="pendiente">Pendiente</SelectItem>
                            <SelectItem value="en_proceso">En proceso</SelectItem>
                            <SelectItem value="completado">Completado</SelectItem>
                            <SelectItem value="cancelado">Cancelado</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div v-if="store.loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
                    <Loader2 class="h-5 w-5 animate-spin" />
                    <span class="text-sm">Cargando solicitudes…</span>
                </div>

                <div v-else-if="store.error"
                    class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
                    <AlertCircle class="h-4 w-4 shrink-0" />
                    {{ store.error }}
                </div>

                <div v-else class="rounded-xl border bg-white shadow-xs overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead>
                                <tr class="border-b bg-muted/40">
                                    <th class="px-4 py-3 text-left font-semibold">Código</th>
                                    <th class="px-4 py-3 text-left font-semibold">Paciente</th>
                                    <th class="px-4 py-3 text-left font-semibold">Médico</th>
                                    <th class="px-4 py-3 text-left font-semibold">Fecha</th>
                                    <th class="px-4 py-3 text-left font-semibold">Exámenes</th>
                                    <th class="px-4 py-3 text-left font-semibold">Muestras pend.</th>
                                    <th class="px-4 py-3 text-left font-semibold">Estado</th>
                                    <th class="px-4 py-3 text-center font-semibold w-20">Ver</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-if="filtered.length === 0">
                                    <td colspan="8" class="px-4 py-12 text-center text-muted-foreground">
                                        {{ search ? 'Sin resultados para tu búsqueda.' : 'No hay solicitudes registradas.' }}
                                    </td>
                                </tr>
                                <tr v-for="s in filtered" :key="s.id"
                                    class="border-b last:border-0 hover:bg-muted/20 transition-colors">
                                    <td class="px-4 py-3 font-medium">{{ s.codigo }}</td>
                                    <td class="px-4 py-3">{{ s.paciente_nombre }}</td>
                                    <td class="px-4 py-3">{{ s.medico_nombre || '—' }}</td>
                                    <td class="px-4 py-3">{{ formatFecha(s.fecha_solicitud) }}</td>
                                    <td class="px-4 py-3">{{ s.detalles?.length ?? 0 }}</td>
                                    <td class="px-4 py-3">
                                        <span v-if="cantidadMuestrasPendientes(s) > 0"
                                            class="inline-flex items-center gap-1 text-amber-700">
                                            <FlaskConical class="h-3.5 w-3.5" /> {{ cantidadMuestrasPendientes(s) }}
                                        </span>
                                        <span v-else class="text-muted-foreground">—</span>
                                    </td>
                                    <td class="px-4 py-3">
                                        <span
                                            :class="`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${ESTADO_BADGE[s.estado]}`">
                                            {{ titleCase(s.estado) }}
                                        </span>
                                    </td>
                                    <td class="px-4 py-3 text-center">
                                        <button @click="verDetalle(s.id)"
                                            class="p-1.5 rounded-md text-primary hover:bg-primary/10 transition-colors"
                                            title="Ver detalle">
                                            <Eye class="h-4 w-4" />
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div v-if="store.paginas > 1"
                        class="flex items-center justify-between px-4 py-3 border-t bg-muted/20">
                        <span class="text-sm text-muted-foreground">
                            Página {{ store.paginaActual }} de {{ store.paginas }} — {{ store.total }} registros
                        </span>
                        <div class="flex items-center gap-1">
                            <Button variant="outline" size="sm" :disabled="store.paginaActual <= 1"
                                @click="goToPage(store.paginaActual - 1)">
                                <ChevronLeft class="h-4 w-4" />
                            </Button>
                            <span class="px-2 text-sm font-medium">{{ store.paginaActual }}</span>
                            <Button variant="outline" size="sm" :disabled="store.paginaActual >= store.paginas"
                                @click="goToPage(store.paginaActual + 1)">
                                <ChevronRight class="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </main>
        </SidebarInset>
    </SidebarProvider>

   
    <NuevaSolicitudView v-model:open="modalOpen" @saved="onSaved" />
</template>