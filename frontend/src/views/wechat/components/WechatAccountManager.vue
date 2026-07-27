<template>
  <section class="source-manager">
    <div class="source-toolbar">
      <el-input v-model="keyword" clearable placeholder="搜索公众号" :prefix-icon="Search" />
      <div class="source-actions">
        <el-button :icon="Refresh" :loading="syncingAll" @click="handleSyncAll">同步全部</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">添加公众号</el-button>
      </div>
    </div>

    <ListSkeleton v-if="loading" :rows="5" />
    <div v-else-if="filteredAccounts.length" class="source-list">
      <article v-for="account in filteredAccounts" :key="account.id" class="source-row">
        <div class="source-main">
          <div class="source-title">
            <h3>{{ account.name }}</h3>
            <span class="status-tag" :class="account.is_active ? 'normal' : 'archived'">{{ account.is_active ? '已启用' : '已停用' }}</span>
            <span class="source-type">{{ account.source_type_label }}</span>
          </div>
          <p v-if="account.description">{{ account.description }}</p>
          <p v-else class="source-empty">未填写简介</p>
          <div class="source-meta">
            <span>{{ account.article_count }} 篇文章</span>
            <span>最近成功：{{ account.last_sync_success_at ? formatPortalDateTime(account.last_sync_success_at) : '尚未同步' }}</span>
          </div>
          <p v-if="account.last_sync_error" class="sync-error" :title="account.last_sync_error">同步错误：{{ account.last_sync_error }}</p>
        </div>
        <div class="row-actions">
          <el-button
            v-if="account.source_type !== 'manual'"
            class="row-action-button sync-row-button"
            :icon="Refresh"
            :loading="syncingId === account.id"
            @click="handleSync(account)"
          >
            同步
          </el-button>
          <el-button class="row-action-button" :icon="EditPen" @click="openEdit(account)">编辑</el-button>
          <el-dropdown trigger="click" @command="(command: string) => command === 'delete' && handleDelete(account)">
            <el-button class="row-action-button more-action-button" :icon="MoreFilled" aria-label="更多操作" />
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="delete">删除公众号</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </article>
    </div>
    <EmptyState v-else title="暂无公众号" description="添加公众号后，可手动录入文章或配置 RSS、开放接口同步。" />

    <el-dialog v-model="dialogOpen" :title="editing ? '编辑公众号' : '添加公众号'" width="min(620px, calc(100vw - 24px))" destroy-on-close>
      <el-form label-position="top">
        <div class="form-grid">
          <el-form-item label="公众号名称" required>
            <el-input v-model="form.name" maxlength="120" />
          </el-form-item>
          <el-form-item label="同步方式" required>
            <el-select v-model="form.source_type">
              <el-option label="RSS" value="rss" />
              <el-option label="开放接口" value="json_api" />
              <el-option label="仅手动录入" value="manual" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="简介">
          <el-input v-model="form.description" maxlength="300" show-word-limit />
        </el-form-item>
        <el-form-item v-if="form.source_type !== 'manual'" :label="form.source_type === 'rss' ? 'RSS 地址' : '开放接口地址'" required>
          <el-input v-model="form.source_url" placeholder="https://..." />
        </el-form-item>
        <el-form-item v-if="form.source_type === 'json_api'" label="接口令牌环境变量">
          <el-input v-model="form.api_token_env" placeholder="例如 WECHAT_API_TOKEN_EXAMPLE" />
          <p class="field-help">如接口无需令牌可留空；这里填写环境变量名称，不填写真实令牌。</p>
        </el-form-item>
        <div class="form-grid compact">
          <el-form-item label="排序">
            <el-input-number v-model="form.sort_order" :min="0" :max="9999" />
          </el-form-item>
          <el-form-item label="状态">
            <el-switch v-model="form.is_active" active-text="启用" inactive-text="停用" />
          </el-form-item>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { EditPen, MoreFilled, Plus, Refresh, Search } from '@element-plus/icons-vue'

import {
  createWechatAccount,
  deleteWechatAccount,
  syncAllWechatAccounts,
  syncWechatAccount,
  updateWechatAccount,
  type ManagedWechatAccount,
  type WechatAccountPayload,
} from '../../../api/wechatArticles'
import EmptyState from '../../../components/EmptyState.vue'
import ListSkeleton from '../../../components/ListSkeleton.vue'
import { formatPortalDateTime } from '../../../utils/date'
import { requestErrorMessage } from '../../../utils/requestErrors'

const props = defineProps<{ accounts: ManagedWechatAccount[]; loading: boolean }>()
const emit = defineEmits<{ reload: [] }>()
const keyword = ref('')
const dialogOpen = ref(false)
const editing = ref<ManagedWechatAccount | null>(null)
const saving = ref(false)
const syncingId = ref<number | null>(null)
const syncingAll = ref(false)
const blankForm = (): WechatAccountPayload => ({
  name: '',
  description: '',
  source_type: 'manual',
  source_url: '',
  api_token_env: '',
  is_active: true,
  sort_order: 0,
})
const form = reactive<WechatAccountPayload>(blankForm())
const filteredAccounts = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  if (!query) return props.accounts
  return props.accounts.filter((item) => `${item.name} ${item.description} ${item.source_url}`.toLowerCase().includes(query))
})

function resetForm(payload = blankForm()) {
  Object.assign(form, payload)
}

function openCreate() {
  editing.value = null
  resetForm()
  dialogOpen.value = true
}

function openEdit(account: ManagedWechatAccount) {
  editing.value = account
  resetForm({
    name: account.name,
    description: account.description,
    source_type: account.source_type,
    source_url: account.source_url,
    api_token_env: account.api_token_env,
    is_active: account.is_active,
    sort_order: account.sort_order,
  })
  dialogOpen.value = true
}

async function save() {
  if (!form.name.trim()) {
    ElMessage.warning('请填写公众号名称。')
    return
  }
  if (form.source_type !== 'manual' && !form.source_url.trim()) {
    ElMessage.warning('请填写同步来源地址。')
    return
  }
  saving.value = true
  try {
    const payload = { ...form, source_url: form.source_type === 'manual' ? '' : form.source_url.trim() }
    if (editing.value) await updateWechatAccount(editing.value.id, payload)
    else await createWechatAccount(payload)
    ElMessage.success(editing.value ? '公众号已更新。' : '公众号已添加。')
    dialogOpen.value = false
    emit('reload')
  } catch (error) {
    ElMessage.error(requestErrorMessage(error, '保存失败，请检查表单内容。'))
  } finally {
    saving.value = false
  }
}

async function handleSync(account: ManagedWechatAccount) {
  syncingId.value = account.id
  try {
    const result = await syncWechatAccount(account.id)
    ElMessage.success(result.detail)
    window.setTimeout(() => emit('reload'), 2500)
  } catch (error) {
    ElMessage.error(requestErrorMessage(error, '同步任务提交失败。'))
  } finally {
    syncingId.value = null
  }
}

async function handleSyncAll() {
  syncingAll.value = true
  try {
    const result = await syncAllWechatAccounts()
    ElMessage.success(result.detail)
    window.setTimeout(() => emit('reload'), 3000)
  } catch (error) {
    ElMessage.error(requestErrorMessage(error, '同步任务提交失败。'))
  } finally {
    syncingAll.value = false
  }
}

async function handleDelete(account: ManagedWechatAccount) {
  try {
    await ElMessageBox.confirm(`删除“${account.name}”会同时删除其全部文章，是否继续？`, '删除公众号', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteWechatAccount(account.id)
    ElMessage.success('公众号已删除。')
    emit('reload')
  } catch (error: any) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(requestErrorMessage(error, '删除失败。'))
  }
}
</script>

<style scoped>
.source-manager {
  display: grid;
  gap: 14px;
}

.source-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.source-toolbar > :deep(.el-input) {
  width: min(360px, 100%);
}

.source-actions {
  display: flex;
  gap: 8px;
}

.source-list {
  display: grid;
  border-top: 1px solid var(--color-line);
}

.source-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  min-height: 112px;
  border-bottom: 1px solid var(--color-line);
  padding: 14px 4px;
}

.source-title,
.source-meta,
.row-actions {
  display: flex;
  align-items: center;
  gap: 9px;
}

.source-title h3 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 17px;
}

.row-action-button {
  min-height: 32px;
  padding: 0 12px;
  background: var(--color-white);
  color: var(--color-text);
}

.row-action-button:hover,
.row-action-button:focus-visible {
  border-color: rgba(31, 61, 43, 0.34);
  background: var(--color-panel);
  color: var(--color-deep-green);
}

.sync-row-button {
  border-color: rgba(0, 135, 60, 0.34);
  color: var(--color-cau-green);
}

.sync-row-button:hover,
.sync-row-button:focus-visible {
  border-color: var(--color-cau-green);
  background: var(--color-eco-green);
  color: var(--color-primary-hover);
}

.more-action-button {
  width: 32px;
  padding: 0;
}

.source-type {
  color: var(--color-blue-gray);
  font-size: 12px;
}

.source-main > p {
  margin: 7px 0 0;
  color: var(--color-muted);
  font-size: 13px;
}

.source-empty {
  opacity: 0.72;
}

.source-meta {
  flex-wrap: wrap;
  color: var(--color-muted);
  font-size: 12px;
}

.sync-error {
  overflow: hidden;
  color: var(--color-danger) !important;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(180px, 0.65fr);
  gap: 14px;
}

.form-grid.compact {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.field-help {
  margin: 5px 0 0;
  color: var(--color-muted);
  font-size: 12px;
}

@media (max-width: 640px) {
  .source-toolbar,
  .source-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .source-actions {
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  .source-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .row-actions {
    justify-content: flex-end;
  }

  .form-grid,
  .form-grid.compact {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>
