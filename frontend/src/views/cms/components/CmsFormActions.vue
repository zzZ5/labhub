<template>
  <div class="form-actions">
    <UploadProgress :active="saving && progress > 0" :progress="progress" uploading-text="正在上传附件，请不要关闭页面。" processing-text="上传完成，正在保存内容。" />
    <el-button type="primary" :loading="saving" @click="$emit('save')">保存</el-button>
    <el-button v-if="deletable" plain @click="$emit('delete')">删除</el-button>
  </div>
</template>

<script setup lang="ts">
import UploadProgress from '../../../components/UploadProgress.vue'
withDefaults(defineProps<{ saving?: boolean; deletable?: boolean; progress?: number }>(), {
  saving: false,
  deletable: false,
  progress: 0,
})
defineEmits<{ save: []; delete: [] }>()
</script>

<style scoped>
.form-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  margin-top: 18px;
  padding-top: 16px;
}

.form-actions :deep(.upload-progress-panel) { flex: 1 1 280px; margin: 0 auto 0 0; }
</style>
