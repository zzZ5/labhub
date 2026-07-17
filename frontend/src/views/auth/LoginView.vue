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
    error.value = loginErrorMessage(err)
  }
}

function loginErrorMessage(err: any) {
  if (!err?.response) return '无法连接服务器，请检查网络后重试。'

  const status = Number(err.response.status || 0)
  const data = err.response.data || {}
  const detail = String(data.detail || data.non_field_errors?.[0] || '')
  const normalized = detail.toLowerCase()

  if (status === 429) return '登录尝试过于频繁，请稍后再试。'
  if (status === 423 || /停用|inactive|disabled|deactivated/.test(normalized)) {
    return '账号已停用，请联系管理员。'
  }
  if (/待审核|审核|approval|approved|pending/.test(normalized)) {
    return '账号尚未通过审核，请等待管理员处理。'
  }
  if (status === 401 || status === 400) return '账号名、邮箱或密码不正确。'
  if (status >= 500) return '服务器暂时无法处理登录请求，请稍后重试。'
  return detail || '登录失败，请稍后重试。'
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
