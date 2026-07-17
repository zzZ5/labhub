<template>
  <button class="mobile-editor-back" type="button" aria-label="返回内容列表" @click="$emit('back')">
    <el-icon><ArrowLeft /></el-icon>
    <span>返回内容列表</span>
  </button>
</template>

<script setup lang="ts">
import { ArrowLeft } from '@element-plus/icons-vue'

defineEmits<{ back: [] }>()
</script>

<style scoped>
.mobile-editor-back {
  display: none;
}

@media (max-width: 720px) {
  .mobile-editor-back {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-height: 44px;
    border: 0;
    margin: -4px 0 8px;
    padding: 0 4px;
    background: transparent;
    color: var(--color-cau-green);
    font: inherit;
    font-size: 14px;
    font-weight: 650;
    cursor: pointer;
  }
}
</style>
