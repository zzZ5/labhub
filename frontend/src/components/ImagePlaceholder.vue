<template>
  <div class="image-placeholder" role="img" :aria-label="label">
    <span v-if="initial" class="image-placeholder__initial">{{ initial.slice(0, 1) }}</span>
    <template v-else>
      <el-icon><Picture /></el-icon>
      <span class="image-placeholder__text">{{ text }}</span>
    </template>
  </div>
</template>

<script setup lang="ts">
import { Picture } from '@element-plus/icons-vue'

withDefaults(defineProps<{ label?: string; initial?: string; text?: string }>(), {
  label: '暂无图片',
  initial: '',
  text: '暂无图片',
})
</script>

<style scoped>
.image-placeholder {
  display: flex;
  width: 100%;
  align-self: stretch;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 7px;
  background: var(--color-panel-strong);
  color: color-mix(in srgb, var(--color-blue-gray) 58%, transparent);
}

.image-placeholder :deep(svg) {
  width: 24px;
  height: 24px;
  stroke-width: 1.5;
}

.image-placeholder__initial {
  color: var(--color-deep-green);
  font-size: clamp(24px, 4vw, 38px);
  font-weight: 600;
}

.image-placeholder__text {
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.4;
}
</style>
