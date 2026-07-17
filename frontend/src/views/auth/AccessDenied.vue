<template>
  <AuthStatePage eyebrow="访问权限" title="当前账号没有访问权限" description="该页面需要相应的系统权限。你仍可返回工作台使用已经授权的功能，如需调整权限请联系管理员。">
    <RouterLink class="primary-link" to="/dashboard">返回工作台</RouterLink>
    <RouterLink class="outline-link" to="/">返回官网</RouterLink>
  </AuthStatePage>
</template>

<script setup lang="ts">
import AuthStatePage from '../../components/AuthStatePage.vue'
</script>

<style scoped>
.primary-link,
.outline-link {
  display: inline-flex;
  align-items: center;
  border-radius: var(--radius-sm);
  padding: 8px 16px;
  font-weight: 700;
}

.primary-link {
  background: var(--color-cau-green);
  color: #fff;
}

.outline-link {
  border: 1px solid rgba(0, 135, 60, 0.28);
  color: var(--color-cau-green);
}
</style>
