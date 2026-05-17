<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Mail, Lock, LogIn, Loader2, AlertCircle } from 'lucide-vue-next'

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
    <!-- Left panel – decorative -->
    <div
      class="hidden lg:flex lg:w-1/2 bg-linear-to-br from-mineral-green-600 to-mineral-green-950 flex-col items-center justify-center p-12 text-white"
    >
      <div class="max-w-md text-center space-y-6">
        <div
          class="w-20 h-20 bg-white/20 rounded-3xl flex items-center justify-center mx-auto backdrop-blur-sm"
        >
          <LogIn class="w-10 h-10 text-white" />
        </div>
        <h2 class="text-4xl font-bold tracking-tight">Bienvenido</h2>
        <p class="text-mineral-green-100 text-lg leading-relaxed">
          Inicia sesión para acceder a tu cuenta y gestionar tus recursos.
        </p>
      </div>
    </div>

    <!-- Right panel – form -->
    <div class="flex flex-1 items-center justify-center bg-mineral-green-50 px-4 py-12 sm:px-8 lg:px-16">
      <div class="w-full max-w-lg">
        <!-- Logo / heading -->
        <div class="mb-10 text-center">
          <span
            class="inline-flex items-center gap-2 text-mineral-green-600 font-bold text-2xl tracking-tight"
          >
            <LogIn class="w-6 h-6" />
            LaClivet
          </span>
          <h1 class="mt-4 text-3xl font-extrabold text-mineral-green-950">Iniciar sesión</h1>
          <p class="mt-1 text-sm text-mineral-green-500">Ingresa tus credenciales para continuar</p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">
          <!-- Email -->
          <div class="space-y-1">
            <label for="email" class="block text-sm font-medium text-mineral-green-800">Correo electrónico</label>
            <div class="relative">
              <span
                class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-mineral-green-400"
              >
                <Mail class="w-4 h-4" />
              </span>
              <input
                id="email"
                v-model="email"
                type="email"
                autocomplete="email"
                required
                placeholder="tu@correo.com"
                class="w-full rounded-xl border border-mineral-green-200 bg-white py-2.5 pl-10 pr-4 text-sm text-mineral-green-950 placeholder-mineral-green-400 shadow-sm transition focus:border-mineral-green-500 focus:outline-none focus:ring-2 focus:ring-mineral-green-500/30"
              />
            </div>
          </div>

          <!-- Password -->
          <div class="space-y-1">
            <label for="password" class="block text-sm font-medium text-mineral-green-800">Contraseña</label>
            <div class="relative">
              <span
                class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-mineral-green-400"
              >
                <Lock class="w-4 h-4" />
              </span>
              <input
                id="password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                required
                placeholder="••••••••"
                class="w-full rounded-xl border border-mineral-green-200 bg-white py-2.5 pl-10 pr-10 text-sm text-mineral-green-950 placeholder-mineral-green-400 shadow-sm transition focus:border-mineral-green-500 focus:outline-none focus:ring-2 focus:ring-mineral-green-500/30"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 flex items-center pr-3 text-mineral-green-400 hover:text-mineral-green-700 transition"
                tabindex="-1"
              >
                <svg
                  v-if="showPassword"
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M13.875 18.825A10.05 10.05 0 0112 19c-5 0-9-4-9-7s4-7 9-7a9.97 9.97 0 015.388 1.582M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18" />
                </svg>
                <svg
                  v-else
                  xmlns="http://www.w3.org/2000/svg"
                  class="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                  />
                </svg>
              </button>
            </div>
          </div>

          <!-- Error alert -->
          <transition name="fade">
            <div
              v-if="auth.error"
              class="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600"
            >
              <AlertCircle class="mt-0.5 w-4 h-4 shrink-0" />
              <span>{{ auth.error }}</span>
            </div>
          </transition>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="auth.loading"
            class="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-mineral-green-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-mineral-green-700 focus:outline-none focus:ring-2 focus:ring-mineral-green-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <Loader2 v-if="auth.loading" class="w-4 h-4 animate-spin" />
            <LogIn v-else class="w-4 h-4" />
            {{ auth.loading ? 'Ingresando...' : 'Ingresar' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.2s ease,
    transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
