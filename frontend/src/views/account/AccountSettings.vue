<template>
  <InternalLayout title="个人设置">
    <section class="account-page">
      <header class="surface-heading account-heading">
        <div>
          <h1>个人设置</h1>
          <p>维护个人资料和账号安全。学校身份、成员状态和系统权限由管理员维护。</p>
        </div>
      </header>

      <div class="account-layout">
        <aside class="card account-summary">
          <div class="profile-avatar large">
            <img v-if="avatarPreview" :src="avatarPreview" :alt="session.displayName" />
            <span v-else>{{ initials }}</span>
          </div>
          <h2>{{ session.displayName }}</h2>
          <p>{{ session.user?.email || session.user?.username }}</p>
          <dl>
            <div><dt>学校身份</dt><dd>{{ session.user?.profile?.school_identity_label || '-' }}</dd></div>
            <div><dt>成员状态</dt><dd>{{ session.user?.profile?.membership_status_label || '-' }}</dd></div>
            <div><dt>账号状态</dt><dd>{{ session.user?.profile?.is_approved ? '已通过审核' : '待审核' }}</dd></div>
          </dl>
          <RouterLink v-if="isStudentIdentity" class="student-profile-link" :to="{ path: '/students', query: { mine: '1' } }">
            <el-icon><Notebook /></el-icon>
            查看我的学生档案
          </RouterLink>
        </aside>

        <main class="account-panels">
          <section id="profile" class="card settings-panel">
            <div class="panel-heading">
              <div><h2>个人资料</h2><p>头像和姓名会同步到成员管理和学生档案。</p></div>
            </div>
            <el-form label-position="top" class="settings-form">
              <el-form-item label="头像">
                <ImageCropField v-model="avatarFile" :existing-url="avatarPreview" :aspect-ratio="1" :output-width="800" :output-height="800" :max-size-mb="10" preview-shape="circle" hint="未上传时使用姓名首字" @preview="avatarPreview = $event" />
              </el-form-item>
              <el-form-item label="账号名">
                <el-input v-model="profileForm.username" maxlength="150" placeholder="用于登录，不能与其他成员重复" />
              </el-form-item>
              <div class="form-pair">
                <el-form-item label="姓名"><el-input v-model="profileForm.real_name" maxlength="80" /></el-form-item>
                <el-form-item label="联系电话"><el-input v-model="profileForm.phone" maxlength="30" /></el-form-item>
              </div>
              <el-form-item label="个人简介"><el-input v-model="profileForm.bio" type="textarea" :rows="5" maxlength="1000" show-word-limit /></el-form-item>
              <div class="form-actions"><el-button type="primary" :loading="savingProfile" @click="saveProfile">保存个人资料</el-button></div>
            </el-form>
          </section>

          <section id="password" class="card settings-panel">
            <div class="panel-heading">
              <div><h2>修改密码</h2><p>修改后当前设备会保持登录。</p></div>
            </div>
            <el-form label-position="top" class="password-form" @submit.prevent>
              <el-form-item label="当前密码"><el-input v-model="passwordForm.current_password" type="password" show-password autocomplete="current-password" /></el-form-item>
              <div class="form-pair">
                <el-form-item label="新密码"><el-input v-model="passwordForm.new_password" type="password" show-password autocomplete="new-password" /></el-form-item>
                <el-form-item label="确认新密码"><el-input v-model="passwordForm.confirm_password" type="password" show-password autocomplete="new-password" /></el-form-item>
              </div>
              <div class="form-actions"><el-button type="primary" :loading="savingPassword" @click="savePassword">更新密码</el-button></div>
            </el-form>
          </section>
        </main>
      </div>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { Notebook } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { changeCurrentUserPassword, updateCurrentUserProfile } from '../../api/accounts'
import ImageCropField from '../../components/ImageCropField.vue'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { useSessionStore } from '../../stores/session'

const session = useSessionStore()
const savingProfile = ref(false)
const savingPassword = ref(false)
const avatarFile = ref<File>()
const avatarPreview = ref('')
const profileForm = reactive({ username: '', real_name: '', phone: '', bio: '' })
const passwordForm = reactive({ current_password: '', new_password: '', confirm_password: '' })

const initials = computed(() => (session.displayName || session.user?.username || '我').slice(0, 1))
const isStudentIdentity = computed(() => ['undergraduate', 'master', 'phd'].includes(session.user?.profile?.school_identity || ''))

function fillProfile() {
  profileForm.username = session.user?.username || ''
  profileForm.real_name = session.user?.profile?.real_name || ''
  profileForm.phone = session.user?.profile?.phone || ''
  profileForm.bio = session.user?.profile?.bio || ''
  avatarPreview.value = session.user?.profile?.avatar || ''
}

function errorMessage(error: any, fallback: string) {
  const data = error?.response?.data
  if (data?.detail) return data.detail
  const first = Object.values(data || {})[0]
  return Array.isArray(first) ? String(first[0]) : String(first || fallback)
}

async function saveProfile() {
  if (!profileForm.username.trim()) {
    ElMessage.warning('请填写账号名。')
    return
  }
  savingProfile.value = true
  try {
    const user = await updateCurrentUserProfile({ ...profileForm, username: profileForm.username.trim(), avatar: avatarFile.value })
    session.setUser(user)
    avatarFile.value = undefined
    fillProfile()
    ElMessage.success('个人资料已保存。')
  } catch (error: any) {
    ElMessage.error(errorMessage(error, '保存失败，请检查填写内容。'))
  } finally {
    savingProfile.value = false
  }
}

async function savePassword() {
  if (!passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password) {
    ElMessage.warning('请完整填写密码信息。')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.warning('两次输入的新密码不一致。')
    return
  }
  savingPassword.value = true
  try {
    await changeCurrentUserPassword(passwordForm)
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    ElMessage.success('密码已更新。')
  } catch (error: any) {
    ElMessage.error(errorMessage(error, '密码更新失败。'))
  } finally {
    savingPassword.value = false
  }
}

onMounted(async () => {
  if (!session.initialized) await session.loadCurrentUser()
  fillProfile()
})
</script>

<style scoped>
.account-page,
.account-panels { display: grid; gap: 18px; }
.account-layout { display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 18px; align-items: start; }
.account-summary { position: sticky; top: 94px; padding: 24px; text-align: center; }
.account-summary h2 { margin: 14px 0 4px; color: var(--color-deep-green); font-size: 21px; }
.account-summary > p { margin: 0; overflow-wrap: anywhere; color: var(--color-muted); font-size: 13px; }
.account-summary dl { margin: 22px 0; border-top: 1px solid var(--color-line); text-align: left; }
.account-summary dl div { display: flex; justify-content: space-between; gap: 14px; border-bottom: 1px solid var(--color-line); padding: 11px 0; font-size: 13px; }
.account-summary dt { color: var(--color-muted); }
.account-summary dd { margin: 0; color: var(--color-text); font-weight: 600; }
.profile-avatar { display: grid; width: 58px; height: 58px; place-items: center; overflow: hidden; border: 1px solid rgba(0, 135, 60, .16); border-radius: 50%; background: var(--color-eco-green); color: var(--color-deep-green); font-size: 20px; font-weight: 700; }
.profile-avatar.large { width: 88px; height: 88px; margin: 0 auto; font-size: 28px; }
.profile-avatar img { display: block; width: 100%; height: 100%; object-fit: cover; object-position: center; }
.student-profile-link { display: flex; align-items: center; justify-content: center; gap: 7px; min-height: 40px; border: 1px solid rgba(0, 135, 60, .24); border-radius: var(--radius-sm); color: var(--color-cau-green); font-size: 14px; font-weight: 650; }
.settings-panel { padding: 22px 24px; }
.panel-heading { margin-bottom: 18px; border-bottom: 1px solid var(--color-line); padding-bottom: 14px; }
.panel-heading h2 { margin: 0 0 4px; color: var(--color-deep-green); font-size: 20px; }
.panel-heading p { margin: 0; color: var(--color-muted); font-size: 14px; }
.settings-form, .password-form { max-width: 760px; }
.form-pair { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
.avatar-editor { display: flex; align-items: center; gap: 12px; }
.avatar-picker { display: inline-flex; align-items: center; min-height: 36px; border: 1px solid rgba(0, 135, 60, .28); border-radius: var(--radius-sm); padding: 0 13px; color: var(--color-cau-green); font-size: 14px; font-weight: 650; cursor: pointer; }
.avatar-picker input { display: none; }
.field-note { color: var(--color-muted); font-size: 13px; }
.form-actions { display: flex; justify-content: flex-end; }
@media (max-width: 820px) {
  .account-layout { grid-template-columns: 1fr; }
  .account-summary { position: static; }
}
@media (max-width: 560px) {
  .settings-panel { padding: 18px; }
  .form-pair { grid-template-columns: 1fr; gap: 0; }
  .avatar-editor { align-items: flex-start; flex-wrap: wrap; }
}
</style>
