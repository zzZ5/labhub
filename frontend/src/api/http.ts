import axios from 'axios'

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

http.interceptors.request.use(async (config) => {
  const method = config.method?.toUpperCase() || 'GET'
  if (!['GET', 'HEAD', 'OPTIONS', 'TRACE'].includes(method)) {
    await ensureCsrfToken()
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
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
