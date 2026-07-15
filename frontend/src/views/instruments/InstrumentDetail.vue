<template>
  <InternalLayout title="仪器详情">
    <section v-if="instrument" class="instrument-detail-page">
      <RouterLink class="back-link" :to="returnTo">返回仪器平台</RouterLink>

      <article class="card detail-card">
        <img v-if="instrument.image" :src="instrument.image" :alt="instrument.name" />
        <div v-else class="detail-image-placeholder">暂无图片</div>
        <div class="detail-content">
          <div class="detail-heading">
            <div>
              <h1>{{ instrument.name }}</h1>
              <p>{{ instrument.model || '型号待补充' }}</p>
            </div>
            <div class="detail-tools">
              <span :class="['status-tag', statusClass(instrument.status)]">{{ statusText(instrument.status) }}</span>
              <button v-if="canManageInstruments && instrument.id > 0" type="button" class="edit-detail" @click="openEdit">编辑设备</button>
              <button v-if="canManageInstruments && instrument.id > 0" type="button" class="delete-detail" @click="confirmDelete">删除设备</button>
            </div>
          </div>

          <section class="info-section">
            <h2>位置</h2>
            <p>{{ instrument.location_detail || instrument.room || '未填写位置' }}</p>
          </section>

          <section class="info-section">
            <h2>使用说明</h2>
            <p class="detail-notes">{{ instrument.notes || '暂无详细说明，可在仪器台账中补充使用方法、注意事项和安全要求。' }}</p>
          </section>
        </div>
      </article>
    </section>

    <EmptyState
      v-else
      title="未找到仪器"
      description="该仪器可能已删除，或当前账号没有查看权限。"
    />

    <el-dialog v-model="formVisible" title="编辑设备" width="620px">
      <el-form label-position="top" class="instrument-form">
        <el-form-item label="仪器名称"><el-input v-model="instrumentForm.name" /></el-form-item>
        <div class="form-two-col">
          <el-form-item label="型号"><el-input v-model="instrumentForm.model" /></el-form-item>
          <el-form-item label="状态">
            <el-select v-model="instrumentForm.status">
              <el-option label="正常" value="normal" />
              <el-option label="维护中" value="maintenance" />
              <el-option label="停用" value="disabled" />
            </el-select>
          </el-form-item>
        </div>
        <el-form-item label="详细位置"><el-input v-model="instrumentForm.location_detail" /></el-form-item>
        <el-form-item label="设备图片">
          <input class="file-input" type="file" accept="image/*" @change="setInstrumentImage" />
          <small v-if="instrumentForm.image" class="upload-file-note">{{ instrumentForm.image.name }}（{{ formatFileSize(instrumentForm.image.size) }}）</small>
          <small v-else-if="instrument?.image" class="upload-file-note">不选择图片则保留当前图片。</small>
        </el-form-item>
        <el-form-item label="使用说明"><el-input v-model="instrumentForm.notes" type="textarea" :rows="8" /></el-form-item>
      </el-form>
      <template #footer>
        <div v-if="saving && uploadProgress > 0" class="upload-progress dialog-upload-progress">
          <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
          <span>{{ uploadProgress < 100 ? '正在上传设备图片，请不要关闭窗口。' : '上传完成，正在保存设备信息。' }}</span>
        </div>
        <el-button @click="formVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveInstrument">保存修改</el-button>
      </template>
    </el-dialog>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

import EmptyState from '../../components/EmptyState.vue'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { deleteInstrument, fetchInstruments, updateInstrument, type Instrument } from '../../api/instruments'
import { useSessionStore } from '../../stores/session'

const route = useRoute()
const router = useRouter()
const session = useSessionStore()
const returnTo = computed(() => {
  const source = Array.isArray(route.query.from) ? route.query.from[0] : route.query.from
  if (!source || !source.startsWith('/') || source.startsWith('//')) return '/instruments'
  return source
})
const instruments = ref<Instrument[]>([])
const formVisible = ref(false)
const saving = ref(false)
const uploadProgress = ref(0)
const instrumentForm = reactive({
  name: '',
  model: '',
  location_detail: '',
  status: 'normal',
  notes: '',
  image: undefined as File | undefined,
})

const displayInstruments = computed(() => instruments.value)
const instrument = computed(() => {
  const id = Number(route.params.id)
  return displayInstruments.value.find((item) => item.id === id) || null
})
const canManageInstruments = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin', 'pi', 'instrument_manager'])))

async function loadInstruments() {
  try {
    instruments.value = await fetchInstruments()
  } catch {
    instruments.value = []
  }
}

async function confirmDelete() {
  if (!instrument.value) return
  try {
    await ElMessageBox.confirm(`确定删除“${instrument.value.name}”吗？删除后不可恢复。`, '删除设备', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })
    await deleteInstrument(instrument.value.id)
    ElMessage.success('设备已删除。')
    await router.replace('/instruments')
  } catch (error: any) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error?.response?.data?.detail || '删除失败，请确认权限后重试。')
  }
}

function openEdit() {
  if (!instrument.value) return
  Object.assign(instrumentForm, {
    name: instrument.value.name || '',
    model: instrument.value.model || '',
    location_detail: instrument.value.location_detail || instrument.value.room || '',
    status: instrument.value.status || 'normal',
    notes: instrument.value.notes || '',
    image: undefined,
  })
  uploadProgress.value = 0
  formVisible.value = true
}

function setInstrumentImage(event: Event) {
  const input = event.target as HTMLInputElement
  instrumentForm.image = input.files?.[0]
  uploadProgress.value = 0
}

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

async function saveInstrument() {
  if (!instrument.value) return
  if (!instrumentForm.name.trim()) {
    ElMessage.warning('请填写仪器名称。')
    return
  }
  saving.value = true
  uploadProgress.value = 0
  try {
    await updateInstrument(instrument.value.id, { ...instrumentForm, name: instrumentForm.name.trim() }, (event) => {
      if (!event.total) return
      uploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    if (uploadProgress.value > 0) uploadProgress.value = 100
    ElMessage.success('设备信息已更新。')
    formVisible.value = false
    await loadInstruments()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败，请确认权限和表单内容。')
  } finally {
    saving.value = false
    setTimeout(() => {
      if (!saving.value) uploadProgress.value = 0
    }, 800)
  }
}

function statusClass(status: string) {
  if (status === 'normal') return 'normal'
  if (status === 'maintenance') return 'maintenance'
  return 'archived'
}

function statusText(status: string) {
  return (
    {
      normal: '正常',
      maintenance: '维护中',
      disabled: '停用',
    }[status] || '待确认'
  )
}

onMounted(async () => {
  if (!session.initialized) await session.loadCurrentUser()
  await loadInstruments()
})
</script>

<style scoped>
.instrument-detail-page {
  display: grid;
  gap: 18px;
}

.back-link {
  width: fit-content;
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: var(--radius-sm);
  padding: 8px 13px;
  background: #fff;
  color: var(--color-cau-green);
  font-weight: 700;
}

.detail-card {
  overflow: hidden;
  border-radius: var(--radius-lg);
}

.detail-card:hover {
  transform: none;
}

.detail-card > img {
  display: block;
  width: 100%;
  max-height: 560px;
  object-fit: contain;
  background: #f7f9f7;
  filter: saturate(0.94);
}

.detail-image-placeholder {
  display: grid;
  place-items: center;
  min-height: 260px;
  background: var(--color-eco-green);
  color: var(--color-muted);
}

.detail-content {
  padding: 30px;
}

.detail-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 20px;
}

.detail-heading h1 {
  margin: 0 0 8px;
  color: var(--color-deep-green);
  font-size: clamp(30px, 4vw, 40px);
  font-weight: 650;
  line-height: 1.2;
}

.detail-heading p,
.info-section p {
  margin: 0;
  color: var(--color-muted);
}

.info-section {
  margin-top: 22px;
}

.info-section h2 {
  margin: 0 0 8px;
  color: var(--color-deep-green);
  font-size: 20px;
  font-weight: 650;
}

.info-section p {
  line-height: 1.85;
}

.detail-tools {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 10px;
}

.edit-detail,
.delete-detail {
  border: 1px solid rgba(159, 47, 47, 0.2);
  border-radius: var(--radius-sm);
  min-height: 32px;
  padding: 0 11px;
  background: var(--color-danger-soft);
  color: var(--color-danger);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.edit-detail {
  border-color: rgba(0, 135, 60, 0.22);
  background: #fff;
  color: var(--color-cau-green);
}

.edit-detail:hover {
  background: var(--color-eco-green);
}

.delete-detail:hover {
  border-color: rgba(159, 47, 47, 0.34);
  background: #fae0e0;
}

.detail-notes {
  white-space: pre-line;
}

.instrument-form {
  display: grid;
}

.form-two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.file-input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 10px 11px;
  background: #fff;
}

.upload-file-note {
  display: block;
  margin-top: 8px;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
  word-break: break-all;
}

.upload-progress {
  display: grid;
  gap: 6px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: var(--color-soft-gray);
}

.upload-progress span {
  color: var(--color-muted);
  font-size: 13px;
}

.dialog-upload-progress {
  margin-bottom: 12px;
  text-align: left;
}

@media (max-width: 760px) {
  .detail-heading {
    display: grid;
  }

  .detail-content {
    padding: 22px;
  }

  .form-two-col {
    grid-template-columns: 1fr;
  }
}
</style>
