<script setup lang="ts" generic="T extends Record<string, unknown>">
import { computed } from 'vue'

export interface Column<TRow> {
  key: keyof TRow & string
  label: string
  sortable?: boolean
  class?: string
}

interface Props {
  columns: Column<T>[]
  rows: T[]
  loading?: boolean
  total?: number
  page?: number
  pageSize?: number
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  total: 0,
  page: 1,
  pageSize: 10,
  emptyText: 'Sin registros',
})

const emit = defineEmits<{
  'update:page': [page: number]
  sort: [key: string]
}>()

const totalPages = computed(() => Math.ceil(props.total / props.pageSize) || 1)
</script>

<template>
  <div class="w-full overflow-auto rounded-md border">
    <table class="w-full caption-bottom text-sm">
      <thead class="[&_tr]:border-b">
        <tr class="border-b transition-colors hover:bg-muted/50">
          <th
            v-for="col in columns"
            :key="col.key"
            class="h-10 px-4 text-left align-middle font-medium text-muted-foreground"
            :class="[col.class, col.sortable ? 'cursor-pointer select-none' : '']"
            @click="col.sortable ? emit('sort', col.key) : undefined"
          >
            {{ col.label }}
          </th>
          <th v-if="$slots.actions" class="h-10 px-4 text-right align-middle font-medium text-muted-foreground">
            Acciones
          </th>
        </tr>
      </thead>
      <tbody class="[&_tr:last-child]:border-0">
        <template v-if="loading">
          <tr v-for="n in pageSize" :key="n" class="border-b">
            <td v-for="col in columns" :key="col.key" class="p-4">
              <div class="h-4 w-full animate-pulse rounded bg-muted" />
            </td>
          </tr>
        </template>
        <template v-else-if="rows.length === 0">
          <tr>
            <td :colspan="columns.length + ($slots.actions ? 1 : 0)" class="h-24 text-center text-muted-foreground">
              {{ emptyText }}
            </td>
          </tr>
        </template>
        <template v-else>
          <tr
            v-for="(row, idx) in rows"
            :key="idx"
            class="border-b transition-colors hover:bg-muted/50"
          >
            <td v-for="col in columns" :key="col.key" class="p-4 align-middle" :class="col.class">
              <slot :name="`cell-${col.key}`" :value="row[col.key]" :row="row">
                {{ row[col.key] ?? '—' }}
              </slot>
            </td>
            <td v-if="$slots.actions" class="p-4 text-right align-middle">
              <slot name="actions" :row="row" />
            </td>
          </tr>
        </template>
      </tbody>
    </table>

    <!-- Pagination -->
    <div v-if="total > pageSize" class="flex items-center justify-between border-t px-4 py-3 text-sm">
      <span class="text-muted-foreground">{{ total }} registros</span>
      <div class="flex gap-1">
        <button
          class="rounded px-2 py-1 hover:bg-muted disabled:opacity-40"
          :disabled="page <= 1"
          @click="emit('update:page', page - 1)"
        >
          ‹ Anterior
        </button>
        <span class="px-2 py-1">{{ page }} / {{ totalPages }}</span>
        <button
          class="rounded px-2 py-1 hover:bg-muted disabled:opacity-40"
          :disabled="page >= totalPages"
          @click="emit('update:page', page + 1)"
        >
          Siguiente ›
        </button>
      </div>
    </div>
  </div>
</template>
