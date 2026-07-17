<template>
  <div class="internal-shell">
    <aside class="internal-sidebar">
      <RouterLink class="internal-brand" to="/">
        <span class="internal-emblem">
          <img :src="brand.logoUrl" :alt="brand.siteName" />
        </span>
        <strong>{{ brand.siteName }}</strong>
      </RouterLink>
      <nav class="internal-menu" aria-label="内部平台导航">
        <RouterLink v-for="item in menu" :key="item.path" :to="item.path" :title="item.label">
          <component :is="item.icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <section class="internal-main">
      <header class="internal-topbar">
        <button ref="menuButton" class="mobile-menu-button" type="button" :aria-expanded="menuOpen" :aria-label="menuOpen ? '关闭内部平台菜单' : '打开内部平台菜单'" @click="menuOpen = !menuOpen">
          <span></span>
          菜单
        </button>
        <div class="topbar-title">
          <h1>{{ title }}</h1>
        </div>
        <div class="topbar-actions">
          <el-dropdown v-if="session.isAuthenticated" trigger="click" placement="bottom-end" @command="handleAccountCommand">
            <button class="account-trigger" type="button">
              <span class="topbar-avatar">
                <img v-if="session.user?.profile?.avatar" :src="session.user.profile.avatar" :alt="session.displayName" />
                <span v-else>{{ (session.displayName || '我').slice(0, 1) }}</span>
              </span>
              <span class="account-trigger-copy"><strong>{{ session.displayName || '未登录用户' }}</strong><small>{{ session.user?.profile?.school_identity_label || '组内成员' }}</small></span>
              <el-icon class="account-arrow"><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu class="account-dropdown">
                <el-dropdown-item command="profile" :icon="User">个人信息</el-dropdown-item>
                <el-dropdown-item v-if="isStudentIdentity" command="student" :icon="Notebook">我的学生档案</el-dropdown-item>
                <el-dropdown-item divided command="logout" :icon="SwitchButton">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <RouterLink v-else class="login-link" to="/login">登录</RouterLink>
        </div>
      </header>

      <button v-if="menuOpen" class="mobile-menu-backdrop" type="button" aria-label="关闭菜单" @click="menuOpen = false"></button>
      <nav ref="menuPanel" class="mobile-menu" :class="{ open: menuOpen }" aria-label="移动端内部平台导航">
        <RouterLink v-for="item in menu" :key="item.path" :to="item.path" @click="menuOpen = false">
          <component :is="item.icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <main class="internal-content">
        <slot />
      </main>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, Calendar, EditPen, Files, HomeFilled, Notebook, Odometer, SwitchButton, User, UserFilled } from '@element-plus/icons-vue'

import { useSessionStore } from '../stores/session'
import { useSiteBrandStore } from '../stores/siteBrand'

defineProps<{
  title: string
}>()

const menuOpen = ref(false)
const menuButton = ref<HTMLButtonElement | null>(null)
const menuPanel = ref<HTMLElement | null>(null)
const baseMenu = [
  { label: '工作台', path: '/dashboard', icon: Odometer },
  { label: '内部资料', path: '/documents', icon: Files },
  { label: '仪器平台', path: '/instruments', icon: Calendar },
  { label: '学生档案', path: '/students', icon: Notebook },
  { label: '门户内容', path: '/cms', icon: EditPen, roles: ['admin', 'editor'] },
  { label: '成员管理', path: '/members', icon: UserFilled, roles: ['admin'] },
  { label: '返回官网', path: '/', icon: HomeFilled },
]

const router = useRouter()
const session = useSessionStore()
const brand = useSiteBrandStore()
const menu = computed(() => baseMenu.filter((item) => !item.roles || session.hasAnyRole(item.roles)))
const isStudentIdentity = computed(() => ['undergraduate', 'master', 'phd'].includes(session.user?.profile?.school_identity || ''))

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  if (!session.isAuthenticated) {
    void session.loadCurrentUser()
  }
  void brand.load()
})

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') menuOpen.value = false
}

watch(menuOpen, async (open, wasOpen) => {
  document.body.style.overflow = open ? 'hidden' : ''
  await nextTick()
  if (open) {
    menuPanel.value?.querySelector<HTMLElement>('a')?.focus()
  } else if (wasOpen) {
    menuButton.value?.focus()
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})

async function handleLogout() {
  await session.logout()
  await router.replace('/login')
}

async function handleAccountCommand(command: string) {
  if (command === 'logout') {
    await handleLogout()
    return
  }
  if (command === 'student') {
    await router.push({ path: '/students', query: { mine: '1' } })
    return
  }
  await router.push('/account')
}
</script>

<style scoped>
.internal-shell {
  display: grid;
  grid-template-columns: var(--sidebar-width) minmax(0, 1fr);
  min-height: 100vh;
  overflow-x: hidden;
  background:
    linear-gradient(180deg, rgba(234, 245, 238, 0.56) 0%, rgba(245, 247, 246, 0.92) 260px),
    var(--color-soft-gray);
}

.internal-sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  border-right: 1px solid var(--color-border);
  background: var(--surface-white-strong);
  padding: 20px 14px;
}

.internal-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 1px solid var(--color-line);
  margin-bottom: 18px;
  padding: 0 10px 20px;
  color: var(--color-deep-green);
}

.internal-emblem {
  display: inline-flex;
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: 10px;
  background: #fff;
  box-shadow: var(--shadow-flat);
}

.internal-emblem img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.internal-brand strong {
  overflow: hidden;
  font-size: 20px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.internal-menu,
.mobile-menu {
  display: grid;
  gap: 6px;
}

.internal-menu a,
.mobile-menu a {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  padding: 0 12px;
  color: var(--color-muted);
  font-size: 14px;
  text-decoration: none;
  transition:
    background 160ms ease,
    border-color 160ms ease,
    color 160ms ease;
}

.internal-menu svg,
.mobile-menu svg {
  width: 18px;
  height: 18px;
  flex: 0 0 auto;
}

.internal-menu a:hover,
.internal-menu a.router-link-active,
.mobile-menu a:hover,
.mobile-menu a.router-link-active {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
  color: var(--color-cau-green);
}

.internal-menu a.router-link-active {
  box-shadow: inset 3px 0 0 var(--color-cau-green);
  font-weight: 650;
}

.internal-main {
  min-width: 0;
}

.internal-topbar {
  position: sticky;
  top: 0;
  z-index: 9;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 66px;
  border-bottom: 1px solid var(--color-border);
  padding: 0 28px;
  background: #fff;
  box-shadow: 0 1px 0 rgba(31, 61, 43, 0.03);
}

.topbar-title {
  min-width: 0;
}

.internal-topbar h1 {
  margin: 0;
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.internal-topbar h1 {
  color: var(--color-deep-green);
  font-size: 21px;
  font-weight: 650;
}

.topbar-actions {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 10px;
}

.account-trigger { display: flex; align-items: center; gap: 9px; min-height: 46px; border: 0; border-left: 1px solid var(--color-line); padding: 4px 0 4px 16px; background: transparent; color: var(--color-text); cursor: pointer; }
.topbar-avatar { display: grid; width: 34px; height: 34px; flex: 0 0 34px; place-items: center; overflow: hidden; border: 1px solid rgba(0, 135, 60, .16); border-radius: 50%; background: var(--color-eco-green); color: var(--color-deep-green); font-size: 14px; font-weight: 700; }
.topbar-avatar img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: center; }
.account-trigger-copy { display: grid; min-width: 0; row-gap: 3px; text-align: left; }
.account-trigger-copy strong, .account-trigger-copy small { display: block; max-width: 150px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.account-trigger-copy strong { color: var(--color-deep-green); font-size: 14px; font-weight: 650; line-height: 1.15; }
.account-trigger-copy small { color: var(--color-muted); font-size: 11px; line-height: 1.15; }
.account-arrow { color: var(--color-muted); transition: transform 160ms ease; }
.account-trigger:hover .account-arrow { transform: translateY(2px); }

.login-link,
.mobile-menu-button {
  border: 1px solid var(--color-cau-green);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-cau-green);
  font-weight: 600;
  text-decoration: none;
}

.login-link {
  padding: 7px 14px;
}

.mobile-menu-button {
  display: none;
  align-items: center;
  gap: 7px;
  min-height: 36px;
  padding: 0 11px;
}

.mobile-menu-button span {
  width: 14px;
  height: 2px;
  border-radius: 999px;
  background: currentColor;
  box-shadow:
    0 -5px 0 currentColor,
    0 5px 0 currentColor;
}

.mobile-menu {
  display: none;
}

.mobile-menu-backdrop {
  display: none;
}

.internal-content {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 24px 28px 40px;
}

@media (min-width: 861px) and (max-width: 1100px) {
  .internal-shell { grid-template-columns: 76px minmax(0, 1fr); }
  .internal-sidebar { padding: 16px 10px; }
  .internal-brand { justify-content: center; margin-bottom: 14px; padding: 0 0 16px; }
  .internal-brand strong,
  .internal-menu a span { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
  .internal-menu a { justify-content: center; min-height: 44px; padding: 0; }
  .internal-menu a.router-link-active { box-shadow: inset 3px 0 0 var(--color-cau-green); }
  .internal-topbar { padding: 0 20px; }
  .internal-content { padding: 20px 20px 36px; }
}

@media (max-width: 860px) {
  .internal-shell {
    display: block;
  }

  .internal-sidebar {
    display: none;
  }

  .internal-topbar {
    min-height: 62px;
    gap: 8px;
    padding: 9px 12px;
  }

  .mobile-menu-button {
    display: inline-flex;
    flex: 0 0 auto;
  }

  .internal-topbar h1 {
    font-size: 17px;
  }

  .topbar-actions {
    gap: 8px;
  }

  .account-trigger { min-height: 40px; border-left: 0; padding-left: 0; }
  .account-trigger-copy small { display: none; }
  .account-trigger-copy strong { max-width: 86px; font-size: 12px; }

  .topbar-actions :deep(.el-button) {
    min-height: 32px;
    padding: 7px 10px;
  }

  .mobile-menu {
    position: fixed;
    top: 62px;
    bottom: 0;
    left: 0;
    z-index: var(--z-menu);
    width: min(320px, 86vw);
    overflow-y: auto;
    border-right: 1px solid var(--color-border);
    padding: 14px;
    background: var(--color-white);
    box-shadow: var(--shadow-drawer);
  }

  .mobile-menu.open {
    display: grid;
    align-content: start;
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .mobile-menu a {
    justify-content: flex-start;
    min-height: 44px;
    padding: 0 12px;
    white-space: nowrap;
  }

  .mobile-menu-backdrop {
    position: fixed;
    inset: 62px 0 0;
    z-index: var(--z-overlay);
    display: block;
    border: 0;
    background: rgba(17, 31, 23, 0.28);
  }

  .mobile-menu a.router-link-active {
    font-weight: 650;
  }

  .internal-content {
    width: 100%;
    padding: 14px 12px 28px;
  }
}

@media (max-width: 420px) {
  .account-trigger-copy, .account-arrow { display: none; }

  .mobile-menu.open {
    grid-template-columns: 1fr;
  }
}
</style>
