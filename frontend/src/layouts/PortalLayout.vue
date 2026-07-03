<template>
  <div class="portal-shell">
    <header class="portal-nav">
      <RouterLink class="portal-brand" to="/" @click="closeMenu">
        <span class="brand-emblem">
          <img :src="brandLogo" :alt="footerName" />
        </span>
        <span class="brand-text">
          <strong>{{ footerName }}</strong>
          <small>{{ siteSetting.site_subtitle || '中国农业大学资源与环境学院' }}</small>
        </span>
      </RouterLink>

      <button class="nav-toggle" type="button" :aria-expanded="menuOpen" aria-label="打开导航菜单" @click="menuOpen = !menuOpen">
        <span></span>
        <span></span>
        <span></span>
      </button>

      <nav class="portal-links" :class="{ open: menuOpen }" aria-label="主导航">
        <RouterLink to="/" @click="closeMenu">首页</RouterLink>
        <RouterLink to="/research" @click="closeMenu">研究方向</RouterLink>
        <RouterLink to="/team" @click="closeMenu">团队成员</RouterLink>
        <RouterLink to="/publications" @click="closeMenu">科研成果</RouterLink>
        <RouterLink to="/news" @click="closeMenu">新闻活动</RouterLink>
        <RouterLink class="internal-entry" to="/dashboard" @click="closeMenu">内部平台</RouterLink>
      </nav>
    </header>

    <main class="portal-main">
      <slot />
    </main>

    <footer class="portal-footer">
      <div class="container footer-grid">
        <div>
          <strong>{{ footerName }}</strong>
          <p>{{ footerDescription }}</p>
        </div>
        <div class="footer-address">
          <span>{{ footerUnit }}</span>
          <span>{{ footerAddress }}</span>
          <nav class="footer-links" aria-label="相关链接">
            <a v-for="link in footerLinks" :key="`${link.label}-${link.url}`" :href="link.url" target="_blank" rel="noopener noreferrer">{{ link.label }}</a>
          </nav>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { fetchSiteSetting, type ExternalLink, type SiteSetting } from '../api/publicPortal'

const menuOpen = ref(false)
const siteSetting = ref<Partial<SiteSetting>>({})

const defaultLinks: ExternalLink[] = [
  { label: '中国农业大学', url: 'https://www.cau.edu.cn/' },
  { label: '资源与环境学院', url: 'https://zihuan.cau.edu.cn/' },
  { label: '教师个人主页', url: 'https://faculty.cau.edu.cn/' },
]

const footerUnit = computed(() => siteSetting.value.site_subtitle ? `${siteSetting.value.site_subtitle}生态系` : '中国农业大学资源与环境学院生态系')
const footerAddress = computed(() => siteSetting.value.address || '北京市海淀区圆明园西路2号 中国农业大学西校区')
const footerName = computed(() => siteSetting.value.site_name || '中农雨磷')
const footerDescription = computed(() => siteSetting.value.footer_text || siteSetting.value.description || '面向农业绿色发展与资源环境治理，开展微生物生态、有机废弃物资源化与高值产品开发研究。')
const assetVersion = computed(() => encodeURIComponent(siteSetting.value.updated_at || 'default'))
const brandLogo = computed(() => withAssetVersion(siteSetting.value.logo || '/site-icon.png'))
const footerLinks = computed(() => {
  const links = siteSetting.value.external_links?.filter((link) => link.label && link.url) || []
  return links.length ? links : defaultLinks
})

function withAssetVersion(url: string) {
  if (!url || url.startsWith('data:')) return url
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}v=${assetVersion.value}`
}

function updateFavicon(url?: string) {
  if (!url) return
  const href = withAssetVersion(url)
  document.querySelectorAll<HTMLLinkElement>('link[rel="icon"], link[rel="apple-touch-icon"]').forEach((link) => {
    link.href = href
  })
}

function closeMenu() {
  menuOpen.value = false
}

onMounted(async () => {
  try {
    siteSetting.value = await fetchSiteSetting()
  } catch {
    siteSetting.value = {}
  }
})

watch(
  () => siteSetting.value.favicon,
  (favicon) => updateFavicon(favicon),
  { immediate: true },
)
</script>

<style scoped>
.portal-shell {
  min-height: 100vh;
  overflow-x: hidden;
  background:
    linear-gradient(180deg, rgba(234, 245, 238, 0.36), rgba(248, 247, 242, 0) 360px),
    var(--color-rice);
}

.portal-nav {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: var(--nav-height);
  gap: 24px;
  border-bottom: 1px solid var(--color-border);
  padding: 0 max(20px, calc((100vw - var(--container)) / 2));
  background: #fff;
  box-shadow: 0 1px 0 rgba(31, 61, 43, 0.04);
}

.portal-main {
  padding-top: var(--nav-height);
}

.portal-brand {
  display: inline-flex;
  align-items: center;
  min-width: 278px;
  height: 100%;
  gap: 12px;
  color: inherit;
  text-decoration: none;
}

.brand-emblem {
  display: inline-flex;
  width: 40px;
  height: 40px;
  flex: 0 0 40px;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.18);
  border-radius: 50%;
  background: #fff;
}

.brand-emblem img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.brand-text {
  min-width: 0;
}

.portal-brand strong,
.portal-brand small {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.portal-brand strong {
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 650;
}

.portal-brand small {
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.3;
}

.portal-links {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  height: 100%;
  gap: 22px;
  color: var(--color-text);
  font-size: 14px;
  white-space: nowrap;
}

.portal-links a {
  position: relative;
  display: inline-flex;
  align-items: center;
  height: 100%;
  min-height: 0;
  color: var(--color-text);
  font-weight: 600;
  text-decoration: none;
  transition:
    background 160ms ease,
    border-color 160ms ease,
    color 160ms ease;
}

.portal-links a::after {
  position: absolute;
  right: 0;
  bottom: -1px;
  left: 0;
  height: 2px;
  border-radius: 999px 999px 0 0;
  background: transparent;
  content: "";
}

.portal-links a:hover,
.portal-links a.router-link-active {
  color: var(--color-cau-green);
}

.portal-links a:hover::after,
.portal-links a.router-link-active::after {
  background: var(--color-cau-green);
}

.portal-links .internal-entry {
  height: 36px;
  min-height: 0;
  border: 1px solid rgba(0, 135, 60, 0.24);
  border-radius: var(--radius-sm);
  padding: 0 14px;
  color: var(--color-cau-green);
}

.portal-links .internal-entry::after {
  display: none;
}

.portal-links .internal-entry:hover,
.portal-links .internal-entry.router-link-active {
  border-color: var(--color-cau-green);
  background: var(--color-eco-green);
}

.nav-toggle {
  position: relative;
  display: none;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: var(--radius-sm);
  background: #fff;
  cursor: pointer;
}

.nav-toggle span {
  position: absolute;
  width: 18px;
  height: 2px;
  border-radius: 999px;
  background: var(--color-deep-green);
}

.nav-toggle span:nth-child(1) {
  transform: translateY(-6px);
}

.nav-toggle span:nth-child(3) {
  transform: translateY(6px);
}

.portal-footer {
  background:
    linear-gradient(90deg, rgba(0, 135, 60, 0.22), transparent 46%),
    var(--color-deep-green);
  color: rgba(255, 255, 255, 0.86);
  padding: 46px 0;
}

.footer-grid {
  display: flex;
  justify-content: space-between;
  gap: 32px;
}

.footer-grid strong {
  display: block;
  color: #fff;
  font-size: 18px;
}

.footer-grid p {
  max-width: 560px;
  margin: 8px 0 0;
  color: rgba(255, 255, 255, 0.74);
  line-height: 1.7;
}

.footer-address {
  display: grid;
  align-content: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.78);
}

.footer-grid span {
  display: block;
  text-align: right;
  line-height: 1.6;
}

.footer-links {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px 14px;
  margin-top: 8px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.86);
  font-size: 13px;
  text-decoration: none;
}

.footer-links a:hover {
  color: #fff;
  text-decoration: underline;
  text-underline-offset: 4px;
}

@media (max-width: 980px) {
  .portal-nav {
    gap: 12px;
    padding: 0 16px;
  }

  .portal-brand {
    flex: 1 1 auto;
    min-width: 0;
  }

  .portal-links {
    position: absolute;
    top: calc(var(--nav-height) - 1px);
    right: 12px;
    left: 12px;
    display: none;
    height: auto;
    max-height: calc(100vh - var(--nav-height) - 18px);
    overflow-y: auto;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: 8px;
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 12px 28px rgba(31, 61, 43, 0.12);
    font-size: 15px;
  }

  .portal-links.open {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
  }

  .portal-links a,
  .portal-links .internal-entry {
    justify-content: center;
    height: 42px;
    border-radius: var(--radius-sm);
    padding: 0 10px;
  }

  .portal-links a::after {
    display: none;
  }

  .portal-links a.router-link-active {
    background: var(--color-eco-green);
  }

  .nav-toggle {
    display: inline-flex;
  }
}

@media (max-width: 640px) {
  .portal-nav {
    height: 62px;
  }

  .portal-main {
    padding-top: 62px;
  }

  .brand-emblem {
    width: 34px;
    height: 34px;
    flex-basis: 34px;
  }

  .portal-brand strong {
    font-size: 16px;
  }

  .portal-brand small {
    max-width: 190px;
    font-size: 11px;
  }

  .portal-links {
    top: 61px;
  }

  .portal-links.open {
    grid-template-columns: 1fr;
  }

  .footer-grid {
    flex-direction: column;
  }

  .footer-grid span {
    text-align: left;
  }

  .footer-links {
    justify-content: flex-start;
  }
}
</style>
