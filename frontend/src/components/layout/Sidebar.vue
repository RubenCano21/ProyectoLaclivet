<script setup lang="ts">
import type { SidebarProps } from '@/components/ui/sidebar'
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

import {
  AudioWaveform,
  LayoutDashboard,
  Users,
  SoapDispenserDroplet,
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

// This is sample data.
const data = {
  user: {
    name: "shadcn",
    email: "m@example.com",
    avatar: "/avatars/shadcn.jpg",
  },
  teams: [
    {
      name: "LACLIVET",
      logo: SoapDispenserDroplet,
      plan: "Laboratorio",
    },
    {
      name: "PRACTICAS",
      logo: AudioWaveform,
      plan: "Estudiantes",
    },
  ],
  navMain: [
    {
      title: "Dashboard",
      url: "/dashboard",
      icon: LayoutDashboard,
      isActive: true,
      items: [],
    },
    {
      title: "Administracion",
      url: "/auth",
      icon: Users,
      items: [
        {
          title: "Usuarios",
          url: "/auth/usuarios",
          icon: Users,
        }
      ]
    },
    {
      title: "Gestion Pacientes",
      url: "",
      icon: Users,
      items: [
        {
          title: "Pacientes",
          url: "/pacientes",
          icon: Users,
        },
        {
          title: "Visitas",
          url: "/visitas",
          icon: Users,
        },
      ],
    },
  ],
  projects: [],
}
</script>

<template>
  <Sidebar v-bind="props">
    <SidebarHeader>
      <TeamSwitcher :teams="data.teams" />
    </SidebarHeader>
    <SidebarContent>
      <NavMain :items="data.navMain" />
    </SidebarContent>
    <SidebarFooter>
      <NavUser :user="currentUser" />
    </SidebarFooter>
    <SidebarRail />
  </Sidebar>
</template>
