/**
 * Axios instance with JWT interceptor, response envelope unwrapping, and 401 handling.
 */
import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

const request: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
})

// Request interceptor: attach JWT
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: unwrap { code, msg, data } envelope
// Handle 401 → logout + redirect
request.interceptors.response.use(
  (response: AxiosResponse) => {
    const payload = response.data
    // Unwrap envelope if present
    if (payload && typeof payload === 'object' && 'code' in payload) {
      if (payload.code === 1 || response.config.url?.includes('/apidocs')) {
        return response
      }
      // Non-success code
      const err = new Error(payload.msg || 'API error') as Error & { code: number; data: unknown }
      err.code = payload.code
      err.data = payload.data
      return Promise.reject(err)
    }
    return response
  },
  (error) => {
    if (axios.isAxiosError(error)) {
      if (error.response?.status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.hash = '#/user/login'
      }
    }
    return Promise.reject(error)
  }
)

export default request
