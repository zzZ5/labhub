<template>
  <el-dialog
    :model-value="open"
    :title="instrument ? '编辑设备' : '新建设备'"
    width="620px"
    @update:model-value="$emit('update:open', $event)"
  >
    <el-form label-position="top" class="instrument-form">
      <el-form-item label="仪器名称"><el-input v-model="form.name" /></el-form-item>
      <div class="form-two-col">
        <el-form-item label="型号"><el-input v-model="form.model" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status">
            <el-option label="正常" value="normal" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="停用" value="disabled" />
          </el-select>
        </el-form-item>
      </div>
      <el-form-item label="详细位置"><el-input v-model="form.location_detail" placeholder="如 沃土实验室一楼" /></el-form-item>
      <el-form-item label="设备图片">
        <input :key="fileInputKey" class="file-input" type="file" accept="image/*" @change="selectImage" />
        <small v-if="form.image" class="upload-file-note">{{ form.image.name }}（{{ formatFileSize(form.image.size) }}）</small>
        <small v-else-if="instrument?.image" class="upload-file-note">当前已有图片；不选择则保留原图。</small>
      </el-form-item>
      <el-form-item label="使用说明">
        <el-input v-model="form.notes" type="textarea" :rows="8" placeholder="可填写操作步骤、注意事项、联系人或维护要求。" />
      </el-form-item>
    </el-form>
    <template #footer>
      <div v-if="saving && progress > 0" class="upload-progress">
        <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined" />
        <span>{{ progress < 100 ? '正在上传设备图片，请不要关闭窗口。' : '上传完成，正在保存设备信息。' }}</span>
      </div>
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">{{ instrument ? '保存修改' : '保存设备' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import type { Instrument, InstrumentFormPayload } from '../../../api/instruments'

const props = defineProps<{
  open: boolean
  instrument: Instrument | null
  saving: boolean
  progress: number
}>()

const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [payload: InstrumentFormPayload]
}>()

const fileInputKey = ref(0)
const form = reactive<InstrumentFormPayload>({
  name: '',
  model: '',
  location_detail: '',
  status: 'normal',
  notes: '',
  image: undefined,
})

function resetForm() {
  Object.assign(form, {
    name: props.instrument?.name || '',
    model: props.instrument?.model || '',
    location_detail: props.instrument?.location_detail || '',
    status: props.instrument?.status || 'normal',
    notes: props.instrument?.notes || '',
    image: undefined,
  })
  fileInputKey.value += 1
}

function selectImage(event: Event) {
  form.image = (event.target as HTMLInputElement).files?.[0]
}

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function submit() {
  const name = form.name.trim()
  if (!name) {
    ElMessage.warning('请填写仪器名称。')
    return
  }
  emit('save', { ...form, name })
}

watch(() => props.open, (open) => {
  if (open) resetForm()
})
</script>

<style scoped>
.instrument-form {
  display: grid;
}

.form-two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
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
  margin-bottom: 12px;
  padding: 12px;
  background: var(--color-soft-gray);
  text-align: left;
}

.upload-progress span {
  color: var(--color-muted);
  font-size: 13px;
}

@media (max-width: 620px) {
  .form-two-col {
    grid-template-columns: 1fr;
  }
}
</style>
