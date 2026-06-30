<script setup lang="ts">
import { onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useSolicitudesStore } from '@/stores/solicitudes'

import AppSidebar from '@/components/layout/Sidebar.vue'
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar'
import {
    Breadcrumb, BreadcrumbItem, BreadcrumbList,
    BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'

import {
    ArrowLeft, Loader2, AlertCircle, FlaskConical, CheckCircle2, Clock,
} from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const store = useSolicitudesStore()

const id = computed(() => Number(route.params.id))

function cargar() {
    if (!id.value || Number.isNaN(id.value)) return
    store.fetchDetalle(id.value)
}

onMounted(cargar)
watch(() => route.params.id, cargar)

const ESTADO_BADGE: Record<string, string> = {
    pendiente: 'bg-amber-50 text-amber-700 border-amber-200',
    en_proceso: 'bg-blue-50 text-blue-700 border-blue-200',
    completado: 'bg-green-50 text-green-700 border-green-200',
    cancelado: 'bg-red-50 text-red-700 border-red-200',
}

const MUESTRA_BADGE: Record<string, string> = {
    pendiente: 'bg-amber-50 text-amber-700 border-amber-200',
    en_proceso: 'bg-blue-50 text-blue-700 border-blue-200',
    completada: 'bg-green-50 text-green-700 border-green-200',
    rechazada: 'bg-red-50 text-red-700 border-red-200',
}

function titleCase(s: string) {
    return s.replace('_', ' ').replace(/^\w/, c => c.toUpperCase())
}

function formatFecha(fecha: string) {
    return new Date(fecha).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const solicitud = computed(() => store.actual)
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
                            <BreadcrumbLink href="/solicitudes">Solicitudes</BreadcrumbLink>
                        </BreadcrumbItem>
                        <BreadcrumbSeparator />
                        <BreadcrumbItem>
                            <BreadcrumbPage>{{ solicitud?.codigo || '...' }}</BreadcrumbPage>
                        </BreadcrumbItem>
                    </BreadcrumbList>
                </Breadcrumb>
            </header>

            <main class="flex flex-1 flex-col gap-6 p-6 max-w-4xl">
                <Button variant="ghost" size="sm" class="w-fit gap-2 -ml-2"
                    @click="router.push({ name: 'solicitudes' })">
                    <ArrowLeft class="h-4 w-4" /> Volver a Solicitudes
                </Button>

                <div v-if="store.loadingDetalle"
                    class="flex items-center justify-center py-16 gap-3 text-muted-foreground">
                    <Loader2 class="h-5 w-5 animate-spin" />
                    <span class="text-sm">Cargando solicitud…</span>
                </div>

                <div v-else-if="store.error"
                    class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                    <AlertCircle class="h-4 w-4 shrink-0" />
                    {{ store.error }}
                </div>

                <template v-else-if="solicitud">
                    <!-- Cabecera -->
                    <div class="rounded-xl border bg-white p-5 shadow-xs">
                        <div class="flex items-start justify-between">
                            <div>
                                <h1 class="text-xl font-bold">{{ solicitud.codigo }}</h1>
                                <p class="text-sm text-muted-foreground mt-1">{{ solicitud.paciente_nombre }}</p>
                            </div>
                            <span
                                :class="`inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium ${ESTADO_BADGE[solicitud.estado]}`">
                                {{ titleCase(solicitud.estado) }}
                            </span>
                        </div>
                        <div class="grid grid-cols-2 gap-4 mt-4 text-sm">
                            <div>
                                <p class="text-muted-foreground">Médico solicitante</p>
                                <p class="font-medium">{{ solicitud.medico_nombre || '—' }}</p>
                            </div>
                            <div>
                                <p class="text-muted-foreground">Fecha de solicitud</p>
                                <p class="font-medium">{{ formatFecha(solicitud.fecha_solicitud) }}</p>
                            </div>
                        </div>
                        <p v-if="solicitud.observaciones" class="text-sm mt-4 text-muted-foreground border-t pt-3">
                            {{ solicitud.observaciones }}
                        </p>
                    </div>

                    <!-- Exámenes -->
                    <div class="space-y-3">
                        <h2 class="text-lg font-semibold">Exámenes solicitados</h2>
                        <div v-for="d in solicitud.detalles" :key="d.id"
                            class="rounded-xl border bg-white p-4 shadow-xs flex items-center justify-between gap-4">
                            <div class="flex-1">
                                <p class="font-medium">{{ d.examen_nombre }}</p>
                                <div class="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                                    <span v-if="d.precio_aplicado">Bs. {{ d.precio_aplicado }}</span>
                                    <span v-if="d.requiere_muestra"
                                        class="inline-flex items-center gap-1 text-amber-700">
                                        <FlaskConical class="h-3.5 w-3.5" /> Requiere muestra
                                    </span>
                                </div>

                                <!-- Muestras asociadas -->
                                <div v-if="d.muestra" class="flex flex-wrap gap-2 mt-2">
                                    <span
                                        :class="`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-xs ${MUESTRA_BADGE[d.muestra.estado]}`">
                                        {{ d.muestra.codigo }} · {{ titleCase(d.muestra.estado) }}
                                    </span>
                                </div>
                            </div>

                            <div class="flex items-center gap-2 shrink-0">
                                <span v-if="d.tiene_resultado"
                                    class="inline-flex items-center gap-1 text-green-700 text-xs font-medium">
                                    <CheckCircle2 class="h-4 w-4" /> Con resultado
                                </span>
                                <span v-else class="inline-flex items-center gap-1 text-muted-foreground text-xs">
                                    <Clock class="h-4 w-4" /> Pendiente
                                </span>
                            </div>
                        </div>
                    </div>
                </template>
            </main>
        </SidebarInset>
    </SidebarProvider>
</template>