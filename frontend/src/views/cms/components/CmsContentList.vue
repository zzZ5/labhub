<template>
  <article class="card list-panel">
    <div class="list-toolbar">
      <div><strong>{{ title }}</strong><span>{{ filteredItems.length }} / {{ items.length }}</span></div>
      <el-button type="primary" @click="$emit('create')">{{ actionLabel }}</el-button>
    </div>
    <input v-model="keyword" class="list-search" :placeholder="`搜索${title}`" @input="page = 1" />
    <div v-if="$slots.tools" class="list-extra"><slot name="tools" /></div>
    <div v-if="filteredItems.length" class="content-list-scroll">
      <button
        v-for="item in pagedItems"
        :key="item.key"
        :class="['content-row', { active: item.key === activeKey }]"
        type="button"
        @click="$emit('edit', item.source)"
      >
        <strong>{{ item.title }}</strong>
        <span>{{ item.meta }}</span>
      </button>
    </div>
    <div v-else class="empty-list">{{ keyword ? '没有找到匹配内容。' : '暂无内容，点击右上角新增。' }}</div>
    <AppPagination compact :page="page" :total-pages="totalPages" @change="setPage" />
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
const { page, totalPages, setPage, resetPage, paginate } = useListPagination(filteredTotal)
const pagedItems = computed(() => paginate(filteredItems.value))
watch(debouncedKeyword, resetPage)
</script>

<style scoped>
.list-panel {
  display: grid;
  align-content: start;
  min-height: 0;
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

.content-list-scroll {
  display: grid;
  grid-auto-rows: max-content;
  align-content: start;
  gap: 8px;
  min-width: 0;
  max-height: 440px;
  overflow-x: hidden;
  overflow-y: auto;
  padding-right: 3px;
}

.list-extra { min-width: 0; margin-bottom: 12px; }
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
  padding: 28px 8px;
  color: var(--color-muted);
  text-align: center;
}

@media (max-width: 720px) {
  .content-list-scroll {
    max-height: 320px;
  }
}

</style>
