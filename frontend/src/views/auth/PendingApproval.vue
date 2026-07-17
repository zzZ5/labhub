<template>
  <AuthStatePage eyebrow="账号审核" title="账号等待审核" description="你的账号已经创建，管理员审核通过后即可进入内部平台。你可以先返回官网，或退出后使用其他账号登录。">
    <RouterLink class="outline-link" to="/">返回官网</RouterLink>
    <el-button type="primary" @click="handleLogout">退出登录</el-button>
  </AuthStatePage>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

import { useSessionStore } from '../../stores/session'
import AuthStatePage from '../../components/AuthStatePage.vue'

const router = useRouter()
const session = useSessionStore()

async function handleLogout() {
  await session.logout()
  await router.push('/')
}
</script>

<style scoped>
.outline-link {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--color-cau-green);
  border-radius: var(--radius-sm);
  padding: 7px 15px;
  color: var(--color-cau-green);
  font-weight: 700;
}
</style>
