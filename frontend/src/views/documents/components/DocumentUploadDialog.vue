<template>
  <el-dialog
    :model-value="open"
    :title="document ? '编辑内部资料' : '上传内部资料'"
    width="560px"
    @update:model-value="$emit('update:open', $event)"
  >
    <el-form label-position="top">
      <el-form-item label="资料标题"><el-input v-model="form.title" placeholder="请输入资料标题" /></el-form-item>
      <el-form-item label="资料分类">
        <el-select v-model="form.category_id" clearable placeholder="选择分类">
          <el-option v-for="category in categories" :key="category.id" :label="categoryName(category)" :value="category.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="资料说明"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
      <el-form-item :label="document ? '替换文件（可选）' : '文件'">
        <input :key="fileInputKey" class="file-input" type="file" @change="selectFile" />
        <small v-if="form.file" class="upload-file-note">{{ form.file.name }}（{{ formatFileSize(form.file.size) }}）</small>
        <small v-else-if="document" class="upload-file-note">不选择文件则保留当前文件：{{ currentFileLabel(document) }}</small>
      </el-form-item>
    </el-form>
    <template #footer>
      <div v-if="saving || progress > 0" class="upload-progress">
        <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined" />
        <span>{{ progress < 100 ? '正在上传，请不要关闭窗口。' : '上传完成，正在保存记录。' }}</span>
      </div>
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">{{ document ? '保存修改' : '保存资料' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { DocumentCategory, DocumentFormPayload, LabDocument } from '../../../api/documents'
import { categoryName, currentFileLabel, formatFileSize } from '../documentPresentation'

const props = defineProps<{
  open: boolean
  document: LabDocument | null
  categories: DocumentCategory[]
  saving: boolean
  progress: number
}>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [payload: DocumentFormPayload]
}>()

const fileInputKey = ref(0)
const form = reactive<DocumentFormPayload>({ title: '', category_id: undefined, description: '', file: undefined })

function reset() {
  Object.assign(form, {
    title: props.document?.title || '',
    category_id: props.document?.category?.id,
    description: props.document?.description || '',
    file: undefined,
  })
  fileInputKey.value += 1
}

function selectFile(event: Event) {
  form.file = (event.target as HTMLInputElement).files?.[0]
}

function submit() {
  const title = form.title.trim()
  if (!title || (!props.document && !form.file)) {
    ElMessage.warning('请填写资料标题并选择文件。')
    return
  }
  emit('save', { ...form, title })
}

watch(() => props.open, (open) => {
  if (open) reset()
})
</script>

<style scoped>
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
  margin-bottom: 12px;
  padding: 12px;
  background: var(--color-soft-gray);
  text-align: left;
}

.upload-progress span {
  color: var(--color-muted);
  font-size: 13px;
}
</style>
