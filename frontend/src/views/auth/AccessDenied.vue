<template>
  <InternalLayout title="无权访问">
    <section class="denied-card card">
      <p class="section-kicker">Permission</p>
      <h1>当前账号没有访问该页面的权限</h1>
      <p>该模块仅对管理员、硕博导师或指定管理角色开放。你仍可使用已授权的内部功能。</p>
      <RouterLink class="primary-link" to="/dashboard">返回工作台</RouterLink>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import InternalLayout from '../../layouts/InternalLayout.vue'
</script>

<style scoped>
.denied-card {
  max-width: 680px;
  padding: 34px;
}

.denied-card h1 {
  margin: 0 0 12px;
  color: var(--color-deep-green);
  font-size: 30px;
}

.denied-card p:not(.section-kicker) {
  margin: 0;
  color: var(--color-muted);
}

.primary-link {
  display: inline-flex;
  margin-top: 24px;
  border-radius: var(--radius-sm);
  padding: 10px 16px;
  background: var(--color-cau-green);
  color: #fff;
  font-weight: 700;
}
</style>
