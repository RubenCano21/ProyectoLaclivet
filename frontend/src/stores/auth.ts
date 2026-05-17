import api from "@/lib/api";
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
    telefono: string | null;
    direccion: string | null;
    fecha_nacimiento: string | null;
    rol: Rol;
    permisos: Permiso[];
    fecha_creacion: string;
    fecha_actualizacion: string;
    is_active: boolean;
    is_staff: boolean;
}

export const useAuthStore = defineStore("auth", () => {
    const accessToken = ref<string | null>(localStorage.getItem("access_token"));
    const refreshToken = ref<string | null>(localStorage.getItem("refresh_token"));
    const user = ref<User | null>(JSON.parse(localStorage.getItem("user") || "null"));
    const error = ref<string | null>(null);
    const loading = ref(false);

    const isAuthenticated = computed(() => !!accessToken.value);

    async function login(email: string, password: string) {
        loading.value = true;
        error.value = null;

        try {
            const { data } = await api.post("/usuarios/auth/login/", { email, password });

            accessToken.value = data.access;
            refreshToken.value = data.refresh;
            user.value = data.usuario;

            localStorage.setItem("access_token", data.access);
            localStorage.setItem("refresh_token", data.refresh);
            localStorage.setItem("user", JSON.stringify(data.usuario));
            return true;
        } catch (err) {
            const axiosErr = err as AxiosError<Record<string, unknown>>;
            const resData = axiosErr.response?.data;
            error.value =
                (resData?.detail as string) ??
                (resData?.non_field_errors as string[])?.[0] ??
                'Credenciales inválidas';
            return false;
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
            const axiosErr = err as AxiosError<Record<string, string | string[]>>;
            const d = axiosErr.response?.data;
            if (d) {
                for (const v of Object.values(d)) {
                    if (Array.isArray(v) && v[0]) return { ok: false, error: String(v[0]) };
                    if (typeof v === "string") return { ok: false, error: v };
                }
            }
            return { ok: false, error: "Error al actualizar el perfil" };
        }
    }

    async function cambiarPassword(form: {
        password_actual: string;
        password_nuevo: string;
        password_nuevo2: string;
    }): Promise<{ ok: boolean; error?: string }> {
        try {
            await api.post("/usuarios/cambiar-password/", form);
            return { ok: true };
        } catch (err) {
            const axiosErr = err as AxiosError<Record<string, string | string[]>>;
            const d = axiosErr.response?.data;
            if (d) {
                for (const v of Object.values(d)) {
                    if (Array.isArray(v) && v[0]) return { ok: false, error: String(v[0]) };
                    if (typeof v === "string") return { ok: false, error: v };
                }
            }
            return { ok: false, error: "Error al cambiar la contraseña" };
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
        // Blacklistear el refresh token en el backend
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

    async function registro(form: {
        username: string;
        email: string;
        password: string;
        password2: string;
        first_name?: string;
        last_name?: string;
    }): Promise<{ ok: boolean; error?: string }> {
        loading.value = true;
        error.value = null;
        try {
            const { data } = await api.post("/usuarios/auth/registro/", form);
            accessToken.value = data.tokens.access;
            refreshToken.value = data.tokens.refresh;
            user.value = data.usuario;
            localStorage.setItem("access_token", data.tokens.access);
            localStorage.setItem("refresh_token", data.tokens.refresh);
            localStorage.setItem("user", JSON.stringify(data.usuario));
            return { ok: true };
        } catch (err) {
            const axiosErr = err as AxiosError<Record<string, string | string[]>>;
            const d = axiosErr.response?.data;
            if (d) {
                for (const v of Object.values(d)) {
                    if (Array.isArray(v) && v[0]) return { ok: false, error: String(v[0]) };
                    if (typeof v === "string") return { ok: false, error: v };
                }
            }
            return { ok: false, error: "Error al registrar el usuario" };
        } finally {
            loading.value = false;
        }
    }

    return { accessToken, refreshToken, user, error, loading, isAuthenticated, login, fetchPerfil, updatePerfil, cambiarPassword, logout, registro };
})