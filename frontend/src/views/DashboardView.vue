<script setup lang="ts">
import { computed, onMounted } from "vue";
import AppSidebar from "@/components/AppSidebar.vue";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbList,
  BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import Card from "@/components/ui/card/Card.vue";
import CardHeader from "@/components/ui/card/CardHeader.vue";
import CardContent from "@/components/ui/card/CardContent.vue";
import CardTitle from "@/components/ui/card/CardTitle.vue";
import CardDescription from "@/components/ui/card/CardDescription.vue";
import { Badge } from "@/components/ui/badge";
import { Users, UserCheck, UserX, Loader2 } from "lucide-vue-next";
import { useUsuariosStore } from "@/stores/usuarios";

const store = useUsuariosStore();

const total = computed(() => store.items.length);
const lastRegistered = computed(() => {
  if (!store.items.length) return null;
  return store.items.reduce((prev, curr) =>
    new Date(curr.fecha_creacion) > new Date(prev.fecha_creacion) ? curr : prev
  );
});

onMounted(() => {
  store.fetchAll();
});
</script>

<template>
  <SidebarProvider>
    <AppSidebar />
    <SidebarInset>
      <header class="flex h-16 shrink-0 items-center gap-2 border-b px-4">
        <SidebarTrigger class="-ml-1" />
        <Separator orientation="vertical" class="mr-2 h-4" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbPage>Dashboard </BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>
      <main class="flex flex-1 flex-col gap-4 p-4">
        <h1 class="text-2xl font-semibold">Dashboard</h1>
        <Card class="w-full max-w-sm border bg-card text-card-foreground shadow-sm">
          <CardHeader class="flex flex-row items-center justify-between pb-2">
            <div class="flex items-center gap-2">
              <Users class="h-5 w-5 text-primary" />
              <CardTitle class="text-sm font-medium">Usuarios</CardTitle>
            </div>
            <Badge variant="secondary" class="text-lg px-3 py-1 font-bold">
              {{ total }}
            </Badge>
          </CardHeader>
          <CardContent>
            <CardDescription class="flex items-center gap-1.5 text-xs">
              <template v-if="store.loading">
                <Loader2 class="h-3.5 w-3.5 animate-spin" />
                Cargando...
              </template>
              <template v-else-if="lastRegistered">
                <UserCheck class="h-3.5 w-3.5 text-green-500 shrink-0" />
                Último registrado:
                <span class="font-medium text-foreground">
                  {{ lastRegistered.first_name }} {{ lastRegistered.last_name }}
                </span>
              </template>
              <template v-else>
                <UserX class="h-3.5 w-3.5" />
                Sin registros aún
              </template>
            </CardDescription>
          </CardContent>
        </Card>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
