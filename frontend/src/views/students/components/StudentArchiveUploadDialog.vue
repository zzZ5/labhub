<template>
  <el-dialog :model-value="open" :title="archive ? '编辑资料信息' : '上传学生资料'" width="560px" @update:model-value="$emit('update:open', $event)">
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
      <el-form-item v-if="!archive" label="文件">
        <UploadFileField v-model="form.file" :disabled="saving" accept=".pdf,.doc,.docx,.ppt,.pptx" :max-size-mb="200" hint="支持 PDF、Word 和 PowerPoint，单个文件不超过 200 MB" />
      </el-form-item>
      <div v-else class="current-file">
        <span>当前文件</span>
        <strong :title="archive.original_filename">{{ archive.original_filename || archive.title }}</strong>
        <small>编辑资料信息不会替换原文件。</small>
      </div>
    </el-form>
    <template #footer>
      <UploadProgress :active="saving && !archive" :progress="progress" processing-text="上传完成，正在保存学生资料。" />
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" :disabled="saving" @click="submit">{{ archive ? '保存修改' : '保存资料' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import UploadFileField from '../../../components/UploadFileField.vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import type { StudentArchiveFile, StudentArchiveMetadataPayload, StudentArchiveUploadPayload } from '../../../api/students'

const props = defineProps<{ open: boolean; saving: boolean; progress: number; archive?: StudentArchiveFile | null }>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [payload: StudentArchiveUploadPayload | StudentArchiveMetadataPayload]
}>()

const form = reactive({ file_type: 'proposal_report', title: '', description: '', file: undefined as File | undefined })

function reset() {
  Object.assign(form, { file_type: 'proposal_report', title: '', description: '', file: undefined })
}

function submit() {
  if (props.saving) return
  if (!form.title.trim()) {
    ElMessage.warning('请填写资料标题。')
    return
  }
  const metadata = { file_type: form.file_type, title: form.title.trim(), description: form.description.trim() }
  if (props.archive) {
    emit('save', metadata)
    return
  }
  if (!form.file) {
    ElMessage.warning('请选择要上传的文件。')
    return
  }
  emit('save', { ...metadata, file: form.file })
}

watch(() => props.open, (open) => {
  if (!open) return
  if (props.archive) {
    Object.assign(form, {
      file_type: props.archive.file_type,
      title: props.archive.title,
      description: props.archive.description || '',
      file: undefined,
    })
  } else reset()
})
</script>

<style scoped>
.current-file {
  display: grid;
  min-width: 0;
  gap: 3px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  background: var(--color-panel);
}

.current-file span,
.current-file small { color: var(--color-muted); font-size: 12px; }
.current-file strong { overflow: hidden; color: var(--color-text); font-size: 13px; text-overflow: ellipsis; white-space: nowrap; }
</style>
