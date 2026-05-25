<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { SidebarTrigger } from '@/components/ui/sidebar'
import { Button } from '@/components/ui/button'
import { LogOut, User } from 'lucide-vue-next'

const authStore = useAuthStore()
const router = useRouter()

const userName = computed(() =>
  authStore.user
    ? `${authStore.user.first_name} ${authStore.user.last_name}`.trim() || authStore.user.username
    : ''
)

function logout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header class="flex h-14 items-center gap-2 border-b px-4">
    <SidebarTrigger />
    <div class="flex flex-1 items-center justify-end gap-2">
      <span class="text-sm text-muted-foreground">{{ userName }}</span>
      <Button variant="ghost" size="icon" title="Perfil" @click="router.push({ name: 'perfil' })">
        <User class="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" title="Cerrar sesión" @click="logout">
        <LogOut class="h-4 w-4" />
      </Button>
    </div>
  </header>
</template>
