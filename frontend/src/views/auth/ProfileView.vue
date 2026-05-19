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
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
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

const activePermisoIds = ref<Set<number>>(new Set());

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

watch(
  () => activeTab.value,
  async (tab) => {
    if (tab === "editar") loadEditForm();
    if (tab === "roles") {
      if (!rpStore.roles.length) await rpStore.fetchAll();
      const userRolId = auth.user?.rol?.id;
      if (userRolId) {
        selectedRolId.value = String(userRolId);
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

const permisosAgrupados = computed(() => {
  const groups: Record<string, typeof rpStore.permisos> = {};
  for (const p of rpStore.permisos) {
    const parts = p.codigo.split("_");
    const raw = (parts.length > 1 ? parts[parts.length - 1] : "general").toLowerCase();
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
  <!-- Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" />
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap" rel="stylesheet" />

  <SidebarProvider>
    <AppSidebar />
    <SidebarInset class="font-['DM_Sans',sans-serif]">

      <!-- ── Header ── -->
      <header class="flex h-16 shrink-0 items-center gap-2 border-b border-mineral-green-100 bg-white/80 backdrop-blur-sm px-4 sticky top-0 z-20">
        <SidebarTrigger class="-ml-1" />
        <Separator orientation="vertical" class="mr-2 h-4 bg-mineral-green-200" />
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/dashboard" class="text-mineral-green-500 hover:text-mineral-green-800 transition-colors text-sm">
                Dashboard
              </BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage class="text-mineral-green-900 font-medium text-sm">Mi Perfil</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </header>

      <!-- ── Page title strip ── -->
      <div class="bg-[linear-gradient(135deg,#0f2e1e_0%,#1a4a2e_60%,#2d6e47_100%)] px-6 py-8">
        <h1 class="font-['Playfair_Display',serif] text-2xl font-bold text-white tracking-tight">
          Mi Perfil
        </h1>
        <p class="text-mineral-green-300 text-sm mt-0.5">
          Gestiona tu información personal y configuración de acceso
        </p>
      </div>

      <main class="flex flex-1 flex-col gap-6 p-6 max-w-5xl mx-auto w-full">

        <!-- Loading -->
        <div v-if="auth.loading && !auth.user" class="flex items-center justify-center py-24">
          <div class="flex flex-col items-center gap-3">
            <Loader2 class="h-8 w-8 animate-spin text-mineral-green-500" />
            <p class="text-sm text-mineral-green-400 font-['DM_Sans',sans-serif]">Cargando perfil…</p>
          </div>
        </div>

        <template v-else-if="auth.user">
          <div class="flex flex-col lg:flex-row gap-6 items-start">

            <!-- ══ Tarjeta izquierda: perfil resumido ══ -->
            <div class="w-full lg:w-80 shrink-0 flex flex-col gap-4">

              <!-- Avatar card -->
              <div class="relative rounded-2xl overflow-hidden
                          bg-white border border-mineral-green-100
                          shadow-[0_2px_16px_rgba(26,74,46,.08)]">

                <!-- Banda decorativa superior -->
                <div class="h-20 bg-[linear-gradient(135deg,#0f2e1e,#2d6e47)]
                            relative overflow-hidden">
                  <div class="absolute inset-0
                              bg-[linear-gradient(rgba(255,255,255,.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.04)_1px,transparent_1px)]
                              bg-size-[24px_24px]" />
                </div>

                <!-- Avatar flotante sobre la banda -->
                <div class="flex flex-col items-center px-6 pb-6">
                  <div class="-mt-10 mb-3 relative">
                    <Avatar class="h-20 w-20 ring-4 ring-white shadow-lg">
                      <AvatarFallback
                        class="text-2xl font-bold
                               bg-[linear-gradient(135deg,#1a4a2e,#2d6e47)]
                               text-white font-['Playfair_Display',serif]">
                        {{ initials }}
                      </AvatarFallback>
                    </Avatar>
                    <!-- Indicador activo -->
                    <span
                      v-if="auth.user.is_active"
                      class="absolute bottom-0.5 right-0.5 w-4 h-4 rounded-full
                             bg-green-400 border-2 border-white
                             shadow-[0_0_6px_#4ade80]
                             animate-[blink_2.5s_ease-in-out_infinite]" />
                  </div>

                  <h2 class="font-['Playfair_Display',serif] text-lg font-bold text-mineral-green-950 text-center leading-tight">
                    {{ fullName }}
                  </h2>
                  <p class="text-xs text-mineral-green-400 mt-0.5 mb-3">@{{ auth.user.username }}</p>

                  <div class="flex flex-wrap justify-center gap-1.5">
                    <Badge v-if="auth.user.rol"
                           class="bg-mineral-green-700 hover:bg-mineral-green-800 text-white border-0 text-[.68rem] px-2.5 py-0.5">
                      <ShieldCheck class="h-3 w-3 mr-1" />
                      {{ auth.user.rol.nombre }}
                    </Badge>
                    <Badge v-if="auth.user.is_staff"
                           class="bg-amber-100 text-amber-700 border border-amber-200 text-[.68rem] px-2.5 py-0.5">
                      Staff
                    </Badge>
                    <Badge :class="auth.user.is_active
                      ? 'bg-green-50 text-green-700 border border-green-200'
                      : 'bg-red-50 text-red-600 border border-red-200'"
                           class="text-[.68rem] px-2.5 py-0.5">
                      {{ auth.user.is_active ? "Activo" : "Inactivo" }}
                    </Badge>
                  </div>
                </div>
              </div>

              <!-- Info card -->
              <div class="rounded-2xl bg-white border border-mineral-green-100
                          shadow-[0_2px_16px_rgba(26,74,46,.06)] overflow-hidden">

                <!-- Sección contacto -->
                <div class="px-5 py-4">
                  <p class="text-[.65rem] font-semibold tracking-widest uppercase
                             text-mineral-green-400 mb-3">Contacto</p>
                  <div class="flex flex-col gap-3.5">
                    <div class="flex items-start gap-3">
                      <span class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center
                                   rounded-lg bg-mineral-green-50 border border-mineral-green-100">
                        <Mail class="h-3.5 w-3.5 text-mineral-green-600" />
                      </span>
                      <div class="min-w-0">
                        <p class="text-[.68rem] text-mineral-green-400">Correo</p>
                        <p class="text-sm font-medium text-mineral-green-900 break-all leading-snug">
                          {{ auth.user.email }}
                        </p>
                      </div>
                    </div>
                    <div class="flex items-start gap-3">
                      <span class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center
                                   rounded-lg bg-mineral-green-50 border border-mineral-green-100">
                        <Phone class="h-3.5 w-3.5 text-mineral-green-600" />
                      </span>
                      <div>
                        <p class="text-[.68rem] text-mineral-green-400">Teléfono</p>
                        <p class="text-sm font-medium text-mineral-green-900">{{ auth.user.telefono ?? "—" }}</p>
                      </div>
                    </div>
                    <div class="flex items-start gap-3">
                      <span class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center
                                   rounded-lg bg-mineral-green-50 border border-mineral-green-100">
                        <MapPin class="h-3.5 w-3.5 text-mineral-green-600" />
                      </span>
                      <div>
                        <p class="text-[.68rem] text-mineral-green-400">Dirección</p>
                        <p class="text-sm font-medium text-mineral-green-900">{{ auth.user.direccion ?? "—" }}</p>
                      </div>
                    </div>
                    <div class="flex items-start gap-3">
                      <span class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center
                                   rounded-lg bg-mineral-green-50 border border-mineral-green-100">
                        <CalendarDays class="h-3.5 w-3.5 text-mineral-green-600" />
                      </span>
                      <div>
                        <p class="text-[.68rem] text-mineral-green-400">Nacimiento</p>
                        <p class="text-sm font-medium text-mineral-green-900">{{ formatDate(auth.user.fecha_nacimiento) }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="h-px bg-mineral-green-100 mx-5" />

                <!-- Sección cuenta -->
                <div class="px-5 py-4">
                  <p class="text-[.65rem] font-semibold tracking-widest uppercase
                             text-mineral-green-400 mb-3">Cuenta</p>
                  <div class="flex flex-col gap-3.5">
                    <div class="flex items-start gap-3">
                      <span class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center
                                   rounded-lg bg-mineral-green-50 border border-mineral-green-100">
                        <CalendarDays class="h-3.5 w-3.5 text-mineral-green-600" />
                      </span>
                      <div>
                        <p class="text-[.68rem] text-mineral-green-400">Miembro desde</p>
                        <p class="text-sm font-medium text-mineral-green-900">{{ formatDate(auth.user.fecha_creacion) }}</p>
                      </div>
                    </div>
                    <div class="flex items-start gap-3">
                      <span class="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center
                                   rounded-lg bg-mineral-green-50 border border-mineral-green-100">
                        <Clock class="h-3.5 w-3.5 text-mineral-green-600" />
                      </span>
                      <div>
                        <p class="text-[.68rem] text-mineral-green-400">Última actualización</p>
                        <p class="text-sm font-medium text-mineral-green-900">{{ formatDate(auth.user.fecha_actualizacion) }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- ══ Tarjeta derecha: tabs de edición ══ -->
            <div class="flex-1 min-w-0 rounded-2xl bg-white border border-mineral-green-100
                        shadow-[0_2px_16px_rgba(26,74,46,.08)] overflow-hidden">

              <!-- Tab bar -->
              <div class="border-b border-mineral-green-100 bg-mineral-green-50/50 px-4 pt-0">
                <nav class="flex gap-0">
                  <!-- Editar Perfil -->
                  <button
                    type="button"
                    @click="activeTab = 'editar'"
                    :class="[
                      'flex items-center gap-1.5 px-4 py-4 text-sm font-medium border-b-2 transition-all duration-150',
                      activeTab === 'editar'
                        ? 'border-mineral-green-700 text-mineral-green-800 bg-transparent'
                        : 'border-transparent text-mineral-green-400 hover:text-mineral-green-700 hover:border-mineral-green-300',
                    ]"
                  >
                    <span :class="[
                      'flex h-6 w-6 items-center justify-center rounded-md transition-colors',
                      activeTab === 'editar' ? 'bg-mineral-green-100' : ''
                    ]">
                      <Pencil class="h-3.5 w-3.5" />
                    </span>
                    Editar Perfil
                  </button>

                  <!-- Contraseña -->
                  <button
                    type="button"
                    @click="activeTab = 'password'"
                    :class="[
                      'flex items-center gap-1.5 px-4 py-4 text-sm font-medium border-b-2 transition-all duration-150',
                      activeTab === 'password'
                        ? 'border-mineral-green-700 text-mineral-green-800 bg-transparent'
                        : 'border-transparent text-mineral-green-400 hover:text-mineral-green-700 hover:border-mineral-green-300',
                    ]"
                  >
                    <span :class="[
                      'flex h-6 w-6 items-center justify-center rounded-md transition-colors',
                      activeTab === 'password' ? 'bg-mineral-green-100' : ''
                    ]">
                      <Lock class="h-3.5 w-3.5" />
                    </span>
                    Contraseña
                  </button>

                  <!-- Roles (solo staff) -->
                  <button
                    v-if="auth.user?.is_staff"
                    type="button"
                    @click="activeTab = 'roles'"
                    :class="[
                      'flex items-center gap-1.5 px-4 py-4 text-sm font-medium border-b-2 transition-all duration-150',
                      activeTab === 'roles'
                        ? 'border-mineral-green-700 text-mineral-green-800 bg-transparent'
                        : 'border-transparent text-mineral-green-400 hover:text-mineral-green-700 hover:border-mineral-green-300',
                    ]"
                  >
                    <span :class="[
                      'flex h-6 w-6 items-center justify-center rounded-md transition-colors',
                      activeTab === 'roles' ? 'bg-mineral-green-100' : ''
                    ]">
                      <KeyRound class="h-3.5 w-3.5" />
                    </span>
                    Roles y Permisos
                  </button>
                </nav>
              </div>

              <!-- ── TAB: Editar Perfil ── -->
              <div v-if="activeTab === 'editar'" class="p-6">
                <div class="mb-5">
                  <h3 class="font-['Playfair_Display',serif] text-lg font-bold text-mineral-green-950">
                    Información personal
                  </h3>
                  <p class="text-xs text-mineral-green-400 mt-0.5">Actualiza tus datos de contacto y perfil</p>
                </div>

                <form class="flex flex-col gap-5" @submit.prevent="submitEdit">
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

                    <div class="flex flex-col gap-1.5">
                      <label class="text-xs font-semibold text-mineral-green-700">Nombre</label>
                      <Input
                        v-model="editForm.first_name"
                        placeholder="Nombre"
                        class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                               focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50
                               text-mineral-green-950 placeholder-mineral-green-300"
                      />
                    </div>

                    <div class="flex flex-col gap-1.5">
                      <label class="text-xs font-semibold text-mineral-green-700">Apellido</label>
                      <Input
                        v-model="editForm.last_name"
                        placeholder="Apellido"
                        class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                               focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50
                               text-mineral-green-950 placeholder-mineral-green-300"
                      />
                    </div>

                    <div class="flex flex-col gap-1.5 sm:col-span-2">
                      <label class="text-xs font-semibold text-mineral-green-700">Correo electrónico</label>
                      <Input
                        v-model="editForm.email"
                        type="email"
                        placeholder="correo@ejemplo.com"
                        class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                               focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50
                               text-mineral-green-950 placeholder-mineral-green-300"
                      />
                    </div>

                    <div class="flex flex-col gap-1.5">
                      <label class="text-xs font-semibold text-mineral-green-700">Teléfono</label>
                      <Input
                        v-model="editForm.telefono"
                        placeholder="Ej. 70000000"
                        class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                               focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50
                               text-mineral-green-950 placeholder-mineral-green-300"
                      />
                    </div>

                    <div class="flex flex-col gap-1.5">
                      <label class="text-xs font-semibold text-mineral-green-700">Fecha de nacimiento</label>
                      <Input
                        v-model="editForm.fecha_nacimiento"
                        type="date"
                        class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                               focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50
                               text-mineral-green-950"
                      />
                    </div>

                    <div class="flex flex-col gap-1.5 sm:col-span-2">
                      <label class="text-xs font-semibold text-mineral-green-700">Dirección</label>
                      <Input
                        v-model="editForm.direccion"
                        placeholder="Dirección"
                        class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                               focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50
                               text-mineral-green-950 placeholder-mineral-green-300"
                      />
                    </div>
                  </div>

                  <!-- Mensaje -->
                  <transition name="fade">
                    <div
                      v-if="editMessage"
                      class="flex items-center gap-2.5 text-sm rounded-xl px-4 py-3 border"
                      :class="editMessage.ok
                        ? 'bg-green-50 text-green-700 border-green-200'
                        : 'bg-red-50 text-red-600 border-red-200'"
                    >
                      <CheckCircle2 v-if="editMessage.ok" class="h-4 w-4 shrink-0" />
                      <AlertCircle v-else class="h-4 w-4 shrink-0" />
                      {{ editMessage.text }}
                    </div>
                  </transition>

                  <div class="flex justify-end pt-1">
                    <button
                      type="submit"
                      :disabled="editSaving"
                      class="relative overflow-hidden flex items-center gap-2
                             rounded-xl px-5 py-2.5 text-sm font-semibold text-white
                             bg-[linear-gradient(135deg,#1a4a2e_0%,#2d6e47_100%)]
                             shadow-[0_3px_12px_rgba(26,74,46,.35)]
                             transition hover:-translate-y-px hover:shadow-[0_5px_18px_rgba(26,74,46,.45)]
                             active:scale-[.98]
                             disabled:opacity-60 disabled:translate-y-0 disabled:cursor-not-allowed"
                    >
                      <span class="absolute top-0 -left-full bottom-0 w-1/2 skew-x-[-20deg]
                                   bg-[linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent)]
                                   animate-[shimmerBtn_3s_ease-in-out_infinite] pointer-events-none" />
                      <Loader2 v-if="editSaving" class="h-4 w-4 animate-spin" />
                      Guardar cambios
                    </button>
                  </div>
                </form>
              </div>

              <!-- ── TAB: Contraseña ── -->
              <div v-else-if="activeTab === 'password'" class="p-6">
                <div class="mb-5">
                  <h3 class="font-['Playfair_Display',serif] text-lg font-bold text-mineral-green-950">
                    Cambiar contraseña
                  </h3>
                  <p class="text-xs text-mineral-green-400 mt-0.5">Elige una contraseña segura y no la compartas</p>
                </div>

                <form class="flex flex-col gap-4 max-w-sm" @submit.prevent="submitPassword">
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-semibold text-mineral-green-700">Contraseña actual</label>
                    <Input
                      v-model="passwordForm.password_actual"
                      type="password"
                      placeholder="••••••••"
                      class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                             focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50"
                    />
                  </div>
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-semibold text-mineral-green-700">Nueva contraseña</label>
                    <Input
                      v-model="passwordForm.password_nuevo"
                      type="password"
                      placeholder="••••••••"
                      class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                             focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50"
                    />
                  </div>
                  <div class="flex flex-col gap-1.5">
                    <label class="text-xs font-semibold text-mineral-green-700">Confirmar nueva contraseña</label>
                    <Input
                      v-model="passwordForm.password_nuevo2"
                      type="password"
                      placeholder="••••••••"
                      class="rounded-xl border-mineral-green-200 focus:border-mineral-green-600
                             focus:ring-2 focus:ring-mineral-green-500/15 bg-mineral-green-50/50"
                    />
                  </div>

                  <transition name="fade">
                    <div
                      v-if="passwordMessage"
                      class="flex items-center gap-2.5 text-sm rounded-xl px-4 py-3 border"
                      :class="passwordMessage.ok
                        ? 'bg-green-50 text-green-700 border-green-200'
                        : 'bg-red-50 text-red-600 border-red-200'"
                    >
                      <CheckCircle2 v-if="passwordMessage.ok" class="h-4 w-4 shrink-0" />
                      <AlertCircle v-else class="h-4 w-4 shrink-0" />
                      {{ passwordMessage.text }}
                    </div>
                  </transition>

                  <div class="flex justify-end pt-1">
                    <button
                      type="submit"
                      :disabled="passwordSaving"
                      class="relative overflow-hidden flex items-center gap-2
                             rounded-xl px-5 py-2.5 text-sm font-semibold text-white
                             bg-[linear-gradient(135deg,#1a4a2e_0%,#2d6e47_100%)]
                             shadow-[0_3px_12px_rgba(26,74,46,.35)]
                             transition hover:-translate-y-px hover:shadow-[0_5px_18px_rgba(26,74,46,.45)]
                             active:scale-[.98]
                             disabled:opacity-60 disabled:translate-y-0 disabled:cursor-not-allowed"
                    >
                      <span class="absolute top-0 -left-full bottom-0 w-1/2 skew-x-[-20deg]
                                   bg-[linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent)]
                                   animate-[shimmerBtn_3s_ease-in-out_infinite] pointer-events-none" />
                      <Loader2 v-if="passwordSaving" class="h-4 w-4 animate-spin" />
                      Cambiar contraseña
                    </button>
                  </div>
                </form>
              </div>

              <!-- ── TAB: Roles y Permisos ── -->
              <div v-else-if="activeTab === 'roles'" class="p-6 flex flex-col gap-6">
                <div class="mb-1">
                  <h3 class="font-['Playfair_Display',serif] text-lg font-bold text-mineral-green-950">
                    Roles y Permisos
                  </h3>
                  <p class="text-xs text-mineral-green-400 mt-0.5">Administra los privilegios de acceso del sistema</p>
                </div>

                <div v-if="rpStore.loading" class="flex items-center justify-center py-12">
                  <Loader2 class="h-6 w-6 animate-spin text-mineral-green-400" />
                </div>

                <template v-else>

                  <!-- Warning admin -->
                  <div
                    v-if="selectedRol?.nombre?.toLowerCase().includes('admin')"
                    class="flex items-start gap-3 rounded-xl border border-amber-200
                           bg-amber-50 px-4 py-3.5 text-sm text-amber-800"
                  >
                    <AlertCircle class="h-4 w-4 shrink-0 mt-0.5 text-amber-500" />
                    <span>
                      Se recomienda un sólo usuario con rol administrador, cualquier usuario con el rol
                      puede <strong>crear/editar/eliminar</strong> otras cuentas y editar sus privilegios.
                    </span>
                  </div>

                  <!-- Selector de rol -->
                  <div class="rounded-xl border border-mineral-green-100 bg-mineral-green-50/50 p-4">
                    <p class="text-[.7rem] font-semibold tracking-[.08em] uppercase
                               text-mineral-green-400 mb-3">Perfil del usuario</p>
                    <div class="flex items-center gap-4">
                      <span class="text-sm font-medium text-mineral-green-700 shrink-0 w-10 text-right">Rol</span>
                      <Select :model-value="selectedRolId" @update:model-value="onRolChange" class="flex-1">
                        <SelectTrigger class="rounded-xl border-mineral-green-200 bg-white
                                              focus:ring-2 focus:ring-mineral-green-500/15">
                          <SelectValue placeholder="Sin rol asignado" />
                        </SelectTrigger>
                        <SelectContent class="rounded-xl">
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
                    <p class="text-xs text-mineral-green-400 mt-2 pl-14">
                      El rol determina los privilegios generales que tendrá el usuario.
                    </p>
                  </div>

                  <div class="h-px bg-mineral-green-100" />

                  <!-- Permisos agrupados -->
                  <template v-if="selectedRol">
                    <div
                      v-for="(grupo, label) in permisosAgrupados"
                      :key="label"
                      class="flex flex-col gap-0"
                    >
                      <!-- Cabecera de grupo -->
                      <div class="flex items-center gap-2 mb-3">
                        <span class="flex h-6 w-6 items-center justify-center rounded-lg
                                     bg-mineral-green-100">
                          <KeyRound class="h-3 w-3 text-mineral-green-600" />
                        </span>
                        <h4 class="text-sm font-semibold text-mineral-green-800">
                          Privilegios de {{ (label as string).toLowerCase() }}
                        </h4>
                        <div class="flex-1 h-px bg-mineral-green-100" />
                      </div>

                      <!-- Filas de permiso -->
                      <div class="rounded-xl border border-mineral-green-100 overflow-hidden mb-5">
                        <div
                          v-for="(permiso, idx) in grupo"
                          :key="permiso.id"
                          :class="[
                            'grid grid-cols-[160px_56px_1fr] items-center gap-3 px-4 py-3 transition-colors',
                            'hover:bg-mineral-green-50/60',
                            idx < grupo.length - 1 ? 'border-b border-mineral-green-100' : '',
                          ]"
                        >
                          <span class="text-sm text-right text-mineral-green-600 font-medium leading-tight pr-1">
                            {{ permiso.nombre }}
                          </span>
                          <div class="flex justify-center">
                            <Switch
                              :checked="activePermisoIds.has(permiso.id)"
                              @update:checked="togglePermiso(permiso.id, $event)"
                              class="data-[state=checked]:bg-mineral-green-600"
                            />
                          </div>
                          <span class="text-xs text-mineral-green-400 leading-snug">
                            {{ permiso.descripcion }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </template>

                  <div v-else class="rounded-xl border border-dashed border-mineral-green-200
                                     bg-mineral-green-50/30 py-10 text-center">
                    <KeyRound class="h-8 w-8 text-mineral-green-300 mx-auto mb-2" />
                    <p class="text-sm text-mineral-green-400">Selecciona un rol para ver y editar sus permisos.</p>
                  </div>

                  <!-- Mensaje resultado -->
                  <transition name="fade">
                    <div
                      v-if="rolesMessage"
                      class="flex items-center gap-2.5 text-sm rounded-xl px-4 py-3 border"
                      :class="rolesMessage.ok
                        ? 'bg-green-50 text-green-700 border-green-200'
                        : 'bg-red-50 text-red-600 border-red-200'"
                    >
                      <CheckCircle2 v-if="rolesMessage.ok" class="h-4 w-4 shrink-0" />
                      <AlertCircle v-else class="h-4 w-4 shrink-0" />
                      {{ rolesMessage.text }}
                    </div>
                  </transition>

                  <!-- Acciones -->
                  <div class="flex items-center justify-between gap-3 pt-1">
                    <button
                      type="button"
                      :disabled="!selectedRolId || rpStore.saving"
                      @click="saveRolUsuario"
                      class="flex items-center gap-2 rounded-xl border border-mineral-green-200
                             bg-white px-4 py-2.5 text-sm font-medium text-mineral-green-700
                             shadow-sm transition
                             hover:bg-mineral-green-50 hover:border-mineral-green-300
                             disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Loader2 v-if="rpStore.saving" class="h-4 w-4 animate-spin" />
                      <ShieldCheck v-else class="h-4 w-4" />
                      Asignar rol al usuario
                    </button>

                    <button
                      type="button"
                      :disabled="!selectedRol || rpStore.saving"
                      @click="saveRolPermisos"
                      class="relative overflow-hidden flex items-center gap-2
                             rounded-xl px-4 py-2.5 text-sm font-semibold text-white
                             bg-[linear-gradient(135deg,#1a4a2e_0%,#2d6e47_100%)]
                             shadow-[0_3px_12px_rgba(26,74,46,.3)]
                             transition hover:-translate-y-px hover:shadow-[0_5px_18px_rgba(26,74,46,.4)]
                             active:scale-[.98]
                             disabled:opacity-50 disabled:translate-y-0 disabled:cursor-not-allowed"
                    >
                      <span class="absolute top-0 -left-full bottom-0 w-1/2 skew-x-[-20deg]
                                   bg-[linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent)]
                                   animate-[shimmerBtn_3s_ease-in-out_infinite] pointer-events-none" />
                      <Loader2 v-if="rpStore.saving" class="h-4 w-4 animate-spin" />
                      <KeyRound v-else class="h-4 w-4" />
                      Guardar permisos del rol
                    </button>
                  </div>
                </template>
              </div>

            </div><!-- /tarjeta derecha -->
          </div>
        </template>
      </main>
    </SidebarInset>
  </SidebarProvider>
</template>

<style scoped>
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: .35; }
}
@keyframes shimmerBtn {
  0%   { left: -100%; }
  60%  { left: 160%; }
  100% { left: 160%; }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>