<script setup lang="ts">
import { useResultadosStore } from '@/stores/resultados'
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
    Search, Loader2, AlertCircle, Microscope, ChevronLeft, ChevronRight,
    PencilLine, FileDown, FlaskConical,
} from 'lucide-vue-next'

const router = useRouter()
const route = useRoute()
const store = useResultadosStore()

const search = ref('')
const estadoFiltro = ref<string>('pendiente')

function abrirCaptura(id: number) {
    router.push({ name: 'captura-resultados', params: { id } })
}

const filtered = computed(() => {
    const q = search.value.trim().toLowerCase()
    if (!q) return store.items
    return store.items.filter((o) =>
        o.examen_nombre?.toLowerCase().includes(q) ||
        o.solicitud_codigo?.toLowerCase().includes(q) ||
        o.paciente?.nombre?.toLowerCase().includes(q),
    )
})

const ESTADO_BADGE: Record<string, string> = {
    pendiente: 'bg-amber-50 text-amber-700 border-amber-200',
    en_proceso: 'bg-blue-50 text-blue-700 border-blue-200',
    completado: 'bg-green-50 text-green-700 border-green-200',
    validado: 'bg-emerald-50 text-emerald-700 border-emerald-200',
}

function titleCase(s: string | undefined | null) {
    if (!s) return '—'
    return s.replace('_', ' ').replace(/^\w/, c => c.toUpperCase())
}

function goToPage(page: number) {
    router.replace({ query: { ...route.query, page: String(page) } })
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
                            <BreadcrumbPage>Resultados</BreadcrumbPage>
                        </BreadcrumbItem>
                    </BreadcrumbList>
                </Breadcrumb>
            </header>

            <main class="flex flex-1 flex-col gap-6 p-6">
                <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
                        <Microscope class="h-5 w-5" />
                    </div>
                    <div>
                        <h1 class="text-2xl font-bold leading-tight">Captura de Resultados</h1>
                        <p class="text-sm text-muted-foreground">
                            {{ store.total }} examen{{ store.total !== 1 ? 'es' : '' }} en cola
                        </p>
                    </div>
                </div>

                <div class="flex items-center gap-3">
                    <div class="relative max-w-sm flex-1">
                        <Search
                            class="pointer-events-none absolute inset-y-0 left-3 my-auto h-4 w-4 text-muted-foreground" />
                        <Input v-model="search" placeholder="Buscar por examen, código, paciente…" class="pl-9" />
                    </div>
                    <Select v-model="estadoFiltro">
                        <SelectTrigger class="w-48">
                            <SelectValue placeholder="Estado" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">Todos los estados</SelectItem>
                            <SelectItem value="pendiente">Pendiente</SelectItem>
                            <SelectItem value="en_proceso">En proceso</SelectItem>
                            <SelectItem value="completado">Completado</SelectItem>
                            <SelectItem value="validado">Validado</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div v-if="store.loading" class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
                    <Loader2 class="h-5 w-5 animate-spin" />
                    <span class="text-sm">Cargando…</span>
                </div>

                <div 
                v-else-if="store.error"
                    class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600 max-w-lg">
                    <AlertCircle class="h-4 w-4 shrink-0" />
                    {{ store.error }}
                </div>

                <div v-else class="rounded-xl border bg-white shadow-xs overflow-hidden">
                    <div class="overflow-x-auto">
                        <table class="w-full text-sm">
                            <thead>
                                <tr class="border-b bg-muted/40">
                                    <th class="px-4 py-3 text-left font-semibold">Solicitud</th>
                                    <th class="px-4 py-3 text-left font-semibold">Paciente</th>
                                    <th class="px-4 py-3 text-left font-semibold">Examen</th>
                                    <th class="px-4 py-3 text-left font-semibold">Muestra</th>
                                    <th class="px-4 py-3 text-left font-semibold">Estado</th>
                                    <th class="px-4 py-3 text-center font-semibold w-24">Acción</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-if="filtered.length === 0">
                                    <td colspan="6" class="px-4 py-12 text-center text-muted-foreground">
                                        No hay exámenes
                                        {{ estadoFiltro && estadoFiltro !== 'all' ? `en estado
                                        "${titleCase(estadoFiltro)}"` : '' }}.
                                    </td>
                                </tr>
                                <tr 
                                v-for="o in filtered" :key="o.id"
                                    class="border-b last:border-0 hover:bg-muted/20 transition-colors">
                                    <td class="px-4 py-3 font-medium">{{ o.solicitud_codigo }}</td>
                                    <td class="px-4 py-3">{{ o.paciente?.nombre }}</td>
                                    <td class="px-4 py-3">{{ o.examen_nombre }}</td>
                                    <td class="px-4 py-3">
                                        <span v-if="o.muestra" class="inline-flex items-center gap-1 text-xs">
                                            <FlaskConical class="h-3.5 w-3.5 text-muted-foreground" /> {{
                                                o.muestra.codigo }}
                                        </span>
                                        <span v-else class="text-muted-foreground text-xs">Sin muestra</span>
                                    </td>
                                    <td class="px-4 py-3">
                                        <span
                                            :class="`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${ESTADO_BADGE[o.estado]}`">
                                            {{ titleCase(o.estado) }}
                                        </span>
                                    </td>
                                    <td class="px-4 py-3 text-center">
                                        <button
                                            class="p-1.5 rounded-md text-primary hover:bg-primary/10 transition-colors"
                                            :title="o.estado === 'pendiente' || o.estado === 'en_proceso' ? 'Registrar resultado' : 'Ver / generar PDF'"
                                            @click="abrirCaptura(o.id)">
                                            <PencilLine 
                                            v-if="o.estado === 'pendiente' || o.estado === 'en_proceso'"
                                                class="h-4 w-4" />
                                            <FileDown v-else class="h-4 w-4" />
                                        </button>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>

                    <div 
                    v-if="store.paginas > 1"
                        class="flex items-center justify-between px-4 py-3 border-t bg-muted/20">
                        <span class="text-sm text-muted-foreground">
                            Página {{ store.paginaActual }} de {{ store.paginas }} — {{ store.total }} registros
                        </span>
                        <div class="flex items-center gap-1">
                            <Button 
                            variant="outline" size="sm" :disabled="store.paginaActual <= 1"
                                @click="goToPage(store.paginaActual - 1)">
                                <ChevronLeft class="h-4 w-4" />
                            </Button>
                            <span class="px-2 text-sm font-medium">{{ store.paginaActual }}</span>
                            <Button 
                            variant="outline" size="sm" :disabled="store.paginaActual >= store.paginas"
                                @click="goToPage(store.paginaActual + 1)">
                                <ChevronRight class="h-4 w-4" />
                            </Button>
                        </div>
                    </div>
                </div>
            </main>
        </SidebarInset>
    </SidebarProvider>
</template>