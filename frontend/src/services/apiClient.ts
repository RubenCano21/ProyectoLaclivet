import axios from "axios";

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

// Añade barra final (Django APPEND_SLASH) y adjunta el access token
api.interceptors.request.use((config) => {
    if (config.url && !config.url.endsWith('/') && !config.url.includes('?')) {
        config.url += '/';
    }
    const token = localStorage.getItem("access_token");
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Auto-renovación del access token cuando el servidor devuelve 401
type QueueItem = { resolve: (token: string) => void; reject: (err: unknown) => void };
let isRefreshing = false;
let failedQueue: QueueItem[] = [];

function processQueue(error: unknown, token: string | null) {
    failedQueue.forEach(({ resolve, reject }) => (error ? reject(error) : resolve(token!)));
    failedQueue = [];
}

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const original = error.config;

        // Solo intentar refresh en 401 y una sola vez por petición
        if (error.response?.status !== 401 || original._retry) {
            return Promise.reject(error);
        }

        const refresh = localStorage.getItem("refresh_token");
        if (!refresh) {
            localStorage.removeItem("access_token");
            localStorage.removeItem("user");
            window.location.href = "/login";
            return Promise.reject(error);
        }

        // Si ya hay un refresh en curso, encolar la petición fallida
        if (isRefreshing) {
            return new Promise<string>((resolve, reject) => {
                failedQueue.push({ resolve, reject });
            }).then((token) => {
                original.headers.Authorization = `Bearer ${token}`;
                return api(original);
            });
        }

        original._retry = true;
        isRefreshing = true;

        try {
            const { data } = await axios.post(
                `${import.meta.env.VITE_API_BASE_URL}/usuarios/auth/refresh/`,
                { refresh }
            );
            localStorage.setItem("access_token", data.access);
            processQueue(null, data.access);
            original.headers.Authorization = `Bearer ${data.access}`;
            return api(original);
        } catch (err) {
            processQueue(err, null);
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            localStorage.removeItem("user");
            window.location.href = "/login";
            return Promise.reject(err);
        } finally {
            isRefreshing = false;
        }
    }
);

export default api;