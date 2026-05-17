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

    function logout() {
        accessToken.value = null;
        refreshToken.value = null;
        user.value = null;
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        localStorage.removeItem("user");
    }

    return { accessToken, refreshToken, user, error, loading, isAuthenticated, login, logout };
})