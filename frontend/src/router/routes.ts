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
    meta: { permiso: 'ver_usuarios' },
  },
  {
    path: '/usuarios/auditoria',
    name: 'auditoria',
    component: () => import('@/views/usuarios/AuditLogView.vue'),
  },
  {
    path: '/perfil',
    name: 'perfil',
    component: () => import('@/views/usuarios/ProfileView.vue'),
  },
  // ── Médicos ────────────────────────────────────────
  {
    path: '/medicos',
    name: 'medicos',
    component: () => import('@/views/medicos/MedicoListView.vue'),
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
    path: '/pacientes/nuevo',
    name: 'nuevo-paciente',
    component: () => import('@/views/pacientes/PacienteFormView.vue'),
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
    path: '/solicitudes',
    name: 'solicitudes',
    component: () => import('@/views/solicitudes/SolicitudesView.vue'),
  },
  {
    path: '/solicitudes/:id',
    name: 'solicitud-detalle',
    component: () => import('@/views/solicitudes/SolicitudDetailView.vue'),
  },

  {
    path: '/muestras/incidencias',
    name: 'incidencias',
    component: () => import('@/views/muestras/IncidenciasView.vue'),
  },
  // ── Business Intelligence ─────────────────────────────────────────
  {
    path: '/bi',
    name: 'bi',
    component: () => import('@/views/bi/BIView.vue'),
  },
  // ── Resultados ────────────────────────────────────────────────────
  {
    path: '/resultados',
    name: 'resultados',
    component: () => import('@/views/resultados/ResultadosListView.vue'),
  },
  {
    path: '/resultados/:id',
    name: 'captura-resultados',
    component: () => import('@/views/resultados/CapturaResultadosView.vue'),
    meta: { permiso: 'registrar_resultados' },
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
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { public: true },
  },

]
