import axios from "axios";

/**
 * Single API origin for all requests.
 * - If VITE_API_URL is set: use it (trim trailing slash).
 * - Dev + unset: relative "" so Vite proxies /api and /contents to the backend.
 * - Prod fallback: direct backend on localhost (set VITE_API_URL in real deployments).
 */
export function resolveApiBaseUrl() {
  const raw = import.meta.env.VITE_API_URL;
  if (raw !== undefined && raw !== null && String(raw).trim() !== "") {
    return String(raw).replace(/\/$/, "");
  }
  if (import.meta.env.DEV) {
    return "";
  }
  return "http://localhost:8000";
}

const API_BASE_URL = resolveApiBaseUrl();

/** FastAPI/Starlette validation errors and HTTPException detail */
export function getApiErrorMessage(error) {
  const d = error.response?.data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d)) {
    return d
      .map((x) => (x && typeof x.msg === "string" ? x.msg : JSON.stringify(x)))
      .join("; ");
  }
  if (d && typeof d === "object") return JSON.stringify(d);
  if (!error.response) {
    return "Cannot reach API. Start the backend on port 8000 (or set VITE_API_URL / use dev proxy).";
  }
  return error.message || "Request failed";
}

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,  // 2 minutes for agent/LLM requests
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Separate client for refresh requests to avoid interceptor loops
const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

let isRefreshing = false;
let failedQueue = [];

/**
 * Resolve or reject all queued requests after refresh completes.
 */
const processQueue = (error = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error);
    } else {
      resolve();
    }
  });

  failedQueue = [];
};

/**
 * Handle authentication failure by redirecting to login
 * Only redirect if we're not already on a login/register page to avoid loops
 */
const handleAuthFailure = () => {
  const currentPath = window.location.pathname;
  // Don't redirect if already on auth pages
  if (currentPath === '/signin' || currentPath === '/signup' || currentPath === '/login' || currentPath === '/register') {
    return;
  }
  console.error("Authentication failed. Redirecting to login.");
  window.location.href = "/signin";
};

/**
 * Request interceptor
 * - withCredentials is already set at client level,
 *   but we enforce it again to be safe.
 * - Useful place for request logging / headers.
 */
apiClient.interceptors.request.use(
  (config) => {
    config.withCredentials = true;
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response interceptor
 * - On 401, attempt refresh once
 * - Queue concurrent requests while refresh is in progress
 * - Retry original request after refresh
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // No response from server (network error / timeout / CORS / backend down)
    if (!error.response) {
      return Promise.reject(error);
    }

    const status = error.response.status;
    const requestUrl = originalRequest?.url || "";

    const isRefreshRequest =
      requestUrl.includes("/api/auth/refresh") || requestUrl.includes("/refresh");

    const isLoginRequest =
      requestUrl.includes("/api/auth/login") || requestUrl.includes("/login");

    const isLogoutRequest =
      requestUrl.includes("/api/auth/logout") || requestUrl.includes("/logout");

    // Don't retry auth check - it's expected to fail when not authenticated
    const isAuthCheckRequest = requestUrl.includes("/api/auth/me") || requestUrl.includes("/me");

    // Do not retry refresh/login/logout/auth-check requests
    if (status !== 401 || isRefreshRequest || isLoginRequest || isLogoutRequest || isAuthCheckRequest) {
      return Promise.reject(error);
    }

    // Prevent infinite retry loops
    if (originalRequest._retry) {
      handleAuthFailure();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    // If refresh already in progress, queue this request
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({
          resolve: async () => {
            try {
              originalRequest.withCredentials = true;
              resolve(apiClient(originalRequest));
            } catch (retryError) {
              reject(retryError);
            }
          },
          reject,
        });
      });
    }

    isRefreshing = true;

    try {
      // Call your backend refresh endpoint
      // Assumes refresh token is stored in HttpOnly cookie
      await refreshClient.post("/api/auth/refresh");

      processQueue(null);

      originalRequest.withCredentials = true;
      return apiClient(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError);
      handleAuthFailure();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default apiClient;