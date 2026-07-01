<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Refresca el perfil del usuario (incluidos sus permisos) desde el backend
// cada vez que se carga la app. Así los cambios de roles/permisos en BD
// se reflejan sin necesidad de cerrar sesión manualmente.
onMounted(async () => {
  if (authStore.isAuthenticated) {
    await authStore.fetchPerfil()
  }
})
</script>

<template>
  <RouterView />
</template>
