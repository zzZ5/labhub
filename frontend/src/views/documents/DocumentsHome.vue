<template>
  <InternalLayout title="内部资料库">
    <LoadErrorNotice v-if="loadError" :description="loadError" :retrying="loading" @retry="reloadLibrary" />

    <section :class="['document-shell', { 'is-reading': previewDocument }]">
      <DocumentSidebar
        :categories="displayCategories"
        :documents="pagedReaderDocuments"
        :preview-document="previewDocument"
        :active-category="activeCategory"
        :total="displayDocuments.length"
        :page="readerPage"
        :total-pages="readerTotalPages"
        @select-category="selectCategory"
        @preview="handlePreview"
        @close-preview="closePreview"
        @update:page="readerPage = $event"
      />

      <main class="document-main">
        <FilterToolbar v-if="!previewDocument" class="filter-bar" has-filters>
          <template #primary>
            <div class="filter-title">
              <strong>{{ activeCategoryName }}</strong>
              <span>{{ loading ? '正在更新资料列表' : `共 ${displayDocuments.length} 条资料` }}</span>
            </div>
            <el-input v-model="keyword" placeholder="搜索实验方法、论文材料、项目资料或组会资料" clearable @keyup.enter="loadDocuments()" />
          </template>
          <template #filters>
            <el-select v-model="sortOrder" aria-label="资料排序">
              <el-option label="最新添加" value="created_desc" />
              <el-option label="最早添加" value="created_asc" />
              <el-option label="最近更新" value="updated_desc" />
              <el-option label="标题顺序" value="title_asc" />
            </el-select>
          </template>
          <template #actions>
            <el-button type="primary" @click="loadDocuments()">搜索</el-button>
            <el-button plain @click="openCreate">上传资料</el-button>
            <el-button plain @click="openImport">批量导入</el-button>
          </template>
        </FilterToolbar>

        <DocumentReader
          v-if="previewDocument"
          :document="previewDocument"
          :preview-url="previewUrl"
          :can-embed="canEmbedPreview(previewDocument)"
          @close="closePreview"
          @edit="openEdit"
          @delete="handleDelete"
          @download="handleDownload"
        />

        <ListSkeleton v-else-if="loading" :rows="6" />
        <EmptyState
          v-else-if="!displayDocuments.length"
          :icon="Files"
          title="暂无可见资料"
          description="当前分类下还没有资料。"
        />
        <DocumentList
          v-else
          :documents="pagedDocuments"
          :total="displayDocuments.length"
          :page="documentPage"
          :total-pages="documentTotalPages"
          @preview="handlePreview"
          @edit="openEdit"
          @download="handleDownload"
          @update:page="documentPage = $event"
        />
      </main>
    </section>

    <DocumentUploadDialog
      v-model:open="uploadVisible"
      :document="editingDocument"
      :categories="displayCategories"
      :default-category-id="activeCategoryId"
      :saving="uploading"
      :progress="uploadProgress"
      @save="submitDocument"
    />
    <DocumentImportDialog
      v-model:open="importVisible"
      :saving="importing"
      :progress="importProgress"
      :result="importResult"
      @import="submitImport"
    />
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Files } from '@element-plus/icons-vue'

import EmptyState from '../../components/EmptyState.vue'
import LoadErrorNotice from '../../components/LoadErrorNotice.vue'
import ListSkeleton from '../../components/ListSkeleton.vue'
import InternalLayout from '../../layouts/InternalLayout.vue'
import FilterToolbar from '../../components/FilterToolbar.vue'
import {
  createDocument,
  deleteDocument,
  downloadDocument,
  fetchDocumentCategories,
  fetchDocument,
  fetchDocuments,
  importDocumentsExcel,
  previewDocumentUrl,
  updateDocument,
  type DocumentImportResult,
  type DocumentFormPayload,
  type DocumentImportPayload,
  type DocumentCategory,
  type LabDocument,
} from '../../api/documents'
import DocumentList from './components/DocumentList.vue'
import DocumentImportDialog from './components/DocumentImportDialog.vue'
import DocumentReader from './components/DocumentReader.vue'
import DocumentSidebar from './components/DocumentSidebar.vue'
import DocumentUploadDialog from './components/DocumentUploadDialog.vue'
import { categoryName, currentFilename } from './documentPresentation'
import { useDocumentPreviewPolling } from './composables/useDocumentPreviewPolling'
import { useListPagination } from '../../composables/useListPagination'
import { requestErrorMessage } from '../../utils/requestErrors'

const route = useRoute()
const router = useRouter()
const categories = ref<DocumentCategory[]>([])
const documents = ref<LabDocument[]>([])
const loading = ref(false)
const loadError = ref('')
const keyword = ref(String(route.query.q || ''))
const activeCategory = ref(String(route.query.category || ''))
const sortOrder = ref(String(route.query.sort || 'created_desc'))
const documentPage = ref(Math.max(1, Number(route.query.page) || 1))
const readerPage = ref(1)
const readerPageSize = 12
const uploadVisible = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const importVisible = ref(false)
const importing = ref(false)
const importProgress = ref(0)
const importResult = ref<DocumentImportResult | null>(null)
const previewDocument = ref<LabDocument | null>(null)
const editingDocument = ref<LabDocument | null>(null)
const initialPreviewId = Math.max(0, Number(route.query.document) || 0)

useDocumentPreviewPolling(previewDocument, async (documentId) => {
  const refreshed = await fetchDocument(documentId)
  const index = documents.value.findIndex((item) => item.id === documentId)
  if (index >= 0) documents.value[index] = refreshed
  return refreshed
})

const displayCategories = computed(() => categories.value)
const displayDocuments = computed(() => {
  const sorted = [...documents.value]
  if (sortOrder.value === 'created_asc') return sorted.sort((a, b) => documentTime(a, 'created') - documentTime(b, 'created'))
  if (sortOrder.value === 'updated_desc') return sorted.sort((a, b) => documentTime(b, 'updated') - documentTime(a, 'updated'))
  if (sortOrder.value === 'title_asc') return sorted.sort((a, b) => a.title.localeCompare(b.title, 'zh-CN'))
  return sorted.sort((a, b) => documentTime(b, 'created') - documentTime(a, 'created'))
})
const documentTotal = computed(() => displayDocuments.value.length)
const { totalPages: documentTotalPages, paginate: paginateDocuments } = useListPagination(documentTotal, { page: documentPage })
const pagedDocuments = computed(() => paginateDocuments(displayDocuments.value))
const readerTotalPages = computed(() => Math.max(1, Math.ceil(displayDocuments.value.length / readerPageSize)))
const pagedReaderDocuments = computed(() => {
  const start = (readerPage.value - 1) * readerPageSize
  return displayDocuments.value.slice(start, start + readerPageSize)
})
const previewUrl = computed(() => (previewDocument.value ? previewDocumentUrl(previewDocument.value) : ''))
const activeCategoryName = computed(() => {
  if (!activeCategory.value) return '全部资料'
  return categoryName(displayCategories.value.find((item) => item.slug === activeCategory.value)) || '当前分类'
})

function selectCategory(slug: string) {
  activeCategory.value = slug
  documentPage.value = 1
  readerPage.value = 1
  previewDocument.value = null
  void loadDocuments(false)
}

async function loadCategories() {
  try {
    categories.value = await fetchDocumentCategories()
  } catch (error) {
    loadError.value = requestErrorMessage(error, '资料分类加载失败，请确认当前账号权限后重试。')
  }
}

async function loadDocuments(resetPages = true) {
  loading.value = true
  try {
    documents.value = await fetchDocuments({
      search: keyword.value || undefined,
      category__slug: activeCategory.value || undefined,
    })
    if (resetPages) {
      documentPage.value = 1
      readerPage.value = 1
    }
  } catch (error) {
    loadError.value = requestErrorMessage(error, '资料列表加载失败，现有内容已保留。')
  } finally {
    loading.value = false
  }
}

function closeUploadDialog() {
  uploadVisible.value = false
  editingDocument.value = null
}

async function reloadLibrary() {
  loadError.value = ''
  await Promise.all([loadCategories(), loadDocuments(false)])
}

function openCreate() {
  editingDocument.value = null
  uploadProgress.value = 0
  uploadVisible.value = true
}

function openImport() {
  importResult.value = null
  importProgress.value = 0
  importVisible.value = true
}

function openEdit(doc: LabDocument) {
  if (!doc.can_edit) {
    ElMessage.warning('当前账号没有编辑该资料的权限。')
    return
  }
  editingDocument.value = doc
  uploadProgress.value = 0
  uploadVisible.value = true
}

async function submitDocument(form: DocumentFormPayload) {
  if (uploading.value) return
  uploading.value = true
  uploadProgress.value = 0
  try {
    const payload = {
      ...form,
      status: 'active',
      allow_download: true,
    }
    const saved = editingDocument.value
      ? await updateDocument(editingDocument.value.id, payload, (event) => {
        if (!event.total) return
        uploadProgress.value = Math.min(100, Math.round((event.loaded / event.total) * 100))
      })
      : await createDocument(payload, (event) => {
      if (!event.total) return
      uploadProgress.value = Math.min(100, Math.round((event.loaded / event.total) * 100))
    })
    uploadProgress.value = 100
    ElMessage.success(editingDocument.value ? '资料已更新。' : '资料已保存到内部资料库。')
    const editedId = editingDocument.value?.id
    closeUploadDialog()
    await loadDocuments(false)
    if (editedId && previewDocument.value?.id === editedId) {
      previewDocument.value = documents.value.find((item) => item.id === editedId) || saved
    }
  } catch (error: any) {
    ElMessage.error(requestErrorMessage(error, '保存失败，请确认账号权限和表单内容。'))
  } finally {
    uploading.value = false
    setTimeout(() => {
      if (!uploading.value) uploadProgress.value = 0
    }, 800)
  }
}

async function submitImport(payload: DocumentImportPayload) {
  if (importing.value || importResult.value) return
  importing.value = true
  importProgress.value = 0
  importResult.value = null
  try {
    const result = await importDocumentsExcel(payload.file, payload.archive, (event) => {
      if (!event.total) return
      importProgress.value = Math.min(100, Math.round((event.loaded / event.total) * 100))
    })
    importProgress.value = 100
    importResult.value = result
    ElMessage.success(`导入完成：新增 ${result.created} 条，更新 ${result.updated} 条。`)
    await loadDocuments(false)
  } catch (error: any) {
    ElMessage.error(requestErrorMessage(error, '导入失败，请检查模板和账号权限。'))
  } finally {
    importing.value = false
    setTimeout(() => {
      if (!importing.value) importProgress.value = 0
    }, 1200)
  }
}

async function handleDownload(doc: LabDocument) {
  if (!doc.can_download || doc.id === 0) {
    ElMessage.warning('当前账号没有该资料的下载权限。')
    return
  }
  try {
    await downloadDocument(doc)
  } catch (error: any) {
    const status = error?.response?.status
    if (status === 401) ElMessage.error('请先登录后再下载内部资料。')
    else if (status === 403) ElMessage.error('你没有该资料的下载权限。')
    else ElMessage.error('下载失败，请稍后重试。')
  }
}

async function handleDelete(doc: LabDocument) {
  if (!doc.can_delete || doc.id === 0) {
    ElMessage.warning('只能删除自己上传的资料，或由管理员处理。')
    return
  }
  try {
    await ElMessageBox.confirm(`确定删除“${doc.title}”吗？删除后该资料及文件将不可恢复。`, '删除内部资料', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteDocument(doc)
    ElMessage.success('资料已删除。')
    if (previewDocument.value?.id === doc.id) previewDocument.value = null
    await loadDocuments(false)
    if (documentPage.value > documentTotalPages.value) documentPage.value = documentTotalPages.value
  } catch (error: any) {
    if (error === 'cancel' || error === 'close') return
    const detail = error?.response?.data?.detail
    ElMessage.error(detail || '删除失败，请确认是否为本人上传的资料。')
  }
}

function handlePreview(doc: LabDocument) {
  if (!doc.can_preview || doc.id === 0) {
    ElMessage.warning('当前资料暂不支持在线查看。')
    return
  }
  previewDocument.value = doc
  const index = displayDocuments.value.findIndex((item) => item.id === doc.id)
  if (index >= 0) readerPage.value = Math.floor(index / readerPageSize) + 1
}

function closePreview() {
  previewDocument.value = null
}

function isDocxDocument(doc: LabDocument) {
  const type = doc.file_type?.toLowerCase() || ''
  const filename = currentFilename(doc).toLowerCase()
  return type.includes('wordprocessingml') || filename.endsWith('.docx')
}

function isLegacyDocDocument(doc: LabDocument) {
  const filename = currentFilename(doc).toLowerCase()
  return filename.endsWith('.doc')
}

function isOfficeDocument(doc: LabDocument) {
  const filename = currentFilename(doc).toLowerCase()
  return (
    filename.endsWith('.doc') ||
    filename.endsWith('.docx') ||
    filename.endsWith('.ppt') ||
    filename.endsWith('.pptx') ||
    filename.endsWith('.xls') ||
    filename.endsWith('.xlsx')
  )
}

function canEmbedPreview(doc: LabDocument) {
  const type = doc.file_type?.toLowerCase() || ''
  const filename = currentFilename(doc).toLowerCase()
  if (doc.preview_status === 'ready') return true
  if (isDocxDocument(doc)) return true
  if (isLegacyDocDocument(doc)) return false
  if (isOfficeDocument(doc)) return false
  return (
    type.startsWith('application/pdf') ||
    type.startsWith('image/') ||
    type.startsWith('text/') ||
    filename.endsWith('.pdf') ||
    filename.endsWith('.png') ||
    filename.endsWith('.jpg') ||
    filename.endsWith('.jpeg') ||
    filename.endsWith('.gif') ||
    filename.endsWith('.txt') ||
    filename.endsWith('.md') ||
    filename.endsWith('.csv')
  )
}

onMounted(async () => {
  await Promise.all([loadCategories(), loadDocuments(false)])
  if (initialPreviewId) {
    const target = documents.value.find((item) => item.id === initialPreviewId)
    if (target?.can_preview) handlePreview(target)
  }
})
const activeCategoryId = computed(() => displayCategories.value.find((item) => item.slug === activeCategory.value)?.id)

function documentTime(document: LabDocument, type: 'created' | 'updated') {
  const value = type === 'updated'
    ? document.updated_at
    : document.created_at || document.uploaded_at || document.updated_at
  const timestamp = value ? Date.parse(value) : 0
  return Number.isNaN(timestamp) ? 0 : timestamp
}

watch(
  [keyword, activeCategory, sortOrder, documentPage, () => previewDocument.value?.id || 0],
  ([q, category, sort, page, document]) => {
    void router.replace({
      query: {
        ...route.query,
        q: q || undefined,
        category: category || undefined,
        sort: sort !== 'created_desc' ? sort : undefined,
        page: page > 1 ? String(page) : undefined,
        document: document ? String(document) : undefined,
      },
    })
  },
)

watch(sortOrder, () => {
  documentPage.value = 1
  readerPage.value = 1
})

watch(readerTotalPages, (total) => {
  if (readerPage.value > total) readerPage.value = total
  if (readerPage.value < 1) readerPage.value = 1
})
</script>

<style scoped>
.document-shell {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  align-items: start;
  gap: 16px;
}

.document-shell.is-reading {
  grid-template-columns: 300px minmax(0, 1fr);
}

.document-main {
  display: grid;
  gap: 14px;
}

.filter-bar {
  padding: 14px;
}

.filter-bar {
  box-shadow: var(--shadow-flat);
}

.filter-bar:hover {
  border-color: var(--color-border);
  transform: none;
}

.filter-title {
  display: grid;
  flex: 0 0 160px;
  gap: 3px;
}

.filter-title strong {
  overflow: hidden;
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.filter-title span {
  color: var(--color-muted);
  font-size: 13px;
}

@media (max-width: 1280px) {
  .filter-title {
    flex-basis: 130px;
  }
}

@media (max-width: 1080px) {
  .document-shell,
  .document-shell.is-reading {
    grid-template-columns: 1fr;
  }

  .document-shell.is-reading .document-main {
    order: -1;
  }

}
</style>
