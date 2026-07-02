<template>
  <div class="internal-shell">
    <aside class="internal-sidebar">
      <RouterLink class="internal-brand" to="/">
        <span class="internal-emblem">
          <img src="/site-icon.png" alt="中农雨磷" />
        </span>
        <strong>中农雨磷</strong>
      </RouterLink>
      <nav class="internal-menu" aria-label="内部平台导航">
        <RouterLink v-for="item in menu" :key="item.path" :to="item.path">
          <component :is="item.icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <section class="internal-main">
      <header class="internal-topbar">
        <div class="topbar-title">
          <small>中国农业大学资源与环境学院生态系</small>
          <strong>{{ title }}</strong>
        </div>
        <div class="topbar-actions">
          <div class="user-chip">{{ session.displayName || '未登录用户' }}</div>
          <el-button v-if="session.isAuthenticated" :loading="session.loading" @click="handleLogout">退出</el-button>
          <RouterLink v-else class="login-link" to="/login">登录</RouterLink>
        </div>
      </header>

      <nav class="mobile-menu" aria-label="移动端内部平台导航">
        <RouterLink v-for="item in menu" :key="item.path" :to="item.path">
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
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, EditPen, Files, HomeFilled, Notebook, Odometer, UserFilled } from '@element-plus/icons-vue'

import { useSessionStore } from '../stores/session'

defineProps<{
  title: string
}>()

const menu = [
  { label: '工作台', path: '/dashboard', icon: Odometer },
  { label: '内部资料', path: '/documents', icon: Files },
  { label: '仪器平台', path: '/instruments', icon: Calendar },
  { label: '学生档案', path: '/students', icon: Notebook },
  { label: '门户内容', path: '/cms', icon: EditPen },
  { label: '成员管理', path: '/members', icon: UserFilled },
  { label: '返回官网', path: '/', icon: HomeFilled },
]

const router = useRouter()
const session = useSessionStore()

onMounted(() => {
  if (!session.isAuthenticated) {
    void session.loadCurrentUser()
  }
})

async function handleLogout() {
  await session.logout()
  await router.replace('/login')
}
</script>

<style scoped>
.internal-shell {
  display: grid;
  grid-template-columns: 252px minmax(0, 1fr);
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
  background: rgba(255, 255, 255, 0.96);
  padding: 22px 16px;
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
  font-size: 20px;
  font-weight: 650;
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
  z-index: 8;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 74px;
  border-bottom: 1px solid var(--color-border);
  padding: 0 34px;
  background: #fff;
  box-shadow: 0 1px 0 rgba(31, 61, 43, 0.03);
}

.topbar-title {
  min-width: 0;
}

.internal-topbar small,
.internal-topbar strong {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.internal-topbar small {
  color: var(--color-muted);
  font-size: 13px;
}

.internal-topbar strong {
  color: var(--color-deep-green);
  font-size: 23px;
  font-weight: 650;
}

.topbar-actions {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 10px;
}

.user-chip {
  max-width: 180px;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.14);
  border-radius: 999px;
  padding: 7px 12px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.login-link {
  border: 1px solid var(--color-cau-green);
  border-radius: var(--radius-sm);
  padding: 7px 14px;
  color: var(--color-cau-green);
  font-weight: 600;
}

.mobile-menu {
  display: none;
}

.internal-content {
  width: min(1440px, 100%);
  padding: 30px 34px 42px;
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
    gap: 12px;
    padding: 9px 14px;
  }

  .internal-topbar small {
    display: none;
  }

  .internal-topbar strong {
    font-size: 18px;
  }

  .topbar-actions {
    gap: 8px;
  }

  .user-chip {
    max-width: 112px;
    padding: 5px 9px;
    font-size: 12px;
  }

  .topbar-actions :deep(.el-button) {
    min-height: 32px;
    padding: 7px 10px;
  }

  .mobile-menu {
    position: sticky;
    top: 62px;
    z-index: 7;
    display: flex;
    gap: 8px;
    overflow-x: auto;
    border-bottom: 1px solid var(--color-border);
    padding: 8px 12px;
    background: rgba(255, 255, 255, 0.98);
    scrollbar-width: none;
  }

  .mobile-menu::-webkit-scrollbar {
    display: none;
  }

  .mobile-menu a {
    flex: 0 0 auto;
    min-height: 36px;
    padding: 0 11px;
    white-space: nowrap;
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
  .user-chip {
    display: none;
  }
}
</style>
