<template>
  <section class="login-page">
    <RouterLink class="back-link" to="/">返回官网</RouterLink>
    <div class="login-card card">
      <div>
        <p class="section-kicker">中农雨磷内部平台</p>
        <h1>内部科研管理平台</h1>
        <p>请使用课题组账号登录。新注册账号需要通过管理员审核后，才能访问内部资料、仪器平台和学生档案等功能。</p>
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
  background:
    linear-gradient(135deg, rgba(234, 245, 238, 0.76), rgba(248, 247, 242, 0.96) 46%, rgba(255, 255, 255, 0.8)),
    var(--color-rice);
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
  width: min(920px, 100%);
  grid-template-columns: 1fr 360px;
  gap: 46px;
  border-radius: var(--radius-lg);
  padding: 42px;
  box-shadow: 0 18px 44px rgba(31, 61, 43, 0.08);
}

.login-card:hover {
  border-color: var(--color-border);
  transform: none;
}

.login-card h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(30px, 4vw, 38px);
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
