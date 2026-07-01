import type { RouteRecordRaw } from 'vue-router'

/** Public routes (accessible without authentication) */
export const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/registro',
    name: 'registro',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { public: true },
  }
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
    meta: { permiso: 'ver_auditoria' },
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
    meta: { permiso: 'ver_usuarios' },
  },
  // ── Propietarios & Pacientes ──────────────────────────────────────
  {
    path: '/propietarios',
    name: 'propietarios',
    component: () => import('@/views/pacientes/PropietariosView.vue'),
    meta: { permiso: 'ver_pacientes' },
  },
  {
    path: '/pacientes/nuevo-propietario',
    name: 'nuevo-propietario',
    component: () => import('@/views/pacientes/PropietarioForm.vue'),
    meta: { permiso: 'crear_paciente' },
  },
  {
    path: '/pacientes',
    name: 'lista-pacientes',
    component: () => import('@/views/pacientes/PacienteListView.vue'),
    meta: { permiso: 'ver_pacientes' },
  },
  {
    path: '/pacientes/especies-razas',
    name: 'catalogo-especies-razas',
    component: () => import('@/views/pacientes/EspecieRazaView.vue'),
    meta: { permiso: 'ver_pacientes' },
  },
  {
    path: '/pacientes/nuevo',
    name: 'nuevo-paciente',
    component: () => import('@/views/pacientes/PacienteFormView.vue'),
    meta: { permiso: 'crear_paciente' },
  },
  {
    path: '/pacientes/:id',
    name: 'detalle-paciente',
    component: () => import('@/views/pacientes/PacienteDetailView.vue'),
    meta: { permiso: 'ver_pacientes' },
  },
  // ── Catálogo & Solicitudes ────────────────────────────────────────
  {
    path: '/solicitudes/catalogo',
    name: 'catalogo',
    component: () => import('@/views/solicitudes/CatalogView.vue'),
    meta: { permiso: 'ver_catalogo' },
  },
  {
    path: '/solicitudes',
    name: 'solicitudes',
    component: () => import('@/views/solicitudes/SolicitudesView.vue'),
    meta: { permiso: 'ver_solicitudes' },
  },
  {
    path: '/solicitudes/:id',
    name: 'solicitud-detalle',
    component: () => import('@/views/solicitudes/SolicitudDetailView.vue'),
    meta: { permiso: 'ver_solicitudes' },
  },
  // ── Muestras ──────────────────────────────────────────────────────
  {
    path: '/muestras/incidencias',
    name: 'incidencias',
    component: () => import('@/views/muestras/IncidenciasView.vue'),
    meta: { permiso: 'ver_muestras' },
  },
  {
    path: '/muestras/recepcion',
    name: 'recepcion-muestras',
    component: () => import('@/views/muestras/RecepcionView.vue'),
    meta: { permiso: 'ver_muestras' },
  },
  // ── Business Intelligence ─────────────────────────────────────────
  {
    path: '/bi',
    name: 'bi',
    component: () => import('@/views/bi/BIView.vue'),
    meta: { permiso: 'ver_reportes' },
  },
  // ── Agenda ────────────────────────────────────────────────────────
  {
    path: '/agenda',
    name: 'agenda',
    component: () => import('@/views/agenda/AgendaView.vue'),
    meta: { permiso: 'ver_solicitudes' },
  },
  // ── Resultados ────────────────────────────────────────────────────
  {
    path: '/resultados',
    name: 'resultados',
    component: () => import('@/views/resultados/ResultadosListView.vue'),
    meta: { permiso: 'ver_resultados' },
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
  // ── Portal Propietario ────────────────────────────────────────────
  {
    path: '/mis-mascotas',
    name: 'portal-mascotas',
    component: () => import('@/views/portal/PortalMascotasView.vue'),
    meta: { roles: ['Propietario'] },
  },
  {
    path: '/mis-mascotas/:id',
    name: 'portal-mascota-detalle',
    component: () => import('@/views/portal/PortalMascotaDetalleView.vue'),
    meta: { roles: ['Propietario'] },
  },
  {
    path: '/mis-resultados',
    name: 'portal-resultados',
    component: () => import('@/views/portal/PortalResultadosView.vue'),
    meta: { roles: ['Propietario'] },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { public: true },
  },
]
