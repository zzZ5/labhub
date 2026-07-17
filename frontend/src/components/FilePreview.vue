<template>
  <div class="file-preview">
    <div v-if="status === 'pending'" class="preview-state"><FeedbackPanel type="processing" title="正在生成预览" description="文件转换完成后会自动刷新。" /></div>
    <div v-else-if="status === 'failed'" class="preview-state"><FeedbackPanel type="error" title="预览生成失败" :description="error || '可以下载原文件查看，或重新上传 PDF、DOCX、PPTX 文件。'"><slot name="fallback" /></FeedbackPanel></div>
    <button v-else-if="kind === 'image' && url" class="image-preview-trigger" type="button" aria-label="查看原图" @click="openImage">
      <img :src="url" :alt="title" />
      <span><el-icon><ZoomIn /></el-icon>查看原图</span>
    </button>
    <video v-else-if="kind === 'video' && url" :src="url" controls preload="metadata" />
    <iframe v-else-if="url" :src="url" :title="title" />
    <div v-else class="preview-state"><FeedbackPanel type="warning" title="当前文件暂不能在线查看" description="可以下载原文件查看，或转换为 PDF 后重新上传。"><slot name="fallback" /></FeedbackPanel></div>
    <Teleport to="body">
      <div v-if="imageOpen" ref="lightbox" class="image-lightbox" role="dialog" aria-modal="true" :aria-label="`${title}原图`" tabindex="-1" @click.self="closeImage" @keydown.esc="closeImage">
        <button class="lightbox-close" type="button" aria-label="关闭原图" @click="closeImage"><el-icon><Close /></el-icon></button>
        <img :src="url" :alt="title" />
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref } from 'vue'
import { Close, ZoomIn } from '@element-plus/icons-vue'
import FeedbackPanel from './FeedbackPanel.vue'

const props = withDefaults(defineProps<{ url?: string; title: string; filename?: string; mimeType?: string; status?: string; error?: string }>(), {
  url: '', filename: '', mimeType: '', status: '', error: '',
})
const kind = computed(() => {
  const value = `${props.filename} ${props.mimeType}`.toLowerCase()
  if (/\.(png|jpe?g|gif|webp)\b|image\//.test(value)) return 'image'
  if (/\.(mp4|webm|mov)\b|video\//.test(value)) return 'video'
  return 'document'
})
const imageOpen = ref(false)
const lightbox = ref<HTMLElement>()

async function openImage() {
  imageOpen.value = true
  await nextTick()
  lightbox.value?.focus()
}

function closeImage() {
  imageOpen.value = false
}
</script>

<style scoped>
.file-preview { overflow: hidden; border: 1px solid #dfe5e1; border-radius: 10px; background: #eef2f0; }
.file-preview iframe { display: block; width: 100%; height: min(78dvh, 980px); min-height: 560px; border: 0; background: #fff; }
.file-preview img, .file-preview video { display: block; width: 100%; max-height: min(78dvh, 980px); background: #111; object-fit: contain; }
.image-preview-trigger { position: relative; display: block; width: 100%; border: 0; padding: 0; background: #111; cursor: zoom-in; }
.image-preview-trigger span { position: absolute; right: 12px; bottom: 12px; display: inline-flex; align-items: center; gap: 5px; border-radius: 4px; padding: 6px 9px; background: rgba(16, 28, 21, .68); color: #fff; font-size: 12px; opacity: .76; transition: opacity .18s ease, transform .18s ease; }
.image-preview-trigger:hover span, .image-preview-trigger:focus-visible span { opacity: 1; transform: translateY(-2px); }
.image-lightbox { position: fixed; z-index: 5000; inset: 0; display: grid; place-items: center; padding: 32px; background: rgba(10, 18, 13, .9); outline: none; }
.image-lightbox img { display: block; max-width: 96vw; max-height: 92dvh; object-fit: contain; touch-action: pinch-zoom; }
.lightbox-close { position: fixed; z-index: 1; top: 20px; right: 20px; display: grid; width: 42px; height: 42px; place-items: center; border: 1px solid rgba(255,255,255,.28); border-radius: 50%; background: rgba(0,0,0,.28); color: #fff; cursor: pointer; font-size: 22px; }
.preview-state { display: grid; min-height: 420px; place-items: center; align-content: center; padding: 32px; }
.preview-state :deep(.feedback-panel) { width: min(100%, 620px); text-align: left; }
@media (max-width: 640px) {
  .file-preview iframe { height: 68dvh; min-height: 440px; }
  .file-preview img, .file-preview video { max-height: 68dvh; }
  .preview-state { min-height: max(440px, 62dvh); padding: 24px 18px; }
  .image-lightbox { padding: 12px; }
  .lightbox-close { top: 12px; right: 12px; }
}
</style>
