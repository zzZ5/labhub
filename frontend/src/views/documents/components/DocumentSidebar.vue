<template>
  <aside class="card category-tree">
    <template v-if="previewDocument">
      <div class="side-heading">
        <h2>资料列表</h2>
        <button class="back-category" type="button" @click="$emit('closePreview')">返回分类</button>
      </div>
      <button
        v-for="document in documents"
        :key="document.id"
        :class="{ active: previewDocument.id === document.id, disabled: !document.can_preview }"
        type="button"
        @click="$emit('preview', document)"
      >
        <strong>{{ document.title }}</strong>
        <span>{{ currentFilename(document) }}</span>
      </button>
      <AppPagination compact :page="page" :total-pages="totalPages" @change="$emit('update:page', $event)" />
    </template>
    <template v-else>
      <div class="side-heading static"><h2>资料分类</h2></div>
      <button :class="{ active: !activeCategory }" type="button" @click="$emit('selectCategory', '')">全部资料</button>
      <button
        v-for="category in categories"
        :key="category.slug"
        :class="{ active: activeCategory === category.slug }"
        type="button"
        @click="$emit('selectCategory', category.slug)"
      >
        {{ categoryName(category) }}
      </button>
    </template>
  </aside>
</template>

<script setup lang="ts">
import AppPagination from '../../../components/AppPagination.vue'
import type { DocumentCategory, LabDocument } from '../../../api/documents'
import { categoryName, currentFilename } from '../documentPresentation'

defineProps<{
  categories: DocumentCategory[]
  documents: LabDocument[]
  previewDocument: LabDocument | null
  activeCategory: string
  total: number
  page: number
  totalPages: number
}>()

defineEmits<{
  selectCategory: [slug: string]
  preview: [document: LabDocument]
  closePreview: []
  'update:page': [page: number]
}>()
</script>

<style scoped>
.category-tree {
  position: sticky;
  top: 24px;
  max-height: calc(100vh - 48px);
  overflow: auto;
  padding: 22px;
  box-shadow: 0 1px 2px rgba(31, 61, 43, 0.035), 0 12px 30px rgba(31, 61, 43, 0.035);
}

.category-tree:hover {
  border-color: var(--color-border);
  transform: none;
}

.side-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 16px;
}

.side-heading h2 {
  margin: 3px 0 0;
  color: var(--color-deep-green);
  font-size: 18px;
  font-weight: 650;
  line-height: 1.25;
  white-space: nowrap;
}

.category-tree > button {
  display: block;
  width: 100%;
  min-height: 42px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  margin-bottom: 7px;
  padding: 10px 12px;
  background: transparent;
  color: var(--color-muted);
  text-align: left;
  cursor: pointer;
}

.category-tree > button.active,
.category-tree > button:hover {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
  color: var(--color-cau-green);
}

.category-tree > button.active {
  font-weight: 650;
}

.category-tree > button.disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

.category-tree > button strong,
.category-tree > button span {
  display: block;
}

.category-tree > button strong {
  color: inherit;
  font-size: 14px;
  line-height: 1.35;
}

.category-tree > button span {
  overflow: hidden;
  margin-top: 3px;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.side-heading .back-category {
  flex: 0 0 auto;
  width: auto;
  min-height: 30px;
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: var(--radius-sm);
  padding: 0 9px;
  background: #fff;
  color: var(--color-cau-green);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

@media (max-width: 1080px) {
  .category-tree {
    position: static;
    max-height: none;
  }
}
</style>
