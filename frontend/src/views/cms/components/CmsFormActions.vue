<template>
  <div class="form-actions">
    <div v-if="progress > 0" class="upload-progress">
      <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined" />
      <span>{{ progress < 100 ? '正在上传附件，请不要关闭页面。' : '上传完成，正在保存内容。' }}</span>
    </div>
    <el-button type="primary" :loading="saving" @click="$emit('save')">保存</el-button>
    <el-button v-if="deletable" plain @click="$emit('delete')">删除</el-button>
  </div>
</template>

<script setup lang="ts">
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

.upload-progress {
  display: grid;
  flex: 1 1 280px;
  gap: 5px;
  margin-right: auto;
  text-align: left;
}

.upload-progress span {
  color: var(--color-muted);
  font-size: 12px;
}
</style>
