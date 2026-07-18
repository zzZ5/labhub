<template>
  <section class="filter-toolbar" aria-label="列表筛选与操作">
    <div class="filter-toolbar__primary"><slot name="primary" /></div>
    <button
      v-if="hasFilters"
      class="filter-toolbar__toggle"
      type="button"
      :aria-expanded="filtersOpen"
      @click="filtersOpen = !filtersOpen"
    >
      <el-icon><Filter /></el-icon>
      {{ filtersOpen ? '收起筛选' : '筛选' }}
    </button>
    <div v-if="hasFilters" :class="['filter-toolbar__filters', { open: filtersOpen }]">
      <slot name="filters" />
    </div>
    <div v-if="$slots.actions" class="filter-toolbar__actions"><slot name="actions" /></div>
    <div v-if="$slots.note" class="filter-toolbar__note"><slot name="note" /></div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Filter } from '@element-plus/icons-vue'

withDefaults(defineProps<{ hasFilters?: boolean }>(), { hasFilters: false })
const filtersOpen = ref(false)
</script>

<style scoped>
.filter-toolbar {
  position: relative;
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto auto;
  align-items: center;
  gap: var(--space-2);
  min-width: 0;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.92);
  box-shadow: inset 0 2px 0 rgba(0, 135, 60, 0.08);
}

.filter-toolbar::before {
  position: absolute;
  top: -1px;
  left: 18px;
  width: 34px;
  height: 2px;
  background: var(--color-cau-gold);
  content: "";
}

.filter-toolbar__primary,
.filter-toolbar__filters,
.filter-toolbar__actions {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: var(--space-2);
}

.filter-toolbar__filters,
.filter-toolbar__actions {
  justify-content: flex-end;
}

.filter-toolbar__primary :deep(.el-input),
.filter-toolbar__primary :deep(input) {
  width: 100%;
}

.filter-toolbar__filters :deep(.el-select) {
  width: 148px;
}

.filter-toolbar__actions :deep(.el-button) {
  margin: 0;
}

.filter-toolbar__toggle {
  display: none;
}

.filter-toolbar__note {
  grid-column: 1 / -1;
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.55;
}

@media (max-width: 960px) {
  .filter-toolbar {
    grid-template-columns: minmax(180px, 1fr) auto;
  }

  .filter-toolbar__filters,
  .filter-toolbar__actions {
    flex-wrap: wrap;
  }
}

@media (max-width: 720px) {
  .filter-toolbar {
    grid-template-columns: minmax(0, 1fr) auto;
    border-radius: var(--radius-sm);
  }

  .filter-toolbar__toggle {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    min-height: var(--control-touch);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: 0 12px;
    background: #fff;
    color: var(--color-deep-green);
    font: inherit;
    font-weight: 650;
  }

  .filter-toolbar__filters {
    display: none;
    grid-column: 1 / -1;
    grid-template-columns: 1fr;
  }

  .filter-toolbar__filters.open {
    display: grid;
  }

  .filter-toolbar__filters :deep(.el-select),
  .filter-toolbar__filters :deep(.el-input) {
    width: 100%;
  }

  .filter-toolbar__actions {
    grid-column: 1 / -1;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
  }

  .filter-toolbar__actions :deep(.el-button),
  .filter-toolbar__actions :deep(a),
  .filter-toolbar__actions :deep(button) {
    width: 100%;
    min-height: var(--control-touch);
  }
}
</style>
