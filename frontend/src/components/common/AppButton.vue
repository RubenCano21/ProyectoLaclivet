<script setup lang="ts">
import { Button } from '@/components/ui/button'
import type { ButtonVariants } from '@/components/ui/button'

interface Props {
  variant?: ButtonVariants['variant']
  size?: ButtonVariants['size']
  loading?: boolean
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
}

withDefaults(defineProps<Props>(), {
  variant: 'default',
  size: 'default',
  loading: false,
  disabled: false,
  type: 'button',
})
</script>

<template>
  <Button
    :variant="variant"
    :size="size"
    :disabled="disabled || loading"
    :type="type"
    v-bind="$attrs"
  >
    <span v-if="loading" class="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
    <slot />
  </Button>
</template>
