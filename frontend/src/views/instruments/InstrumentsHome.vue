<template>
  <InternalLayout title="仪器平台">
    <section class="instrument-page">
      <div class="page-heading">
        <div>
          <span>Instrument Platform</span>
          <h1>仪器设备台账</h1>
          <p>
            查看课题组仪器设备状态、位置、图片和使用说明，便于组内成员快速了解设备情况。
          </p>
        </div>
        <span class="heading-note">内部平台</span>
      </div>

      <section class="status-grid">
        <article v-for="item in statusSummary" :key="item.label" class="card status-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.note }}</p>
        </article>
      </section>

      <section class="content-grid">
        <div class="instrument-toolbar card">
          <input v-model="keyword" type="search" placeholder="搜索仪器名称、型号、房间或说明" />
          <select v-model="statusFilter">
            <option value="">全部状态</option>
            <option value="normal">正常</option>
            <option value="maintenance">维护中</option>
            <option value="disabled">停用</option>
          </select>
          <button v-if="canManageInstruments" type="button" @click="openCreate">新建设备</button>
        </div>
        <div class="instrument-grid">
          <article
            v-for="instrument in filteredInstruments"
            :key="instrument.id"
            class="card instrument-card"
            @click="goDetail(instrument.id)"
          >
            <img v-if="instrument.image" :src="instrument.image" :alt="instrument.name" />
            <div v-else class="instrument-image-placeholder">暂无图片</div>
            <div class="instrument-body">
              <div class="instrument-title">
                <h2>{{ instrument.name }}</h2>
                <span :class="['status-tag', statusClass(instrument.status)]">
                  {{ statusText(instrument.status) }}
                </span>
              </div>
              <p>{{ instrument.model || '型号待补充' }}</p>
              <dl>
                <div>
                  <dt>位置</dt>
                  <dd>{{ instrument.room || '未填写房间' }} {{ instrument.location_detail }}</dd>
                </div>
                <div>
                  <dt>说明</dt>
                  <dd>{{ instrument.notes || '暂无详细说明，可补充使用方法、注意事项和安全要求。' }}</dd>
                </div>
              </dl>
              <div class="instrument-actions">
                <span class="detail-link">查看设备详情</span>
                <button v-if="canManageInstruments && instrument.id > 0" type="button" class="delete-action" @click.stop="confirmDelete(instrument)">删除</button>
              </div>
            </div>
          </article>
        </div>
        <div v-if="!filteredInstruments.length" class="card empty-panel">没有找到匹配的仪器设备。</div>
      </section>

      <el-dialog v-model="formVisible" title="新建设备" width="620px">
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
          <div class="form-two-col">
            <el-form-item label="房间"><el-input v-model="instrumentForm.room" /></el-form-item>
            <el-form-item label="详细位置"><el-input v-model="instrumentForm.location_detail" /></el-form-item>
          </div>
          <el-form-item label="设备图片">
            <input class="file-input" type="file" accept="image/*" @change="setInstrumentImage" />
            <small v-if="instrumentForm.image" class="upload-file-note">{{ instrumentForm.image.name }}（{{ formatFileSize(instrumentForm.image.size) }}）</small>
          </el-form-item>
          <div v-if="saving && uploadProgress > 0" class="upload-progress">
            <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
            <span>{{ uploadProgress < 100 ? '正在上传设备图片，请不要关闭窗口。' : '上传完成，正在保存设备信息。' }}</span>
          </div>
          <el-form-item label="使用说明"><el-input v-model="instrumentForm.notes" type="textarea" :rows="4" /></el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveInstrument">保存设备</el-button>
        </template>
      </el-dialog>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

import InternalLayout from '../../layouts/InternalLayout.vue'
import { createInstrument, deleteInstrument, fetchInstruments, type Instrument } from '../../api/instruments'
import { useSessionStore } from '../../stores/session'

const session = useSessionStore()
const router = useRouter()
const instruments = ref<Instrument[]>([])
const keyword = ref('')
const statusFilter = ref('')
const formVisible = ref(false)
const saving = ref(false)
const uploadProgress = ref(0)
const instrumentForm = reactive({
  name: '',
  model: '',
  room: '',
  location_detail: '',
  status: 'normal',
  notes: '',
  image: undefined as File | undefined,
})

const displayInstruments = computed(() => instruments.value)
const canManageInstruments = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin', 'pi', 'instrument_manager'])))
const filteredInstruments = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return displayInstruments.value.filter((item) => {
    const haystack = `${item.name} ${item.model || ''} ${item.room || ''} ${item.location_detail || ''} ${item.notes || ''}`.toLowerCase()
    return (!statusFilter.value || item.status === statusFilter.value) && (!q || haystack.includes(q))
  })
})
const statusSummary = computed(() => {
  const items = displayInstruments.value
  return [
    { label: '设备总数', value: items.length, note: '当前台账设备' },
    { label: '正常设备', value: items.filter((item) => item.status === 'normal').length, note: '可按线下台账使用' },
    { label: '维护/停用', value: items.filter((item) => item.status !== 'normal').length, note: '需联系负责人确认' },
  ]
})

async function loadInstruments() {
  try {
    instruments.value = await fetchInstruments()
  } catch {
    instruments.value = []
  }
}

function openCreate() {
  Object.assign(instrumentForm, {
    name: '',
    model: '',
    room: '',
    location_detail: '',
    status: 'normal',
    notes: '',
    image: undefined,
  })
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
  if (!instrumentForm.name.trim()) {
    ElMessage.warning('请填写仪器名称。')
    return
  }
  saving.value = true
  uploadProgress.value = 0
  try {
    await createInstrument({ ...instrumentForm, name: instrumentForm.name.trim() }, (event) => {
      if (!event.total) return
      uploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    if (uploadProgress.value > 0) uploadProgress.value = 100
    ElMessage.success('设备已保存。')
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

function goDetail(id: number) {
  void router.push({ name: 'instrument-detail', params: { id } })
}

async function confirmDelete(instrument: Instrument) {
  try {
    await ElMessageBox.confirm(`确定删除“${instrument.name}”吗？删除后不可恢复。`, '删除设备', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })
    await deleteInstrument(instrument.id)
    ElMessage.success('设备已删除。')
    await loadInstruments()
  } catch (error: any) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error?.response?.data?.detail || '删除失败，请确认权限后重试。')
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
.instrument-page {
  display: grid;
  gap: 14px;
}

.page-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-lg);
  padding: 22px 26px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(251, 253, 251, 0.94) 60%, rgba(234, 245, 238, 0.86)),
    #fff;
  box-shadow: var(--shadow-flat);
}

.page-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.page-heading h1 {
  margin: 5px 0 6px;
  color: var(--color-deep-green);
  font-size: clamp(24px, 2.7vw, 31px);
  font-weight: 650;
  line-height: 1.2;
}

.page-heading p,
.instrument-card p,
.detail-model,
.offline-note p {
  margin: 0;
  color: var(--color-muted);
}

.page-heading p {
  font-size: 15px;
  line-height: 1.6;
}

.heading-note {
  flex: 0 0 auto;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: 999px;
  padding: 7px 12px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 700;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.status-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  min-height: 54px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  box-shadow: none;
}

.status-card:hover {
  transform: none;
}

.status-card span {
  min-width: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 13px;
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-card strong {
  grid-column: 2;
  grid-row: 1 / span 2;
  margin: 0;
  color: var(--color-deep-green);
  font-size: 24px;
  font-weight: 650;
  line-height: 1;
}

.status-card p {
  min-width: 0;
  margin: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.35;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.content-grid {
  display: grid;
  gap: 14px;
}

.instrument-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 150px auto;
  gap: 10px;
  align-items: center;
  padding: 12px;
  box-shadow: none;
}

.instrument-toolbar input,
.instrument-toolbar select {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 38px;
  padding: 0 12px;
  background: #fff;
  color: var(--color-text);
  font: inherit;
}

.instrument-toolbar input:focus,
.instrument-toolbar select:focus {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

.instrument-toolbar button {
  border: 1px solid var(--color-cau-green);
  border-radius: var(--radius-sm);
  min-height: 38px;
  padding: 0 14px;
  background: var(--color-cau-green);
  color: #fff;
  cursor: pointer;
  font-weight: 700;
}

.instrument-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.instrument-card {
  overflow: hidden;
  border-radius: var(--radius-lg);
  cursor: pointer;
}

.instrument-card:hover {
  border-color: rgba(0, 135, 60, 0.24);
  transform: translateY(-1px);
}

.instrument-card img {
  width: 100%;
  aspect-ratio: 16 / 8.5;
  object-fit: cover;
  filter: saturate(0.92);
}

.instrument-image-placeholder {
  display: grid;
  place-items: center;
  width: 100%;
  aspect-ratio: 16 / 8.5;
  background: var(--color-eco-green);
  color: var(--color-muted);
  font-size: 14px;
}

.instrument-body {
  padding: 22px;
}

.instrument-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 8px;
}

.instrument-title h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.instrument-card dl {
  display: grid;
  gap: 8px;
  margin: 18px 0 0;
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

.instrument-card dl div {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 12px;
  font-size: 14px;
}

.instrument-card dt {
  color: var(--color-text);
}

.instrument-card dd {
  margin: 0;
  color: var(--color-muted);
}

.instrument-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 18px;
  border-top: 1px solid var(--color-line);
  padding-top: 14px;
}

.detail-link {
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}

.delete-action {
  border: 1px solid rgba(159, 47, 47, 0.18);
  border-radius: var(--radius-sm);
  min-height: 30px;
  padding: 0 10px;
  background: var(--color-danger-soft);
  color: var(--color-danger);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.delete-action:hover {
  border-color: rgba(159, 47, 47, 0.34);
  background: #fae0e0;
}

.empty-panel {
  padding: 24px;
  color: var(--color-muted);
  text-align: center;
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
  margin-bottom: 14px;
  padding: 12px;
  background: var(--color-soft-gray);
}

.upload-progress span {
  color: var(--color-muted);
  font-size: 13px;
}

@media (max-width: 1080px) {
  .instrument-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .page-heading {
    display: grid;
  }

  .status-grid {
    grid-template-columns: repeat(3, minmax(110px, 1fr));
    overflow-x: auto;
    padding-bottom: 2px;
  }

  .instrument-grid {
    grid-template-columns: 1fr;
  }

  .instrument-toolbar,
  .form-two-col {
    grid-template-columns: 1fr;
  }
}
</style>
