<template>
  <InternalLayout title="内部资料库">
    <section class="library-hero">
      <div>
        <span>内部资料</span>
        <h1>课题组内部资料库</h1>
        <p>集中管理 SOP、实验记录模板、数据分析教程、论文开题与毕业材料，支持在线阅读、权限查看和版本追踪。</p>
      </div>
      <dl>
        <div>
          <dt>{{ displayDocuments.length }}</dt>
          <dd>当前资料</dd>
        </div>
        <div>
          <dt>{{ displayCategories.length }}</dt>
          <dd>资料分类</dd>
        </div>
        <div>
          <dt>{{ previewableCount }}</dt>
          <dd>可在线查看</dd>
        </div>
      </dl>
    </section>

    <section :class="['document-shell', { 'is-reading': previewDocument }]">
      <aside class="card category-tree">
        <template v-if="previewDocument">
          <div class="side-heading">
            <div>
              <span>资料列表</span>
              <h2>当前可查看资料</h2>
            </div>
            <button class="back-category" type="button" @click="closePreview">返回分类</button>
          </div>
          <button
            v-for="doc in displayDocuments"
            :key="doc.id"
            :class="{ active: previewDocument.id === doc.id, disabled: !doc.can_preview }"
            type="button"
            @click="handlePreview(doc)"
          >
            <strong>{{ doc.title }}</strong>
            <span>{{ currentFilename(doc) }}</span>
          </button>
        </template>
        <template v-else>
          <div class="side-heading static">
            <div>
              <span>分类导航</span>
              <h2>资料分类</h2>
            </div>
          </div>
          <button :class="{ active: !activeCategory }" type="button" @click="selectCategory('')">全部资料</button>
          <button
            v-for="item in displayCategories"
            :key="item.slug"
            :class="{ active: activeCategory === item.slug }"
            type="button"
            @click="selectCategory(item.slug)"
          >
            {{ item.name }}
          </button>
        </template>
      </aside>

      <main class="document-main">
        <div class="card filter-bar">
          <div class="filter-title">
            <strong>{{ activeCategoryName }}</strong>
            <span>{{ loading ? '正在更新资料列表' : `共 ${displayDocuments.length} 条资料` }}</span>
          </div>
          <el-input v-model="keyword" placeholder="搜索 SOP、实验方法、数据模板或论文材料" clearable @keyup.enter="loadDocuments" />
          <el-button type="primary" @click="loadDocuments">搜索</el-button>
          <el-button plain @click="uploadVisible = true">上传资料</el-button>
          <div class="filter-tags">
            <span class="status-tag normal">成员可见</span>
            <span class="status-tag pending">博士可见</span>
            <span class="status-tag maintenance">导师可见</span>
            <span class="status-tag archived">指定权限</span>
          </div>
        </div>

        <section v-if="previewDocument" class="card embedded-reader">
          <header class="reader-heading">
            <div>
              <span>资料阅读</span>
              <h2>{{ previewDocument.title }}</h2>
            </div>
            <div class="reader-actions">
              <el-button plain @click="closePreview">返回列表</el-button>
              <el-button v-if="previewDocument.can_delete" plain type="danger" @click="handleDelete(previewDocument)">删除</el-button>
              <el-button v-if="previewDocument.can_download" type="primary" @click="handleDownload(previewDocument)">下载</el-button>
            </div>
          </header>
          <dl class="reader-meta">
            <div><dt>分类</dt><dd>{{ previewDocument.category?.name || '未分类' }}</dd></div>
            <div><dt>文件</dt><dd>{{ currentFilename(previewDocument) }}</dd></div>
            <div><dt>权限</dt><dd>{{ previewDocument.visibility_label }}</dd></div>
            <div><dt>更新</dt><dd>{{ formatDate(previewDocument.updated_at) }}</dd></div>
          </dl>
          <p class="reader-description">{{ previewDocument.description || '暂无资料说明。' }}</p>
          <div class="document-reader">
            <iframe v-if="previewUrl && canEmbedPreview(previewDocument)" :src="previewUrl" title="资料在线查看" />
            <div v-else class="preview-empty">
              <strong>当前文件暂不能在线查看</strong>
              <p>请下载后查看，或将旧版 Word 文件转换为 PDF / DOCX 后重新上传。</p>
              <el-button v-if="previewDocument.can_download" type="primary" @click="handleDownload(previewDocument)">下载文件</el-button>
            </div>
          </div>
        </section>

        <div v-else-if="loading" class="card loading-panel">正在加载资料...</div>
        <EmptyState
          v-else-if="!displayDocuments.length"
          :icon="Files"
          title="暂无可见资料"
          description="当前分类下没有资料，或你的账号尚未获得访问权限。"
        />
        <div v-else class="document-grid">
          <article
            v-for="doc in displayDocuments"
            :key="doc.id"
            :class="['card document-card', { previewable: doc.can_preview }]"
            @click="handlePreview(doc)"
          >
            <div class="document-topline">
              <span :class="['status-tag', visibilityClass(doc.visibility)]">{{ doc.visibility_label }}</span>
              <span class="file-type">{{ fileTypeLabel(doc) }}</span>
            </div>
            <div>
              <h3>{{ doc.title }}</h3>
              <p>{{ doc.description || '暂无资料说明。' }}</p>
            </div>
            <dl>
              <div><dt>分类</dt><dd>{{ doc.category?.name || '未分类' }}</dd></div>
              <div><dt>版本</dt><dd>{{ doc.current_version || latestVersion(doc) }}</dd></div>
              <div><dt>更新</dt><dd>{{ formatDate(doc.updated_at) }}</dd></div>
            </dl>
            <footer>
              <span class="preview-hint">{{ doc.can_preview ? '点击卡片查看' : '暂无可预览文件' }}</span>
              <div class="document-actions">
                <el-button v-if="doc.can_delete" plain type="danger" @click.stop="handleDelete(doc)">删除</el-button>
                <el-button type="primary" :disabled="!doc.can_download" @click.stop="handleDownload(doc)">
                  {{ doc.can_download ? '下载' : '不可下载' }}
                </el-button>
              </div>
            </footer>
          </article>
        </div>
      </main>
    </section>

    <el-dialog v-model="uploadVisible" title="上传内部资料" width="560px">
      <el-form label-position="top">
        <el-form-item label="资料标题">
          <el-input v-model="uploadForm.title" placeholder="请输入资料标题" />
        </el-form-item>
        <el-form-item label="资料分类">
          <el-select v-model="uploadForm.category_id" clearable placeholder="选择分类">
            <el-option v-for="item in categories" :key="item.id" :label="item.name" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="可见范围">
          <el-select v-model="uploadForm.visibility">
            <el-option label="成员可见" value="members" />
            <el-option label="博士 / 管理员可见" value="phd" />
            <el-option label="硕博导师 / 管理员可见" value="pi" />
            <el-option label="公开" value="public" />
          </el-select>
        </el-form-item>
        <el-form-item label="版本号">
          <el-input v-model="uploadForm.version" placeholder="v1.0" />
        </el-form-item>
        <el-form-item label="资料说明">
          <el-input v-model="uploadForm.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="更新说明">
          <el-input v-model="uploadForm.change_log" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="文件">
          <input class="file-input" type="file" @change="handleFileChange" />
          <small v-if="uploadForm.file" class="upload-file-note">{{ uploadForm.file.name }}（{{ formatFileSize(uploadForm.file.size) }}）</small>
        </el-form-item>
        <div v-if="uploading || uploadProgress > 0" class="upload-progress">
          <el-progress :percentage="uploadProgress" :status="uploadProgress === 100 ? 'success' : undefined" />
          <span>{{ uploadProgress < 100 ? '正在上传，请不要关闭窗口。' : '上传完成，正在保存记录。' }}</span>
        </div>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">取消</el-button>
        <el-button type="primary" :loading="uploading" @click="submitDocument">保存资料</el-button>
      </template>
    </el-dialog>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Files } from '@element-plus/icons-vue'

import EmptyState from '../../components/EmptyState.vue'
import InternalLayout from '../../layouts/InternalLayout.vue'
import {
  createDocument,
  deleteDocument,
  downloadDocument,
  fetchDocumentCategories,
  fetchDocuments,
  previewDocumentUrl,
  type DocumentCategory,
  type LabDocument,
} from '../../api/documents'

const categories = ref<DocumentCategory[]>([])
const documents = ref<LabDocument[]>([])
const loading = ref(false)
const keyword = ref('')
const activeCategory = ref('')
const uploadVisible = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const previewDocument = ref<LabDocument | null>(null)

const uploadForm = reactive({
  title: '',
  category_id: undefined as number | undefined,
  description: '',
  visibility: 'members',
  version: 'v1.0',
  change_log: '',
  file: undefined as File | undefined,
})

const displayCategories = computed(() => categories.value)
const displayDocuments = computed(() => documents.value)
const previewUrl = computed(() => (previewDocument.value ? previewDocumentUrl(previewDocument.value) : ''))
const previewableCount = computed(() => displayDocuments.value.filter((doc) => doc.can_preview).length)
const activeCategoryName = computed(() => {
  if (!activeCategory.value) return '全部资料'
  return displayCategories.value.find((item) => item.slug === activeCategory.value)?.name || '当前分类'
})

function selectCategory(slug: string) {
  activeCategory.value = slug
  previewDocument.value = null
  void loadDocuments()
}

async function loadCategories() {
  try {
    categories.value = await fetchDocumentCategories()
  } catch {
    categories.value = []
    ElMessage.error('资料分类加载失败，请确认已登录并刷新页面。')
  }
}

async function loadDocuments() {
  loading.value = true
  try {
    documents.value = await fetchDocuments({
      search: keyword.value || undefined,
      category__slug: activeCategory.value || undefined,
    })
  } catch {
    documents.value = []
    previewDocument.value = null
  } finally {
    loading.value = false
  }
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  uploadForm.file = input.files?.[0]
  uploadProgress.value = 0
}

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function uploadErrorMessage(error: any) {
  const data = error?.response?.data
  if (data?.detail) return data.detail
  if (data?.file?.length) return data.file[0]
  if (error?.code === 'ECONNABORTED') return '上传超时，请检查网络或稍后重试。'
  if (!error?.response) return '上传连接失败，请检查网络或服务器上传大小限制。'
  return '保存失败，请确认账号权限和表单内容。'
}

async function submitDocument() {
  if (!uploadForm.title.trim()) {
    ElMessage.warning('请填写资料标题。')
    return
  }
  uploading.value = true
  uploadProgress.value = 0
  try {
    await createDocument({
      ...uploadForm,
      title: uploadForm.title.trim(),
      status: 'active',
      allow_download: true,
    }, (event) => {
      if (!event.total) return
      uploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    uploadProgress.value = 100
    ElMessage.success('资料已保存到内部资料库。')
    uploadVisible.value = false
    uploadForm.title = ''
    uploadForm.description = ''
    uploadForm.change_log = ''
    uploadForm.version = 'v1.0'
    uploadForm.file = undefined
    await loadDocuments()
  } catch (error: any) {
    ElMessage.error(uploadErrorMessage(error))
  } finally {
    uploading.value = false
    setTimeout(() => {
      if (!uploading.value) uploadProgress.value = 0
    }, 800)
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
    await ElMessageBox.confirm(`确定删除“${doc.title}”吗？删除后该资料及其文件版本将不可恢复。`, '删除内部资料', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await deleteDocument(doc)
    ElMessage.success('资料已删除。')
    if (previewDocument.value?.id === doc.id) previewDocument.value = null
    await loadDocuments()
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
}

function closePreview() {
  previewDocument.value = null
}

function visibilityClass(visibility: string) {
  if (visibility === 'members' || visibility === 'public') return 'normal'
  if (visibility === 'phd') return 'pending'
  if (visibility === 'pi') return 'maintenance'
  return 'archived'
}

function latestVersion(doc: LabDocument) {
  return doc.versions.find((item) => item.is_current)?.version || '-'
}

function currentVersion(doc: LabDocument) {
  return doc.versions.find((item) => item.is_current) || doc.versions[0]
}

function currentFilename(doc: LabDocument) {
  return currentVersion(doc)?.original_filename || doc.title
}

function isDocxDocument(doc: LabDocument) {
  const version = currentVersion(doc)
  const type = version?.file_type?.toLowerCase() || ''
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
  const version = currentVersion(doc)
  const type = version?.file_type?.toLowerCase() || ''
  const filename = currentFilename(doc).toLowerCase()
  if (version?.preview_status === 'ready') return true
  if (isOfficeDocument(doc)) return false
  if (isLegacyDocDocument(doc)) return false
  return (
    isDocxDocument(doc) ||
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

function fileTypeLabel(doc: LabDocument) {
  const filename = currentFilename(doc).toLowerCase()
  if (filename.endsWith('.pdf')) return 'PDF'
  if (filename.endsWith('.docx') || filename.endsWith('.doc')) return 'Word'
  if (filename.endsWith('.pptx') || filename.endsWith('.ppt')) return 'PPT'
  if (filename.endsWith('.xlsx') || filename.endsWith('.xls')) return 'Excel'
  if (filename.endsWith('.txt') || filename.endsWith('.md')) return '文本'
  return '资料'
}

function formatDate(value: string) {
  return value ? value.slice(0, 10) : '-'
}

onMounted(() => {
  void loadCategories()
  void loadDocuments()
})
</script>

<style scoped>
.library-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 22px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: 14px;
  margin-bottom: 16px;
  padding: 20px 24px;
  background:
    linear-gradient(135deg, rgba(234, 245, 238, 0.72), rgba(255, 255, 255, 0.82) 48%, rgba(248, 247, 242, 0.9)),
    #fff;
}

.library-hero span {
  display: block;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 750;
}

.library-hero h1 {
  margin: 5px 0 6px;
  color: var(--color-deep-green);
  font-size: clamp(24px, 2.7vw, 31px);
  font-weight: 650;
  line-height: 1.25;
}

.library-hero p {
  max-width: 720px;
  margin: 0;
  color: var(--color-muted);
  font-size: 15px;
  line-height: 1.62;
}

.library-hero dl {
  display: grid;
  grid-template-columns: repeat(3, minmax(84px, 1fr));
  gap: 8px;
  margin: 0;
}

.library-hero dl div {
  min-width: 92px;
  border-left: 1px solid rgba(0, 135, 60, 0.16);
  padding-left: 14px;
}

.library-hero dt,
.library-hero dd {
  margin: 0;
}

.library-hero dt {
  color: var(--color-deep-green);
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
}

.library-hero dd {
  margin-top: 4px;
  color: var(--color-muted);
  font-size: 13px;
}

.document-shell {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  align-items: start;
  gap: 24px;
}

.document-shell.is-reading {
  grid-template-columns: 300px minmax(0, 1fr);
}

.category-tree,
.filter-bar,
.document-card,
.loading-panel,
.embedded-reader {
  padding: 22px;
}

.category-tree,
.embedded-reader,
.filter-bar {
  box-shadow: 0 1px 2px rgba(31, 61, 43, 0.035), 0 12px 30px rgba(31, 61, 43, 0.035);
}

.category-tree {
  position: sticky;
  top: 24px;
  max-height: calc(100vh - 48px);
  overflow: auto;
}

.category-tree:hover,
.filter-bar:hover,
.embedded-reader:hover {
  border-color: var(--color-border);
  box-shadow: 0 1px 2px rgba(31, 61, 43, 0.035), 0 12px 30px rgba(31, 61, 43, 0.035);
  transform: none;
}

.side-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 16px;
}

.side-heading.static {
  display: block;
}

.side-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.side-heading h2 {
  margin: 3px 0 0;
  color: var(--color-deep-green);
  font-size: 18px;
  font-weight: 650;
  line-height: 1.25;
  white-space: nowrap;
}

.category-tree button {
  display: block;
  width: 100%;
  min-height: 42px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  margin-bottom: 7px;
  padding: 10px 12px;
  background: transparent;
  color: var(--color-muted);
  text-align: left;
  cursor: pointer;
}

.category-tree button.active,
.category-tree button:hover {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
  color: var(--color-cau-green);
}

.category-tree button.active {
  font-weight: 650;
}

.category-tree button.disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.side-heading .back-category {
  flex: 0 0 auto;
  width: auto;
  min-height: 30px;
  border: 1px solid rgba(0, 135, 60, 0.2);
  margin: 0;
  padding: 0 9px;
  background: #fff;
  color: var(--color-cau-green);
  font-size: 12px;
  font-weight: 700;
  line-height: 28px;
  text-align: center;
  white-space: nowrap;
}

.category-tree button strong,
.category-tree button span {
  display: block;
}

.category-tree button strong {
  color: inherit;
  font-size: 14px;
  line-height: 1.35;
}

.category-tree button span {
  overflow: hidden;
  margin-top: 3px;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-main {
  display: grid;
  gap: 20px;
}

.filter-bar {
  display: grid;
  grid-template-columns: minmax(140px, 180px) minmax(240px, 1fr) auto auto;
  align-items: center;
  gap: 12px;
}

.filter-title {
  display: grid;
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

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  grid-column: 1 / -1;
  justify-content: flex-start;
  gap: 8px;
  border-top: 1px solid var(--color-line);
  padding-top: 12px;
}

.document-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.document-card {
  display: flex;
  flex-direction: column;
  min-height: 286px;
  padding: 20px;
  box-shadow: 0 1px 2px rgba(31, 61, 43, 0.035);
}

.document-card.previewable {
  cursor: pointer;
}

.document-card.previewable:hover {
  border-color: rgba(0, 135, 60, 0.24);
  box-shadow: 0 12px 26px rgba(31, 61, 43, 0.055);
}

.document-card.previewable:hover h3 {
  color: var(--color-cau-green);
}

.document-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.file-type {
  border: 1px solid var(--color-line);
  border-radius: 999px;
  padding: 3px 9px;
  background: var(--color-panel);
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 700;
}

.document-card h3 {
  margin: 0 0 10px;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
  line-height: 1.35;
}

.document-card p {
  display: -webkit-box;
  overflow: hidden;
  margin: 0;
  color: var(--color-muted);
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.document-card dl {
  display: grid;
  gap: 8px;
  margin: 18px 0;
  border-top: 1px solid var(--color-line);
  padding-top: 14px;
}

.document-card dl div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  color: var(--color-muted);
  font-size: 14px;
}

.document-card dt {
  color: var(--color-text);
}

.document-card dd {
  margin: 0;
  text-align: right;
}

.document-card footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: auto;
}

.preview-hint {
  color: var(--color-muted);
  font-size: 13px;
}

.document-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.reader-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 16px;
}

.reader-actions {
  display: flex;
  gap: 10px;
}

.reader-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.reader-heading h2 {
  margin: 4px 0 0;
  color: var(--color-deep-green);
  font-size: 22px;
  font-weight: 650;
}

.reader-meta {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 16px 0 0;
}

.reader-meta div {
  overflow: hidden;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  background: var(--color-panel);
}

.reader-meta dt,
.reader-meta dd {
  margin: 0;
}

.reader-meta dt {
  color: var(--color-muted);
  font-size: 13px;
}

.reader-meta dd {
  overflow: hidden;
  margin-top: 4px;
  color: var(--color-text);
  font-weight: 600;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.reader-description {
  margin: 16px 0 0;
  color: var(--color-muted);
  font-size: 14px;
}

.document-reader {
  overflow: hidden;
  border: 1px solid #dfe5e1;
  border-radius: 12px;
  margin-top: 20px;
  background: linear-gradient(180deg, #f4f6f5 0%, #eef2f0 100%);
}

.document-reader iframe {
  display: block;
  width: 100%;
  height: 100%;
  min-height: min(76vh, 820px);
  border: 0;
  background: #fff;
}

.preview-empty {
  display: grid;
  min-height: 420px;
  place-items: center;
  align-content: center;
  gap: 10px;
  padding: 32px;
  color: var(--color-muted);
  text-align: center;
}

.preview-empty strong {
  color: var(--color-deep-green);
  font-size: 20px;
}

.preview-empty p {
  max-width: 460px;
  margin: 0;
}

.loading-panel {
  color: var(--color-muted);
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

@media (max-width: 1280px) {
  .filter-bar {
    grid-template-columns: 1fr auto auto;
  }

  .filter-title {
    grid-column: 1 / -1;
  }
}

@media (max-width: 1080px) {
  .library-hero,
  .document-shell,
  .document-shell.is-reading,
  .document-grid,
  .filter-bar,
  .reader-meta {
    grid-template-columns: 1fr;
  }

  .library-hero {
    align-items: start;
  }

  .library-hero dl {
    width: 100%;
  }

  .category-tree {
    position: static;
    max-height: none;
  }

  .filter-tags {
    justify-content: flex-start;
  }
}

@media (max-width: 640px) {
  .library-hero {
    padding: 18px;
  }

  .library-hero dl {
    grid-template-columns: 1fr;
  }

  .library-hero dl div {
    border-left: 0;
    border-top: 1px solid rgba(0, 135, 60, 0.16);
    padding: 12px 0 0;
  }

  .reader-heading,
  .document-card footer {
    display: grid;
  }

  .reader-actions {
    flex-wrap: wrap;
  }
}
</style>
