<template>
  <aside class="card student-list">
    <div class="side-heading">
      <div>
        <h2>学生列表</h2>
        <span>{{ total === allCount ? `共 ${allCount} 人` : `${total} / ${allCount} 人` }}</span>
      </div>
      <el-button v-if="canCreate" type="primary" @click="$emit('create')">新建档案</el-button>
    </div>
    <div class="student-list-tools">
      <el-input :model-value="keyword" size="small" clearable placeholder="搜索姓名、年级、方向" @update:model-value="$emit('update:keyword', String($event))" />
      <el-select :model-value="degree" size="small" placeholder="学位" clearable @update:model-value="$emit('update:degree', String($event || ''))">
        <el-option label="本科" value="undergraduate" />
        <el-option label="硕士" value="master" />
        <el-option label="博士" value="phd" />
      </el-select>
    </div>
    <button
      v-for="student in students"
      :key="student.id"
      :class="{ active: selectedId === student.id }"
      type="button"
      @click="$emit('select', student.id)"
    >
      <span class="student-list-avatar">
        <img v-if="student.avatar" :src="student.avatar" :alt="student.name" />
        <template v-else>{{ student.name.slice(0, 1) }}</template>
      </span>
      <span class="student-list-copy">
        <strong>{{ student.name }}</strong>
        <span>{{ student.degree_label }} · {{ student.grade || '未填写年级' }}</span>
        <small>{{ student.research_direction || student.research_topic || '研究方向待补充' }}</small>
      </span>
    </button>
    <div v-if="!total" class="empty-note">{{ allCount ? '没有找到匹配学生。' : '暂无学生档案。' }}</div>
    <AppPagination compact :page="page" :total-pages="totalPages" @change="$emit('update:page', $event)" />
  </aside>
</template>

<script setup lang="ts">
import AppPagination from '../../../components/AppPagination.vue'
import type { StudentProfile } from '../../../api/students'

defineProps<{
  students: StudentProfile[]
  allCount: number
  total: number
  selectedId: number | null
  keyword: string
  degree: string
  page: number
  totalPages: number
  canCreate: boolean
}>()

defineEmits<{
  select: [id: number]
  'update:keyword': [value: string]
  'update:degree': [value: string]
  'update:page': [page: number]
  create: []
}>()
</script>

<style scoped>
.student-list {
  position: sticky;
  top: 96px;
  max-height: calc(100vh - 120px);
  overflow: auto;
  padding: 14px;
  box-shadow: none;
}

.student-list:hover {
  transform: none;
}

.side-heading {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
}

.side-heading::after {
  position: absolute;
  bottom: -1px;
  left: 0;
  width: 44px;
  height: 2px;
  background: linear-gradient(90deg, var(--color-cau-green) 0 72%, var(--color-cau-gold) 72% 100%);
  content: "";
}

.side-heading > div {
  display: grid;
  gap: 3px;
}

.side-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.side-heading span,
.student-list small {
  color: var(--color-muted);
  font-size: 12px;
  line-height: 1.35;
}

.student-list-tools {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 92px;
  gap: 10px;
  margin-bottom: 14px;
}

.student-list-tools :deep(.el-input__wrapper),
.student-list-tools :deep(.el-select__wrapper) {
  min-height: 38px;
  border-radius: var(--radius-sm);
  box-shadow: 0 0 0 1px var(--color-border) inset;
}

.student-list > button {
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr);
  align-items: center;
  gap: 11px;
  width: 100%;
  border: 1px solid transparent;
  border-radius: 5px;
  margin-bottom: 6px;
  padding: 8px 10px;
  background: #fff;
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
}

.student-list > button.active,
.student-list > button:hover {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
}

.student-list > button.active {
  box-shadow: inset 3px 0 0 var(--color-cau-green);
}

.student-list-avatar {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  overflow: hidden;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: 50%;
  background: rgba(234, 245, 238, 0.8);
  color: var(--color-deep-green);
  font-size: 13px;
  font-weight: 650;
}

.student-list-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.student-list-copy {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.student-list-copy strong,
.student-list-copy span,
.student-list-copy small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.student-list-copy strong {
  color: var(--color-deep-green);
  font-size: 14px;
}

.student-list-copy span {
  color: var(--color-muted);
  font-size: 12px;
}

.empty-note {
  padding: 16px 4px;
  color: var(--color-muted);
  text-align: center;
}

@media (max-width: 1180px) {
  .student-list {
    position: static;
    max-height: none;
  }
}
</style>
