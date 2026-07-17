<template>
  <div class="instrument-tools">
    <FilterToolbar class="instrument-toolbar" has-filters>
      <template #primary>
        <input
          :value="keyword"
          type="search"
          placeholder="搜索仪器名称、型号、位置或说明"
          @input="$emit('update:keyword', ($event.target as HTMLInputElement).value)"
        />
      </template>
      <template #filters>
        <select :value="status" @change="$emit('update:status', ($event.target as HTMLSelectElement).value)">
          <option value="">全部状态</option>
          <option value="normal">正常</option>
          <option value="maintenance">维护中</option>
          <option value="disabled">停用</option>
        </select>
        <select :value="sort" aria-label="仪器排序" @change="$emit('update:sort', ($event.target as HTMLSelectElement).value)">
          <option value="created_desc">最新添加</option>
          <option value="created_asc">最早添加</option>
          <option value="name_asc">名称顺序</option>
          <option value="status_asc">状态顺序</option>
        </select>
      </template>
      <template v-if="canManage" #actions>
        <el-button type="primary" @click="$emit('create')">新建设备</el-button>
        <el-button plain @click="$emit('import')">批量导入</el-button>
      </template>
    </FilterToolbar>
  </div>
</template>

<script setup lang="ts">
import FilterToolbar from '../../../components/FilterToolbar.vue'

defineProps<{
  keyword: string
  status: string
  sort: string
  canManage: boolean
}>()

const emit = defineEmits<{
  'update:keyword': [value: string]
  'update:status': [value: string]
  'update:sort': [value: string]
  create: []
  import: []
}>()
</script>

<style scoped>
.instrument-tools {
  display: grid;
  gap: 8px;
}

.instrument-toolbar {
  box-shadow: none;
}

.instrument-toolbar input,
.instrument-toolbar select {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 38px;
  padding: 0 12px;
  background: #fff;
  color: var(--color-text);
  font: inherit;
}

.instrument-toolbar input:focus,
.instrument-toolbar select:focus {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

</style>
