<template>
  <el-dialog :model-value="open" title="上传学生资料" width="560px" @update:model-value="$emit('update:open', $event)">
    <el-form label-position="top">
      <el-form-item label="资料类型">
        <el-select v-model="form.file_type">
          <el-option label="开题报告" value="proposal_report" />
          <el-option label="开题 PPT" value="proposal_ppt" />
          <el-option label="中期报告" value="midterm_report" />
          <el-option label="中期 PPT" value="midterm_ppt" />
          <el-option label="毕业论文" value="thesis" />
          <el-option label="答辩 PPT" value="defense_ppt" />
          <el-option label="发表论文" value="paper" />
          <el-option label="其它" value="other" />
        </el-select>
      </el-form-item>
      <el-form-item label="标题"><el-input v-model="form.title" placeholder="例如：硕士毕业论文终稿" /></el-form-item>
      <el-form-item label="说明"><el-input v-model="form.description" type="textarea" :rows="3" /></el-form-item>
      <el-form-item label="文件">
        <input :key="fileInputKey" class="file-input" type="file" accept=".pdf,.doc,.docx,.ppt,.pptx" @change="selectFile" />
        <small v-if="form.file" class="upload-file-note">{{ form.file.name }}（{{ formatFileSize(form.file.size) }}）</small>
      </el-form-item>
    </el-form>
    <template #footer>
      <div v-if="saving || progress > 0" class="upload-progress">
        <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined" />
        <span>{{ progress < 100 ? '正在上传，请不要关闭窗口。' : '上传完成，正在保存记录。' }}</span>
      </div>
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">保存资料</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { StudentArchiveUploadPayload } from '../../../api/students'

const props = defineProps<{ open: boolean; saving: boolean; progress: number }>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [payload: StudentArchiveUploadPayload]
}>()

const fileInputKey = ref(0)
const form = reactive({ file_type: 'proposal_report', title: '', description: '', file: undefined as File | undefined })

function reset() {
  Object.assign(form, { file_type: 'proposal_report', title: '', description: '', file: undefined })
  fileInputKey.value += 1
}

function selectFile(event: Event) {
  form.file = (event.target as HTMLInputElement).files?.[0]
}

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function submit() {
  if (!form.file || !form.title.trim()) {
    ElMessage.warning('请填写标题并选择文件。')
    return
  }
  emit('save', { ...form, title: form.title.trim(), file: form.file })
}

watch(() => props.open, (open) => {
  if (open) reset()
})
</script>

<style scoped>
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
