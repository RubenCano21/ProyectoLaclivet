<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  title: '',
  size: 'md',
})

const emit = defineEmits<{ 'update:modelValue': [value: boolean]; close: [] }>()

const widthClass = computed(() => ({
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
}[props.size]))

function close() {
  emit('update:modelValue', false)
  emit('close')
}
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
        @click.self="close"
      >
        <div class="relative w-full rounded-lg border bg-background shadow-lg" :class="widthClass">
          <!-- Header -->
          <div v-if="title" class="flex items-center justify-between border-b p-4">
            <h2 class="text-lg font-semibold">{{ title }}</h2>
            <button class="rounded-sm opacity-70 hover:opacity-100" aria-label="Cerrar" @click="close">✕</button>
          </div>
          <!-- Body -->
          <div class="p-4">
            <slot />
          </div>
          <!-- Footer -->
          <div v-if="$slots.footer" class="flex justify-end gap-2 border-t p-4">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
