import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { fetchSiteSetting, type ExternalLink, type SiteSetting } from '../api/publicPortal'

const CACHE_KEY = 'labhub-site-brand-v2'

const fallbackSetting: Partial<SiteSetting> = {
  logo: '/site-icon.png',
  favicon: '/site-icon.png',
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

  const siteName = computed(() => setting.value.site_name || '')
  const siteSubtitle = computed(() => setting.value.site_subtitle || '')
  const footerDescription = computed(() => setting.value.footer_text || '')
  const address = computed(() => setting.value.address || '')
  const externalLinks = computed<ExternalLink[]>(() => setting.value.external_links?.filter((link) => link.label && link.url) || [])
  const logoUrl = computed(() => versionedAsset(setting.value.logo || fallbackSetting.logo, setting.value.updated_at))
  const faviconUrl = computed(() => versionedAsset(setting.value.favicon || setting.value.logo || fallbackSetting.favicon, setting.value.updated_at))

  function applyBrowserBrand() {
    if (siteName.value) document.title = siteName.value
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
