<template>
  <section class="editor-grid" :class="{ 'mobile-editor-open': mobileEditorOpen }">
    <CmsContentList title="论文成果" action-label="新增论文" :items="rows" :active-key="editingId || ''" @create="createPublication" @edit="openPublication">
      <template #tools><CmsImportStrip description="批量导入论文成果，优先按 DOI 更新；没有 DOI 时按题目和年份匹配。" template-url="/templates/publications-import-template.xlsx" :loading="importing" :progress="importProgress" :completed="importCompleted" uploading-text="正在上传论文成果表，请不要关闭页面。" processing-text="上传完成，正在写入论文成果。" @import="emit('import', $event)" @reset="emit('resetImport')" /></template>
    </CmsContentList>
    <article class="card form-panel">
      <CmsMobileEditorBack @back="mobileEditorOpen = false" />
      <div class="form-heading"><div><span>{{ editingId ? '正在编辑' : '新增内容' }}</span><h2>{{ form.title || '论文成果' }}</h2></div></div>
      <el-form label-position="top">
        <div class="form-section-label"><strong>引文信息</strong><span>粘贴引文并确认拆分结果</span></div>
        <el-form-item label="GB/T 7714-2025格式引文"><el-input v-model="form.citation_text" type="textarea" :rows="4" placeholder="例：作者. 论文题目. 期刊, 2026, 14(5): 123765. DOI: 10.xxxx/xxxxx" /></el-form-item>
        <div class="citation-actions"><button class="secondary-inline-action" type="button" @click="parsePublicationCitation()">拆分并预览</button><span>保存前请确认拆分出的标题、作者和期刊信息。</span></div>
        <FeedbackPanel v-if="hasPreview" type="info" title="拆分预览" description="请核对识别结果，未识别字段需要修改引文后重新拆分。" class="citation-preview">
          <dl>
            <div><dt>题名</dt><dd>{{ preview.title || '未识别' }}</dd></div>
            <div><dt>作者</dt><dd>{{ preview.authors || '未识别' }}</dd></div>
            <div><dt>期刊</dt><dd>{{ preview.journal || '未识别' }}</dd></div>
            <div><dt>年份</dt><dd>{{ preview.year || '未识别' }}</dd></div>
            <div><dt>卷期页</dt><dd>{{ volumePreview || '未识别' }}</dd></div>
            <div><dt>DOI</dt><dd>{{ preview.doi || '未填写' }}</dd></div>
          </dl>
        </FeedbackPanel>
        <div class="form-two-col">
          <el-form-item label="可见范围"><el-select v-model="form.visibility"><el-option label="公开" value="public" /><el-option label="成员可见" value="members" /><el-option label="管理员可见" value="admins" /></el-select></el-form-item>
          <el-form-item label="首页排序"><el-input-number v-model="form.sort_order" :min="0" /></el-form-item>
        </div>
        <div class="form-section-label"><strong>摘要与附件</strong><span>论文摘要和可公开查看的 PDF</span></div>
        <el-form-item label="摘要"><el-input v-model="form.abstract" type="textarea" :rows="4" /></el-form-item>
        <el-form-item label="PDF 附件"><UploadFileField v-model="form.pdf_file" :disabled="saving" accept="application/pdf,.pdf" :max-size-mb="200" :existing-label="currentPdf ? displayFileLabel(currentPdf) : ''" /></el-form-item>
      </el-form>
      <CmsFormActions :saving="saving" :progress="progress" :deletable="Boolean(editingId)" @save="savePublication" @delete="deletePublication" />
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi, type ParsedPublicationCitation } from '../../../api/cms'
import type { Publication } from '../../../api/publicPortal'
import CmsContentList from './CmsContentList.vue'
import CmsFormActions from './CmsFormActions.vue'
import CmsImportStrip from './CmsImportStrip.vue'
import CmsMobileEditorBack from './CmsMobileEditorBack.vue'
import UploadFileField from '../../../components/UploadFileField.vue'
import FeedbackPanel from '../../../components/FeedbackPanel.vue'
import type { CmsListRow } from '../composables/useCmsContentData'
import { useCmsEditorMutation } from '../composables/useCmsEditorMutation'

defineProps<{ rows: CmsListRow<Publication>[]; importing: boolean; importProgress: number; importCompleted: boolean; displayFileLabel: (value: string) => string }>()
const emit = defineEmits<{ import: [file: File]; changed: []; resetImport: [] }>()

type PublicationForm = Record<string, unknown> & {
  citation_text: string
  title: string
  authors: string
  journal: string
  year: number | string
  volume: string
  issue: string
  pages: string
  doi: string
  impact_factor: string | number
  jcr_partition: string
  cas_partition: string
  abstract: string
  pdf_file?: File
  visibility: string
  sort_order: number
}
type PublicationPreview = Omit<Pick<ParsedPublicationCitation, 'authors' | 'title' | 'journal' | 'year' | 'volume' | 'issue' | 'pages' | 'doi'>, 'year'> & {
  year: number | string
}

const editingId = ref<number | null>(null)
const mobileEditorOpen = ref(false)
const currentPdf = ref('')
const form = reactive<PublicationForm>({
  citation_text: '', title: '', authors: '', journal: '', year: new Date().getFullYear(), volume: '', issue: '', pages: '', doi: '',
  impact_factor: '', jcr_partition: '', cas_partition: '', abstract: '', pdf_file: undefined, visibility: 'public', sort_order: 0,
})
const preview = reactive<PublicationPreview>({ authors: '', title: '', journal: '', year: '', volume: '', issue: '', pages: '', doi: '' })
const hasPreview = computed(() => Boolean(preview.title || preview.authors || preview.journal || preview.year || preview.doi))
const volumePreview = computed(() => {
  const volumeIssue = [preview.volume, preview.issue ? `(${preview.issue})` : ''].filter(Boolean).join('')
  return [volumeIssue, preview.pages].filter(Boolean).join(': ')
})
const { saving, progress, save, remove, errorMessage } = useCmsEditorMutation(async () => emit('changed'))

function clearPreview() {
  Object.assign(preview, { authors: '', title: '', journal: '', year: '', volume: '', issue: '', pages: '', doi: '' })
}

function applyPreview(parsed: Partial<PublicationPreview>, writeForm = true) {
  Object.assign(preview, {
    authors: parsed.authors || '', title: parsed.title || '', journal: parsed.journal || '', year: parsed.year || '',
    volume: parsed.volume || '', issue: parsed.issue || '', pages: parsed.pages || '', doi: parsed.doi || '',
  })
  if (!writeForm) return
  Object.entries(preview).forEach(([key, value]) => { form[key] = value })
}

function resetPublication() {
  editingId.value = null
  currentPdf.value = ''
  Object.assign(form, {
    citation_text: '', title: '', authors: '', journal: '', year: new Date().getFullYear(), volume: '', issue: '', pages: '', doi: '',
    impact_factor: '', jcr_partition: '', cas_partition: '', abstract: '', pdf_file: undefined, visibility: 'public', sort_order: 0,
  })
  clearPreview()
}

function createPublication() {
  resetPublication()
  mobileEditorOpen.value = true
}

function openPublication(item: Publication) {
  editPublication(item)
  mobileEditorOpen.value = true
}

function editPublication(item: Publication) {
  editingId.value = item.id
  currentPdf.value = item.pdf_file || ''
  Object.assign(form, {
    citation_text: formatCitation(item), title: item.title, authors: item.authors, journal: item.journal || '', year: item.year,
    volume: item.volume || '', issue: item.issue || '', pages: item.pages || '', doi: item.doi || '',
    impact_factor: item.impact_factor || '', jcr_partition: item.jcr_partition || '', cas_partition: item.cas_partition || '',
    abstract: item.abstract || '', pdf_file: undefined, visibility: item.visibility || 'public', sort_order: item.sort_order || 0,
  })
  applyPreview(item, false)
}

async function parsePublicationCitation(showMessage = true) {
  const citation = form.citation_text.replace(/\s+/g, ' ').trim()
  if (!citation) {
    clearPreview()
    if (showMessage) ElMessage.warning('请先填写 GB/T 7714-2025 格式引文。')
    return false
  }
  try {
    const parsed = await cmsApi.parsePublicationCitation(citation)
    applyPreview(parsed)
    if (!parsed.complete) {
      if (showMessage) ElMessage.warning('拆分结果不完整，请检查预览后补充缺失信息。')
      return false
    }
    if (showMessage) ElMessage.success('已拆分，请检查预览结果后保存。')
    return true
  } catch (error) {
    if (showMessage) ElMessage.error(errorMessage(error, '引文拆分失败，请稍后重试。'))
    return false
  }
}

function formatCitation(item: Publication) {
  const volumeIssue = [item.volume, item.issue ? `(${item.issue})` : ''].filter(Boolean).join('')
  const pages = item.pages ? `: ${item.pages}` : ''
  const meta = [item.year, [volumeIssue, pages].filter(Boolean).join('')].filter(Boolean).join(', ')
  const doi = item.doi ? ` DOI: ${item.doi}` : ''
  return [item.authors, item.title, item.journal, meta].filter(Boolean).join('. ') + doi
}

function payload() {
  const { citation_text: _citationText, ...data } = form
  return data
}

async function savePublication() {
  if (!await parsePublicationCitation(false)) {
    ElMessage.warning('请先点击“拆分并预览”，确认结果后再保存。')
    return
  }
  const id = editingId.value
  const succeeded = await save((onUploadProgress) =>
    id ? cmsApi.updatePublication(id, payload(), onUploadProgress) : cmsApi.createPublication(payload(), onUploadProgress),
  )
  if (succeeded) {
    resetPublication()
    mobileEditorOpen.value = false
  }
}

async function deletePublication() {
  const id = editingId.value
  if (!id) return
  const succeeded = await remove('确定删除这篇论文吗？', () => cmsApi.deletePublication(id))
  if (succeeded) {
    resetPublication()
    mobileEditorOpen.value = false
  }
}
</script>
