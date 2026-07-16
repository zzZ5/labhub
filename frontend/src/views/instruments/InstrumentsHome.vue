<template>
  <InternalLayout title="仪器平台">
    <section class="instrument-page">
      <div class="page-heading">
        <div>
          <h1>仪器平台</h1>
          <p>查看课题组仪器设备状态、位置、图片和使用说明，便于组内成员快速了解设备情况。</p>
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
        <InstrumentToolbar
          v-model:keyword="keyword"
          v-model:status="statusFilter"
          :can-manage="canManageInstruments"
          :importing="importing"
          :progress="importProgress"
          @create="openCreate"
          @import="handleExcelImport"
        />
        <InstrumentList
          :instruments="pagedInstruments"
          :total="filteredInstruments.length"
          :page="instrumentPage"
          :total-pages="instrumentTotalPages"
          :page-size="instrumentPageSize"
          :can-manage="canManageInstruments"
          @detail="goDetail"
          @edit="openEdit"
          @update:page="instrumentPage = $event"
          @update:page-size="instrumentPageSize = $event"
        />
      </section>

      <InstrumentFormDialog
        v-model:open="formVisible"
        :instrument="editingInstrument"
        :saving="saving"
        :progress="uploadProgress"
        @save="saveInstrument"
      />
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

import InternalLayout from '../../layouts/InternalLayout.vue'
import {
  createInstrument,
  fetchInstruments,
  importInstrumentsExcel,
  updateInstrument,
  type Instrument,
  type InstrumentFormPayload,
} from '../../api/instruments'
import { useSessionStore } from '../../stores/session'
import InstrumentFormDialog from './components/InstrumentFormDialog.vue'
import InstrumentList from './components/InstrumentList.vue'
import InstrumentToolbar from './components/InstrumentToolbar.vue'

const session = useSessionStore()
const route = useRoute()
const router = useRouter()
const instruments = ref<Instrument[]>([])
const queryText = (value: unknown) => typeof value === 'string' ? value : ''
const queryNumber = (value: unknown, fallback: number) => Math.max(1, Number.parseInt(queryText(value), 10) || fallback)
const keyword = ref(queryText(route.query.q))
const statusFilter = ref(queryText(route.query.status))
const instrumentPage = ref(queryNumber(route.query.page, 1))
const initialPageSize = queryNumber(route.query.size, 12)
const instrumentPageSize = ref([12, 24, 48].includes(initialPageSize) ? initialPageSize : 12)
const formVisible = ref(false)
const editingInstrument = ref<Instrument | null>(null)
const saving = ref(false)
const uploadProgress = ref(0)
const importing = ref(false)
const importProgress = ref(0)

const canManageInstruments = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin', 'instrument_manager'])))
const filteredInstruments = computed(() => {
  const q = keyword.value.trim().toLowerCase()
  return instruments.value.filter((item) => {
    const haystack = `${item.name} ${item.model || ''} ${item.location_detail || ''} ${item.manager_name || ''} ${item.notes || ''}`.toLowerCase()
    return (!statusFilter.value || item.status === statusFilter.value) && (!q || haystack.includes(q))
  })
})
const instrumentTotalPages = computed(() => Math.max(1, Math.ceil(filteredInstruments.value.length / instrumentPageSize.value)))
const pagedInstruments = computed(() => {
  const start = (instrumentPage.value - 1) * instrumentPageSize.value
  return filteredInstruments.value.slice(start, start + instrumentPageSize.value)
})
const statusSummary = computed(() => [
  { label: '设备总数', value: instruments.value.length, note: '当前台账设备' },
  { label: '正常设备', value: instruments.value.filter((item) => item.status === 'normal').length, note: '可按线下台账使用' },
  { label: '维护/停用', value: instruments.value.filter((item) => item.status !== 'normal').length, note: '需联系负责人确认' },
])

async function loadInstruments() {
  try {
    instruments.value = await fetchInstruments()
  } catch {
    instruments.value = []
  }
}

function openCreate() {
  editingInstrument.value = null
  uploadProgress.value = 0
  formVisible.value = true
}

function openEdit(instrument: Instrument) {
  editingInstrument.value = instrument
  uploadProgress.value = 0
  formVisible.value = true
}

function clampInstrumentPage() {
  if (instrumentPage.value > instrumentTotalPages.value) instrumentPage.value = instrumentTotalPages.value
  if (instrumentPage.value < 1) instrumentPage.value = 1
}

function openEditFromQuery() {
  if (!canManageInstruments.value) return
  const editId = Number(route.query.edit)
  if (!editId) return
  const target = instruments.value.find((item) => item.id === editId)
  if (!target) return
  openEdit(target)
  const { edit: _edit, ...query } = route.query
  void router.replace({ name: 'instruments-home', query })
}

async function handleExcelImport(file: File) {
  if (!file.name.toLowerCase().endsWith('.xlsx')) {
    ElMessage.warning('请上传 .xlsx 文件。')
    return
  }
  importing.value = true
  importProgress.value = 0
  try {
    const result = await importInstrumentsExcel(file, (event) => {
      if (event.total) importProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
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

async function saveInstrument(payload: InstrumentFormPayload) {
  saving.value = true
  uploadProgress.value = 0
  try {
    const progressHandler = (event: any) => {
      if (event.total) uploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    }
    if (editingInstrument.value) await updateInstrument(editingInstrument.value.id, payload, progressHandler)
    else await createInstrument(payload, progressHandler)
    if (uploadProgress.value > 0) uploadProgress.value = 100
    ElMessage.success(editingInstrument.value ? '设备信息已更新。' : '设备已保存。')
    formVisible.value = false
    editingInstrument.value = null
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
.instrument-page,
.content-grid {
  display: grid;
  gap: 14px;
}

.page-heading {
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-lg);
  padding: 22px 26px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(251, 253, 251, 0.94) 60%, rgba(234, 245, 238, 0.86));
  box-shadow: var(--shadow-flat);
}

.page-heading h1 {
  margin: 0 0 6px;
  color: var(--color-deep-green);
  font-size: clamp(24px, 2.7vw, 31px);
  font-weight: 650;
  line-height: 1.2;
}

.page-heading p {
  margin: 0;
  color: var(--color-muted);
  font-size: 15px;
  line-height: 1.6;
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

.status-card span,
.status-card p {
  min-width: 0;
  overflow: hidden;
  color: var(--color-muted);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-card span {
  font-size: 13px;
  font-weight: 600;
}

.status-card strong {
  grid-column: 2;
  grid-row: 1 / span 2;
  color: var(--color-deep-green);
  font-size: 24px;
  font-weight: 650;
  line-height: 1;
}

.status-card p {
  margin: 0;
  font-size: 12px;
  line-height: 1.35;
}

@media (max-width: 760px) {
  .status-grid {
    grid-template-columns: repeat(3, minmax(110px, 1fr));
    overflow-x: auto;
    padding-bottom: 2px;
  }
}
</style>
