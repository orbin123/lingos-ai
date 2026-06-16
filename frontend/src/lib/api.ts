import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

import { API_BASE_URL as BASE_URL } from "@/lib/api-config";
import { useAuthStore } from "@/store/authStore";

// One axios instance, used everywhere in the app.
// withCredentials so the httpOnly refresh cookie rides on /auth requests.
export const api = axios.create({
    baseURL: BASE_URL,
    headers: {"Content-Type": "application/json"},
    withCredentials: true,
})

// Request Interceptor: Attach JWT to every request if we have one
api.interceptors.request.use((config) => {
    if (typeof window !== "undefined") {
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
    }
    return config;

});

// Auth endpoints handle their own errors (forms) and must never trigger the
// silent-refresh/auto-logout path.
function isAuthEndpoint(url: string): boolean {
    return [
        "/auth/login",
        "/auth/signup",
        "/auth/refresh",
        "/auth/logout",
        "/auth/verify-email",
        "/auth/resend-otp",
        "/auth/password-reset",
    ].some((path) => url.includes(path));
}

// One refresh in flight at a time — concurrent 401s await the same promise.
let refreshPromise: Promise<string> | null = null;

function refreshAccessToken(): Promise<string> {
    refreshPromise ??= axios
        // Bare axios (not `api`) so this call skips the interceptors.
        .post<{ access_token: string }>(
            `${BASE_URL}/auth/refresh`,
            {},
            { withCredentials: true },
        )
        .then((r) => r.data.access_token)
        .finally(() => {
            refreshPromise = null;
        });
    return refreshPromise;
}

function forceLogout(): void {
    localStorage.removeItem("token");
    useAuthStore.getState().logout();
    window.location.href = "/login";
}

// Response interceptor: on 401, try one silent refresh + retry; only if
// that fails does the user get logged out.
api.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
        const config = error.config as
            | (InternalAxiosRequestConfig & { _retried?: boolean })
            | undefined;
        const url: string = config?.url ?? "";

        if (
            error.response?.status === 401 &&
            typeof window !== "undefined" &&
            !isAuthEndpoint(url)
        ) {
            if (config && !config._retried) {
                config._retried = true;
                try {
                    const token = await refreshAccessToken();
                    useAuthStore.getState().setToken(token);
                    config.headers.Authorization = `Bearer ${token}`;
                    return api.request(config);
                } catch {
                    forceLogout();
                }
            } else {
                // Already retried (or no config) — session is really dead.
                forceLogout();
            }
        }
        return Promise.reject(error);
    }
)
