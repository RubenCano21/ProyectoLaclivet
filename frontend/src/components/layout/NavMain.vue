<script setup lang="ts">
import type { LucideIcon } from "lucide-vue-next"
import { ChevronRight } from "lucide-vue-next"
import { ref } from 'vue'
import { useRoute, RouterLink } from "vue-router"
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible'
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
} from '@/components/ui/sidebar'

defineProps<{
  items: {
    title: string
    url: string
    icon?: LucideIcon
    isActive?: boolean
    items?: {
      title: string
      url: string
    }[]
  }[]
}>()

const route = useRoute()
const openStates = ref<Record<string, boolean>>({})

function groupIsActive(item: { url: string; items?: { url: string }[] }): boolean {
  if (item.url && route.path.startsWith(item.url)) return true
  return item.items?.some((sub) => route.path === sub.url || route.path.startsWith(sub.url + '/')) ?? false
}

function isGroupOpen(item: { title: string; url: string; items?: { url: string }[] }): boolean {
  return groupIsActive(item) || (openStates.value[item.title] ?? false)
}

function setGroupOpen(title: string, val: boolean) {
  openStates.value[title] = val
}
</script>

<template>
  <SidebarGroup>
    <SidebarGroupLabel>Menú</SidebarGroupLabel>
    <SidebarMenu>
      <template v-for="item in items" :key="item.title">

        <!-- Ítem directo (sin subitems) -->
        <SidebarMenuItem v-if="!item.items || item.items.length === 0">
          <SidebarMenuButton as-child :tooltip="item.title" :is-active="route.path === item.url">
            <RouterLink :to="item.url">
              <component :is="item.icon" v-if="item.icon" />
              <span>{{ item.title }}</span>
            </RouterLink>
          </SidebarMenuButton>
        </SidebarMenuItem>

        <!-- Ítem colapsable (con subitems) -->
        <Collapsible
          v-else
          as-child
          :open="isGroupOpen(item)"
          @update:open="setGroupOpen(item.title, $event)"
          class="group/collapsible"
        >
          <SidebarMenuItem>
            <CollapsibleTrigger as-child>
              <SidebarMenuButton :tooltip="item.title" :is-active="groupIsActive(item)">
                <component :is="item.icon" v-if="item.icon" />
                <span>{{ item.title }}</span>
                <ChevronRight class="ml-auto transition-transform duration-200 group-data-[state=open]/collapsible:rotate-90" />
              </SidebarMenuButton>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <SidebarMenuSub>
                <SidebarMenuSubItem v-for="subItem in item.items" :key="subItem.title">
                  <SidebarMenuSubButton as-child :is-active="route.path === subItem.url">
                    <RouterLink :to="subItem.url">
                      <span>{{ subItem.title }}</span>
                    </RouterLink>
                  </SidebarMenuSubButton>
                </SidebarMenuSubItem>
              </SidebarMenuSub>
            </CollapsibleContent>
          </SidebarMenuItem>
        </Collapsible>

      </template>
    </SidebarMenu>
  </SidebarGroup>
</template>

