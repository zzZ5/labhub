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
      <el-form-item label="视频链接（可选）">
        <el-input v-model="form.external_url" placeholder="支持哔哩哔哩或其他公开视频链接" />
        <small class="field-help">视频资料可只填写链接；普通文档继续上传文件。</small>
      </el-form-item>
      <el-form-item :label="document ? '替换文件（可选）' : '文件'">
        <UploadFileField v-model="form.file" :disabled="saving" :max-size-mb="200" :existing-label="document ? currentFileLabel(document) : ''" />
      </el-form-item>
    </el-form>
    <template #footer>
      <UploadProgress :active="saving" :progress="progress" processing-text="上传完成，正在保存资料。" />
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">{{ document ? '保存修改' : '保存资料' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import UploadFileField from '../../../components/UploadFileField.vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import type { DocumentCategory, DocumentFormPayload, LabDocument } from '../../../api/documents'
import { categoryName, currentFileLabel } from '../documentPresentation'

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

const form = reactive<DocumentFormPayload>({ title: '', category_id: undefined, description: '', external_url: '', file: undefined })

function reset() {
  Object.assign(form, {
    title: props.document?.title || '',
    category_id: props.document?.category?.id,
    description: props.document?.description || '',
    external_url: props.document?.external_url || '',
    file: undefined,
  })
}

function submit() {
  const title = form.title.trim()
  if (!title || (!props.document && !form.file && !form.external_url?.trim())) {
    ElMessage.warning('请填写资料标题，并上传文件或填写视频链接。')
    return
  }
  emit('save', { ...form, title })
}

watch(() => props.open, (open) => {
  if (open) reset()
})
</script>

<style scoped>
.field-help { display: block; margin-top: 6px; color: var(--color-muted); font-size: 12px; line-height: 1.5; }
</style>
