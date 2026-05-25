import { ref } from 'vue'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: number
  type: NotificationType
  message: string
  duration?: number
}

let nextId = 0

const notifications = ref<Notification[]>([])

/**
 * Composable for showing transient toast/alert notifications.
 *
 * @example
 * const { notify } = useNotification()
 * notify('success', 'Propietario guardado correctamente')
 */
export function useNotification() {
  function notify(type: NotificationType, message: string, duration = 4000) {
    const id = ++nextId
    notifications.value.push({ id, type, message, duration })
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
  }

  function dismiss(id: number) {
    const idx = notifications.value.findIndex((n) => n.id === id)
    if (idx !== -1) notifications.value.splice(idx, 1)
  }

  return { notifications, notify, dismiss }
}
