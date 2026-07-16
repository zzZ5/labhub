<template>
  <div class="instrument-tools">
    <div class="instrument-toolbar card">
      <input
        :value="keyword"
        type="search"
        placeholder="搜索仪器名称、型号、位置或说明"
        @input="$emit('update:keyword', ($event.target as HTMLInputElement).value)"
      />
      <select :value="status" @change="$emit('update:status', ($event.target as HTMLSelectElement).value)">
        <option value="">全部状态</option>
        <option value="normal">正常</option>
        <option value="maintenance">维护中</option>
        <option value="disabled">停用</option>
      </select>
      <template v-if="canManage">
        <input ref="excelInput" class="hidden-file-input" type="file" accept=".xlsx" @change="selectExcel" />
        <a class="toolbar-link" href="/templates/instruments-import-template.xlsx" download>下载模板</a>
        <button type="button" class="secondary-action" @click="excelInput?.click()">导入 Excel</button>
        <button type="button" @click="$emit('create')">新建设备</button>
      </template>
    </div>
    <p v-if="canManage" class="import-tip">
      模板填写仪器名称、型号、状态、详细位置、设备图片和使用说明；图片插入对应行即可批量导入。
    </p>
    <UploadProgress :active="importing" :progress="progress" uploading-text="正在上传设备表，请不要关闭页面。" processing-text="上传完成，正在解析仪器和图片。" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import UploadProgress from '../../../components/UploadProgress.vue'
import { validateUploadFile } from '../../../utils/files'

defineProps<{
  keyword: string
  status: string
  canManage: boolean
  importing: boolean
  progress: number
}>()

const emit = defineEmits<{
  'update:keyword': [value: string]
  'update:status': [value: string]
  create: []
  import: [file: File]
}>()

const excelInput = ref<HTMLInputElement | null>(null)

function selectExcel(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (file) {
    const message = validateUploadFile(file)
    if (message) ElMessage.warning(message)
    else emit('import', file)
  }
}
</script>

<style scoped>
.instrument-tools {
  display: grid;
  gap: 8px;
}

.instrument-toolbar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 150px auto auto auto;
  gap: 10px;
  align-items: center;
  padding: 12px;
  box-shadow: none;
}

.instrument-toolbar input,
.instrument-toolbar select {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 38px;
  padding: 0 12px;
  background: #fff;
  color: var(--color-text);
  font: inherit;
}

.instrument-toolbar input:focus,
.instrument-toolbar select:focus {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

.instrument-toolbar button,
.toolbar-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-cau-green);
  border-radius: var(--radius-sm);
  min-height: 38px;
  padding: 0 14px;
  background: var(--color-cau-green);
  color: #fff;
  cursor: pointer;
  font-size: 14px;
  font-weight: 700;
  white-space: nowrap;
}

.toolbar-link,
.instrument-toolbar .secondary-action {
  border-color: rgba(0, 135, 60, 0.22);
  background: #fff;
  color: var(--color-cau-green);
}

.toolbar-link:hover,
.instrument-toolbar .secondary-action:hover {
  background: var(--color-eco-green);
}

.hidden-file-input {
  display: none;
}

.import-tip {
  margin: 0 4px;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 900px) {
  .instrument-toolbar {
    grid-template-columns: minmax(0, 1fr) 140px;
  }
}

@media (max-width: 620px) {
  .instrument-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
