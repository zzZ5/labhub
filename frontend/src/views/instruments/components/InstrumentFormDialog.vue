<template>
  <el-dialog
    :model-value="open"
    class="instrument-form-dialog"
    :title="instrument ? '编辑设备' : '新建设备'"
    width="720px"
    align-center
    destroy-on-close
    :close-on-click-modal="!saving"
    :close-on-press-escape="!saving"
    @update:model-value="$emit('update:open', $event)"
  >
    <p class="entity-form-intro">维护设备基本信息、位置、图片和使用说明。</p>
    <el-form label-position="top" class="entity-form instrument-form">
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
        <ImageCropField v-model="form.image" :disabled="saving" :existing-url="instrument?.image || ''" :existing-size="instrument?.image_size || 0" :aspect-ratio="4 / 3" :output-width="1400" :output-height="1050" :max-size-mb="20" hint="按设备列表比例裁剪，原图不超过 20 MB" />
      </el-form-item>
      <el-form-item label="使用说明">
        <el-input v-model="form.notes" type="textarea" :rows="8" placeholder="可填写操作步骤、注意事项、联系人或维护要求。" />
      </el-form-item>
    </el-form>
    <template #footer>
      <UploadProgress :active="saving" :progress="progress" uploading-text="正在上传设备图片，请不要关闭窗口。" processing-text="上传完成，正在保存设备信息。" />
      <div class="entity-form-footer">
        <el-button @click="$emit('update:open', false)">取消</el-button>
        <el-button type="primary" :loading="saving" @click="submit">{{ instrument ? '保存修改' : '创建设备' }}</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'

import ImageCropField from '../../../components/ImageCropField.vue'
import UploadProgress from '../../../components/UploadProgress.vue'
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

:global(.instrument-form-dialog) {
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 32px);
}

:global(.instrument-form-dialog .el-dialog__body) {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
}

.form-two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 620px) {
  .form-two-col {
    grid-template-columns: 1fr;
  }
}
</style>
