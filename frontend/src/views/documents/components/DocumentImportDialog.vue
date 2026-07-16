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
          <UploadFileField v-model="form.file" :disabled="saving" accept=".xlsx" :max-size-mb="50" hint="请选择内部资料导入模板，单个文件不超过 50 MB" />
        </el-form-item>
        <el-form-item label="资料文件包（.zip，可选）">
          <UploadFileField v-model="form.archive" :disabled="saving" accept=".zip" :max-size-mb="200" hint="文件名需与清单一致，压缩包不超过 200 MB" />
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
      <UploadProgress :active="saving" :progress="progress" uploading-text="正在上传并导入，请不要关闭窗口。" processing-text="上传完成，正在处理资料。" />
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">开始导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import UploadFileField from '../../../components/UploadFileField.vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import type { DocumentImportPayload, DocumentImportResult } from '../../../api/documents'

const props = defineProps<{ open: boolean; saving: boolean; progress: number; result: DocumentImportResult | null }>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  import: [payload: DocumentImportPayload]
}>()

const form = reactive<{ file?: File; archive?: File }>({ file: undefined, archive: undefined })

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

</style>
