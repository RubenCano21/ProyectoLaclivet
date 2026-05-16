import api from "@/lib/api";
import type { AxiosError } from "axios";
import { defineStore } from "pinia";
import { ref, computed } from "vue";

interface User {
    username: string;
    [key: string]: any;
}

export const useAuthStore = defineStore("auth", () => {
    const token = ref<string | null>(localStorage.getItem("token"));
    const user = ref<User | null>(JSON.parse(localStorage.getItem("user") || "null"));
    const error = ref<string | null>(null);
    const loading = ref(false);

    const isAuthenticated = computed(() => !!token.value);

    async function login(username: string, password: string) {
        loading.value = true;
        error.value = null;

        try {
            const {data} = await api.post("/usuarios/auth/login/", {username, password});

            token.value = data.token ?? data.access ?? data.key ?? null;
            user.value = data.user ?? { username };

            localStorage.setItem("token", token.value ?? '');
            localStorage.setItem("user", JSON.stringify(user.value));
            return true;
        } catch (err) {
            const axiosErr = err as AxiosError<Record<string, unknown>>;
            const data = axiosErr.response?.data
            error.value =
                (data?.detail as string) ??
                (data?.non_field_errors as string[])?.[0] ??
                'Credenciales inválidas';
            return false;
        } finally {
            loading.value = false;
        }
    }

    function logout() {
        token.value = null;
        user.value = null;
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    }

    return { token, user, error, loading, isAuthenticated, login, logout };
})