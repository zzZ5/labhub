<template>
  <nav v-if="totalPages > 1" :class="['app-pagination', { compact }]" aria-label="分页导航">
    <button type="button" class="page-nav" :disabled="page <= 1" aria-label="上一页" @click="change(page - 1)">
      <el-icon><ArrowLeft /></el-icon><span>上一页</span>
    </button>
    <PageJump compact inline :page="page" :total-pages="totalPages" @change="change" />
    <button type="button" class="page-nav" :disabled="page >= totalPages" aria-label="下一页" @click="change(page + 1)">
      <span>下一页</span><el-icon><ArrowRight /></el-icon>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import PageJump from './PageJump.vue'

const props = withDefaults(defineProps<{ page: number; totalPages: number; compact?: boolean }>(), { compact: false })
const emit = defineEmits<{ change: [page: number] }>()

function change(value: number) {
  emit('change', Math.min(props.totalPages, Math.max(1, value)))
}
</script>

<style scoped>
.app-pagination {
  display: grid;
  grid-template-columns: 84px minmax(58px, auto) 84px;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  border-top: 1px solid var(--color-line);
  padding-top: 12px;
}

.page-nav {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  width: 84px;
  min-height: 34px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-deep-green);
  cursor: pointer;
  font: inherit;
  font-size: 13px;
  font-weight: 650;
}

.page-nav:hover:not(:disabled) {
  border-color: rgba(0, 135, 60, 0.35);
  background: var(--color-eco-green);
  color: var(--color-cau-green);
}

.page-nav:disabled {
  cursor: not-allowed;
  opacity: 0.42;
}

.compact {
  grid-template-columns: 70px minmax(50px, auto) 70px;
  gap: 6px;
}

.compact .page-nav {
  width: 70px;
  min-height: 32px;
  padding: 0 6px;
  font-size: 12px;
}

@media (max-width: 420px) {
  .app-pagination,
  .compact {
    grid-template-columns: minmax(64px, 1fr) minmax(52px, auto) minmax(64px, 1fr);
    gap: 5px;
  }

  .page-nav,
  .compact .page-nav {
    width: 100%;
    min-height: var(--control-touch);
  }

  .app-pagination :deep(.page-jump input) {
    height: var(--control-touch);
  }
}
</style>
