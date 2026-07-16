<template>
  <InternalLayout title="仪器平台">
    <section class="instrument-page">
      <div class="page-heading">
        <div>
          <h1>仪器平台</h1>
          <p>
            查看课题组仪器设备状态、位置、图片和使用说明，便于组内成员快速了解设备情况。
          </p>
        </div>
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
          <input v-model="keyword" type="search" placeholder="搜索仪器名称、型号、位置或说明" />
          <select v-model="statusFilter">
            <option value="">全部状态</option>
            <option value="normal">正常</option>
            <option value="maintenance">维护中</option>
            <option value="disabled">停用</option>
          </select>
          <input ref="excelInputRef" class="hidden-file-input" type="file" accept=".xlsx" @change="handleExcelImport" />
          <a v-if="canManageInstruments" class="toolbar-link" href="/templates/instruments-import-template.xlsx" download>下载模板</a>
          <button v-if="canManageInstruments" type="button" class="secondary-action" @click="chooseExcelFile">导入 Excel</button>
          <button v-if="canManageInstruments" type="button" @click="openCreate">新建设备</button>
        </div>
        <p v-if="canManageInstruments" class="import-tip">
          模板只需填写：仪器名称、型号、状态、详细位置、设备图片、使用说明；图片插入对应行即可批量导入。
        </p>
        <div v-if="importing" class="upload-progress import-progress">
          <el-progress :percentage="importProgress" :status="importProgress === 100 ? 'success' : undefined" />
          <span>{{ importProgress < 100 ? '正在上传设备表，请不要关闭页面。' : '上传完成，正在解析仪器和图片。' }}</span>
        </div>
        <div class="instrument-grid">
          <article
            v-for="instrument in pagedInstruments"
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
                  <dd>{{ instrument.location_detail || '未填写位置' }}</dd>
                </div>
                <div v-if="instrument.manager_name">
                  <dt>负责人</dt>
                  <dd>{{ instrument.manager_name }}</dd>
                </div>
                <div>
                  <dt>说明</dt>
                  <dd class="instrument-note-preview">{{ shortNote(instrument.notes) }}</dd>
                </div>
              </dl>
              <div class="instrument-actions">
                <span class="detail-link">查看设备详情</span>
                <button v-if="canManageInstruments && instrument.id > 0" type="button" class="edit-action" @click.stop="openEdit(instrument)">编辑</button>
              </div>
            </div>
          </article>
        </div>
        <div v-if="!filteredInstruments.length" class="card empty-panel">没有找到匹配的仪器设备。</div>
        <div v-if="filteredInstruments.length > 12" class="list-pager">
          <span class="pager-summary">共 {{ filteredInstruments.length }} 台设备</span>
          <div class="pager-controls">
            <button class="pager-nav" type="button" :disabled="instrumentPage === 1" @click="instrumentPage -= 1">上一页</button>
            <PageJump compact inline :page="instrumentPage" :total-pages="instrumentTotalPages" @change="instrumentPage = $event" />
            <button class="pager-nav" type="button" :disabled="instrumentPage === instrumentTotalPages" @click="instrumentPage += 1">下一页</button>
          </div>
          <el-select v-model="instrumentPageSize" size="small" class="page-size-select" placeholder="分页">
            <el-option label="12 台/页" :value="12" />
            <el-option label="24 台/页" :value="24" />
            <el-option label="48 台/页" :value="48" />
          </el-select>
        </div>
      </section>

      <el-dialog v-model="formVisible" :title="editingInstrumentId ? '编辑设备' : '新建设备'" width="620px">
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
          <el-form-item label="详细位置"><el-input v-model="instrumentForm.location_detail" placeholder="如 沃土实验室一楼" /></el-form-item>
          <el-form-item label="设备图片">
            <input class="file-input" type="file" accept="image/*" @change="setInstrumentImage" />
            <small v-if="editingImageUrl && !instrumentForm.image" class="upload-file-note">当前已有图片；如需更换，请重新选择图片。</small>
            <small v-if="instrumentForm.image" class="upload-file-note">{{ instrumentForm.image.name }}（{{ formatFileSize(instrumentForm.image.size) }}）</small>
          </el-form-item>
          <el-form-item label="使用说明"><el-input v-model="instrumentForm.notes" type="textarea" :rows="8" placeholder="可填写操作步骤、注意事项、联系人或维护要求。" /></el-form-item>
        </el-form>
        <template #footer>
          <div v-if="saving && uploadProgress > 0" class="upload-progress dialog-upload-progress">
            <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
            <span>{{ uploadProgress < 100 ? '正在上传设备图片，请不要关闭窗口。' : '上传完成，正在保存设备信息。' }}</span>
          </div>
          <el-button @click="formVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveInstrument">{{ editingInstrumentId ? '保存修改' : '保存设备' }}</el-button>
        </template>
      </el-dialog>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

import PageJump from '../../components/PageJump.vue'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { createInstrument, fetchInstruments, importInstrumentsExcel, updateInstrument, type Instrument } from '../../api/instruments'
import { useSessionStore } from '../../stores/session'

const session = useSessionStore()
const route = useRoute()
const router = useRouter()
const instruments = ref<Instrument[]>([])
const queryText = (value: unknown) => typeof value === 'string' ? value : ''
const queryNumber = (value: unknown, fallback: number) => Math.max(1, Number.parseInt(queryText(value), 10) || fallback)
const keyword = ref(queryText(route.query.q))
const statusFilter = ref(queryText(route.query.status))
const instrumentPage = ref(queryNumber(route.query.page, 1))
const instrumentPageSize = ref([12, 24, 48].includes(queryNumber(route.query.size, 12)) ? queryNumber(route.query.size, 12) : 12)
const formVisible = ref(false)
const saving = ref(false)
const editingInstrumentId = ref<number | null>(null)
const editingImageUrl = ref('')
const uploadProgress = ref(0)
const importing = ref(false)
const importProgress = ref(0)
const excelInputRef = ref<HTMLInputElement | null>(null)
const instrumentForm = reactive({
  name: '',
  model: '',
  location_detail: '',
  status: 'normal',
  notes: '',
  image: undefined as File | undefined,
})

const displayInstruments = computed(() => instruments.value)
const canManageInstruments = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin', 'instrument_manager'])))
const filteredInstruments = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return displayInstruments.value.filter((item) => {
    const haystack = `${item.name} ${item.model || ''} ${item.location_detail || ''} ${item.manager_name || ''} ${item.notes || ''}`.toLowerCase()
    return (!statusFilter.value || item.status === statusFilter.value) && (!q || haystack.includes(q))
  })
})
const instrumentTotalPages = computed(() => Math.max(1, Math.ceil(filteredInstruments.value.length / instrumentPageSize.value)))
const pagedInstruments = computed(() => {
  const start = (instrumentPage.value - 1) * instrumentPageSize.value
  return filteredInstruments.value.slice(start, start + instrumentPageSize.value)
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
  editingInstrumentId.value = null
  editingImageUrl.value = ''
  Object.assign(instrumentForm, {
    name: '',
    model: '',
    location_detail: '',
    status: 'normal',
    notes: '',
    image: undefined,
  })
  formVisible.value = true
}

function openEdit(instrument: Instrument) {
  editingInstrumentId.value = instrument.id
  editingImageUrl.value = instrument.image || ''
  Object.assign(instrumentForm, {
    name: instrument.name || '',
    model: instrument.model || '',
    location_detail: instrument.location_detail || '',
    status: instrument.status || 'normal',
    notes: instrument.notes || '',
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

function chooseExcelFile() {
  excelInputRef.value?.click()
}

function clampInstrumentPage() {
  if (instrumentPage.value > instrumentTotalPages.value) instrumentPage.value = instrumentTotalPages.value
  if (instrumentPage.value < 1) instrumentPage.value = 1
}

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function shortNote(note: string) {
  const text = (note || '').replace(/\s+/g, ' ').trim()
  if (!text) return '暂无详细说明，可补充使用方法、注意事项和安全要求。'
  return text.length > 58 ? `${text.slice(0, 58)}...` : text
}

function openEditFromQuery() {
  if (!canManageInstruments.value) return
  const editId = Number(route.query.edit)
  if (!editId) return
  const target = instruments.value.find((item) => item.id === editId)
  if (target) {
    openEdit(target)
    const { edit: _edit, ...query } = route.query
    void router.replace({ name: 'instruments-home', query })
  }
}

async function handleExcelImport(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.xlsx')) {
    ElMessage.warning('请上传 .xlsx 文件。')
    return
  }
  importing.value = true
  importProgress.value = 0
  try {
    const result = await importInstrumentsExcel(file, (progressEvent) => {
      if (!progressEvent.total) return
      importProgress.value = Math.min(99, Math.round((progressEvent.loaded / progressEvent.total) * 100))
    })
    importProgress.value = 100
    ElMessage.success(`导入完成：新增 ${result.created} 条，更新 ${result.updated} 条，匹配图片 ${result.images} 张。`)
    await loadInstruments()
    clampInstrumentPage()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '导入失败，请确认模板列和设备图片位置。')
  } finally {
    importing.value = false
    setTimeout(() => {
      if (!importing.value) importProgress.value = 0
    }, 900)
  }
}

async function saveInstrument() {
  if (!instrumentForm.name.trim()) {
    ElMessage.warning('请填写仪器名称。')
    return
  }
  saving.value = true
  uploadProgress.value = 0
  try {
    const payload = { ...instrumentForm, name: instrumentForm.name.trim() }
    const progressHandler = (event: any) => {
      if (!event.total) return
      uploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    }
    if (editingInstrumentId.value) await updateInstrument(editingInstrumentId.value, payload, progressHandler)
    else await createInstrument(payload, progressHandler)
    if (uploadProgress.value > 0) uploadProgress.value = 100
    ElMessage.success(editingInstrumentId.value ? '设备信息已更新。' : '设备已保存。')
    formVisible.value = false
    editingInstrumentId.value = null
    editingImageUrl.value = ''
    await loadInstruments()
    clampInstrumentPage()
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
  void router.push({ name: 'instrument-detail', params: { id }, query: { from: route.fullPath } })
}

function syncInstrumentQuery() {
  const query: Record<string, string> = {}
  if (keyword.value.trim()) query.q = keyword.value.trim()
  if (statusFilter.value) query.status = statusFilter.value
  if (instrumentPage.value > 1) query.page = String(instrumentPage.value)
  if (instrumentPageSize.value !== 12) query.size = String(instrumentPageSize.value)
  void router.replace({ name: 'instruments-home', query })
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
  openEditFromQuery()
})

watch([keyword, statusFilter], () => {
  instrumentPage.value = 1
  syncInstrumentQuery()
})

watch(instrumentPageSize, () => {
  instrumentPage.value = 1
  syncInstrumentQuery()
})

watch(instrumentPage, syncInstrumentQuery)

watch(instrumentTotalPages, clampInstrumentPage)
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

.page-heading h1 {
  margin: 0 0 6px;
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
  grid-template-columns: minmax(0, 1fr) 150px auto auto auto;
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

.toolbar-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 135, 60, 0.22);
  border-radius: var(--radius-sm);
  min-height: 38px;
  padding: 0 14px;
  background: #fff;
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}

.toolbar-link:hover {
  background: var(--color-eco-green);
}

.instrument-toolbar .secondary-action {
  background: #fff;
  color: var(--color-cau-green);
}

.instrument-toolbar .secondary-action:hover {
  background: var(--color-eco-green);
}

.hidden-file-input {
  display: none;
}

.import-progress {
  margin: -4px 0 0;
}

.import-tip {
  margin: -6px 4px 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
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
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: contain;
  background: #f7f9f7;
  filter: saturate(0.96);
}

.instrument-image-placeholder {
  display: grid;
  place-items: center;
  width: 100%;
  aspect-ratio: 4 / 3;
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
  margin-right: auto;
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}

.edit-action {
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: var(--radius-sm);
  min-height: 30px;
  padding: 0 10px;
  background: #fff;
  color: var(--color-cau-green);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.edit-action:hover {
  background: var(--color-eco-green);
}

.empty-panel {
  padding: 24px;
  color: var(--color-muted);
  text-align: center;
}

.list-pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: nowrap;
  gap: 12px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  background: #fff;
  color: var(--color-muted);
  font-size: 14px;
}

.pager-summary {
  flex: 0 0 auto;
  color: var(--color-text);
  font-weight: 700;
  white-space: nowrap;
}

.pager-controls {
  display: flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.page-size-select {
  flex: 0 0 112px;
  width: 128px;
}

.list-pager button {
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: var(--radius-sm);
  min-height: 32px;
  padding: 0 12px;
  background: #fff;
  color: var(--color-cau-green);
  cursor: pointer;
  font-weight: 700;
}

.list-pager .pager-nav {
  width: 72px;
  padding: 0;
  text-align: center;
}

.list-pager button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
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

.dialog-upload-progress {
  margin-bottom: 12px;
  text-align: left;
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

  .list-pager {
    justify-content: center;
    flex-wrap: wrap;
  }

  .pager-summary {
    width: 100%;
    text-align: center;
  }
}
</style>
