# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about the recommended Project Setup and IDE Support in the [Vue Docs TypeScript Guide](https://vuejs.org/guide/typescript/overview.html#project-setup).


## ESTRUCTURA BASE DEL PROYECTO
```bash
frontend/
├── public/                  # Archivos estáticos globales (favicons, logos públicos)
├── src/
│   ├── assets/              # Estilos globales (Tailwind/Sass), imágenes fijas, fuentes
│   │   ├── css/
│   │   └── images/
│   │
│   ├── components/          # Componentes globales y 100% reutilizables (UI común)
│   │   ├── common/
│   │   │   ├── AppButton.vue
│   │   │   ├── AppModal.vue
│   │   │   ├── AppInput.vue
│   │   │   └── DataTable.vue # Tabla genérica para listados con paginación
│   │   └── layout/
│   │       ├── Sidebar.vue   # Menú lateral dinámico según el Rol del usuario
│   │       ├── Navbar.vue
│   │       └── AuthLayout.vue
│   │
│   ├── composables/         # Lógica reutilizable con la Composition API (Custom Hooks)
│   │   ├── useAuth.js       # Control de sesión, login, logout
│   │   ├── useFetch.js      # Manejo genérico de peticiones HTTP, carga y errores
│   │   └── useNotification.js
│   │
│   ├── router/              # Configuración de rutas (Vue Router)
│   │   ├── index.js         # Enrutador principal y Guards de seguridad (control de acceso)
│   │   └── routes.js        # Desglose de rutas protegidas y públicas
│   │
│   ├── services/            # Capa de comunicación HTTP con tu API de Django (Axios)
│   │   ├── apiClient.js     # Instancia centralizada de Axios (inyecta tokens JWT automáticamente)
│   │   ├── authService.js
│   │   ├── pacienteService.js
│   │   ├── muestraService.js
│   │   └── resultadoService.js
│   │
│   ├── stores/              # Manejo del estado global con Pinia
│   │   ├── auth.js          # Datos del usuario autenticado, roles y permisos (RF1)
│   │   ├── pacientes.js     # Estado temporal de la mascota activa en pantalla
│   │   └── solicitudes.js   # Carrito de exámenes antes de enviar la orden (RF6)
│   │
│   ├── utils/               # Funciones auxiliares o helpers independientes de Vue
│   │   ├── formatters.js    # Formateadores de fechas veterinarias, monedas, etc.
│   │   └── validators.js    # Validaciones de formularios (rut, emails, teléfonos)
│   │
│   ├── views/               # Vistas de página (Contenedores principales estructurados por Módulo)
│   │   ├── auth/
│   │   │   └── LoginView.vue
│   │   ├── usuarios/        # Gestión de Usuarios, Roles y Auditoría (RF1, RF15)
│   │   │   ├── UserListView.vue
│   │   │   └── AuditLogView.vue
│   │   ├── pacientes/       # Gestión de Propietarios y Pacientes (RF2, RF3)
│   │   │   ├── PropietarioForm.vue
│   │   │   ├── PacienteListView.vue
│   │   │   └── PacienteDetailView.vue # Aquí se consume la consulta dinámica de Historial (RF10)
│   │   ├── solicitudes/     # Órdenes de Examen y Catálogo (RF5, RF6)
│   │   │   ├── CatalogView.vue
│   │   │   └── NuevaSolicitudView.vue
│   │   ├── muestras/        # Recepción, Trazabilidad e Incidencias de muestras (RF7, RF13)
│   │   │   ├── RecepcionView.vue
│   │   │   └── IncidenciasView.vue
│   │   ├── resultados/      # Ingreso, Registro y Validación de Resultados (RF8)
│   │   │   ├── CapturaResultadosView.vue
│   │   │   └── ValidacionView.vue
│   │   └── dashboard/       # Estadísticas y Reportes Administrativos (RF14)
│   │       └── DashboardView.vue
│   │
│   ├── App.vue              # Componente raíz del sistema
│   └── main.js              # Archivo de inicialización (Monta Vue, Pinia, Router y Plugins)
│
├── .env.development         # Variables de entorno locales (VITE_API_URL=http://localhost:8000/api/)
├── .env.production          # Variables de entorno para producción (URL del servidor real)
├── index.html               # Archivo HTML base donde se monta Vue
├── package.json             # Dependencias del proyecto (npm / yarn)
└── vite.config.js           # Configuración del empaquetador Vite
```