import type { RouteRecordRaw } from 'vue-router'

/** Public routes (accessible without authentication) */
export const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { public: true },
  },
]

/** Protected routes (require authentication) */
export const protectedRoutes: RouteRecordRaw[] = [
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('@/views/dashboard/DashboardView.vue'),
  },
  // ── Usuarios & Auditoría ──────────────────────────────────────────
  {
    path: '/usuarios',
    name: 'usuarios',
    component: () => import('@/views/usuarios/UserListView.vue'),
    meta: { permiso: 'gestionar_usuarios' },
  },
  {
    path: '/usuarios/auditoria',
    name: 'auditoria',
    component: () => import('@/views/usuarios/AuditLogView.vue'),
    meta: { permiso: 'ver_auditoria' },
  },
  {
    path: '/perfil',
    name: 'perfil',
    component: () => import('@/views/usuarios/ProfileView.vue'),
  },
  // ── Propietarios & Pacientes ──────────────────────────────────────
  {
    path: '/propietarios',
    name: 'propietarios',
    component: () => import('@/views/pacientes/PropietariosView.vue'),
  },
  {
    path: '/pacientes/nuevo-propietario',
    name: 'nuevo-propietario',
    component: () => import('@/views/pacientes/PropietarioForm.vue'),
  },
  {
    path: '/pacientes',
    name: 'lista-pacientes',
    component: () => import('@/views/pacientes/PacienteListView.vue'),
  },
  {
    path: '/pacientes/especies-razas',
    name: 'catalogo-especies-razas',
    component: () => import('@/views/pacientes/EspecieRazaView.vue'),
  },
  {
    path: '/pacientes/:id',
    name: 'detalle-paciente',
    component: () => import('@/views/pacientes/PacienteDetailView.vue'),
  },
  // ── Catálogo & Solicitudes ────────────────────────────────────────
  {
    path: '/solicitudes/catalogo',
    name: 'catalogo',
    component: () => import('@/views/solicitudes/CatalogView.vue'),
  },
  {
    path: '/solicitudes/nueva',
    name: 'nueva-solicitud',
    component: () => import('@/views/solicitudes/NuevaSolicitudView.vue'),
  },
  // ── Muestras ─────────────────────────────────────────────────────
  {
    path: '/muestras/recepcion',
    name: 'recepcion',
    component: () => import('@/views/muestras/RecepcionView.vue'),
  },
  {
    path: '/muestras/incidencias',
    name: 'incidencias',
    component: () => import('@/views/muestras/IncidenciasView.vue'),
  },
  // ── Resultados ────────────────────────────────────────────────────
  {
    path: '/resultados/captura',
    name: 'captura-resultados',
    component: () => import('@/views/resultados/CapturaResultadosView.vue'),
  },
  {
    path: '/resultados/validacion',
    name: 'validacion',
    component: () => import('@/views/resultados/ValidacionView.vue'),
    meta: { permiso: 'validar_resultados' },
  },
]

export const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/login' },
  ...publicRoutes,
  ...protectedRoutes,
]
