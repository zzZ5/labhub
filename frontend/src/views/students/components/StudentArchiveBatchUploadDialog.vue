<template>
  <el-dialog :model-value="open" title="批量上传个人归档资料" width="760px" @update:model-value="$emit('update:open', $event)">
    <div class="batch-upload">
      <div
        :class="['batch-toolbar', { dragging, disabled: saving }]"
        @dragenter.prevent="handleDragEnter"
        @dragover.prevent
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
      >
        <div>
          <strong>{{ dragging ? '松开即可添加文件' : '选择或拖入多份资料' }}</strong>
          <span>可将文件直接拖入此区域；支持 PDF、Word 和 PowerPoint，单个文件不超过 200 MB，单次最多 30 份。</span>
        </div>
        <label :class="['file-picker', { disabled: saving }]">
          选择文件
          <input type="file" multiple :disabled="saving" accept=".pdf,.doc,.docx,.ppt,.pptx" @change="selectFiles" />
        </label>
      </div>

      <div v-if="items.length" class="batch-defaults">
        <span>统一设置类型</span>
        <el-select v-model="defaultType" :disabled="saving" @change="applyDefaultType">
          <el-option v-for="option in typeOptions" :key="option.value" :label="option.label" :value="option.value" />
        </el-select>
        <small>可在下方逐份调整。</small>
      </div>

      <div v-if="items.length" class="batch-list">
        <article v-for="(item, index) in items" :key="item.key" class="batch-item">
          <div class="file-summary">
            <span>{{ index + 1 }}</span>
            <div><strong :title="item.file.name">{{ item.file.name }}</strong><small>{{ formatFileSize(item.file.size) }}</small></div>
            <button type="button" :disabled="saving" aria-label="移除文件" @click="removeItem(index)">移除</button>
          </div>
          <div class="file-fields">
            <el-select v-model="item.file_type" :disabled="saving" aria-label="资料类型">
              <el-option v-for="option in typeOptions" :key="option.value" :label="option.label" :value="option.value" />
            </el-select>
            <el-input v-model="item.title" :disabled="saving" maxlength="200" aria-label="资料标题" placeholder="资料标题" />
          </div>
        </article>
      </div>
      <div v-else class="batch-empty">尚未选择文件。</div>
    </div>

    <template #footer>
      <UploadProgress
        :active="saving"
        :progress="progress"
        :uploading-text="statusText || '正在依次上传归档资料，请不要关闭窗口。'"
        processing-text="文件已传输完成，正在保存最后一份资料。"
      />
      <el-button :disabled="saving" @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" :disabled="saving || !items.length" @click="submit">
        {{ items.length ? `上传 ${items.length} 份资料` : '开始上传' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import UploadProgress from '../../../components/UploadProgress.vue'
import type { StudentArchiveUploadPayload } from '../../../api/students'
import { formatFileSize, UPLOAD_LIMIT, validateUploadFile } from '../../../utils/files'

type BatchItem = StudentArchiveUploadPayload & { key: string }

const props = defineProps<{ open: boolean; saving: boolean; progress: number; statusText?: string }>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [items: StudentArchiveUploadPayload[]]
}>()

const typeOptions = [
  { label: '开题报告', value: 'proposal_report' },
  { label: '开题 PPT', value: 'proposal_ppt' },
  { label: '中期报告', value: 'midterm_report' },
  { label: '中期 PPT', value: 'midterm_ppt' },
  { label: '毕业论文', value: 'thesis' },
  { label: '答辩 PPT', value: 'defense_ppt' },
  { label: '发表论文', value: 'paper' },
  { label: '其它', value: 'other' },
]
const defaultType = ref('other')
const dragging = ref(false)
let dragDepth = 0
const items = reactive<BatchItem[]>([])

function titleFromFilename(filename: string) {
  return filename.replace(/\.(pdf|docx?|pptx?)$/i, '').trim() || filename
}

function selectFiles(event: Event) {
  const input = event.target as HTMLInputElement
  const selected = Array.from(input.files || [])
  input.value = ''
  addFiles(selected)
}

function addFiles(selected: File[]) {
  if (!selected.length) return
  const remaining = Math.max(0, 30 - items.length)
  if (!remaining) {
    ElMessage.warning('单次最多上传 30 份资料。')
    return
  }
  if (selected.length > remaining) ElMessage.warning(`单次最多上传 30 份资料，本次已选择前 ${remaining} 份。`)
  selected.slice(0, remaining).forEach((file) => {
    if (!/\.(pdf|docx?|pptx?)$/i.test(file.name)) {
      ElMessage.warning(`${file.name}：仅支持 PDF、Word 和 PowerPoint 文件。`)
      return
    }
    const message = validateUploadFile(file, UPLOAD_LIMIT.document)
    if (message) {
      ElMessage.warning(`${file.name}：${message}`)
      return
    }
    const duplicate = items.some((item) => item.file.name === file.name && item.file.size === file.size && item.file.lastModified === file.lastModified)
    if (duplicate) return
    items.push({
      key: `${file.name}-${file.size}-${file.lastModified}`,
      file,
      file_type: defaultType.value,
      title: titleFromFilename(file.name),
      description: '',
    })
  })
}

function handleDragEnter() {
  if (props.saving) return
  dragDepth += 1
  dragging.value = true
}

function handleDragLeave() {
  dragDepth = Math.max(0, dragDepth - 1)
  if (!dragDepth) dragging.value = false
}

function handleDrop(event: DragEvent) {
  dragDepth = 0
  dragging.value = false
  if (props.saving) return
  addFiles(Array.from(event.dataTransfer?.files || []))
}

function applyDefaultType(value: string) {
  items.forEach((item) => { item.file_type = value })
}

function removeItem(index: number) {
  if (!props.saving) items.splice(index, 1)
}

function submit() {
  if (props.saving || !items.length) return
  const missingTitle = items.find((item) => !item.title.trim())
  if (missingTitle) {
    ElMessage.warning(`请补充“${missingTitle.file.name}”的资料标题。`)
    return
  }
  emit('save', items.map(({ key: _key, ...item }) => ({ ...item, title: item.title.trim() })))
}

watch(() => props.open, (open) => {
  if (!open) return
  defaultType.value = 'other'
  dragDepth = 0
  dragging.value = false
  items.splice(0)
})
</script>

<style scoped>
.batch-upload { display: grid; gap: 12px; }
.batch-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; border: 1px dashed #b9c9bf; border-radius: var(--radius-sm); padding: 13px 14px; background: var(--color-panel); transition: border-color 150ms ease, background-color 150ms ease; }
.batch-toolbar.dragging { border-color: var(--color-cau-green); background: var(--color-eco-green); }
.batch-toolbar.disabled { opacity: .68; }
.batch-toolbar > div { display: grid; gap: 3px; min-width: 0; }
.batch-toolbar strong { color: var(--color-deep-green); font-size: 14px; }
.batch-toolbar span, .batch-defaults small { color: var(--color-muted); font-size: 12px; line-height: 1.5; }
.file-picker { flex: 0 0 auto; border: 1px solid var(--color-cau-green); border-radius: var(--radius-sm); padding: 7px 12px; background: #fff; color: var(--color-cau-green); cursor: pointer; font-size: 13px; font-weight: 700; }
.file-picker.disabled { cursor: not-allowed; opacity: .58; }
.file-picker input { display: none; }
.batch-defaults { display: grid; grid-template-columns: auto minmax(150px, 220px) minmax(0, 1fr); align-items: center; gap: 10px; }
.batch-defaults > span { color: var(--color-text); font-size: 13px; font-weight: 650; }
.batch-list { display: grid; gap: 8px; max-height: min(52vh, 520px); overflow-y: auto; padding-right: 3px; }
.batch-item { display: grid; gap: 8px; border: 1px solid var(--color-line); border-radius: var(--radius-sm); padding: 10px; background: #fff; }
.file-summary { display: grid; grid-template-columns: 24px minmax(0, 1fr) auto; align-items: center; gap: 8px; }
.file-summary > span { display: grid; width: 24px; height: 24px; place-items: center; border-radius: 50%; background: var(--color-eco-green); color: var(--color-cau-green); font-size: 11px; font-weight: 700; }
.file-summary > div { display: flex; min-width: 0; align-items: baseline; gap: 8px; }
.file-summary strong { min-width: 0; overflow: hidden; color: var(--color-text); font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }
.file-summary small { flex: 0 0 auto; color: var(--color-muted); font-size: 11px; }
.file-summary button { border: 0; padding: 3px; background: transparent; color: var(--color-muted); cursor: pointer; font-size: 12px; }
.file-fields { display: grid; grid-template-columns: minmax(140px, 180px) minmax(0, 1fr); gap: 8px; }
.batch-empty { border: 1px dashed var(--color-border); border-radius: var(--radius-sm); padding: 28px 16px; color: var(--color-muted); text-align: center; font-size: 13px; }

@media (max-width: 640px) {
  .batch-toolbar { align-items: stretch; flex-direction: column; }
  .file-picker { text-align: center; }
  .batch-defaults, .file-fields { grid-template-columns: 1fr; }
  .batch-defaults { gap: 6px; }
  .file-summary > div { display: grid; gap: 1px; }
}
</style>
