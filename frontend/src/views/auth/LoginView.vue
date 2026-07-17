<template>
  <section class="login-page">
    <RouterLink class="back-link" to="/">返回官网</RouterLink>
    <div class="login-card card">
      <div>
        <p class="section-kicker">中农雨磷内部平台</p>
        <h1>内部科研管理平台</h1>
        <p>请使用课题组账号登录。新账号通过管理员审核后即可访问内部平台。</p>
      </div>
      <el-form class="login-form" @submit.prevent="submit">
        <el-form-item label="账号名或邮箱">
          <el-input v-model="username" autocomplete="username" placeholder="可输入账号名或邮箱" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="password" type="password" autocomplete="current-password" show-password />
        </el-form-item>
        <el-alert v-if="error" :title="error" type="error" :closable="false" />
        <el-button type="primary" :disabled="!canSubmit" :loading="session.loading" native-type="submit">登录</el-button>
      </el-form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useSessionStore } from '../../stores/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()
const username = ref('')
const password = ref('')
const error = ref('')
const canSubmit = computed(() => Boolean(username.value.trim() && password.value))
const redirectTo = computed(() => {
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
  return redirect.startsWith('/') ? redirect : '/dashboard'
})

async function submit() {
  error.value = ''
  if (!canSubmit.value) {
    error.value = '请输入账号名或邮箱和密码。'
    return
  }
  try {
    await session.login(username.value, password.value)
    await router.push(redirectTo.value)
  } catch (err: any) {
    const detail = err?.response?.data?.detail || err?.response?.data?.non_field_errors?.[0]
    error.value = detail || '账号名/邮箱或密码不正确，请重新输入。'
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 32px;
  background: var(--color-rice);
}

.back-link {
  position: fixed;
  top: 24px;
  left: 32px;
  border: 1px solid rgba(0, 135, 60, 0.18);
  border-radius: var(--radius-sm);
  padding: 7px 12px;
  background: rgba(255, 255, 255, 0.82);
  color: var(--color-cau-green);
  font-weight: 700;
}

.login-card {
  display: grid;
  width: min(780px, 100%);
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 34px;
  border-radius: var(--radius-lg);
  padding: 34px;
  box-shadow: var(--shadow-soft);
}

.login-card:hover {
  border-color: var(--color-border);
  transform: none;
}

.login-card h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(27px, 3.6vw, 34px);
  line-height: 1.2;
}

.login-card p {
  max-width: 460px;
  color: var(--color-muted);
}

.login-form {
  display: grid;
  align-content: center;
}

.login-form .el-button {
  width: 100%;
  margin-top: 8px;
}

@media (max-width: 760px) {
  .login-card {
    grid-template-columns: 1fr;
    padding: 28px;
  }
}
</style>
