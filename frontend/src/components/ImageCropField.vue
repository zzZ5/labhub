<template>
  <div class="image-crop-field" :class="{ wide: cropAspectRatio >= 1.7 }" tabindex="0" @paste="handlePaste">
    <div class="crop-preview" :class="{ circle: props.previewShape === 'circle' }" :style="previewStyle">
      <img v-if="displayUrl" :src="displayUrl" alt="图片预览" />
      <div v-else class="preview-empty"><el-icon><Picture /></el-icon><span>暂无图片</span></div>
    </div>
    <div class="crop-actions">
      <input ref="inputRef" type="file" accept="image/*" :disabled="props.disabled" @change="handleInput" />
      <el-button :disabled="props.disabled" @click="inputRef?.click()">{{ displayUrl ? '重新选择' : '选择图片' }}</el-button>
      <el-button v-if="props.modelValue" text :disabled="props.disabled" @click="clear">移除</el-button>
      <span>{{ props.hint || `按 ${ratioLabel} 裁剪，原图不超过 ${props.maxSizeMb} MB` }}</span>
      <span v-if="props.modelValue" class="file-meta">{{ props.modelValue.name }} · {{ formatFileSize(props.modelValue.size) }}</span>
      <span v-else-if="props.existingUrl && props.existingSize" class="file-meta">当前图片 · {{ formatFileSize(props.existingSize) }}</span>
    </div>

    <el-dialog
      v-model="dialogVisible"
      title="调整图片"
      width="min(900px, calc(100vw - 24px))"
      append-to-body
      destroy-on-close
      @opened="refreshCropper"
      @closed="closeCropper"
    >
      <div class="crop-dialog-body">
        <div class="crop-specification">
          <div>
            <strong>固定裁剪比例 {{ ratioLabel }}</strong>
            <span>移动或缩放照片，将需要保留的内容放入框内</span>
          </div>
          <span>{{ props.outputWidth }} × {{ props.outputHeight }} px</span>
        </div>
        <el-alert v-if="cropError" type="error" :closable="false" :title="cropError" />
        <div class="crop-stage">
          <Cropper
            v-if="sourceUrl"
            ref="cropperRef"
            class="cropper"
            :src="sourceUrl"
            :stencil-size="fixedStencilSize"
            :stencil-props="fixedStencilProps"
            :canvas="{ width: props.outputWidth, height: props.outputHeight, imageSmoothingQuality: 'high' }"
            image-restriction="stencil"
            :move-image="{ mouse: true, touch: true }"
            :resize-image="{ wheel: true, touch: true, adjustStencil: false }"
            :auto-zoom="true"
            :transitions="true"
            @ready="handleCropperReady"
            @error="handleCropperError"
          />
        </div>
        <div class="crop-toolbar">
          <el-tooltip content="向左旋转"><el-button circle aria-label="向左旋转" :disabled="!cropperReady" @click="rotate(-90)"><el-icon><RefreshLeft /></el-icon></el-button></el-tooltip>
          <el-tooltip content="向右旋转"><el-button circle aria-label="向右旋转" :disabled="!cropperReady" @click="rotate(90)"><el-icon><RefreshRight /></el-icon></el-button></el-tooltip>
          <el-tooltip content="缩小"><el-button circle aria-label="缩小" :disabled="!cropperReady" @click="zoom(0.85)"><el-icon><ZoomOut /></el-icon></el-button></el-tooltip>
          <el-tooltip content="放大"><el-button circle aria-label="放大" :disabled="!cropperReady" @click="zoom(1.15)"><el-icon><ZoomIn /></el-icon></el-button></el-tooltip>
          <el-tooltip content="重置"><el-button circle aria-label="重置" :disabled="!cropperReady" @click="resetCropper"><el-icon><Refresh /></el-icon></el-button></el-tooltip>
          <span>{{ cropperReady ? `可拖动照片、滚轮缩放，输出 ${props.outputWidth} × ${props.outputHeight} px` : '正在载入图片…' }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="cropping" :disabled="!cropperReady || Boolean(cropError)" @click="confirmCrop">使用此裁剪</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { Picture, Refresh, RefreshLeft, RefreshRight, ZoomIn, ZoomOut } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

import { formatFileSize, validateUploadFile } from '../utils/files'

const props = withDefaults(defineProps<{
  modelValue?: File
  existingUrl?: string
  existingSize?: number
  aspectRatio: number
  outputWidth: number
  outputHeight: number
  maxSizeMb?: number
  hint?: string
  previewShape?: 'rectangle' | 'circle'
  disabled?: boolean
}>(), {
  existingUrl: '',
  existingSize: 0,
  maxSizeMb: 20,
  hint: '',
  previewShape: 'rectangle',
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [file: File | undefined]
  preview: [url: string]
}>()

const inputRef = ref<HTMLInputElement | null>(null)
const cropperRef = ref<InstanceType<typeof Cropper> | null>(null)
const dialogVisible = ref(false)
const cropping = ref(false)
const cropperReady = ref(false)
const cropError = ref('')
const sourceUrl = ref('')
const croppedPreviewUrl = ref('')
const sourceName = ref('image')

const displayUrl = computed(() => croppedPreviewUrl.value || props.existingUrl)
const cropAspectRatio = computed(() => props.aspectRatio)
const hiddenStencilEdges = { north: false, east: false, south: false, west: false }
const hiddenStencilCorners = {
  eastNorth: false,
  eastSouth: false,
  westNorth: false,
  westSouth: false,
}
const fixedStencilProps = computed(() => ({
  aspectRatio: cropAspectRatio.value,
  movable: false,
  resizable: false,
  handlers: hiddenStencilCorners,
  lines: hiddenStencilEdges,
  previewClass: 'labhub-fixed-stencil',
}))
const ratioLabel = computed(() => {
  const gcd = (left: number, right: number): number => right ? gcd(right, left % right) : left
  const divisor = gcd(props.outputWidth, props.outputHeight)
  return `${props.outputWidth / divisor}:${props.outputHeight / divisor}`
})
const previewStyle = computed(() => ({ aspectRatio: `${props.outputWidth} / ${props.outputHeight}` }))

function fixedStencilSize({ boundaries }: { boundaries: { width: number; height: number } }) {
  const padding = boundaries.width < 520 ? 24 : 72
  const maxWidth = Math.max(120, boundaries.width - padding)
  const maxHeight = Math.max(120, boundaries.height - padding)
  const ratio = cropAspectRatio.value

  if (maxWidth / maxHeight > ratio) {
    return { width: Math.round(maxHeight * ratio), height: Math.round(maxHeight) }
  }
  return { width: Math.round(maxWidth), height: Math.round(maxWidth / ratio) }
}

function choose(file?: File) {
  if (!file) return
  const message = validateUploadFile(file, props.maxSizeMb * 1024 * 1024)
  if (message) {
    ElMessage.warning(message)
    return
  }
  releaseSource()
  cropperReady.value = false
  cropError.value = ''
  sourceName.value = file.name.replace(/\.[^.]+$/, '') || 'image'
  sourceUrl.value = URL.createObjectURL(file)
  dialogVisible.value = true
}

function handleInput(event: Event) {
  const input = event.target as HTMLInputElement
  choose(input.files?.[0])
  input.value = ''
}

function handlePaste(event: ClipboardEvent) {
  const item = Array.from(event.clipboardData?.items || []).find((candidate) => candidate.type.startsWith('image/'))
  const file = item?.getAsFile()
  if (!file) return
  event.preventDefault()
  choose(file)
}

function canvasBlob(canvas: HTMLCanvasElement) {
  return new Promise<Blob>((resolve, reject) => {
    canvas.toBlob((blob) => blob ? resolve(blob) : reject(new Error('图片处理失败')), 'image/webp', 0.9)
  })
}

async function confirmCrop() {
  const canvas = cropperRef.value?.getResult().canvas
  if (!canvas) {
    ElMessage.warning('请先选择有效的裁剪区域。')
    return
  }
  cropping.value = true
  try {
    const blob = await canvasBlob(canvas)
    const file = new File([blob], `${sourceName.value}.webp`, { type: 'image/webp', lastModified: Date.now() })
    if (croppedPreviewUrl.value) URL.revokeObjectURL(croppedPreviewUrl.value)
    croppedPreviewUrl.value = URL.createObjectURL(file)
    emit('update:modelValue', file)
    emit('preview', croppedPreviewUrl.value)
    dialogVisible.value = false
  } catch {
    ElMessage.error('图片裁剪失败，请换一张图片重试。')
  } finally {
    cropping.value = false
  }
}

async function refreshCropper() {
  await nextTick()
  window.requestAnimationFrame(() => {
    window.requestAnimationFrame(() => cropperRef.value?.refresh())
  })
}

function handleCropperReady() {
  cropperReady.value = true
  cropError.value = ''
  refreshCropper()
}

function handleCropperError() {
  cropperReady.value = false
  cropError.value = '图片读取失败，请使用 JPG、PNG 或 WebP 图片重试。'
}

function rotate(angle: number) {
  cropperRef.value?.rotate(angle)
  refreshCropper()
}

function zoom(factor: number) {
  cropperRef.value?.zoom(factor)
}

function resetCropper() {
  cropperRef.value?.reset()
  refreshCropper()
}

function clear() {
  if (croppedPreviewUrl.value) URL.revokeObjectURL(croppedPreviewUrl.value)
  croppedPreviewUrl.value = ''
  emit('update:modelValue', undefined)
  emit('preview', '')
}

function releaseSource() {
  if (sourceUrl.value) URL.revokeObjectURL(sourceUrl.value)
  sourceUrl.value = ''
}

function closeCropper() {
  cropperReady.value = false
  cropError.value = ''
  releaseSource()
}

watch(() => props.modelValue, (file) => {
  if (!file && croppedPreviewUrl.value) {
    URL.revokeObjectURL(croppedPreviewUrl.value)
    croppedPreviewUrl.value = ''
  }
})

onBeforeUnmount(() => {
  releaseSource()
  if (croppedPreviewUrl.value) URL.revokeObjectURL(croppedPreviewUrl.value)
})
</script>

<style scoped>
.image-crop-field {
  display: grid;
  grid-template-columns: minmax(120px, 180px) minmax(0, 1fr);
  align-items: center;
  gap: 14px;
  width: 100%;
}

.image-crop-field:focus-visible {
  border-radius: var(--radius-sm);
  outline: 2px solid rgba(0, 135, 60, 0.22);
  outline-offset: 4px;
}

.image-crop-field.wide {
  grid-template-columns: 1fr;
}

.image-crop-field.wide .crop-preview {
  max-width: 100%;
}

.crop-preview {
  width: 100%;
  overflow: hidden;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #f4f7f5;
}

.crop-preview.circle {
  aspect-ratio: 1 !important;
  border-radius: 50%;
}

.crop-preview img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-empty {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  align-content: center;
  gap: 5px;
  color: var(--color-muted);
  font-size: 12px;
}

.preview-empty .el-icon {
  color: var(--color-cau-green);
  font-size: 24px;
}

.crop-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  min-width: 0;
}

.crop-actions input {
  display: none;
}

.crop-actions > span {
  flex-basis: 100%;
  color: var(--color-muted);
  font-size: 12px;
}

.crop-actions .file-meta {
  overflow: hidden;
  color: var(--color-text);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.crop-dialog-body {
  display: grid;
  gap: 12px;
}

.crop-specification {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 48px;
  padding: 0 2px;
}

.crop-specification > div {
  display: grid;
  gap: 2px;
}

.crop-specification strong {
  color: var(--color-heading);
  font-size: 14px;
  font-weight: 600;
}

.crop-specification span {
  color: var(--color-muted);
  font-size: 12px;
}

.crop-specification > span {
  flex: 0 0 auto;
  padding: 5px 9px;
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: var(--radius-sm);
  background: var(--color-soft-green);
  color: var(--color-deep-green);
  font-variant-numeric: tabular-nums;
}

.crop-stage {
  position: relative;
  width: 100%;
  height: clamp(360px, 58vh, 540px);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: var(--radius-sm);
  background: #151b17;
}

.cropper {
  width: 100%;
  height: 100%;
  background: #151b17;
}

.cropper :deep(.labhub-fixed-stencil) {
  border: 2px solid rgba(255, 255, 255, 0.96);
  box-shadow: 0 0 0 9999px rgba(7, 12, 9, 0.58);
}

.crop-toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.crop-toolbar > span {
  margin-left: auto;
  color: var(--color-muted);
  font-size: 12px;
}

@media (max-width: 620px) {
  .image-crop-field {
    grid-template-columns: 112px minmax(0, 1fr);
  }

  .cropper {
    height: 100%;
  }

  .crop-stage {
    height: min(54vh, 440px);
  }

  .crop-specification {
    align-items: flex-start;
  }

  .crop-specification > div span {
    display: none;
  }

  .crop-toolbar > span {
    width: 100%;
    margin-left: 0;
  }
}
</style>
