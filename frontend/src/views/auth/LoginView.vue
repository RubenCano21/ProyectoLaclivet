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
  if (ok) router.push({ name: 'dashboard' })
}
</script>

<template>
  <!-- Playfair Display + DM Sans -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap"
    rel="stylesheet" />

  <div class="min-h-screen flex items-stretch font-['DM_Sans',sans-serif]">

    <!-- ══ Panel izquierdo ══ -->
    <div class="hidden lg:flex lg:w-[55%] relative flex-col overflow-hidden
                bg-[radial-gradient(ellipse_at_top_left,#1a4a2e_0%,#0f2e1e_50%,#0a1f13_100%)]">

      <!-- Grid pattern -->
      <div class="absolute inset-0 pointer-events-none
                  bg-[linear-gradient(rgba(255,255,255,.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.04)_1px,transparent_1px)]
                  bg-size-[40px_40px]" />

      <!-- Orbes -->
      <div class="absolute -top-28 -left-28 w-96 h-96 rounded-full pointer-events-none
                  bg-[radial-gradient(circle,rgba(134,239,172,.14)_0%,transparent_70%)]
                  blur-3xl animate-[drift_14s_ease-in-out_infinite_alternate]" />
      <div class="absolute -bottom-16 -right-16 w-72 h-72 rounded-full pointer-events-none
                  bg-[radial-gradient(circle,rgba(180,220,130,.09)_0%,transparent_70%)]
                  blur-3xl animate-[drift_10s_ease-in-out_infinite_alternate-reverse]" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none
                  w-48 h-48 rounded-full
                  bg-[radial-gradient(circle,rgba(251,191,36,.07)_0%,transparent_70%)]
                  blur-2xl animate-[pulseOrb_6s_ease-in-out_infinite]" />

      <!-- Partículas -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <span v-for="n in 16" :key="n" class="absolute w-0.75 h-0.75 rounded-full bg-white/20
                     animate-[floatUp_8s_ease-in-out_infinite]"
          :style="`left:${n * 6}%;top:${n * 5 + 8}%;animation-delay:-${n * 0.5}s;animation-duration:${7 + n * 0.4}s`" />
      </div>

      <!-- Contenido -->
      <div class="relative z-10 flex flex-col justify-between h-full p-12 text-white">

        <!-- Logo + badge -->
        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-10 h-10 rounded-xl
                      bg-white/10 border border-white/20 backdrop-blur-sm">
            <PawPrint class="w-5 h-5 text-white" />
          </div>
          <span class="font-extrabold text-lg tracking-widest">LACLIVET</span>
          <div class="ml-auto flex items-center gap-1.5 text-[.68rem] font-medium
                      bg-green-400/10 border border-green-400/25 text-green-300
                      rounded-full px-3 py-1">
            <span class="w-1.5 h-1.5 rounded-full bg-green-400
                         shadow-[0_0_6px_#4ade80] animate-[blink_2s_ease-in-out_infinite]" />
            Sistema activo
          </div>
        </div>

        <!-- Hero -->
        <div class="flex flex-col items-center text-center gap-7">

          <!-- Foto con anillos orbitantes -->
          <div class="relative w-52 h-52 animate-[heroIn_1s_ease_both]">
            <img src="@/assets/images/perrolab.jpeg" alt="Laboratorio clínico veterinario" class="w-full h-full rounded-full object-cover object-center
                     opacity-60 border-2 border-white/15
                     filter-[saturate(.9)_brightness(.95)]" draggable="false" />
            <span class="absolute -inset-3 rounded-full border border-white/10
                         pointer-events-none animate-[spinRing_25s_linear_infinite]" />
            <span class="absolute -inset-6 rounded-full border border-dashed border-white/[.07]
                         pointer-events-none animate-[spinRing_35s_linear_infinite_reverse]" />
          </div>

          <!-- Texto -->
          <div class="space-y-2 animate-[fadeUp_.8s_.2s_ease_both]">
            <h2 class="font-['Playfair_Display',serif] text-[2.3rem] font-extrabold leading-[1.15] tracking-tight">
              Laboratorio Clínico<br />
              <em class="text-green-200 not-italic">Veterinario UAGRM</em>
            </h2>
            <p class="text-white/50 text-sm leading-relaxed max-w-[26ch] mx-auto">
              Diagnósticos precisos, historial clínico y seguimiento integral para el cuidado de tus pacientes.
            </p>
          </div>

          <!-- Badges -->
          <div class="flex flex-wrap justify-center gap-2 animate-[fadeUp_.8s_.45s_ease_both]">
            <span class="inline-flex items-center gap-1.5 rounded-full
                         bg-white/[.07] border border-white/13
                         px-3.5 py-1.5 text-xs font-medium backdrop-blur-sm
                         transition hover:bg-white/13">
              <Stethoscope class="w-3.5 h-3.5" /> Pacientes
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-full
                         bg-white/[.07] border border-white/13
                         px-3.5 py-1.5 text-xs font-medium backdrop-blur-sm
                         transition hover:bg-white/13">
              <FlaskConical class="w-3.5 h-3.5" /> Laboratorio
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-full
                         bg-white/[.07] border border-white/13
                         px-3.5 py-1.5 text-xs font-medium backdrop-blur-sm
                         transition hover:bg-white/13">
              <ClipboardList class="w-3.5 h-3.5" /> Citas
            </span>
          </div>
        </div>

        <!-- Footer -->
        <p class="text-[.68rem] text-white/25">© 2026 LaClivet · Todos los derechos reservados</p>
      </div>
    </div>

    <!-- ══ Panel derecho ══ -->
    <div class="flex flex-1 items-center justify-center
                bg-[#f4f7f4] px-6 py-12 sm:px-10 lg:px-16 relative overflow-hidden">

      <!-- Ruido sutil -->
      <div class="absolute inset-0 pointer-events-none opacity-40
                  bg-[url('data:image/svg+xml,%3Csvg%20viewBox%3D%220%200%20256%20256%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cfilter%20id%3D%22n%22%3E%3CfeTurbulence%20type%3D%22fractalNoise%22%20baseFrequency%3D%22.75%22%20numOctaves%3D%224%22%20stitchTiles%3D%22stitch%22%2F%3E%3C%2Ffilter%3E%3Crect%20width%3D%22100%25%22%20height%3D%22100%25%22%20filter%3D%22url(%23n)%22%20opacity%3D%22.05%22%2F%3E%3C%2Fsvg%3E')]
                  bg-size-[180px]" />

      <!-- Tarjeta -->
      <div class="relative z-10 w-full max-w-105 bg-white rounded-[1.6rem] p-8 sm:p-10
                  shadow-[0_1px_3px_rgba(0,0,0,.05),0_8px_32px_rgba(0,0,0,.09),0_0_0_1px_rgba(26,74,46,.06)]
                  animate-[cardIn_.7s_cubic-bezier(.22,.61,.36,1)_both]
                  before:absolute before:top-0 before:left-8 before:right-8 before:h-0.75
                  before:rounded-b-full
                  before:bg-[linear-gradient(90deg,#1a4a2e,#4ade80,#1a4a2e)]
                  before:bg-size-[200%_100%]
                  before:animate-[shimmerLine_4s_ease_infinite]">

        <!-- Logo móvil -->
        <div class="mb-7 flex items-center gap-2 lg:hidden">
          <div class="flex items-center justify-center w-9 h-9 rounded-xl bg-mineral-green-700 text-white">
            <PawPrint class="w-5 h-5" />
          </div>
          <span class="font-extrabold text-mineral-green-900 text-lg tracking-wide">LACLIVET</span>
        </div>

        <!-- Header -->
        <div class="mb-7">
          <p class="text-[.68rem] font-semibold tracking-[.12em] uppercase text-green-500 mb-1">
            Bienvenido de vuelta
          </p>
          <h1 class="font-['Playfair_Display',serif] text-[1.9rem] font-extrabold
                     text-mineral-green-950 leading-[1.15] mb-1">
            Iniciar sesión
          </h1>
          <p class="text-[.8rem] text-mineral-green-500">
            Accede al sistema de laboratorio clínico veterinario
          </p>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-5">

          <!-- Email -->
          <div class="space-y-1.5">
            <label for="email" class="block text-[.8rem] font-semibold text-mineral-green-800">
              Correo electrónico
            </label>
            <div class="relative group">
              <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5
                           text-mineral-green-400 transition-colors
                           group-focus-within:text-mineral-green-700">
                <Mail class="w-4 h-4" />
              </span>
              <input id="email" v-model="email" type="email" autocomplete="email" required
                placeholder="ejemplo@laclivet.com" class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200
                       bg-mineral-green-50/60 py-3 pl-10 pr-4
                       text-sm text-mineral-green-950 placeholder-mineral-green-400/70
                       font-['DM_Sans',sans-serif]
                       transition
                       focus:border-mineral-green-600 focus:bg-white
                       focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15
                       focus:shadow-[0_0_18px_rgba(74,222,128,.14)]" />
            </div>
          </div>

          <!-- Contraseña -->
          <div class="space-y-1.5">
            <label for="password" class="block text-[.8rem] font-semibold text-mineral-green-800">
              Contraseña
            </label>
            <div class="relative group">
              <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5
                           text-mineral-green-400 transition-colors
                           group-focus-within:text-mineral-green-700">
                <Lock class="w-4 h-4" />
              </span>
              <input id="password" v-model="password" :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password" required placeholder="••••••••" class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200
                       bg-mineral-green-50/60 py-3 pl-10 pr-11
                       text-sm text-mineral-green-950 placeholder-mineral-green-400/70
                       font-['DM_Sans',sans-serif]
                       transition
                       focus:border-mineral-green-600 focus:bg-white
                       focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15
                       focus:shadow-[0_0_18px_rgba(74,222,128,.14)]" />
              <button type="button" @click="showPassword = !showPassword" class="absolute inset-y-0 right-0 flex items-center pr-3.5
                       text-mineral-green-400 hover:text-mineral-green-700
                       transition-colors bg-transparent border-none cursor-pointer" tabindex="-1"
                :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'">
                <EyeOff v-if="showPassword" class="w-4 h-4" />
                <Eye v-else class="w-4 h-4" />
              </button>
            </div>
          </div>

          <!-- Error -->
          <transition name="fade">
            <div v-if="auth.error" class="flex items-start gap-2.5 rounded-[.875rem]
                     border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              <AlertCircle class="mt-0.5 w-4 h-4 shrink-0" />
              <span>{{ auth.error }}</span>
            </div>
          </transition>

          <!-- Botón submit -->
          <button type="submit" :disabled="auth.loading" class="relative overflow-hidden mt-1
                   flex w-full items-center justify-center gap-2
                   rounded-[.875rem]
                   bg-[linear-gradient(135deg,#1a4a2e_0%,#2d6e47_100%)]
                   px-4 py-3.5 text-sm font-semibold text-white
                   font-['DM_Sans',sans-serif]
                   shadow-[0_4px_14px_rgba(26,74,46,.4)]
                   transition
                   hover:-translate-y-px hover:shadow-[0_6px_20px_rgba(26,74,46,.5)]
                   active:scale-[.98]
                   focus:outline-none focus:ring-2 focus:ring-mineral-green-500 focus:ring-offset-2
                   disabled:cursor-not-allowed disabled:opacity-60
                   disabled:translate-y-0 disabled:shadow-none">
            <!-- Shimmer sweep -->
            <span class="absolute top-0 -left-full bottom-0 w-3/5 pointer-events-none
                         skew-x-[-20deg]
                         bg-[linear-gradient(90deg,transparent,rgba(255,255,255,.15),transparent)]
                         animate-[shimmerBtn_3s_ease-in-out_infinite]" />
            <Loader2 v-if="auth.loading" class="w-4 h-4 animate-spin" />
            <LogIn v-else class="w-4 h-4" />
            {{ auth.loading ? 'Verificando...' : 'Ingresar al sistema' }}
          </button>
        </form>

        <!-- Divider decorativo -->
        <div class="flex items-center gap-3 mt-7">
          <span class="flex-1 h-px bg-linear-to-r from-transparent to-mineral-green-100" />
          <PawPrint class="w-3 h-3 text-mineral-green-200" />
          <span class="flex-1 h-px bg-linear-to-l from-transparent to-mineral-green-100" />
        </div>

        <!-- Footer -->
        <div
          class="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-700 rounded-xl p-5 max-w-sm mx-auto mt-4">

          <div
            class="inline-flex items-center gap-1.5 bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 text-xs font-medium px-2.5 py-1 rounded-md mb-4">
            Usuario de prueba
          </div>
          <div class="flex items-center gap-2.5 py-2.5 border-t border-zinc-100 dark:border-zinc-800">
            <span class="text-xs text-zinc-400 w-20 shrink-0">Correo</span>
            <span
              class="text-xs text-zinc-700 dark:text-zinc-300 flex-1 truncate">admin@production.laclivet.com</span>
          </div>

          <div class="flex items-center gap-2.5 py-2.5 border-t border-zinc-100 dark:border-zinc-800">
            <span class="text-xs text-zinc-400 w-20 shrink-0">Contraseña</span>
            <span class="text-xs text-zinc-700 dark:text-zinc-300 flex-1 tracking-widest">admin123</span>
          </div>
        </div>
        <p class="mt-3 text-center text-[.68rem] text-mineral-green-300 tracking-wide">
          Acceso restringido · Solo personal autorizado
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Keyframes: declarados aquí, invocados via clases arbitrarias [animation:...] de Tailwind */

@keyframes drift {
  from {
    transform: translate(0, 0) scale(1);
  }

  to {
    transform: translate(28px, 18px) scale(1.08);
  }
}

@keyframes pulseOrb {

  0%,
  100% {
    opacity: .4;
    transform: translate(-50%, -50%) scale(1);
  }

  50% {
    opacity: .75;
    transform: translate(-50%, -50%) scale(1.15);
  }
}

@keyframes floatUp {
  0% {
    transform: translateY(0) scale(1);
    opacity: .55;
  }

  50% {
    transform: translateY(-38px) scale(1.4);
    opacity: 1;
  }

  100% {
    transform: translateY(-76px) scale(.8);
    opacity: 0;
  }
}

@keyframes blink {

  0%,
  100% {
    opacity: 1;
  }

  50% {
    opacity: .3;
  }
}

@keyframes heroIn {
  from {
    opacity: 0;
    transform: scale(.86) translateY(18px);
  }

  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@keyframes spinRing {
  from {
    transform: rotate(0deg);
  }

  to {
    transform: rotate(360deg);
  }
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(22px) scale(.97);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes shimmerLine {
  0% {
    background-position: 100% 0;
  }

  100% {
    background-position: -100% 0;
  }
}

@keyframes shimmerBtn {
  0% {
    left: -100%;
  }

  60% {
    left: 160%;
  }

  100% {
    left: 160%;
  }
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