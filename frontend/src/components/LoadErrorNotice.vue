<template>
  <div class="load-error-notice" role="alert">
    <div>
      <strong>{{ title }}</strong>
      <span>{{ description }}</span>
    </div>
    <el-button plain :loading="retrying" @click="$emit('retry')">重新加载</el-button>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ title?: string; description: string; retrying?: boolean }>(), {
  title: '内容加载失败',
  retrying: false,
})
defineEmits<{ retry: [] }>()
</script>

<style scoped>
.load-error-notice {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid #ead7b7;
  border-radius: var(--radius-sm);
  padding: 11px 14px;
  background: #fffaf0;
}

.load-error-notice > div {
  display: grid;
  gap: 2px;
}

.load-error-notice strong {
  color: #75502b;
  font-size: 14px;
}

.load-error-notice span {
  color: var(--color-muted);
  font-size: 13px;
}

@media (max-width: 640px) {
  .load-error-notice { align-items: stretch; flex-direction: column; }
  .load-error-notice :deep(.el-button) { width: 100%; }
}
</style>
