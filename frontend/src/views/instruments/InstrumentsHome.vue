<template>
  <InternalLayout title="仪器平台">
    <section class="instrument-page">
      <LoadErrorNotice v-if="loadError" :description="loadError" :retrying="loading" @retry="loadInstruments" />

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
        <ListSkeleton v-if="loading" :rows="6" thumbnail />
        <InstrumentList
          v-else
          :instruments="pagedInstruments"
          :total="filteredInstruments.length"
          :page="instrumentPage"
          :total-pages="instrumentTotalPages"
          :can-manage="canManageInstruments"
          @detail="goDetail"
          @edit="openEdit"
          @update:page="instrumentPage = $event"
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
import LoadErrorNotice from '../../components/LoadErrorNotice.vue'
import ListSkeleton from '../../components/ListSkeleton.vue'
import {
  createInstrument,
  fetchInstruments,
  importInstrumentsExcel,
  updateInstrument,
  type Instrument,
  type InstrumentFormPayload,
} from '../../api/instruments'
import { useSessionStore } from '../../stores/session'
import { requestErrorMessage } from '../../utils/requestErrors'
import { useListPagination } from '../../composables/useListPagination'
import { useDebouncedValue } from '../../composables/useDebouncedValue'
import InstrumentFormDialog from './components/InstrumentFormDialog.vue'
import InstrumentList from './components/InstrumentList.vue'
import InstrumentToolbar from './components/InstrumentToolbar.vue'

const session = useSessionStore()
const route = useRoute()
const router = useRouter()
const instruments = ref<Instrument[]>([])
const loading = ref(false)
const loadError = ref('')
const queryText = (value: unknown) => typeof value === 'string' ? value : ''
const queryNumber = (value: unknown, fallback: number) => Math.max(1, Number.parseInt(queryText(value), 10) || fallback)
const keyword = ref(queryText(route.query.q))
const debouncedKeyword = useDebouncedValue(keyword)
const statusFilter = ref(queryText(route.query.status))
const instrumentPage = ref(queryNumber(route.query.page, 1))
const formVisible = ref(false)
const editingInstrument = ref<Instrument | null>(null)
const saving = ref(false)
const uploadProgress = ref(0)
const importing = ref(false)
const importProgress = ref(0)

const canManageInstruments = computed(() => Boolean(session.user?.is_superuser || session.hasAnyRole(['admin', 'instrument_manager'])))
const filteredInstruments = computed(() => {
  const q = debouncedKeyword.value.trim().toLowerCase()
  return instruments.value.filter((item) => {
    const haystack = `${item.name} ${item.model || ''} ${item.location_detail || ''} ${item.manager_name || ''} ${item.notes || ''}`.toLowerCase()
    return (!statusFilter.value || item.status === statusFilter.value) && (!q || haystack.includes(q))
  })
})
const instrumentTotal = computed(() => filteredInstruments.value.length)
const { totalPages: instrumentTotalPages, paginate: paginateInstruments } = useListPagination(instrumentTotal, { page: instrumentPage })
const pagedInstruments = computed(() => paginateInstruments(filteredInstruments.value))

async function loadInstruments() {
  loading.value = true
  loadError.value = ''
  try {
    instruments.value = await fetchInstruments()
  } catch (error) {
    loadError.value = requestErrorMessage(error, '仪器列表加载失败，现有内容已保留。')
  } finally {
    loading.value = false
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
    ElMessage.error(requestErrorMessage(error, '导入失败，请确认模板列和设备图片位置。'))
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
    ElMessage.error(requestErrorMessage(error, '保存失败，请确认权限和表单内容。'))
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
  void router.replace({ name: 'instruments-home', query })
}

onMounted(async () => {
  if (!session.initialized) await session.loadCurrentUser()
  await loadInstruments()
  openEditFromQuery()
})

watch([debouncedKeyword, statusFilter], () => {
  instrumentPage.value = 1
  syncInstrumentQuery()
})
watch(instrumentPage, syncInstrumentQuery)
</script>

<style scoped>
.instrument-page,
.content-grid {
  display: grid;
  gap: 14px;
}

</style>
