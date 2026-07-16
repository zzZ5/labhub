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
        <UploadFileField v-model="form.file" :disabled="saving" accept=".pdf,.doc,.docx,.ppt,.pptx" :max-size-mb="200" hint="支持 PDF、Word 和 PowerPoint，单个文件不超过 200 MB" />
      </el-form-item>
    </el-form>
    <template #footer>
      <UploadProgress :active="saving" :progress="progress" processing-text="上传完成，正在保存学生资料。" />
      <el-button @click="$emit('update:open', false)">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">保存资料</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import UploadFileField from '../../../components/UploadFileField.vue'
import UploadProgress from '../../../components/UploadProgress.vue'
import type { StudentArchiveUploadPayload } from '../../../api/students'

const props = defineProps<{ open: boolean; saving: boolean; progress: number }>()
const emit = defineEmits<{
  'update:open': [value: boolean]
  save: [payload: StudentArchiveUploadPayload]
}>()

const form = reactive({ file_type: 'proposal_report', title: '', description: '', file: undefined as File | undefined })

function reset() {
  Object.assign(form, { file_type: 'proposal_report', title: '', description: '', file: undefined })
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
