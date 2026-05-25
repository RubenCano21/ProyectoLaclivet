<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <div class="p-6">
    <h1 class="text-2xl font-semibold">Historial del Paciente</h1>
    <p class="mt-2 text-muted-foreground">
      Historial clínico y de exámenes del paciente #{{ route.params.id }} (RF10).
    </p>
  </div>
</template>
