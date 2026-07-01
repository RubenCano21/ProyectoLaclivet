<script setup lang="ts">
import type { SidebarProps } from '@/components/ui/sidebar'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

import {
  LayoutDashboard,
  Users,
  SoapDispenserDroplet,
  PawPrint,
  ClipboardList,
  BookOpen,
  FlaskConical,
  FilePlus,
  Stethoscope,
  ScrollText,
  ClipboardPlus,
  ClipboardCheck,
  Microscope,
  AlertTriangle,
  BarChart3,
} from "lucide-vue-next"
import NavMain from './NavMain.vue'
import NavUser from './NavUser.vue'
import TeamSwitcher from './TeamSwitcher.vue'

const authStore = useAuthStore()
const currentUser = computed(() => ({
  name: authStore.user
    ? (`${authStore.user.first_name} ${authStore.user.last_name}`.trim() || authStore.user.username)
    : '',
  email: authStore.user?.email ?? '',
  avatar: '',
}))

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from '@/components/ui/sidebar'

const props = withDefaults(defineProps<SidebarProps>(), {
  collapsible: "icon",
})

const teams = [
  {
    name: "LACLIVET",
    logo: SoapDispenserDroplet,
    plan: "Laboratorio",
  },
]

// Nav items are computed so they react to auth state and hide items the user can't access.
const navMain = computed(() => {
  const p = authStore.tienePermiso
  const esPropietario = authStore.tieneRol('Propietario')

  // ── Portal Propietario ──────────────────────────────────────────────────────
  if (esPropietario) {
    return [
      {
        title: 'Mis Mascotas',
        url: '/mis-mascotas',
        icon: PawPrint,
        isActive: true,
        items: [],
        visible: true,
      },
      {
        title: 'Mis Resultados',
        url: '/mis-resultados',
        icon: ClipboardCheck,
        items: [],
        visible: true,
      },
    ]
  }

  // ── Panel interno (staff) ──────────────────────────────────────────────────
  const items = [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: LayoutDashboard,
      isActive: true,
      items: [],
      visible: true,
    },
    {
      title: "Administracion",
      url: "",
      icon: Users,
      visible: p('ver_usuarios'),
      items: [
        { title: "Usuarios",  url: "/usuarios",          icon: Users,        visible: p('ver_usuarios') },
        { title: "Médicos",   url: "/medicos",            icon: Stethoscope,  visible: p('ver_usuarios') },
        { title: "Bitácora",  url: "/usuarios/auditoria", icon: ScrollText,   visible: p('ver_auditoria') },
      ].filter(i => i.visible),
    },
    {
      title: "Gestión Pacientes",
      url: "",
      icon: PawPrint,
      visible: p('ver_pacientes'),
      items: [
        { title: "Propietarios",    url: "/propietarios",          icon: Users,         visible: p('ver_pacientes') },
        { title: "Pacientes",       url: "/pacientes",             icon: ClipboardList, visible: p('ver_pacientes') },
        { title: "Especies & Razas",url: "/pacientes/especies-razas", icon: BookOpen,   visible: p('ver_pacientes') },
      ].filter(i => i.visible),
    },
    {
      title: "Solicitudes",
      url: "",
      icon: FlaskConical,
      visible: p('ver_solicitudes') || p('ver_catalogo'),
      items: [
        { title: "Catálogo de Exámenes", url: "/solicitudes/catalogo", icon: BookOpen,  visible: p('ver_catalogo') },
        { title: "Listado de Solicitudes", url: "/solicitudes",        icon: FilePlus,  visible: p('ver_solicitudes') },
      ].filter(i => i.visible),
    },
    {
      title: "Resultados",
      url: "",
      icon: Microscope,
      visible: p('ver_resultados'),
      items: [
        { title: "Pendientes de Resultado", url: "/resultados",            icon: ClipboardPlus,  visible: p('ver_resultados') },
        { title: "Validación",              url: "/resultados/validacion", icon: ClipboardCheck, visible: p('validar_resultados') },
      ].filter(i => i.visible),
    },
    {
      title: "Gestion de Muestras",
      url: "",
      icon: ClipboardPlus,
      visible: p('ver_muestras'),
      items: [
        { title: "Incidencias", url: "/muestras/incidencias", icon: AlertTriangle, visible: p('ver_muestras') },
        { title: "Recepcion",   url: "/muestras/recepcion",   icon: FlaskConical,  visible: p('ver_muestras') },
      ].filter(i => i.visible),
    },
    {
      title: "Business Intelligence",
      url: "/bi",
      icon: BarChart3,
      visible: p('ver_reportes'),
      items: [],
    },
  ]

  return items.filter(i => i.visible)
})
</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <TeamSwitcher :teams="teams" />
    </SidebarHeader>
    <SidebarContent>
      <NavMain :items="navMain" />
    </SidebarContent>
    <SidebarFooter>
      <NavUser :user="currentUser" />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>
