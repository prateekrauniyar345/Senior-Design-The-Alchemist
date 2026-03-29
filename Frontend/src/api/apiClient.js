import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 120000,  // 2 minutes for agent/LLM requests
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
    Accept: "application/json",
  },
});

// Separate client for refresh requests to avoid interceptor loops
const refreshClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
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
 * This is called when token refresh fails or user is no longer authenticated
 */
const handleAuthFailure = () => {
  console.error("Authentication failed. Redirecting to login.");
  // Clear any stale tokens if needed
  // Redirect to login page
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

    // Do not retry refresh/login/logout requests
    if (status !== 401 || isRefreshRequest || isLoginRequest || isLogoutRequest) {
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