<template>
  <section class="state-page">
    <div class="card state-card">
      <p class="section-kicker">账号审核</p>
      <h1>账号等待审核</h1>
      <p>你的账号已登录，但尚未通过课题组管理员审核。审核通过后即可访问内部资料、仪器平台和学生档案等功能。</p>
      <div class="state-actions">
        <RouterLink class="outline-link" to="/">返回官网</RouterLink>
        <el-button type="primary" @click="handleLogout">退出登录</el-button>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

import { useSessionStore } from '../../stores/session'

const router = useRouter()
const session = useSessionStore()

async function handleLogout() {
  await session.logout()
  await router.push('/')
}
</script>

<style scoped>
.state-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 32px;
  background: var(--color-rice);
}

.state-card {
  width: min(620px, 100%);
  padding: 38px;
}

.state-card h1 {
  margin: 0 0 12px;
  color: var(--color-deep-green);
  font-size: 34px;
}

.state-card p:not(.section-kicker) {
  margin: 0;
  color: var(--color-muted);
}

.state-actions {
  display: flex;
  gap: 12px;
  margin-top: 26px;
}

.outline-link {
  border: 1px solid var(--color-cau-green);
  border-radius: var(--radius-sm);
  padding: 8px 15px;
  color: var(--color-cau-green);
  font-weight: 700;
}
</style>
