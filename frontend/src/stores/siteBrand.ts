import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { fetchSiteSetting, type ExternalLink, type SiteSetting } from '../api/publicPortal'

const CACHE_KEY = 'labhub-site-brand'

const fallbackSetting: Partial<SiteSetting> = {
  site_name: '中农雨磷',
  site_subtitle: '中国农业大学资源与环境学院',
  logo: '/site-icon.png',
  favicon: '/site-icon.png',
  description: '面向农业绿色发展与资源环境治理，开展微生物生态、有机废弃物资源化与高值产品开发研究。',
  address: '北京市海淀区圆明园西路2号 中国农业大学西校区',
  external_links: [
    { label: '中国农业大学', url: 'https://www.cau.edu.cn/' },
    { label: '资源与环境学院', url: 'https://zihuan.cau.edu.cn/' },
    { label: '教师个人主页', url: 'https://faculty.cau.edu.cn/' },
  ],
}

function readCache() {
  try {
    const cached = localStorage.getItem(CACHE_KEY)
    return cached ? (JSON.parse(cached) as Partial<SiteSetting>) : {}
  } catch {
    return {}
  }
}

function writeCache(setting: Partial<SiteSetting>) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(setting))
  } catch {
    // Local storage may be unavailable in private browsing modes.
  }
}

function versionedAsset(url?: string, version?: string) {
  if (!url) return ''
  if (url.startsWith('data:')) return url
  if (url.startsWith('/site-icon') || url.startsWith('/favicon') || url.startsWith('/apple-touch-icon')) return url
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}v=${encodeURIComponent(version || 'latest')}`
}

function updateFaviconLinks(href: string) {
  if (!href || typeof document === 'undefined') return
  document.querySelectorAll<HTMLLinkElement>('link[rel="icon"], link[rel="apple-touch-icon"], link[data-labhub-icon]').forEach((link) => link.remove())

  const icon = document.createElement('link')
  icon.rel = 'icon'
  icon.type = 'image/png'
  icon.href = href
  icon.dataset.labhubIcon = 'true'
  document.head.appendChild(icon)

  const appleIcon = document.createElement('link')
  appleIcon.rel = 'apple-touch-icon'
  appleIcon.href = href
  appleIcon.dataset.labhubIcon = 'true'
  document.head.appendChild(appleIcon)
}

export const useSiteBrandStore = defineStore('siteBrand', () => {
  const setting = ref<Partial<SiteSetting>>({ ...fallbackSetting, ...readCache() })
  const loading = ref(false)

  const siteName = computed(() => setting.value.site_name || fallbackSetting.site_name || '')
  const siteSubtitle = computed(() => setting.value.site_subtitle || fallbackSetting.site_subtitle || '')
  const footerDescription = computed(() => setting.value.footer_text || setting.value.description || fallbackSetting.description || '')
  const address = computed(() => setting.value.address || fallbackSetting.address || '')
  const externalLinks = computed<ExternalLink[]>(() => {
    const links = setting.value.external_links?.filter((link) => link.label && link.url) || []
    return links.length ? links : fallbackSetting.external_links || []
  })
  const logoUrl = computed(() => versionedAsset(setting.value.logo || fallbackSetting.logo, setting.value.updated_at))
  const faviconUrl = computed(() => versionedAsset(setting.value.favicon || setting.value.logo || fallbackSetting.favicon, setting.value.updated_at))

  function applyBrowserBrand() {
    document.title = siteName.value
    updateFaviconLinks(faviconUrl.value)
  }

  async function load(force = false) {
    if (loading.value && !force) return setting.value
    loading.value = true
    try {
      const data = await fetchSiteSetting()
      setting.value = { ...fallbackSetting, ...data }
      writeCache(setting.value)
    } catch {
      setting.value = { ...fallbackSetting, ...readCache() }
    } finally {
      loading.value = false
      applyBrowserBrand()
    }
    return setting.value
  }

  function replace(data: Partial<SiteSetting>) {
    setting.value = { ...fallbackSetting, ...data }
    writeCache(setting.value)
    applyBrowserBrand()
  }

  return {
    setting,
    loading,
    siteName,
    siteSubtitle,
    footerDescription,
    address,
    externalLinks,
    logoUrl,
    faviconUrl,
    load,
    replace,
    applyBrowserBrand,
  }
})
