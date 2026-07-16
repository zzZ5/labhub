<template>
  <div class="file-preview">
    <div v-if="status === 'pending'" class="preview-state"><el-icon class="is-loading"><Loading /></el-icon><strong>正在生成预览</strong><p>文件转换完成后会自动刷新。</p></div>
    <div v-else-if="status === 'failed'" class="preview-state"><strong>预览生成失败</strong><p>{{ error || '可以下载原文件查看，或重新上传 PDF、DOCX、PPTX 文件。' }}</p><slot name="fallback" /></div>
    <img v-else-if="kind === 'image' && url" :src="url" :alt="title" />
    <video v-else-if="kind === 'video' && url" :src="url" controls preload="metadata" />
    <iframe v-else-if="url" :src="url" :title="title" />
    <div v-else class="preview-state"><strong>当前文件暂不能在线查看</strong><p>可以下载原文件查看，或转换为 PDF 后重新上传。</p><slot name="fallback" /></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{ url?: string; title: string; filename?: string; mimeType?: string; status?: string; error?: string }>(), {
  url: '', filename: '', mimeType: '', status: '', error: '',
})
const kind = computed(() => {
  const value = `${props.filename} ${props.mimeType}`.toLowerCase()
  if (/\.(png|jpe?g|gif|webp)\b|image\//.test(value)) return 'image'
  if (/\.(mp4|webm|mov)\b|video\//.test(value)) return 'video'
  return 'document'
})
</script>

<style scoped>
.file-preview { overflow: hidden; border: 1px solid #dfe5e1; border-radius: 10px; background: #eef2f0; }
.file-preview iframe { display: block; width: 100%; min-height: min(86vh, 980px); border: 0; background: #fff; }
.file-preview img, .file-preview video { display: block; width: 100%; max-height: min(86vh, 980px); background: #111; object-fit: contain; }
.preview-state { display: grid; min-height: 420px; place-items: center; align-content: center; gap: 10px; padding: 32px; color: var(--color-muted); text-align: center; }
.preview-state .el-icon { color: var(--color-cau-green); font-size: 28px; }
.preview-state strong { color: var(--color-deep-green); font-size: 20px; }
.preview-state p { max-width: 480px; margin: 0; line-height: 1.65; }
@media (max-width: 640px) { .file-preview iframe, .preview-state { min-height: 62vh; } }
</style>
