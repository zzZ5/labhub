<template>
  <article class="card list-panel">
    <div class="list-toolbar">
      <div><strong>{{ title }}</strong><span>{{ filteredItems.length }} / {{ items.length }}</span></div>
      <el-button type="primary" @click="$emit('create')">{{ actionLabel }}</el-button>
    </div>
    <input v-model="keyword" class="list-search" :placeholder="`搜索${title}`" @input="page = 1" />
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
    <div v-if="filteredItems.length > 12" class="list-pager">
      <div class="pager-controls">
        <button type="button" :disabled="page === 1" @click="setPage(page - 1)">上一页</button>
        <PageJump compact inline :page="page" :total-pages="totalPages" @change="setPage" />
        <button type="button" :disabled="page === totalPages" @click="setPage(page + 1)">下一页</button>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import PageJump from '../../../components/PageJump.vue'

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
const page = ref(1)
const pageSize = 12
const filteredItems = computed(() => {
  const query = keyword.value.trim().toLowerCase()
  return query ? props.items.filter((item) => `${item.title} ${item.meta}`.toLowerCase().includes(query)) : props.items
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredItems.value.length / pageSize)))
const pagedItems = computed(() => filteredItems.value.slice((page.value - 1) * pageSize, page.value * pageSize))

function setPage(nextPage: number) {
  page.value = Math.min(totalPages.value, Math.max(1, nextPage))
}

watch(totalPages, () => setPage(page.value))
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
  gap: 8px;
}

.content-row {
  display: grid;
  gap: 4px;
  width: 100%;
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

.list-pager {
  border-top: 1px solid var(--color-line);
  margin-top: 12px;
  padding-top: 12px;
}

.pager-controls {
  display: grid;
  grid-template-columns: 72px minmax(44px, 1fr) 72px;
  align-items: center;
  gap: 8px;
}

.pager-controls :deep(.page-jump) {
  justify-self: center;
}

.list-pager button {
  width: 72px;
  min-height: 30px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-text);
  cursor: pointer;
  font-size: 12px;
}

.list-pager button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}
</style>
