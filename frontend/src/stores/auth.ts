import api from "@/services/apiClient";
import type { AxiosError } from "axios";
import { defineStore } from "pinia";
import { ref, computed } from "vue";

interface Permiso {
    id: number;
    nombre: string;
    codigo: string;
    descripcion: string;
}

interface Rol {
    id: number;
    nombre: string;
    descripcion: string;
}

interface User {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    ci: string | null;
    telefono: string | null;
    direccion: string | null;
    fecha_nacimiento: string | null;
    rol: Rol;
    permisos: Permiso[];
    fecha_creacion: string;
    fecha_actualizacion: string;
    is_active: boolean;
    is_staff: boolean;
    debe_cambiar_password: boolean;
}

// Coincide exactamente con RegistroUsuarioSerializer.Meta.fields.
// NO incluye 'username' -> el backend lo genera automáticamente a partir del email.
// password / password2 son opcionales: si se omiten, el backend genera una
// contraseña temporal (= CI del usuario) y marca debe_cambiar_password = true.
export interface RegistroForm {
    email: string;
    first_name: string;
    last_name: string;
    ci: string;
    telefono?: string;
    direccion?: string;
    fecha_nacimiento?: string;
    password?: string;
    password2?: string;
}

function extraerError(err: unknown): string {
    const axiosErr = err as AxiosError<Record<string, string | string[]>>;
    const d = axiosErr.response?.data;
    if (!d) return "Error de conexión";
    for (const v of Object.values(d)) {
        if (Array.isArray(v) && v[0]) return String(v[0]);
        if (typeof v === "string") return v;
    }
    return "Error inesperado";
}

export const useAuthStore = defineStore("auth", () => {
    const accessToken = ref<string | null>(localStorage.getItem("access_token"));
    const refreshToken = ref<string | null>(localStorage.getItem("refresh_token"));
    const user = ref<User | null>(JSON.parse(localStorage.getItem("user") || "null"));
    const error = ref<string | null>(null);
    const loading = ref(false);

    const isAuthenticated = computed(() => !!accessToken.value)
    const tienePermiso = (codigo: string) =>
        user.value?.permisos?.some((p) => p.codigo === codigo) ?? false
    const tieneRol = (nombre: string) =>
        user.value?.rol?.nombre === nombre
    const esAdmin = computed(() => user.value?.rol?.nombre === 'Administrador');

    function guardarSesion(access: string, refresh: string, usuario: User) {
        accessToken.value = access;
        refreshToken.value = refresh;
        user.value = usuario;
        localStorage.setItem("access_token", access);
        localStorage.setItem("refresh_token", refresh);
        localStorage.setItem("user", JSON.stringify(usuario));
    }

    async function login(email: string, password: string) {
        loading.value = true;
        error.value = null;

        try {
            const { data } = await api.post("/usuarios/auth/login/", { email, password });
            guardarSesion(data.access, data.refresh, data.usuario);
            return true;
        } catch (err) {
            const axiosErr = err as AxiosError<Record<string, unknown>>;
            const resData = axiosErr.response?.data;
            error.value =
                (resData?.detail as string) ??
                (resData?.non_field_errors as string[])?.[0] ??
                "Credenciales inválidas";
            return false;
        } finally {
            loading.value = false;
        }
    }

    async function registro(form: RegistroForm): Promise<{ ok: boolean; error?: string; debeCambiarPassword?: boolean }> {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await api.post("/usuarios/auth/registro/", form);
            guardarSesion(data.tokens.access, data.tokens.refresh, data.usuario);
            return { ok: true, debeCambiarPassword: data.usuario.debe_cambiar_password };
        } catch (err) {
            const mensaje = extraerError(err);
            error.value = mensaje;
            return { ok: false, error: mensaje };
        } finally {
            loading.value = false;
        }
    }

    async function updatePerfil(form: {
        first_name?: string;
        last_name?: string;
        email?: string;
        telefono?: string | null;
        direccion?: string | null;
        fecha_nacimiento?: string | null;
    }): Promise<{ ok: boolean; error?: string }> {
        try {
            const { data } = await api.put("/usuarios/perfil/", form);
            user.value = data.usuario;
            localStorage.setItem("user", JSON.stringify(data.usuario));
            return { ok: true };
        } catch (err) {
            return { ok: false, error: extraerError(err) };
        }
    }

    async function cambiarPassword(form: {
        password_actual: string;
        password_nuevo: string;
        password_nuevo2: string;
    }): Promise<{ ok: boolean; error?: string }> {
        try {
            await api.post("/usuarios/cambiar-password/", form);
            if (user.value) {
                user.value.debe_cambiar_password = false;
                localStorage.setItem("user", JSON.stringify(user.value));
            }
            return { ok: true };
        } catch (err) {
            return { ok: false, error: extraerError(err) };
        }
    }

    async function fetchPerfil() {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await api.get("/usuarios/perfil/");
            user.value = data;
            localStorage.setItem("user", JSON.stringify(data));
        } catch (err) {
            const axiosErr = err as AxiosError<Record<string, unknown>>;
            error.value = (axiosErr.response?.data?.detail as string) ?? "Error al obtener el perfil";
        } finally {
            loading.value = false;
        }
    }

    async function logout() {
        const rt = refreshToken.value ?? localStorage.getItem("refresh_token");
        if (rt) {
            try {
                await api.post("/usuarios/auth/logout/", { refresh_token: rt });
            } catch {
                // Si falla (token ya expirado, etc.) se continúa limpiando el estado
            }
        }
        accessToken.value = null;
        refreshToken.value = null;
        user.value = null;
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
    }

    return {
        accessToken,
        refreshToken,
        user,
        error,
        loading,
        isAuthenticated,
        tienePermiso,
        tieneRol,
        esAdmin,
        login,
        registro,
        fetchPerfil,
        updatePerfil,
        cambiarPassword,
        logout,
    };
});