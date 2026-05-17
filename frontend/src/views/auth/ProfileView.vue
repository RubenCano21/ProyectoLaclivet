<script setup lang="ts">
import { onMounted, computed, ref, watch } from "vue";
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
  BreadcrumbSeparator,
  BreadcrumbLink,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuLink,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import {
  Mail,
  Phone,
  MapPin,
  CalendarDays,
  ShieldCheck,
  Clock,
  Loader2,
  Pencil,
  Lock,
  CheckCircle2,
  AlertCircle,
  KeyRound,
} from "lucide-vue-next";
import { useAuthStore } from "@/stores/auth";
import { useRolesPermisosStore } from "@/stores/rolesPermisos";

type Tab = "editar" | "password" | "roles";

const auth = useAuthStore();
const rpStore = useRolesPermisosStore();
const activeTab = ref<Tab>("editar");

// ── computed helpers ──────────────────────────────────────────────────────────
const initials = computed(() => {
  const u = auth.user;
  if (!u) return "?";
  const f = u.first_name?.[0] ?? "";
  const l = u.last_name?.[0] ?? "";
  return (f + l).toUpperCase() || u.username[0].toUpperCase();
});

const fullName = computed(() => {
  const u = auth.user;
  if (!u) return "";
  return `${u.first_name} ${u.last_name}`.trim() || u.username;
});

function formatDate(val: string | null) {
  if (!val) return "—";
  return new Date(val).toLocaleDateString("es-BO", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

// ── edit profile form ─────────────────────────────────────────────────────────
const editForm = ref({
  first_name: "",
  last_name: "",
  email: "",
  telefono: "",
  direccion: "",
  fecha_nacimiento: "",
});
const editSaving = ref(false);
const editMessage = ref<{ ok: boolean; text: string } | null>(null);

function loadEditForm() {
  const u = auth.user;
  if (!u) return;
  editForm.value = {
    first_name: u.first_name ?? "",
    last_name: u.last_name ?? "",
    email: u.email ?? "",
    telefono: u.telefono ?? "",
    direccion: u.direccion ?? "",
    fecha_nacimiento: u.fecha_nacimiento ?? "",
  };
}

// ── roles & permisos ──────────────────────────────────────────────────────────
const selectedRolId = ref<string>("");
const rolesMessage = ref<{ ok: boolean; text: string } | null>(null);

const selectedRol = computed(() =>
  rpStore.roles.find((r) => r.id === Number(selectedRolId.value)) ?? null
);

// IDs de permisos activos en el rol seleccionado (mutable para switches)
const activePermisoIds = ref<Set<number>>(new Set());

// Llamado cuando el usuario cambia el Select de rol manualmente
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function onRolChange(newRolId: any) {
  const id = newRolId != null ? String(newRolId) : "";
  selectedRolId.value = id;
  const rol = rpStore.roles.find((r) => r.id === Number(id));
  activePermisoIds.value = new Set(rol?.permisos.map((p) => p.id) ?? []);
  rolesMessage.value = null;
}

function togglePermiso(id: number, checked: boolean) {
  const next = new Set(activePermisoIds.value);
  checked ? next.add(id) : next.delete(id);
  activePermisoIds.value = next;
}

async function saveRolPermisos() {
  if (!selectedRol.value) return;
  rolesMessage.value = null;
  const result = await rpStore.updateRolPermisos(
    selectedRol.value.id,
    [...activePermisoIds.value]
  );
  rolesMessage.value = result.ok
    ? { ok: true, text: `Permisos del rol "${selectedRol.value.nombre}" actualizados.` }
    : { ok: false, text: result.error ?? "Error al guardar." };
  if (result.ok) auth.fetchPerfil();
}

async function saveRolUsuario() {
  if (!auth.user) return;
  rolesMessage.value = null;
  const rolId = selectedRolId.value ? Number(selectedRolId.value) : null;
  const result = await rpStore.asignarRolUsuario(auth.user.id, rolId);
  rolesMessage.value = result.ok
    ? { ok: true, text: "Rol del usuario actualizado." }
    : { ok: false, text: result.error ?? "Error al asignar rol." };
  if (result.ok) auth.fetchPerfil();
}

// ── watch tab changes ─────────────────────────────────────────────────────────
watch(
  () => activeTab.value,
  async (tab) => {
    if (tab === "editar") loadEditForm();
    if (tab === "roles") {
      if (!rpStore.roles.length) await rpStore.fetchAll();
      // Pre-seleccionar el rol actual del usuario y activar sus permisos
      const userRolId = auth.user?.rol?.id;
      if (userRolId) {
        selectedRolId.value = String(userRolId);
        // Inicializar switches con los permisos que el usuario tiene actualmente
        const userPermisoIds = auth.user?.permisos?.map((p) => p.id) ?? [];
        activePermisoIds.value = new Set(userPermisoIds);
      }
    }
    editMessage.value = null;
    passwordMessage.value = null;
    rolesMessage.value = null;
  }
);

// ── change password form ──────────────────────────────────────────────────────
const passwordForm = ref({
  password_actual: "",
  password_nuevo: "",
  password_nuevo2: "",
});
const passwordSaving = ref(false);
const passwordMessage = ref<{ ok: boolean; text: string } | null>(null);

async function submitEdit() {
  editSaving.value = true;
  editMessage.value = null;
  const payload = {
    ...editForm.value,
    telefono: editForm.value.telefono || null,
    direccion: editForm.value.direccion || null,
    fecha_nacimiento: editForm.value.fecha_nacimiento || null,
  };
  const result = await auth.updatePerfil(payload);
  editMessage.value = result.ok
    ? { ok: true, text: "Perfil actualizado exitosamente." }
    : { ok: false, text: result.error ?? "Error al actualizar." };
  editSaving.value = false;
}

async function submitPassword() {
  passwordSaving.value = true;
  passwordMessage.value = null;
  const result = await auth.cambiarPassword(passwordForm.value);
  if (result.ok) {
    passwordMessage.value = { ok: true, text: "Contraseña cambiada exitosamente." };
    passwordForm.value = { password_actual: "", password_nuevo: "", password_nuevo2: "" };
  } else {
    passwordMessage.value = { ok: false, text: result.error ?? "Error al cambiar." };
  }
  passwordSaving.value = false;
}

// Group permissions by last word of codigo, normalizing singular/plural
const permisosAgrupados = computed(() => {
  const groups: Record<string, typeof rpStore.permisos> = {};
  for (const p of rpStore.permisos) {
    const parts = p.codigo.split("_");
    const raw = (parts.length > 1 ? parts[parts.length - 1] : "general").toLowerCase();
    // Normalizar plural → singular (ej. "usuarios" → "usuario", "mascotas" → "mascota")
    const normalized = raw.endsWith("s") && raw.length > 2 ? raw.slice(0, -1) : raw;
    const label = normalized.charAt(0).toUpperCase() + normalized.slice(1);
    if (!groups[label]) groups[label] = [];
    groups[label].push(p);
  }
  return groups;
});

onMounted(() => {
  auth.fetchPerfil();
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
              <BreadcrumbLink href="/dashboard">Dashboard</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>Mi Perfil</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <main class="flex flex-1 flex-col gap-6 p-6 max-w-5xl mx-auto w-full">
        <!-- Loading inicial -->
        <div v-if="auth.loading && !auth.user" class="flex items-center justify-center py-20">
          <Loader2 class="h-8 w-8 animate-spin text-muted-foreground" />
        </div>

        <template v-else-if="auth.user">
          <div class="flex flex-col lg:flex-row gap-6 items-start">

          <!-- ── Left card: perfil resumido (solo lectura) ── -->
          <Card class="w-full lg:w-100 shrink-0">
            <CardContent class="flex flex-col items-center gap-4 pt-6 pb-6">
              <Avatar class="h-20 w-20">
                <AvatarFallback class="text-2xl font-semibold bg-primary/10 text-primary">
                  {{ initials }}
                </AvatarFallback>
              </Avatar>
              <div class="flex flex-col items-center gap-1 text-center">
                <h2 class="text-xl font-bold leading-tight">{{ fullName }}</h2>
                <p class="text-sm text-muted-foreground">@{{ auth.user.username }}</p>
                <div class="flex flex-wrap justify-center gap-2 mt-1">
                  <Badge v-if="auth.user.rol" variant="default">
                    <ShieldCheck class="h-3 w-3 mr-1" />
                    {{ auth.user.rol.nombre }}
                  </Badge>
                  <Badge variant="secondary" v-if="auth.user.is_staff">Staff</Badge>
                  <Badge :variant="auth.user.is_active ? 'default' : 'destructive'">
                    {{ auth.user.is_active ? "Activo" : "Inactivo" }}
                  </Badge>
                </div>
              </div>

              <Separator />

              <div class="w-full flex flex-col gap-3 text-sm">
                <div class="flex items-start gap-3">
                  <Mail class="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                  <div>
                    <p class="text-xs text-muted-foreground">Correo</p>
                    <p class="font-medium break-all">{{ auth.user.email }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <Phone class="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                  <div>
                    <p class="text-xs text-muted-foreground">Teléfono</p>
                    <p class="font-medium">{{ auth.user.telefono ?? "—" }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <MapPin class="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                  <div>
                    <p class="text-xs text-muted-foreground">Dirección</p>
                    <p class="font-medium">{{ auth.user.direccion ?? "—" }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <CalendarDays class="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                  <div>
                    <p class="text-xs text-muted-foreground">Nacimiento</p>
                    <p class="font-medium">{{ formatDate(auth.user.fecha_nacimiento) }}</p>
                  </div>
                </div>
              </div>

              <Separator />

              <div class="w-full flex flex-col gap-3 text-sm">
                <div class="flex items-start gap-3">
                  <CalendarDays class="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                  <div>
                    <p class="text-xs text-muted-foreground">Miembro desde</p>
                    <p class="font-medium">{{ formatDate(auth.user.fecha_creacion) }}</p>
                  </div>
                </div>
                <div class="flex items-start gap-3">
                  <Clock class="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
                  <div>
                    <p class="text-xs text-muted-foreground">Última actualización</p>
                    <p class="font-medium">{{ formatDate(auth.user.fecha_actualizacion) }}</p>
                  </div>
                </div>
              </div>

            </CardContent>
          </Card>

          <!-- ── Right card: tabs de edición ── -->
          <Card class="flex-1 min-w-0">
            <!-- NavigationMenu como tabs -->
            <div class="border-b px-4 pt-3 pb-0">
              <NavigationMenu>
                <NavigationMenuList class="gap-0">
                  <NavigationMenuItem>
                    <NavigationMenuLink
                      :class="[
                        navigationMenuTriggerStyle(),
                        'cursor-pointer rounded-none border-b-2 transition-none',
                        activeTab === 'editar'
                          ? 'border-primary text-primary bg-transparent hover:bg-transparent'
                          : 'border-transparent text-muted-foreground',
                      ]"
                      @click="activeTab = 'editar'"
                    >
                      <Pencil class="h-4 w-4 mr-1.5" />
                      Editar Perfil
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem>
                    <NavigationMenuLink
                      :class="[
                        navigationMenuTriggerStyle(),
                        'cursor-pointer rounded-none border-b-2 transition-none',
                        activeTab === 'password'
                          ? 'border-primary text-primary bg-transparent hover:bg-transparent'
                          : 'border-transparent text-muted-foreground',
                      ]"
                      @click="activeTab = 'password'"
                    >
                      <Lock class="h-4 w-4 mr-1.5" />
                      Contraseña
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                  <NavigationMenuItem v-if="auth.user?.is_staff">
                    <NavigationMenuLink
                      :class="[
                        navigationMenuTriggerStyle(),
                        'cursor-pointer rounded-none border-b-2 transition-none',
                        activeTab === 'roles'
                          ? 'border-primary text-primary bg-transparent hover:bg-transparent'
                          : 'border-transparent text-muted-foreground',
                      ]"
                      @click="activeTab = 'roles'"
                    >
                      <KeyRound class="h-4 w-4 mr-1.5" />
                      Roles y Permisos
                    </NavigationMenuLink>
                  </NavigationMenuItem>
                </NavigationMenuList>
              </NavigationMenu>
            </div>

            <!-- ── TAB: Editar Perfil ─────────────────────────────────────── -->
            <CardContent v-if="activeTab === 'editar'" class="pt-6">
              <form class="flex flex-col gap-4" @submit.prevent="submitEdit">
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Nombre</label>
                    <Input v-model="editForm.first_name" placeholder="Nombre" />
                  </div>
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Apellido</label>
                    <Input v-model="editForm.last_name" placeholder="Apellido" />
                  </div>
                  <div class="flex flex-col gap-1.5 sm:col-span-2">
                    <label class="text-xs font-medium text-muted-foreground">Correo electrónico</label>
                    <Input v-model="editForm.email" type="email" placeholder="correo@ejemplo.com" />
                  </div>
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Teléfono</label>
                    <Input v-model="editForm.telefono" placeholder="Ej. 70000000" />
                  </div>
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-medium text-muted-foreground">Fecha de nacimiento</label>
                    <Input v-model="editForm.fecha_nacimiento" type="date" />
                  </div>
                  <div class="flex flex-col gap-1.5 sm:col-span-2">
                    <label class="text-xs font-medium text-muted-foreground">Dirección</label>
                    <Input v-model="editForm.direccion" placeholder="Dirección" />
                  </div>
                </div>

                <div
                  v-if="editMessage"
                  class="flex items-center gap-2 text-sm rounded-md px-3 py-2"
                  :class="editMessage.ok ? 'bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-400' : 'bg-destructive/10 text-destructive'"
                >
                  <CheckCircle2 v-if="editMessage.ok" class="h-4 w-4 shrink-0" />
                  <AlertCircle v-else class="h-4 w-4 shrink-0" />
                  {{ editMessage.text }}
                </div>

                <div class="flex justify-end">
                  <Button type="submit" :disabled="editSaving">
                    <Loader2 v-if="editSaving" class="h-4 w-4 mr-2 animate-spin" />
                    Guardar cambios
                  </Button>
                </div>
              </form>
            </CardContent>

            <!-- ── TAB: Contraseña ────────────────────────────────────────────────────── -->
            <CardContent v-else-if="activeTab === 'password'" class="pt-6">
              <form class="flex flex-col gap-4 max-w-sm" @submit.prevent="submitPassword">
                <div class="flex flex-col gap-1.5">
                  <label class="text-xs font-medium text-muted-foreground">Contraseña actual</label>
                  <Input v-model="passwordForm.password_actual" type="password" placeholder="••••••••" />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="text-xs font-medium text-muted-foreground">Nueva contraseña</label>
                  <Input v-model="passwordForm.password_nuevo" type="password" placeholder="••••••••" />
                </div>
                <div class="flex flex-col gap-1.5">
                  <label class="text-xs font-medium text-muted-foreground">Confirmar nueva contraseña</label>
                  <Input v-model="passwordForm.password_nuevo2" type="password" placeholder="••••••••" />
                </div>

                <div
                  v-if="passwordMessage"
                  class="flex items-center gap-2 text-sm rounded-md px-3 py-2"
                  :class="passwordMessage.ok ? 'bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-400' : 'bg-destructive/10 text-destructive'"
                >
                  <CheckCircle2 v-if="passwordMessage.ok" class="h-4 w-4 shrink-0" />
                  <AlertCircle v-else class="h-4 w-4 shrink-0" />
                  {{ passwordMessage.text }}
                </div>

                <div class="flex justify-end">
                  <Button type="submit" :disabled="passwordSaving">
                    <Loader2 v-if="passwordSaving" class="h-4 w-4 mr-2 animate-spin" />
                    Cambiar contraseña
                  </Button>
                </div>
              </form>
            </CardContent>

            <!-- ── TAB: Roles y Permisos ─────────────────────────────────────────────── -->
            <CardContent v-else-if="activeTab === 'roles'" class="pt-6 flex flex-col gap-6">
              <div v-if="rpStore.loading" class="flex items-center justify-center py-10">
                <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
              </div>

              <template v-else>
                <!-- ── Warning si el rol es administrador ── -->
                <div
                  v-if="selectedRol?.nombre?.toLowerCase().includes('admin')"
                  class="flex items-start gap-2.5 rounded-md border border-destructive/40 bg-destructive/5 px-4 py-3 text-sm text-destructive"
                >
                  <AlertCircle class="h-4 w-4 shrink-0 mt-0.5" />
                  <span>
                    Se recomienda un sólo usuario con rol administrador, cualquier usuario con el rol
                    puede <strong>crear/editar/eliminar</strong> otras cuentas y editar sus privilegios.
                  </span>
                </div>

                <!-- ── Sección: Perfil del usuario (selector de rol) ── -->
                <div class="flex flex-col gap-1">
                  <h3 class="text-sm font-semibold mb-3">Perfil del usuario</h3>

                  <div class="grid grid-cols-[100px_1fr] items-center gap-4">
                    <span class="text-sm text-right text-muted-foreground">Rol</span>
                    <Select :model-value="selectedRolId" @update:model-value="onRolChange">
                      <SelectTrigger>
                        <SelectValue placeholder="Sin rol asignado" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem
                          v-for="rol in rpStore.roles"
                          :key="rol.id"
                          :value="String(rol.id)"
                        >
                          {{ rol.nombre }}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <p class="text-xs text-primary pl-29">
                    El rol determina los privilegios generales que tendrá el usuario.
                  </p>
                </div>

                <Separator />

                <!-- ── Permisos agrupados por categoría ── -->
                <template v-if="selectedRol">
                  <div
                    v-for="(grupo, label) in permisosAgrupados"
                    :key="label"
                    class="flex flex-col"
                  >
                    <h4 class="text-sm font-semibold mb-1">Privilegios de {{ (label as string).toLowerCase() }}</h4>
                    <Separator class="mb-3" />

                    <div
                      v-for="permiso in grupo"
                      :key="permiso.id"
                      class="grid grid-cols-[160px_56px_1fr] items-center gap-2 py-2.5 border-b last:border-b-0"
                    >
                      <span class="text-sm text-right text-muted-foreground leading-tight pr-1">
                        {{ permiso.nombre }}
                      </span>
                      <div class="flex justify-center">
                        <Switch
                          :checked="activePermisoIds.has(permiso.id)"
                          @update:checked="togglePermiso(permiso.id, $event)"
                        />
                      </div>
                      <span class="text-sm text-muted-foreground leading-snug">
                        {{ permiso.descripcion }}
                      </span>
                    </div>
                  </div>
                </template>
                <div v-else class="text-sm text-muted-foreground text-center py-6">
                  Selecciona un rol para ver y editar sus permisos.
                </div>

                <!-- ── Mensaje de resultado ── -->
                <div
                  v-if="rolesMessage"
                  class="flex items-center gap-2 text-sm rounded-md px-3 py-2"
                  :class="rolesMessage.ok ? 'bg-green-50 text-green-700 dark:bg-green-950 dark:text-green-400' : 'bg-destructive/10 text-destructive'"
                >
                  <CheckCircle2 v-if="rolesMessage.ok" class="h-4 w-4 shrink-0" />
                  <AlertCircle v-else class="h-4 w-4 shrink-0" />
                  {{ rolesMessage.text }}
                </div>

                <!-- ── Botones de acción ── -->
                <div class="flex items-center justify-between gap-3 pt-2">
                  <Button
                    variant="outline"
                    :disabled="!selectedRolId || rpStore.saving"
                    @click="saveRolUsuario"
                  >
                    <Loader2 v-if="rpStore.saving" class="h-4 w-4 mr-2 animate-spin" />
                    <ShieldCheck class="h-4 w-4 mr-2" />
                    Asignar rol al usuario
                  </Button>
                  <Button
                    :disabled="!selectedRol || rpStore.saving"
                    @click="saveRolPermisos"
                  >
                    <Loader2 v-if="rpStore.saving" class="h-4 w-4 mr-2 animate-spin" />
                    <KeyRound class="h-4 w-4 mr-2" />
                    Guardar permisos del rol
                  </Button>
                </div>
              </template>
            </CardContent>
          </Card>
          </div>
        </template>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>
