<script setup lang="ts" generic="T extends { id: number }">
import { shallowRef, watch, type Ref } from 'vue'
import { Check, ChevronsUpDown, Loader2 } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import {
  Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList,
} from '@/components/ui/command'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/utils'

const props = defineProps<{
  modelValue: number | null
  placeholder?: string
  emptyText?: string
  fetcher: (search: string) => Promise<T[]>
  labelFn: (item: T) => string
}>()

const emit = defineEmits<{ 'update:modelValue': [value: number | null] }>()

const open = shallowRef(false)
const search = shallowRef('')
const loading = shallowRef(false)
const opciones = shallowRef<T[]>([]) as Ref<T[]>
const seleccionado = shallowRef<T | null>(null) as Ref<T | null>

async function buscar(q: string) {
  loading.value = true
  try {
    opciones.value = await props.fetcher(q)
  } finally {
    loading.value = false
  }
}

watch(search, (q) => buscar(q))
watch(open, (val) => { if (val && opciones.value.length === 0) buscar('') })

function seleccionar(item: T) {
  seleccionado.value = item
  emit('update:modelValue', item.id)
  open.value = false
}

defineExpose({
  setSeleccionado: (item: T | null) => { seleccionado.value = item },
})
</script>

<template>
  <Popover v-model:open="open">
    <PopoverTrigger as-child>
      <Button
        variant="outline"
        role="combobox"
        :aria-expanded="open"
        class="w-full justify-between font-normal"
      >
        <span class="truncate">{{ seleccionado ? labelFn(seleccionado) : (placeholder || 'Selecciona…') }}</span>
        <ChevronsUpDown class="ml-2 h-4 w-4 shrink-0 opacity-50" />
      </Button>
    </PopoverTrigger>
    <PopoverContent class="w-[--reka-popover-trigger-width] p-0">
      <Command :filter="() => 1">
        <CommandInput v-model="search" :placeholder="placeholder || 'Buscar…'" />
        <CommandList>
          <div v-if="loading" class="flex items-center justify-center gap-2 py-6 text-sm text-muted-foreground">
            <Loader2 class="h-4 w-4 animate-spin" /> Buscando…
          </div>
          <CommandEmpty v-else>{{ emptyText || 'Sin resultados.' }}</CommandEmpty>
          <CommandGroup>
            <CommandItem
              v-for="item in opciones"
              :key="item.id"
              :value="String(item.id)"
              @select="seleccionar(item)"
            >
              <Check :class="cn('mr-2 h-4 w-4', modelValue === item.id ? 'opacity-100' : 'opacity-0')" />
              {{ labelFn(item) }}
            </CommandItem>
          </CommandGroup>
        </CommandList>
      </Command>
    </PopoverContent>
  </Popover>
</template>