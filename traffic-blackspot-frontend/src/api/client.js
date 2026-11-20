/**
 * Centralized Axios instance.
 * All API calls go through this — never import axios directly in components.
 * Handles: base URL, timeouts, auth headers, error normalization,
 * request/response logging in dev mode.
 */
import axios from 'axios'
import toast from 'react-hot-toast'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept':       'application/json',
  },
})

// ── Request interceptor ───────────────────────────────────────────────────
apiClient.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.debug(`[API] ${config.method?.toUpperCase()} ${config.url}`)
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ── Response interceptor ──────────────────────────────────────────────────
apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.debug(`[API] ${response.status} ${response.config.url}`)
    }
    return response
  },
  (error) => {
    const status  = error.response?.status
    const message = error.response?.data?.detail || error.message

    if (status !== 422) {
      if (status === 429) {
        toast.error('Too many requests — please wait a moment')
      } else if (status >= 500) {
        toast.error('Server error — the prediction API is unavailable')
      } else if (!error.response) {
        toast.error('Cannot reach API — is the backend running?', {
          id:       'api-offline',
          duration: 6000,
        })
      }
    }

    return Promise.reject({ status, message, originalError: error })
  }
)

export default apiClient
