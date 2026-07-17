<template>
  <article class="card list-panel">
    <div class="list-toolbar">
      <div><strong>{{ title }}</strong><span>{{ countText }}</span></div>
      <el-button type="primary" @click="$emit('create')">{{ actionLabel }}</el-button>
    </div>
    <input v-model="keyword" class="list-search" :placeholder="`搜索${title}`" @input="page = 1" />
    <div class="list-results">
      <div v-if="filteredItems.length" class="content-list-scroll">
        <button
          v-for="item in pagedItems"
          :key="item.key"
          :class="['content-row', { active: item.key === activeKey }]"
          type="button"
          @click="$emit('edit', item.source)"
        >
          <strong>{{ item.title }}</strong>
          <span v-if="item.meta">{{ item.meta }}</span>
        </button>
      </div>
      <div v-else class="empty-list">{{ keyword ? '没有找到匹配内容。' : '暂无内容，点击右上角新增。' }}</div>
    </div>
    <AppPagination compact :page="page" :total-pages="totalPages" @change="setPage" />
    <details v-if="$slots.tools" class="list-extra">
      <summary>数据导入</summary>
      <div class="list-extra__content"><slot name="tools" /></div>
    </details>
  </article>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import AppPagination from '../../../components/AppPagination.vue'
import { useListPagination } from '../../../composables/useListPagination'
import { useDebouncedValue } from '../../../composables/useDebouncedValue'

interface CmsListRow {
  key: string | number
  title: string
  meta: string
  source: any
}

const props = defineProps<{
  title: string
  actionLabel: string
  items: CmsListRow[]
  activeKey?: string | number
}>()
defineEmits<{ create: []; edit: [source: any] }>()

const keyword = ref('')
const debouncedKeyword = useDebouncedValue(keyword)
const filteredItems = computed(() => {
  const query = debouncedKeyword.value.trim().toLowerCase()
  return query ? props.items.filter((item) => `${item.title} ${item.meta}`.toLowerCase().includes(query)) : props.items
})
const filteredTotal = computed(() => filteredItems.value.length)
const countText = computed(() => keyword.value.trim()
  ? `找到 ${filteredItems.value.length} 条，共 ${props.items.length} 条`
  : `共 ${props.items.length} 条`)
const { page, totalPages, setPage, resetPage, paginate } = useListPagination(filteredTotal)
const pagedItems = computed(() => paginate(filteredItems.value))
watch(debouncedKeyword, resetPage)
</script>

<style scoped>
.list-panel {
  display: grid;
  grid-template-rows: auto;
  align-content: start;
  align-self: start;
  height: auto;
  min-height: 0;
  overflow: hidden;
  padding: 18px;
}

.list-panel:hover {
  transform: none;
}

.list-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.list-toolbar > div {
  display: grid;
  gap: 2px;
}

.list-toolbar strong {
  color: var(--color-deep-green);
  font-size: 17px;
}

.list-toolbar span {
  color: var(--color-muted);
  font-size: 12px;
}

.list-search {
  width: 100%;
  min-height: 38px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 12px;
  padding: 0 11px;
  background: #fff;
  color: var(--color-text);
  font: inherit;
}

.list-search:focus {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

.list-results {
  min-width: 0;
  min-height: 0;
}

.content-list-scroll {
  display: grid;
  grid-auto-rows: max-content;
  align-content: start;
  gap: 8px;
  min-width: 0;
}

.list-extra {
  min-width: 0;
  margin-top: 10px;
  border-top: 1px solid var(--color-line);
  padding-top: 8px;
}

.list-extra summary {
  width: fit-content;
  color: var(--color-cau-green);
  cursor: pointer;
  font-size: 12px;
  font-weight: 650;
}

.list-extra__content { margin-top: 8px; }
.list-extra :deep(.cms-import-block) { display: grid; gap: 8px; }
.list-extra :deep(.import-strip) { display: grid; grid-template-columns: 1fr auto auto; gap: 8px; padding: 10px; }
.list-extra :deep(.import-strip span) { grid-column: 1 / -1; white-space: normal; line-height: 1.5; }

.content-row {
  display: grid;
  gap: 4px;
  width: 100%;
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 10px 11px;
  background: #fff;
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
}

.content-row:hover,
.content-row.active {
  border-color: rgba(0, 135, 60, 0.2);
  background: var(--color-eco-green);
}

.content-row strong,
.content-row span {
  overflow: hidden;
  text-overflow: ellipsis;
}

.content-row strong {
  display: -webkit-box;
  color: var(--color-deep-green);
  font-size: 14px;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.content-row span {
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.45;
  white-space: nowrap;
}

.empty-list {
  display: grid;
  height: 100%;
  min-height: 76px;
  place-items: center;
  padding: 16px 8px;
  color: var(--color-muted);
  text-align: center;
}

@media (max-width: 720px) {
  .list-panel { padding: 12px; }
}

</style>
