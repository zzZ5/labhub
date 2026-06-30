<template>
  <div class="internal-shell">
    <aside class="internal-sidebar">
      <RouterLink class="internal-brand" to="/">
        <span class="internal-emblem">
          <img src="/site-icon.png" alt="中农雨磷" />
        </span>
        <strong>中农雨磷</strong>
      </RouterLink>
      <nav>
        <RouterLink v-for="item in menu" :key="item.path" :to="item.path">
          <component :is="item.icon" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>
    <section class="internal-main">
      <header class="internal-topbar">
        <div>
          <small>中国农业大学资源与环境学院生态系</small>
          <strong>{{ title }}</strong>
        </div>
        <div class="topbar-actions">
          <div class="user-chip">{{ session.displayName || '未登录用户' }}</div>
          <el-button v-if="session.isAuthenticated" :loading="session.loading" @click="handleLogout">退出</el-button>
          <RouterLink v-else class="login-link" to="/login">登录</RouterLink>
        </div>
      </header>
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
  border-radius: 10px;
  border: 1px solid rgba(0, 135, 60, 0.16);
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

.internal-sidebar nav {
  display: grid;
  gap: 6px;
}

.internal-sidebar nav a {
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

.internal-sidebar svg {
  width: 18px;
  height: 18px;
}

.internal-sidebar nav a:hover,
.internal-sidebar nav a.router-link-active {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
  color: var(--color-cau-green);
}

.internal-sidebar nav a.router-link-active {
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
  background: rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(8px);
}

.internal-topbar small,
.internal-topbar strong {
  display: block;
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

.user-chip {
  border: 1px solid rgba(0, 135, 60, 0.14);
  border-radius: 999px;
  padding: 7px 12px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 600;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.login-link {
  border: 1px solid var(--color-cau-green);
  border-radius: var(--radius-sm);
  padding: 7px 14px;
  color: var(--color-cau-green);
  font-weight: 600;
}

.internal-content {
  width: min(1440px, 100%);
  padding: 30px 34px 42px;
}

@media (max-width: 860px) {
  .internal-shell {
    grid-template-columns: 1fr;
  }

  .internal-sidebar {
    position: sticky;
    top: 0;
    height: auto;
    overflow: visible;
    z-index: 10;
    border-right: 0;
    border-bottom: 1px solid var(--color-border);
    padding: 16px;
  }

  .internal-sidebar nav {
    display: flex;
    overflow-x: auto;
    padding-bottom: 2px;
  }

  .internal-brand {
    margin-bottom: 12px;
    padding-bottom: 14px;
  }

  .internal-sidebar nav a {
    white-space: nowrap;
  }

  .internal-content {
    padding: 20px;
  }

  .internal-topbar {
    display: grid;
    gap: 10px;
    padding: 16px 20px;
  }
}
</style>
