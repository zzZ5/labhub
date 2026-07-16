<template>
  <el-dialog :model-value="open" title="批量导入内部资料" width="620px" @update:model-value="$emit('update:open', $event)">
    <div class="import-panel">
      <div class="import-note">
        <strong>按模板填写资料清单</strong>
        <p>第二张表填写资料标题、分类、说明和文件名。需要带文件时，把所有文件打包成 zip，表格里的文件名要和 zip 内文件名一致。</p>
        <a href="/templates/documents-import-template.xlsx" download>下载内部资料导入模板</a>
      </div>
      <el-form label-position="top">
        <el-form-item label="资料清单（.xlsx）">
          <input :key="inputKey" class="file-input" type="file" accept=".xlsx" @change="selectExcel" />
          <small v-if="form.file" class="upload-file-note">{{ form.file.name }}（{{ formatFileSize(form.file.size) }}）</small>
        </el-form-item>
        <el-form-item label="资料文件包（.zip，可选）">
          <input :key="inputKey + 1" class="file-input" type="file" accept=".zip" @change="selectArchive" />
          <small v-if="form.archive" class="upload-file-note">{{ form.archive.name }}（{{ formatFileSize(form.archive.size) }}）</small>
        </el-form-item>
      </el-form>
      <div v-if="result" class="import-result">
        <strong>导入结果</strong>
        <span>新增 {{ result.created }} 条，更新 {{ result.updated }} 条，跳过 {{ result.skipped }} 条。</span>
        <ul v-if="result.errors.length">
          <li v-for="item in result.errors.slice(0, 6)" :key="item">{{ item }}</li>
        </ul>
      </div>
    </div>
    <template #footer>
      <div v-if="saving || progress > 0" class="upload-progress">
        <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined" />
        <span>{{ progress < 100 ? '正在上传并导入，请不要关闭窗口。' : '上传完成，正在处理资料。' }}</span>
      </div>
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">开始导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { DocumentImportPayload, DocumentImportResult } from '../../../api/documents'
import { formatFileSize } from '../documentPresentation'

const props = defineProps<{ open: boolean; saving: boolean; progress: number; result: DocumentImportResult | null }>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  import: [payload: DocumentImportPayload]
}>()

const inputKey = ref(0)
const form = reactive<{ file?: File; archive?: File }>({ file: undefined, archive: undefined })

function selectExcel(event: Event) {
  form.file = (event.target as HTMLInputElement).files?.[0]
}

function selectArchive(event: Event) {
  form.archive = (event.target as HTMLInputElement).files?.[0]
}

function submit() {
  if (!form.file) {
    ElMessage.warning('请选择 .xlsx 资料清单。')
    return
  }
  emit('import', { file: form.file, archive: form.archive })
}

watch(() => props.open, (open) => {
  if (!open) return
  Object.assign(form, { file: undefined, archive: undefined })
  inputKey.value += 2
})
</script>

<style scoped>
.import-panel {
  display: grid;
  gap: 16px;
}

.import-note,
.import-result {
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  background: var(--color-eco-green);
}

.import-note strong,
.import-result strong {
  display: block;
  margin-bottom: 5px;
  color: var(--color-deep-green);
  font-weight: 650;
}

.import-note p {
  margin: 0 0 8px;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

.import-note a {
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
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
  word-break: break-all;
}

.import-result {
  display: grid;
  gap: 6px;
  border-color: var(--color-border);
  background: #fff;
  color: var(--color-muted);
  font-size: 14px;
}

.import-result ul {
  margin: 4px 0 0;
  padding-left: 18px;
  color: #9f5135;
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
