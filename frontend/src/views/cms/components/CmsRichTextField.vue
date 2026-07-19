<template>
  <div class="cms-rich-text-field">
    <RichTextEditor
      ref="editorRef"
      :model-value="modelValue"
      :placeholder="placeholder"
      :uploading="uploading"
      :upload-progress="progress"
      @update:model-value="emit('update:modelValue', $event)"
      @image-selected="insertImage"
    />
    <small>可设置标题、列表和链接，也可在光标位置插入图片。</small>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi } from '../../../api/cms'
import RichTextEditor from '../../../components/RichTextEditor.vue'
import { UPLOAD_LIMIT, validateUploadFile } from '../../../utils/files'

withDefaults(defineProps<{ modelValue: string; placeholder?: string }>(), {
  placeholder: '开始撰写详细内容…',
})
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()

const editorRef = ref<{ insertImage: (src: string, alt?: string) => void } | null>(null)
const uploading = ref(false)
const progress = ref(0)

async function insertImage(file: File) {
  const validationMessage = validateUploadFile(file, UPLOAD_LIMIT.image)
  if (validationMessage) {
    ElMessage.warning(validationMessage)
    return
  }

  uploading.value = true
  progress.value = 0
  try {
    const uploaded = await cmsApi.createContentImage(file, (event) => {
      if (event.total) progress.value = Math.min(100, Math.round((event.loaded / event.total) * 100))
    })
    progress.value = 100
    editorRef.value?.insertImage(uploaded.image, file.name)
    ElMessage.success('图片已插入，请保存当前内容。')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '图片上传失败，请稍后重试。')
  } finally {
    uploading.value = false
    window.setTimeout(() => {
      if (!uploading.value) progress.value = 0
    }, 800)
  }
}
</script>

<style scoped>
.cms-rich-text-field { width: 100%; min-width: 0; }
.cms-rich-text-field :deep(.editor-content),
.cms-rich-text-field :deep(.editor-content .tiptap) { min-height: 280px; }
.cms-rich-text-field > small { display: block; margin-top: 7px; color: var(--color-muted); line-height: 1.6; }
</style>
