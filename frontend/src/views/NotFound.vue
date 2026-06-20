<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Stethoscope, Home, ArrowLeft } from 'lucide-vue-next'

const router = useRouter()

function goBack() {
  if (window.history.state?.back) {
    router.back()
  } else {
    router.push('/dashboard')
  }
}
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-muted/30 px-4">
    <div class="flex flex-col items-center text-center max-w-md">

      <!-- Icono -->
      <div class="relative mb-6">
        <div class="flex h-20 w-20 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <Stethoscope class="h-10 w-10" />
        </div>
      </div>

      <!-- Código -->
      <p class="text-6xl font-extrabold tracking-tight text-primary/80">404</p>

      <!-- Mensaje -->
      <h1 class="mt-3 text-xl font-bold text-foreground">
        Página no encontrada
      </h1>
      <p class="mt-2 text-sm text-muted-foreground">
        La página que buscas no existe, fue movida o la URL es incorrecta.
        Verifica el enlace o vuelve al inicio.
      </p>

      <!-- Acciones -->
      <div class="mt-6 flex items-center gap-3">
        <Button variant="outline" class="gap-2" @click="goBack">
          <ArrowLeft class="h-4 w-4" />
          Volver
        </Button>
        <Button class="gap-2" @click="router.push('/dashboard')">
          <Home class="h-4 w-4" />
          Ir al inicio
        </Button>
      </div>

    </div>
  </div>
</template>