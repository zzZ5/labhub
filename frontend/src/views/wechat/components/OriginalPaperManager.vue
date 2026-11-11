<template>
  <section class="paper-manager">
    <div class="manager-tools">
      <el-input v-model="keyword" clearable placeholder="搜索标题、DOI、作者或期刊" @keyup.enter="search" @clear="search" />
      <el-button @click="search">搜索</el-button>
      <el-button type="primary" @click="openForm()">添加原文</el-button>
      <RouterLink :to="{ name: 'wechat-articles', query: { tab: 'papers' } }" target="_blank">查看公开页</RouterLink>
    </div>
    <LoadErrorNotice v-if="loadError" :description="loadError" :retrying="loading" @retry="load" />
    <ListSkeleton v-if="loading" :rows="4" />
    <div v-else>
      <article v-for="paper in papers" :key="paper.id" class="manager-row">
        <div>
          <strong>{{ paper.chinese_title || paper.title }}</strong>
          <p>{{ paper.topic_label }} · {{ paper.journal || '未填期刊' }} · {{ paper.is_visible ? '公开' : '未公开' }} · {{ paper.has_pdf ? '已上传 PDF' : '未上传 PDF' }}</p>
          <small>{{ paper.doi }}</small>
        </div>
        <div class="row-actions"><el-button @click="openForm(paper)">编辑</el-button><el-button type="danger" plain @click="remove(paper)">删除</el-button></div>
      </article>
      <EmptyState v-if="!papers.length && !loadError" title="暂无论文原文" description="添加文献信息后，可上传 PDF 或填写出版社原文链接。" />
    </div>
    <AppPagination :page="page" :total-pages="Math.max(1, Math.ceil(total / 12))" @change="changePage" />
    <el-dialog v-model="dialogOpen" :title="editingId ? '编辑论文原文' : '添加论文原文'" width="min(720px, calc(100vw - 24px))" :close-on-click-modal="!saving" :close-on-press-escape="!saving" :show-close="!saving" destroy-on-close>
      <el-form label-position="top" @submit.prevent="save">
        <el-form-item label="DOI">
          <div class="doi-input-row">
            <el-input v-model="form.doi" aria-label="DOI" placeholder="10.xxxx/xxxxx 或 https://doi.org/…" :disabled="lookingUp || saving" />
            <el-button :loading="lookingUp" :disabled="saving || !form.doi.trim()" @click="lookup">识别信息</el-button>
          </div>
        </el-form-item>
        <p class="file-note">填写 DOI、选择 PDF 后即可保存，后台会自动补齐文献信息。</p>
        <el-form-item label="PDF 文件（不超过 50 MB）">
          <input type="file" accept=".pdf,application/pdf" aria-label="选择论文 PDF" @change="selectFile" />
          <p v-if="hasExistingPdf" class="file-note">已上传 PDF，未选新文件时保留原文件。</p>
        </el-form-item>
        <el-checkbox v-if="hasExistingPdf" v-model="removePdf">移除现有 PDF</el-checkbox>
        <div v-if="form.title" class="metadata-summary">
          <strong>{{ form.title }}</strong>
          <p>{{ [form.journal, form.year].filter(Boolean).join(' · ') }}</p>
          <small v-if="metadataNotice">{{ metadataNotice }}</small>
        </div>
        <el-collapse v-model="expandedSections" class="paper-extra">
          <el-collapse-item title="补充信息与分享设置（可选）" name="details">
        <el-form-item label="原文标题"><el-input v-model="form.title" aria-label="原文标题" placeholder="自动获取；未查到时可手动填写" /></el-form-item>
        <el-form-item label="中文标题"><el-input v-model="form.chinese_title" /></el-form-item>
        <el-form-item label="作者"><el-input v-model="form.authors" /></el-form-item>
        <div class="form-pair">
          <el-form-item label="期刊"><el-input v-model="form.journal" /></el-form-item>
          <el-form-item label="发表年份"><el-input v-model="form.year" inputmode="numeric" /></el-form-item>
        </div>
        <el-form-item label="研究专题"><el-select v-model="form.topic"><el-option value="" label="自动推荐，无法判断时暂不分类" /><el-option v-for="item in paperTopics" :key="item.value" :value="item.value" :label="item.label" /></el-select></el-form-item>
        <el-form-item label="出版社或开放获取原文链接"><el-input v-model="form.publisher_url" /></el-form-item>
        <el-form-item label="公众号解读链接"><el-input v-model="form.wechat_url" /></el-form-item>
        <el-form-item label="PDF 分享方式">
          <el-select v-model="form.sharing">
            <el-option value="link_only" label="仅提供原文入口（PDF 不公开）" />
            <el-option value="open_access" label="开放获取且许可允许分享" />
            <el-option value="authorized" label="已获分享授权" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.sharing !== 'link_only'" label="分享许可或授权依据" required>
          <el-input v-model="form.rights_note" type="textarea" placeholder="如 CC BY 4.0 及许可链接，或授权说明。仅能下载不等于允许转载。" />
        </el-form-item>
          </el-collapse-item>
        </el-collapse>
        <p class="file-note">默认保存为未公开，PDF 不会自动开放下载。</p>
        <el-checkbox v-model="form.is_visible">公开展示此文献</el-checkbox>
        <el-progress v-if="saving && selectedFile" :percentage="uploadProgress" />
      </el-form>
      <template #footer><el-button :disabled="saving" @click="dialogOpen = false">取消</el-button><el-button type="primary" :loading="saving" :disabled="lookingUp" @click="save">保存</el-button></template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { deleteOriginalPaper, fetchOriginalPapers, lookupPaperMetadata, paperTopics, saveOriginalPaper, type ManagedOriginalPaper } from '../../../api/originalPapers'
import AppPagination from '../../../components/AppPagination.vue'
import EmptyState from '../../../components/EmptyState.vue'
import ListSkeleton from '../../../components/ListSkeleton.vue'
import LoadErrorNotice from '../../../components/LoadErrorNotice.vue'
import { requestErrorMessage } from '../../../utils/requestErrors'

const papers = ref<ManagedOriginalPaper[]>([])
const keyword = ref('')
const page = ref(1)
const total = ref(0)
const loading = ref(false)
const loadError = ref('')
const dialogOpen = ref(false)
const saving = ref(false)
const editingId = ref<number | null>(null)
const selectedFile = ref<File | null>(null)
const hasExistingPdf = ref(false)
const removePdf = ref(false)
const uploadProgress = ref(0)
const lookingUp = ref(false)
const metadataNotice = ref('')
const expandedSections = ref<string[]>([])
let lookupId = 0
let resolvedDoi = ''
const blank = () => ({ title: '', chinese_title: '', authors: '', journal: '', year: '', doi: '', topic: '', publisher_url: '', wechat_url: '', sharing: 'link_only', rights_note: '', is_visible: false })
const form = reactive(blank())
let requestId = 0

async function load() {
  const current = ++requestId
  loading.value = true
  loadError.value = ''
  try {
    const result = await fetchOriginalPapers({ search: keyword.value.trim() || undefined, page: page.value }, true)
    if (current !== requestId) return
    papers.value = result.results
    total.value = result.count
  } catch (error) {
    if (current !== requestId) return
    loadError.value = requestErrorMessage(error, '原文列表加载失败。')
  } finally { if (current === requestId) loading.value = false }
}
function search() { page.value = 1; void load() }
function changePage(value: number) { page.value = value; void load() }
function openForm(paper?: ManagedOriginalPaper) {
  lookupId++
  lookingUp.value = false
  metadataNotice.value = ''
  expandedSections.value = []
  resolvedDoi = ''
  editingId.value = paper?.id || null
  Object.assign(form, blank(), paper ? { ...paper, year: String(paper.year || ''), doi: paper.doi || '' } : {})
  resolvedDoi = normalizeDoi(form.doi)
  selectedFile.value = null
  hasExistingPdf.value = Boolean(paper?.has_pdf)
  removePdf.value = false
  uploadProgress.value = 0
  dialogOpen.value = true
}
async function lookup() {
  const current = ++lookupId
  const doi = form.doi.trim()
  lookingUp.value = true
  try {
    const result = await lookupPaperMetadata(doi)
    if (current !== lookupId || form.doi.trim() !== doi || !dialogOpen.value) return
    Object.assign(form, { title: result.title, doi: result.doi, authors: result.authors,
      journal: result.journal, year: String(result.year || ''), publisher_url: result.publisher_url, topic: result.topic })
    resolvedDoi = result.doi
    metadataNotice.value = `信息来源：${result.metadata_source}；专题为关键词推荐，可展开调整。`
  } catch (error) {
    if (current === lookupId && dialogOpen.value) ElMessage.error(requestErrorMessage(error, '识别失败，可稍后重试或展开补充信息手动填写。'))
  } finally { if (current === lookupId) lookingUp.value = false }
}
function normalizeDoi(value: string) {
  return value.trim().replace(/^https?:\/\/(dx\.)?doi\.org\//i, '').replace(/^doi\s*:\s*/i, '').toLowerCase()
}
watch(() => form.doi, value => {
  if (!resolvedDoi || normalizeDoi(value) === resolvedDoi) return
  Object.assign(form, { title: '', chinese_title: '', authors: '', journal: '', year: '', topic: '', publisher_url: '', wechat_url: '' })
  resolvedDoi = ''
  metadataNotice.value = ''
})
function selectFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0] || null
  if (file && (!file.name.toLowerCase().endsWith('.pdf') || file.size > 50 * 1024 * 1024)) {
    ElMessage.warning('请选择不超过 50 MB 的 PDF。')
    input.value = ''
    selectedFile.value = null
    return
  }
  selectedFile.value = file
  if (file) removePdf.value = false
}
async function save() {
  if (!form.doi.trim() && !form.title.trim()) { ElMessage.warning('请填写 DOI，或展开补充信息手动填写标题。'); return }
  if (form.sharing !== 'link_only' && !form.rights_note.trim()) { ElMessage.warning('请填写分享许可或授权依据。'); return }
  if (selectedFile.value && removePdf.value) { ElMessage.warning('请选择上传新文件或移除原文件其中一种操作。'); return }
  saving.value = true
  try {
    const data = new FormData()
    const keys = Object.keys(blank()) as (keyof ReturnType<typeof blank>)[]
    keys.forEach(key => data.append(key, String(form[key])))
    data.append('remove_pdf', String(removePdf.value))
    if (selectedFile.value) data.append('pdf', selectedFile.value)
    const result = await saveOriginalPaper(editingId.value, data, value => { uploadProgress.value = value })
    dialogOpen.value = false
    ElMessage.success(`已保存：${result.chinese_title || result.title}`)
    await load()
  } catch (error) { ElMessage.error(requestErrorMessage(error, '保存失败，请检查文献信息。')) }
  finally { saving.value = false }
}
async function remove(paper: ManagedOriginalPaper) {
  try { await ElMessageBox.confirm(`确定删除“${paper.chinese_title || paper.title}”吗？`, '删除文献', { type: 'warning' }) }
  catch { return }
  try {
    await deleteOriginalPaper(paper.id)
    if (papers.value.length === 1 && page.value > 1) page.value--
    await load()
  } catch (error) { ElMessage.error(requestErrorMessage(error, '删除失败。')) }
}
onMounted(load)
</script>

<style scoped>
.paper-manager { display: grid; gap: 16px; min-width: 0; }
.manager-tools { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
.manager-tools .el-input { flex: 1; min-width: 180px; }
.manager-tools a { font-size: 13px; }
.manager-row { display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 16px 0; border-bottom: 1px solid var(--color-border); }
.manager-row > div:first-child { min-width: 0; overflow-wrap: anywhere; }
.manager-row strong { font-size: 15px; }
.manager-row p, .manager-row small, .file-note { font-size: 12px; color: var(--color-muted); }
.row-actions { display: flex; flex-shrink: 0; }
.form-pair { display: grid; grid-template-columns: 2fr 1fr; gap: 12px; }
.el-select { width: 100%; }
.doi-input-row { display: flex; gap: 8px; width: 100%; }
.doi-input-row .el-input { min-width: 0; flex: 1; }
.metadata-summary { padding: 12px; margin: 12px 0; background: var(--color-panel); border: 1px solid var(--color-border); overflow-wrap: anywhere; }
.metadata-summary strong { font-size: 14px; }
.metadata-summary p, .metadata-summary small { color: var(--color-muted); font-size: 12px; }
.paper-extra { margin: 16px 0; }
input[type=file] { max-width: 100%; }
@media (max-width: 640px) { .manager-row { align-items: start; flex-direction: column; } }
</style>
