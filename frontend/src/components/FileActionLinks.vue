<template>
  <div class="file-action-links">
    <template v-if="url">
      <a class="file-view" :href="url" target="_blank" rel="noreferrer">{{ viewLabel }}</a>
      <a class="file-download" :href="url" download>{{ downloadLabel }}</a>
    </template>
    <p v-else>{{ emptyLabel }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  url?: string | null
  viewLabel?: string
  downloadLabel?: string
  emptyLabel?: string
}>(), {
  url: '',
  viewLabel: '在线查看',
  downloadLabel: '下载文件',
  emptyLabel: '暂无公开附件',
})
</script>

<style scoped>
.file-action-links {
  display: grid;
  gap: 9px;
}

.file-action-links a {
  display: flex;
  min-height: 40px;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  padding: 8px 13px;
  font-size: 14px;
  font-weight: 700;
}

.file-view {
  background: var(--color-cau-green);
  color: #fff;
}

.file-download {
  border: 1px solid rgba(0, 135, 60, 0.28);
  background: #fff;
  color: var(--color-cau-green);
}

.file-action-links p {
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
}
</style>
