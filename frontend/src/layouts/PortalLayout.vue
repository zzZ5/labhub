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
      <button v-if="menuOpen" class="portal-menu-backdrop" type="button" aria-label="关闭导航菜单" @click="closeMenu"></button>
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useSiteBrandStore } from '../stores/siteBrand'

const menuOpen = ref(false)
const brand = useSiteBrandStore()

const siteSetting = computed(() => brand.setting)
const footerUnit = computed(() => brand.siteSubtitle)
const footerAddress = computed(() => brand.address)
const footerName = computed(() => brand.siteName)
const footerDescription = computed(() => brand.footerDescription)
const brandLogo = computed(() => brand.logoUrl)
const footerLinks = computed(() => brand.externalLinks)

function closeMenu() {
  menuOpen.value = false
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') closeMenu()
}

watch(menuOpen, (open) => {
  document.body.style.overflow = open ? 'hidden' : ''
})

onMounted(async () => {
  window.addEventListener('keydown', handleKeydown)
  await brand.load()
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.portal-shell {
  min-height: 100vh;
  background:
    linear-gradient(180deg, rgba(234, 245, 238, 0.22), rgba(248, 247, 242, 0) 320px),
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
  gap: 20px;
  border-top: 2px solid var(--color-cau-green);
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 0 max(20px, calc((100vw - var(--container)) / 2));
  background: rgba(255, 255, 255, 0.98);
}

.portal-main {
  padding-top: var(--nav-height);
}

.portal-brand {
  display: inline-flex;
  align-items: center;
  min-width: 260px;
  height: 100%;
  gap: 13px;
  color: inherit;
  text-decoration: none;
}

.brand-emblem {
  display: inline-flex;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: 50%;
  background: #fff;
  box-shadow: 0 4px 12px rgba(31, 61, 43, 0.08);
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
  padding: 0;
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
  bottom: 15px;
  left: 0;
  height: 2px;
  border-radius: 999px;
  background: transparent;
  content: "";
}

.portal-links a:hover,
.portal-links a.router-link-active {
  color: var(--color-cau-green);
  background: transparent;
}

.portal-links a:hover::after,
.portal-links a.router-link-active::after {
  background: var(--color-cau-green);
}

.portal-links .internal-entry {
  height: 34px;
  min-height: 0;
  border: 1px solid rgba(0, 135, 60, 0.28);
  border-radius: 2px;
  margin-left: 2px;
  padding: 0 13px;
  color: var(--color-cau-green);
  background: transparent;
}

.portal-links .internal-entry::after {
  display: none;
}

.portal-links .internal-entry:hover,
.portal-links .internal-entry.router-link-active {
  border-color: var(--color-cau-green);
  background: rgba(234, 245, 238, 0.7);
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

.portal-menu-backdrop {
  display: none;
}

.portal-footer {
  background: var(--color-deep-green);
  color: rgba(255, 255, 255, 0.86);
  padding: 42px 0;
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
    position: fixed;
    top: calc(var(--nav-height) - 1px);
    right: 0;
    bottom: 0;
    left: auto;
    z-index: var(--z-menu);
    display: none;
    width: min(320px, 88vw);
    height: auto;
    max-height: none;
    overflow-y: auto;
    border-left: 1px solid var(--color-border);
    border-radius: 0;
    padding: 14px;
    background: #fff;
    box-shadow: -12px 0 30px rgba(31, 61, 43, 0.1);
    font-size: 15px;
  }

  .portal-links.open {
    display: grid;
    align-content: start;
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .portal-links a,
  .portal-links .internal-entry {
    justify-content: flex-start;
    height: 44px;
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
    z-index: calc(var(--z-menu) + 1);
  }

  .portal-menu-backdrop {
    position: fixed;
    inset: var(--nav-height) 0 0;
    z-index: var(--z-overlay);
    display: block;
    border: 0;
    background: rgba(17, 31, 23, 0.28);
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

  .portal-menu-backdrop {
    inset: 62px 0 0;
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
