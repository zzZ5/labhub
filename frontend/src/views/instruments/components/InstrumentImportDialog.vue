<template>
  <el-dialog
    :model-value="open"
    title="批量导入仪器设备"
    width="620px"
    @update:model-value="$emit('update:open', $event)"
  >
    <div class="import-panel">
      <div class="import-note">
        <strong>按模板整理仪器清单</strong>
        <p>第一张表说明填写规则，第二张表填写仪器名称、型号、状态、详细位置、设备图片和使用说明。图片请直接插入对应数据行。</p>
        <a href="/templates/instruments-import-template.xlsx" download>下载仪器设备导入模板</a>
      </div>

      <el-form label-position="top">
        <el-form-item label="仪器清单（.xlsx）">
          <UploadFileField
            v-model="file"
            :disabled="saving"
            accept=".xlsx"
            :max-size-mb="50"
            hint="请选择仪器设备导入模板，文件和内嵌图片合计不超过 50 MB"
          />
        </el-form-item>
      </el-form>

      <FeedbackPanel
        v-if="result"
        type="success"
        title="导入完成"
        :description="`共处理 ${result.total} 条，新增 ${result.created} 条，更新 ${result.updated} 条，匹配图片 ${result.images} 张。`"
      />
    </div>

    <template #footer>
      <UploadProgress
        :active="saving"
        :progress="progress"
        uploading-text="正在上传仪器清单，请不要关闭窗口。"
        processing-text="上传完成，正在解析仪器信息和图片。"
      />
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">开始导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import FeedbackPanel from '../../../components/FeedbackPanel.vue'
import UploadFileField from '../../../components/UploadFileField.vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import type { InstrumentImportResult } from '../../../api/instruments'

const props = defineProps<{
  open: boolean
  saving: boolean
  progress: number
  result: InstrumentImportResult | null
}>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  import: [file: File]
}>()

const file = ref<File>()

function submit() {
  if (!file.value) {
    ElMessage.warning('请选择 .xlsx 仪器清单。')
    return
  }
  emit('import', file.value)
}

watch(() => props.open, (open) => {
  if (open) file.value = undefined
})
</script>

<style scoped>
.import-panel { display: grid; gap: 16px; }
.import-note {
  border: 1px solid var(--color-success-border);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  background: var(--color-eco-green);
}
.import-note strong { display: block; margin-bottom: 5px; color: var(--color-deep-green); font-weight: 650; }
.import-note p { margin: 0 0 8px; color: var(--color-muted); font-size: 14px; line-height: 1.65; }
.import-note a { color: var(--color-cau-green); font-size: 14px; font-weight: 700; }
</style>
