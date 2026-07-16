import axios from 'axios'

import { beginNetworkRequest, finishNetworkRequest } from '../stores/networkActivity'

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
})

let csrfReady: Promise<void> | null = null

function getCookie(name: string) {
  return document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${name}=`))
    ?.split('=')[1]
}

export async function ensureCsrfToken() {
  if (getCookie('csrftoken')) return
  if (!csrfReady) {
    csrfReady = http.get('/csrf/').then(() => undefined)
  }
  await csrfReady
}

function normalizeMediaUrl(value: string) {
  return value.replace(/https?:\/\/(?:backend|localhost|127\.0\.0\.1|0\.0\.0\.0):8000(\/media\/[^\s"'<>)]*)/gi, '$1')
}

function normalizeResponseMediaUrls<T>(data: T): T {
  if (typeof data === 'string') return normalizeMediaUrl(data) as T
  if (Array.isArray(data)) return data.map((item) => normalizeResponseMediaUrls(item)) as T
  if (data && typeof data === 'object') {
    Object.entries(data).forEach(([key, value]) => {
      ;(data as Record<string, unknown>)[key] = normalizeResponseMediaUrls(value)
    })
  }
  return data
}

http.interceptors.request.use(async (config) => {
  beginNetworkRequest()
  const method = config.method?.toUpperCase() || 'GET'
  if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
    await ensureCsrfToken()
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    finishNetworkRequest()
    response.data = normalizeResponseMediaUrls(response.data)
    return response
  },
  (error) => {
    finishNetworkRequest()
    const status = error?.response?.status
    const detail = String(error?.response?.data?.detail || '')
    const isInternalRoute = ['/dashboard', '/documents', '/instruments', '/students', '/members', '/cms', '/pending'].some((path) =>
      window.location.pathname.startsWith(path),
    )
    const isUnauthenticated =
      status === 401 ||
      (status === 403 &&
        (detail.includes('身份认证信息未提供') ||
          detail.includes('Authentication credentials were not provided') ||
          detail.includes('CSRF Failed')))
    if (isUnauthenticated && isInternalRoute && window.location.pathname !== '/login') {
      const redirect = encodeURIComponent(`${window.location.pathname}${window.location.search}`)
      window.location.assign(`/login?redirect=${redirect}`)
    }
    return Promise.reject(error)
  },
)
