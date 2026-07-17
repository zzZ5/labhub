<template>
  <div class="list-skeleton" role="status" aria-label="正在加载列表">
    <div v-for="index in rows" :key="index" class="list-skeleton__row">
      <span v-if="thumbnail" class="list-skeleton__thumbnail"></span>
      <span class="list-skeleton__copy">
        <i :style="{ width: `${titleWidth(index)}%` }"></i>
        <i></i>
        <i class="short"></i>
      </span>
    </div>
    <span class="sr-only">正在加载内容</span>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ rows?: number; thumbnail?: boolean }>(), {
  rows: 5,
  thumbnail: false,
})

function titleWidth(index: number) {
  return 48 + ((index * 13) % 34)
}
</script>

<style scoped>
.list-skeleton {
  display: grid;
  gap: 10px;
}

.list-skeleton__row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 14px;
  min-height: 82px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 13px 16px;
  background: var(--color-white);
}

.list-skeleton__thumbnail {
  width: 72px;
  aspect-ratio: 4 / 3;
  border-radius: var(--radius-sm);
  background: var(--color-panel-strong);
}

.list-skeleton__copy { display: grid; gap: 9px; min-width: 0; }
.list-skeleton__copy i {
  display: block;
  width: 88%;
  height: 10px;
  border-radius: 3px;
  background: var(--color-panel-strong);
  animation: skeleton-pulse 1.25s ease-in-out infinite alternate;
}
.list-skeleton__copy i:first-child { height: 13px; }
.list-skeleton__copy i.short { width: 42%; }

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

@keyframes skeleton-pulse {
  from { opacity: 0.58; }
  to { opacity: 1; }
}

@media (max-width: 640px) {
  .list-skeleton__row { min-height: 70px; padding: 11px 12px; }
  .list-skeleton__thumbnail { width: 54px; }
}

@media (prefers-reduced-motion: reduce) {
  .list-skeleton__copy i { animation: none; }
}
</style>
