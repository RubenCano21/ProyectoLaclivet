<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  Mail, Lock, LogIn, Loader2, AlertCircle,
  PawPrint, FlaskConical, Stethoscope, ClipboardList, Eye, EyeOff,
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const showPassword = ref(false)

async function handleLogin() {
  const ok = await auth.login(email.value, password.value)
  if (ok) {
    router.push({ name: 'dashboard' })
  }
}
</script>

<template>
  <div class="min-h-screen flex items-stretch">

    <!-- ── Panel izquierdo ── -->
    <div class="hidden lg:flex lg:w-[55%] relative flex-col overflow-hidden bg-linear-to-br from-mineral-green-800 via-mineral-green-700 to-mineral-green-950">

      <!-- Fondo decorativo -->
      <div class="pointer-events-none absolute -top-24 -left-24 w-96 h-96 rounded-full bg-white/5 blur-3xl" />
      <div class="pointer-events-none absolute bottom-0 right-0 w-md h-112 rounded-full bg-mineral-green-950/60 blur-3xl" />

      <div class="relative z-10 flex flex-col justify-between h-full p-12 text-white">

        <!-- Logo superior -->
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-white/15 backdrop-blur-sm border border-white/20">
            <PawPrint class="w-5 h-5 text-white" />
          </div>
          <span class="font-bold text-lg tracking-wide">LaClivet</span>
        </div>

        <!-- Ilustración + texto central -->
        <div class="flex flex-col items-center text-center space-y-6">
          <img
            src="/lab-dog.svg"
            alt="Laboratorio clínico veterinario"
            class="w-64 h-64 drop-shadow-2xl select-none"
            draggable="false"
          />
          <div class="space-y-2">
            <h2 class="text-4xl font-extrabold tracking-tight leading-tight">
              Laboratorio<br />Clínico Veterinario
            </h2>
            <p class="text-mineral-green-200 text-base leading-relaxed max-w-xs mx-auto">
              Diagnósticos precisos, historial clínico y seguimiento integral para el cuidado de tus pacientes.
            </p>
          </div>

          <!-- Badges de características -->
          <div class="flex flex-wrap justify-center gap-2 pt-2">
            <span class="inline-flex items-center gap-1.5 rounded-full bg-white/10 border border-white/15 px-3 py-1 text-xs font-medium backdrop-blur-sm">
              <Stethoscope class="w-3.5 h-3.5" /> Pacientes
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-full bg-white/10 border border-white/15 px-3 py-1 text-xs font-medium backdrop-blur-sm">
              <FlaskConical class="w-3.5 h-3.5" /> Laboratorio
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-full bg-white/10 border border-white/15 px-3 py-1 text-xs font-medium backdrop-blur-sm">
              <ClipboardList class="w-3.5 h-3.5" /> Citas
            </span>
          </div>
        </div>

        <!-- Footer -->
        <p class="text-xs text-mineral-green-400">© 2026 LaClivet · Todos los derechos reservados</p>
      </div>
    </div>

    <!-- ── Panel derecho – formulario ── -->
    <div class="flex flex-1 items-center justify-center bg-white px-6 py-12 sm:px-10 lg:px-16">
      <div class="w-full max-w-md">

        <!-- Logo móvil -->
        <div class="mb-8 flex items-center gap-2 lg:hidden">
          <div class="flex items-center justify-center w-9 h-9 rounded-xl bg-mineral-green-600 text-white">
            <PawPrint class="w-5 h-5" />
          </div>
          <span class="font-bold text-mineral-green-800 text-lg">LaClivet</span>
        </div>

        <!-- Encabezado -->
        <div class="mb-8 space-y-1">
          <h1 class="text-3xl font-extrabold text-mineral-green-950 tracking-tight">Iniciar sesión</h1>
          <p class="text-sm text-mineral-green-500">Accede al sistema de laboratorio clínico veterinario</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">

          <!-- Email -->
          <div class="space-y-1.5">
            <label for="email" class="block text-sm font-medium text-mineral-green-800">
              Correo electrónico
            </label>
            <div class="relative">
              <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400">
                <Mail class="w-4 h-4" />
              </span>
              <input
                id="email"
                v-model="email"
                type="email"
                autocomplete="email"
                required
                placeholder="ejemplo@laclivet.com"
                class="w-full rounded-xl border border-mineral-green-200 bg-mineral-green-50/50 py-3 pl-10 pr-4 text-sm text-mineral-green-950 placeholder-mineral-green-400 shadow-xs transition focus:border-mineral-green-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-mineral-green-500/25"
              />
            </div>
          </div>

          <!-- Contraseña -->
          <div class="space-y-1.5">
            <label for="password" class="block text-sm font-medium text-mineral-green-800">
              Contraseña
            </label>
            <div class="relative">
              <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400">
                <Lock class="w-4 h-4" />
              </span>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                placeholder="••••••••"
                class="w-full rounded-xl border border-mineral-green-200 bg-mineral-green-50/50 py-3 pl-10 pr-11 text-sm text-mineral-green-950 placeholder-mineral-green-400 shadow-xs transition focus:border-mineral-green-500 focus:bg-white focus:outline-none focus:ring-2 focus:ring-mineral-green-500/25"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 flex items-center pr-3.5 text-mineral-green-400 hover:text-mineral-green-700 transition"
                tabindex="-1"
                :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
              >
                <EyeOff v-if="showPassword" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Error -->
          <transition name="fade">
            <div
              v-if="auth.error"
              class="flex items-start gap-2.5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
            >
              <AlertCircle class="mt-0.5 w-4 h-4 shrink-0" />
              <span>{{ auth.error }}</span>
            </div>
          </transition>

          <!-- Botón -->
          <button
            type="submit"
            :disabled="auth.loading"
            class="mt-2 flex w-full items-center justify-center gap-2 rounded-xl bg-mineral-green-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-mineral-green-700 active:scale-[.98] focus:outline-none focus:ring-2 focus:ring-mineral-green-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Loader2 v-if="auth.loading" class="w-4 h-4 animate-spin" />
            <LogIn v-else class="w-4 h-4" />
            {{ auth.loading ? 'Verificando...' : 'Ingresar al sistema' }}
          </button>
        </form>

        <!-- Footer -->
        <p class="mt-8 text-center text-xs text-mineral-green-400">
          Acceso restringido · Solo personal autorizado
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
