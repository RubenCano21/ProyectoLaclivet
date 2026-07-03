<script setup lang="ts">
import { ref, nextTick, computed } from 'vue'
import { biService } from '@/services/biService'
import { useAuthStore } from '@/stores/auth'
import { Bot, X, Send, Loader2, MessageCircle, Trash2 } from 'lucide-vue-next'

const auth = useAuthStore()

// Solo visible para staff (no propietarios)
const visible = computed(() => auth.isAuthenticated && auth.user?.rol?.nombre !== 'Propietario')

interface Mensaje {
  rol: 'user' | 'bot' | 'error'
  texto: string
  tiempo: string
}

const abierto   = ref(false)
const pregunta  = ref('')
const cargando  = ref(false)
const mensajes  = ref<Mensaje[]>([
  {
    rol: 'bot',
    texto: '¡Hola! Soy **VetBot**, el asistente inteligente de LACLIVET. Puedo ayudarte a consultar datos del laboratorio, interpretar métricas o responder preguntas sobre las operaciones del sistema. ¿En qué puedo ayudarte?',
    tiempo: ahora(),
  },
])

const contenedor = ref<HTMLElement | null>(null)

function ahora() {
  return new Date().toLocaleTimeString('es-BO', { hour: '2-digit', minute: '2-digit' })
}

function toggleChat() {
  abierto.value = !abierto.value
  if (abierto.value) scrollAbajo()
}

async function scrollAbajo() {
  await nextTick()
  if (contenedor.value) contenedor.value.scrollTop = contenedor.value.scrollHeight
}

function limpiar() {
  mensajes.value = [{
    rol: 'bot',
    texto: 'Historial limpiado. ¿En qué puedo ayudarte?',
    tiempo: ahora(),
  }]
}

/** Convierte Markdown básico a HTML seguro para el chat */
function markdownToHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code class="bg-black/10 px-1 rounded text-xs">$1</code>')
    .replace(/\n/g, '<br>')
}

async function enviar() {
  const texto = pregunta.value.trim()
  if (!texto || cargando.value) return

  mensajes.value.push({ rol: 'user', texto, tiempo: ahora() })
  pregunta.value = ''
  cargando.value = true
  await scrollAbajo()

  try {
    const { data } = await biService.chatbot(texto)
    if (data.error) {
      mensajes.value.push({ rol: 'error', texto: data.error, tiempo: ahora() })
    } else {
      mensajes.value.push({ rol: 'bot', texto: data.respuesta ?? '', tiempo: ahora() })
    }
  } catch (err: unknown) {
    // Extraer el mensaje de error del body JSON si existe
    let msg = 'No se pudo conectar con el servicio de IA. Verifica tu conexión.'
    const axiosErr = err as { response?: { data?: { error?: string }; status?: number } }
    if (axiosErr?.response?.data?.error) {
      msg = axiosErr.response.data.error
    } else if (axiosErr?.response?.status === 503) {
      msg = 'El servicio de IA no está configurado. Contacta al administrador.'
    } else if (axiosErr?.response?.status === 502) {
      msg = 'El servicio de IA no está disponible en este momento. Intenta más tarde.'
    }
    mensajes.value.push({ rol: 'error', texto: msg, tiempo: ahora() })
  } finally {
    cargando.value = false
    await scrollAbajo()
  }
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    enviar()
  }
}

// Sugerencias rápidas
const sugerencias = [
  '¿Cuántas muestras pendientes hay?',
  '¿Cuáles son los exámenes más solicitados?',
  '¿Cuál es el total de ingresos este mes?',
  '¿Hay parámetros fuera de rango?',
]
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="fixed bottom-5 right-5 z-50 flex flex-col items-end gap-3">

      <!-- ── Panel de chat ────────────────────────────────────────────────── -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-y-4 scale-95"
        enter-to-class="opacity-100 translate-y-0 scale-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 translate-y-0 scale-100"
        leave-to-class="opacity-0 translate-y-4 scale-95"
      >
        <div
          v-if="abierto"
          class="flex flex-col w-90 h-130 rounded-2xl border border-border bg-white shadow-2xl overflow-hidden"
        >
          <!-- Cabecera -->
          <div class="flex items-center gap-3 px-4 py-3 bg-primary text-primary-foreground shrink-0">
            <div class="flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
              <Bot class="h-4 w-4" />
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold leading-none">VetBot</p>
              <p class="text-xs opacity-70 mt-0.5">Asistente IA · LACLIVET</p>
            </div>
            <button class="opacity-70 hover:opacity-100 transition-opacity" title="Limpiar chat" @click="limpiar">
              <Trash2 class="h-4 w-4" />
            </button>
            <button class="opacity-70 hover:opacity-100 transition-opacity" @click="toggleChat">
              <X class="h-4 w-4" />
            </button>
          </div>

          <!-- Mensajes -->
          <div ref="contenedor" class="flex-1 overflow-y-auto p-4 space-y-3 bg-muted/20">

            <div
              v-for="(msg, i) in mensajes"
              :key="i"
              :class="['flex gap-2', msg.rol === 'user' ? 'flex-row-reverse' : 'flex-row']"
            >
              <!-- Avatar -->
              <div
                v-if="msg.rol !== 'user'"
                class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-white mt-0.5"
                :class="msg.rol === 'error' ? 'bg-red-500' : 'bg-primary'"
              >
                <Bot class="h-3.5 w-3.5" />
              </div>

              <!-- Burbuja -->
              <div
                :class="[
                  'max-w-[80%] rounded-2xl px-3 py-2 text-sm leading-relaxed shadow-xs',
                  msg.rol === 'user'
                    ? 'bg-primary text-primary-foreground rounded-tr-none'
                    : msg.rol === 'error'
                      ? 'bg-red-50 text-red-700 border border-red-200 rounded-tl-none'
                      : 'bg-white border border-border rounded-tl-none',
                ]"
              >
                <!-- eslint-disable vue/no-v-html -->
                <span v-if="msg.rol === 'bot'" v-html="markdownToHtml(msg.texto)" />
                <span v-else>{{ msg.texto }}</span>
                <p class="text-[10px] mt-1 opacity-50 text-right">{{ msg.tiempo }}</p>
              </div>
            </div>

            <!-- Indicador de carga -->
            <div v-if="cargando" class="flex gap-2">
              <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary text-white">
                <Bot class="h-3.5 w-3.5" />
              </div>
              <div class="bg-white border border-border rounded-2xl rounded-tl-none px-3 py-2 shadow-xs">
                <div class="flex items-center gap-1">
                  <span class="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style="animation-delay:0ms" />
                  <span class="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style="animation-delay:150ms" />
                  <span class="h-1.5 w-1.5 rounded-full bg-primary animate-bounce" style="animation-delay:300ms" />
                </div>
              </div>
            </div>

          </div>

          <!-- Sugerencias rápidas (solo cuando hay pocos mensajes) -->
          <div v-if="mensajes.length <= 2" class="px-3 py-2 border-t bg-muted/10 flex flex-wrap gap-1.5 shrink-0">
            <button
              v-for="s in sugerencias" :key="s"
              class="text-[11px] rounded-full border border-primary/30 bg-primary/5 text-primary px-2.5 py-1 hover:bg-primary/10 transition-colors"
              @click="pregunta = s; enviar()"
            >{{ s }}</button>
          </div>

          <!-- Input -->
          <div class="flex items-end gap-2 border-t bg-white px-3 py-2.5 shrink-0">
            <textarea
              v-model="pregunta"
              rows="1"
              placeholder="Escribe una pregunta…"
              class="flex-1 resize-none rounded-xl border border-border bg-muted/30 px-3 py-2 
              text-sm outline-none focus:ring-2 focus:ring-primary/40 placeholder:text-muted-foreground max-h-24 min-h-9.5"
              @keydown="onKeydown"
            />
            <button
              :disabled="!pregunta.trim() || cargando"
              class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-primary 
              text-primary-foreground transition-all hover:bg-primary/90 disabled:opacity-40 disabled:cursor-not-allowed"
              @click="enviar"
            >
              <Loader2 v-if="cargando" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
            </button>
          </div>
        </div>
      </Transition>

      <!-- ── Botón flotante ────────────────────────────────────────────────── -->
      <button
        class="relative flex h-13 w-13 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-all hover:scale-110 hover:shadow-xl active:scale-95"
        :class="{ 'rotate-0': !abierto }"
        @click="toggleChat"
      >
        <Transition
          enter-active-class="transition-all duration-200"
          enter-from-class="opacity-0 rotate-90 scale-50"
          leave-active-class="transition-all duration-200"
          leave-to-class="opacity-0 rotate-90 scale-50"
          mode="out-in"
        >
          <X v-if="abierto" class="h-5 w-5" />
          <MessageCircle v-else class="h-5 w-5" />
        </Transition>
        <!-- Badge de notificación (visible cuando cerrado) -->
        <span
          v-if="!abierto"
          class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-emerald-500 text-[9px] font-bold text-white"
        >IA</span>
      </button>

    </div>
  </Teleport>
</template>

