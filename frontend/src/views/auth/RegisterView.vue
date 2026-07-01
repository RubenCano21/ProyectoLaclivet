<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RegistroForm } from '@/stores/auth'
import {
  Mail, Lock, UserPlus, Loader2, AlertCircle, CheckCircle2,
  PawPrint, FlaskConical, Stethoscope, ClipboardList, Eye, EyeOff,
  User, IdCard, Phone, MapPin, CalendarDays, KeyRound, Info,
} from 'lucide-vue-next'

const auth = useAuthStore()
const router = useRouter()

const form = ref({
  first_name: '',
  last_name: '',
  email: '',
  ci: '',
  telefono: '',
  direccion: '',
  fecha_nacimiento: '',
})

// Por defecto el sistema genera una contraseña temporal (= CI del usuario).
// El usuario puede optar por definir la suya propia en su lugar.
const definirPasswordPropia = ref(false)
const password = ref('')
const password2 = ref('')
const showPassword = ref(false)
const showPassword2 = ref(false)

const errorLocal = ref<string | null>(null)
const enviado = ref(false)

const passwordsCoinciden = computed(
  () => !definirPasswordPropia.value || (password.value.length > 0 && password.value === password2.value)
)

const formularioValido = computed(() => {
  const base = form.value.first_name.trim() && form.value.last_name.trim() &&
    form.value.email.trim() && form.value.ci.trim()
  if (!base) return false
  if (definirPasswordPropia.value) {
    return password.value.length >= 8 && password.value === password2.value
  }
  return true
})

async function handleRegistro() {
  errorLocal.value = null

  if (definirPasswordPropia.value && password.value !== password2.value) {
    errorLocal.value = 'Las contraseñas no coinciden.'
    return
  }

  const payload: RegistroForm = {
    email: form.value.email,
    first_name: form.value.first_name,
    last_name: form.value.last_name,
    ci: form.value.ci,
    telefono: form.value.telefono || undefined,
    direccion: form.value.direccion || undefined,
    fecha_nacimiento: form.value.fecha_nacimiento || undefined,
  }

  if (definirPasswordPropia.value) {
    payload.password = password.value
    payload.password2 = password2.value
  }

  const resultado = await auth.registro(payload)

  if (resultado.ok) {
    enviado.value = true
    setTimeout(() => {
      if (resultado.debeCambiarPassword) {
        router.push({ name: 'cambiar-password-inicial' })
      } else {
        router.push({ name: 'dashboard' })
      }
    }, 1400)
  } else {
    errorLocal.value = resultado.error ?? 'No se pudo completar el registro.'
  }
}
</script>

<template>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link
    href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,800;1,700&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap"
    rel="stylesheet" />

  <div class="min-h-screen flex items-stretch font-['DM_Sans',sans-serif]">

    <!-- ══ Panel izquierdo (idéntico al login, coherencia de marca) ══ -->
    <div
      class="hidden lg:flex lg:w-[45%] relative flex-col overflow-hidden
                bg-[radial-gradient(ellipse_at_top_left,#1a4a2e_0%,#0f2e1e_50%,#0a1f13_100%)]">

      <div
        class="absolute inset-0 pointer-events-none
                  bg-[linear-gradient(rgba(255,255,255,.04)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,.04)_1px,transparent_1px)]
                  bg-size-[40px_40px]" />

      <div
        class="absolute -top-28 -left-28 w-96 h-96 rounded-full pointer-events-none
                  bg-[radial-gradient(circle,rgba(134,239,172,.14)_0%,transparent_70%)]
                  blur-3xl animate-[drift_14s_ease-in-out_infinite_alternate]" />
      <div
        class="absolute -bottom-16 -right-16 w-72 h-72 rounded-full pointer-events-none
                  bg-[radial-gradient(circle,rgba(180,220,130,.09)_0%,transparent_70%)]
                  blur-3xl animate-[drift_10s_ease-in-out_infinite_alternate-reverse]" />

      <div class="absolute inset-0 pointer-events-none" aria-hidden="true">
        <span
          v-for="n in 16" :key="n" class="absolute w-0.75 h-0.75 rounded-full bg-white/20
                     animate-[floatUp_8s_ease-in-out_infinite]"
          :style="`left:${n * 6}%;top:${n * 5 + 8}%;animation-delay:-${n * 0.5}s;animation-duration:${7 + n * 0.4}s`" />
      </div>

      <div class="relative z-10 flex flex-col justify-between h-full p-12 text-white">

        <div class="flex items-center gap-3">
          <div class="flex items-center justify-center w-10 h-10 rounded-xl bg-white/10 border border-white/20 backdrop-blur-sm">
            <PawPrint class="w-5 h-5 text-white" />
          </div>
          <span class="font-extrabold text-lg tracking-widest">LACLIVET</span>
        </div>

        <div class="flex flex-col items-center text-center gap-7">
          <div class="relative w-40 h-40 animate-[heroIn_1s_ease_both]">
            <div
              class="w-full h-full rounded-full flex items-center justify-center
                        bg-white/6 border-2 border-white/15">
              <UserPlus class="w-14 h-14 text-green-200/70" />
            </div>
            <span class="absolute -inset-3 rounded-full border border-white/10 pointer-events-none animate-[spinRing_25s_linear_infinite]" />
            <span class="absolute -inset-6 rounded-full border border-dashed border-white/[.07] pointer-events-none animate-[spinRing_35s_linear_infinite_reverse]" />
          </div>

          <div class="space-y-2 animate-[fadeUp_.8s_.2s_ease_both]">
            <h2 class="font-['Playfair_Display',serif] text-[2.1rem] font-extrabold leading-[1.15] tracking-tight">
              Crea tu cuenta<br />
              <em class="text-green-200 not-italic">como propietario</em>
            </h2>
            <p class="text-white/50 text-sm leading-relaxed max-w-[28ch] mx-auto">
              Registra tus datos para dar seguimiento al historial clínico y resultados de tus mascotas.
            </p>
          </div>

          <div class="flex flex-wrap justify-center gap-2 animate-[fadeUp_.8s_.45s_ease_both]">
            <span class="inline-flex items-center gap-1.5 rounded-full bg-white/[.07] border border-white/13 px-3.5 py-1.5 text-xs font-medium backdrop-blur-sm">
              <Stethoscope class="w-3.5 h-3.5" /> Pacientes
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-full bg-white/[.07] border border-white/13 px-3.5 py-1.5 text-xs font-medium backdrop-blur-sm">
              <FlaskConical class="w-3.5 h-3.5" /> Laboratorio
            </span>
            <span class="inline-flex items-center gap-1.5 rounded-full bg-white/[.07] border border-white/13 px-3.5 py-1.5 text-xs font-medium backdrop-blur-sm">
              <ClipboardList class="w-3.5 h-3.5" /> Resultados
            </span>
          </div>
        </div>

        <p class="text-[.68rem] text-white/25">© 2026 LaClivet · Todos los derechos reservados</p>
      </div>
    </div>

    <!-- ══ Panel derecho ══ -->
    <div class="flex flex-1 items-center justify-center bg-[#f4f7f4] px-6 py-12 sm:px-10 lg:px-16 relative overflow-hidden">

      <div
        class="absolute inset-0 pointer-events-none opacity-40
                  bg-[url('data:image/svg+xml,%3Csvg%20viewBox%3D%220%200%20256%20256%22%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%3E%3Cfilter%20id%3D%22n%22%3E%3CfeTurbulence%20type%3D%22fractalNoise%22%20baseFrequency%3D%22.75%22%20numOctaves%3D%224%22%20stitchTiles%3D%22stitch%22%2F%3E%3C%2Ffilter%3E%3Crect%20width%3D%22100%25%22%20height%3D%22100%25%22%20filter%3D%22url(%23n)%22%20opacity%3D%22.05%22%2F%3E%3C%2Fsvg%3E')]
                  bg-size-[180px]" />

      <div
        class="relative z-10 w-full max-w-125 bg-white rounded-[1.6rem] p-8 sm:p-10
                  shadow-[0_1px_3px_rgba(0,0,0,.05),0_8px_32px_rgba(0,0,0,.09),0_0_0_1px_rgba(26,74,46,.06)]
                  animate-[cardIn_.7s_cubic-bezier(.22,.61,.36,1)_both]
                  before:absolute before:top-0 before:left-8 before:right-8 before:h-0.75
                  before:rounded-b-full
                  before:bg-[linear-gradient(90deg,#1a4a2e,#4ade80,#1a4a2e)]
                  before:bg-size-[200%_100%]
                  before:animate-[shimmerLine_4s_ease_infinite]">

        <div class="mb-7 flex items-center gap-2 lg:hidden">
          <div class="flex items-center justify-center w-9 h-9 rounded-xl bg-mineral-green-700 text-white">
            <PawPrint class="w-5 h-5" />
          </div>
          <span class="font-extrabold text-mineral-green-900 text-lg tracking-wide">LACLIVET</span>
        </div>

        <div class="mb-6">
          <p class="text-[.68rem] font-semibold tracking-[.12em] uppercase text-green-500 mb-1">
            Nuevo en LaClivet
          </p>
          <h1 class="font-['Playfair_Display',serif] text-[1.75rem] font-extrabold text-mineral-green-950 leading-[1.15] mb-1">
            Crear cuenta
          </h1>
          <p class="text-[.8rem] text-mineral-green-500">
            Completa tus datos para acceder al portal de propietarios
          </p>
        </div>

        <!-- Confirmación de éxito -->
        <transition name="fade">
          <div v-if="enviado" class="flex items-start gap-2.5 rounded-[.875rem] border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700 mb-5">
            <CheckCircle2 class="mt-0.5 w-4 h-4 shrink-0" />
            <span>Cuenta creada correctamente. Redirigiendo...</span>
          </div>
        </transition>

        <form v-if="!enviado" class="space-y-4" @submit.prevent="handleRegistro">

          <!-- Nombres / Apellidos -->
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <label for="first_name" class="block text-[.8rem] font-semibold text-mineral-green-800">Nombres</label>
              <div class="relative group">
                <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400 group-focus-within:text-mineral-green-700">
                  <User class="w-4 h-4" />
                </span>
                <input 
                    id="first_name" v-model="form.first_name" type="text" required placeholder="María"
                  class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200 bg-mineral-green-50/60 py-3 pl-10 pr-3 text-sm text-mineral-green-950 placeholder-mineral-green-400/70 transition focus:border-mineral-green-600 focus:bg-white focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15" />
              </div>
            </div>
            <div class="space-y-1.5">
              <label for="last_name" class="block text-[.8rem] font-semibold text-mineral-green-800">Apellidos</label>
              <input 
                id="last_name" v-model="form.last_name" type="text" required placeholder="Pérez"
                class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200 bg-mineral-green-50/60 py-3 px-3.5 text-sm text-mineral-green-950 placeholder-mineral-green-400/70 transition focus:border-mineral-green-600 focus:bg-white focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15" />
            </div>
          </div>

          <!-- Email -->
          <div class="space-y-1.5">
            <label for="email" class="block text-[.8rem] font-semibold text-mineral-green-800">Correo electrónico</label>
            <div class="relative group">
              <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400 group-focus-within:text-mineral-green-700">
                <Mail class="w-4 h-4" />
              </span>
              <input 
                id="email" v-model="form.email" type="email" autocomplete="email" required placeholder="ejemplo@laclivet.com"
                class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200 bg-mineral-green-50/60 py-3 pl-10 pr-4 text-sm text-mineral-green-950 placeholder-mineral-green-400/70 transition focus:border-mineral-green-600 focus:bg-white focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15" />
            </div>
          </div>

          <!-- CI / Teléfono -->
          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <label for="ci" class="block text-[.8rem] font-semibold text-mineral-green-800">Cédula de identidad</label>
              <div class="relative group">
                <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400 group-focus-within:text-mineral-green-700">
                  <IdCard class="w-4 h-4" />
                </span>
                <input 
                    id="ci" v-model="form.ci" type="text" required placeholder="1234567"
                  class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200 bg-mineral-green-50/60 py-3 pl-10 pr-3 text-sm text-mineral-green-950 placeholder-mineral-green-400/70 transition focus:border-mineral-green-600 focus:bg-white focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15" />
              </div>
            </div>
            <div class="space-y-1.5">
              <label for="telefono" class="block text-[.8rem] font-semibold text-mineral-green-800">Teléfono</label>
              <div class="relative group">
                <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400 group-focus-within:text-mineral-green-700">
                  <Phone class="w-4 h-4" />
                </span>
                <input 
                    id="telefono" v-model="form.telefono" type="tel" placeholder="70000000"
                  class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200 bg-mineral-green-50/60 py-3 pl-10 pr-3 text-sm text-mineral-green-950 placeholder-mineral-green-400/70 transition focus:border-mineral-green-600 focus:bg-white focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15" />
              </div>
            </div>
          </div>

          <!-- Dirección -->
          <div class="space-y-1.5">
            <label for="direccion" class="block text-[.8rem] font-semibold text-mineral-green-800">Dirección</label>
            <div class="relative group">
              <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400 group-focus-within:text-mineral-green-700">
                <MapPin class="w-4 h-4" />
              </span>
              <input 
                id="direccion" v-model="form.direccion" type="text" placeholder="Av. Cristo Redentor #123"
                class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200 bg-mineral-green-50/60 py-3 pl-10 pr-3 text-sm text-mineral-green-950 placeholder-mineral-green-400/70 transition focus:border-mineral-green-600 focus:bg-white focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15" />
            </div>
          </div>

          <!-- Fecha de nacimiento -->
          <div class="space-y-1.5">
            <label for="fecha_nacimiento" class="block text-[.8rem] font-semibold text-mineral-green-800">Fecha de nacimiento</label>
            <div class="relative group">
              <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400 group-focus-within:text-mineral-green-700">
                <CalendarDays class="w-4 h-4" />
              </span>
              <input 
                id="fecha_nacimiento" v-model="form.fecha_nacimiento" type="date"
                class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200 bg-mineral-green-50/60 py-3 pl-10 pr-3 text-sm text-mineral-green-950 transition focus:border-mineral-green-600 focus:bg-white focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15" />
            </div>
          </div>

          <!-- Divider -->
          <div class="flex items-center gap-3 pt-2">
            <span class="flex-1 h-px bg-mineral-green-100" />
            <span class="text-[.68rem] font-semibold uppercase tracking-wider text-mineral-green-400">Seguridad</span>
            <span class="flex-1 h-px bg-mineral-green-100" />
          </div>

          <!-- Toggle: elegir contraseña propia -->
          <label class="flex items-center gap-2.5 cursor-pointer select-none py-1">
            <input 
                v-model="definirPasswordPropia" type="checkbox"
              class="w-4 h-4 rounded border-mineral-green-300 text-mineral-green-700 focus:ring-mineral-green-500/30" />
            <span class="text-[.8rem] text-mineral-green-700">Quiero elegir mi propia contraseña</span>
          </label>

          <!-- Password fields (condicional) -->
          <div v-if="definirPasswordPropia" class="space-y-3 animate-[fadeUp_.3s_ease_both]">
            <div class="space-y-1.5">
              <label for="password" class="block text-[.8rem] font-semibold text-mineral-green-800">Contraseña</label>
              <div class="relative group">
                <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400 group-focus-within:text-mineral-green-700">
                  <Lock class="w-4 h-4" />
                </span>
                <input 
                    id="password" v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="new-password" placeholder="Mínimo 8 caracteres"
                  class="w-full rounded-[.875rem] border-[1.5px] border-mineral-green-200 bg-mineral-green-50/60 py-3 pl-10 pr-11 text-sm text-mineral-green-950 placeholder-mineral-green-400/70 transition focus:border-mineral-green-600 focus:bg-white focus:outline-none focus:ring-[3px] focus:ring-mineral-green-500/15" />
                <button type="button" class="absolute inset-y-0 right-0 flex items-center pr-3.5 text-mineral-green-400 hover:text-mineral-green-700 bg-transparent border-none cursor-pointer" tabindex="-1" @click="showPassword = !showPassword">
                  <EyeOff v-if="showPassword" class="w-4 h-4" />
                  <Eye v-else class="w-4 h-4" />
                </button>
              </div>
            </div>
            <div class="space-y-1.5">
              <label for="password2" class="block text-[.8rem] font-semibold text-mineral-green-800">Confirmar contraseña</label>
              <div class="relative group">
                <span class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-mineral-green-400 group-focus-within:text-mineral-green-700">
                  <KeyRound class="w-4 h-4" />
                </span>
                <input 
                    id="password2" v-model="password2" :type="showPassword2 ? 'text' : 'password'" autocomplete="new-password" placeholder="Repite tu contraseña"
                  class="w-full rounded-[.875rem] border-[1.5px] bg-mineral-green-50/60 py-3 pl-10 pr-11 text-sm text-mineral-green-950 placeholder-mineral-green-400/70 transition focus:bg-white focus:outline-none focus:ring-[3px]"
                  :class="passwordsCoinciden ? 'border-mineral-green-200 focus:border-mineral-green-600 focus:ring-mineral-green-500/15' : 'border-red-300 focus:border-red-500 focus:ring-red-500/15'" />
                <button type="button" class="absolute inset-y-0 right-0 flex items-center pr-3.5 text-mineral-green-400 hover:text-mineral-green-700 bg-transparent border-none cursor-pointer" tabindex="-1" @click="showPassword2 = !showPassword2">
                  <EyeOff v-if="showPassword2" class="w-4 h-4" />
                  <Eye v-else class="w-4 h-4" />
                </button>
              </div>
              <p v-if="password2 && !passwordsCoinciden" class="text-[.72rem] text-red-500">Las contraseñas no coinciden.</p>
            </div>
          </div>

          <!-- Aviso de contraseña temporal -->
          <div v-else class="flex items-start gap-2.5 rounded-[.875rem] border border-amber-200 bg-amber-50 px-4 py-3 text-[.78rem] text-amber-700 animate-[fadeUp_.3s_ease_both]">
            <Info class="mt-0.5 w-4 h-4 shrink-0" />
            <span>Se generará una contraseña temporal con tu cédula de identidad. Deberás cambiarla al iniciar sesión por primera vez.</span>
          </div>

          <!-- Error -->
          <transition name="fade">
            <div v-if="errorLocal" class="flex items-start gap-2.5 rounded-[.875rem] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
              <AlertCircle class="mt-0.5 w-4 h-4 shrink-0" />
              <span>{{ errorLocal }}</span>
            </div>
          </transition>

          <!-- Submit -->
          <button 
            type="submit" :disabled="auth.loading || !formularioValido"
            class="relative overflow-hidden mt-1 flex w-full items-center justify-center gap-2 rounded-[.875rem]
                   bg-[linear-gradient(135deg,#1a4a2e_0%,#2d6e47_100%)] px-4 py-3.5 text-sm font-semibold text-white
                   shadow-[0_4px_14px_rgba(26,74,46,.4)] transition
                   hover:-translate-y-px hover:shadow-[0_6px_20px_rgba(26,74,46,.5)] active:scale-[.98]
                   focus:outline-none focus:ring-2 focus:ring-mineral-green-500 focus:ring-offset-2
                   disabled:cursor-not-allowed disabled:opacity-60 disabled:translate-y-0 disabled:shadow-none">
            <Loader2 v-if="auth.loading" class="w-4 h-4 animate-spin" />
            <UserPlus v-else class="w-4 h-4" />
            {{ auth.loading ? 'Creando cuenta...' : 'Crear cuenta' }}
          </button>
        </form>

        <div class="flex items-center gap-3 mt-6">
          <span class="flex-1 h-px bg-linear-to-r from-transparent to-mineral-green-100" />
          <PawPrint class="w-3 h-3 text-mineral-green-200" />
          <span class="flex-1 h-px bg-linear-to-l from-transparent to-mineral-green-100" />
        </div>

        <p class="mt-4 text-center text-[.8rem] text-mineral-green-600">
          ¿Ya tienes cuenta?
          <router-link :to="{ name: 'login' }" class="font-semibold text-mineral-green-800 hover:underline">
            Inicia sesión
          </router-link>
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
@keyframes drift {
  from { transform: translate(0, 0) scale(1); }
  to { transform: translate(28px, 18px) scale(1.08); }
}
@keyframes floatUp {
  0% { transform: translateY(0) scale(1); opacity: .55; }
  50% { transform: translateY(-38px) scale(1.4); opacity: 1; }
  100% { transform: translateY(-76px) scale(.8); opacity: 0; }
}
@keyframes heroIn {
  from { opacity: 0; transform: scale(.86) translateY(18px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
@keyframes spinRing {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(22px) scale(.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes shimmerLine {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .2s ease, transform .2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>