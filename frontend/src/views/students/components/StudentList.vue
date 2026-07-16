<template>
  <aside class="card student-list">
    <div class="side-heading">
      <h2>学生列表</h2>
      <span>{{ total }} / {{ allCount }} 人</span>
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
        <small>{{ student.user_email || student.user_username || '未绑定账号' }}</small>
      </span>
    </button>
    <div v-if="!total" class="empty-note">{{ allCount ? '没有找到匹配学生。' : '暂无学生档案。' }}</div>
    <div v-if="total > 12" class="student-pager">
      <div class="pager-controls">
        <button type="button" :disabled="page === 1" @click="$emit('update:page', page - 1)">上一页</button>
        <PageJump compact inline :page="page" :total-pages="totalPages" @change="$emit('update:page', $event)" />
        <button type="button" :disabled="page === totalPages" @click="$emit('update:page', page + 1)">下一页</button>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import PageJump from '../../../components/PageJump.vue'
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
}>()

defineEmits<{
  select: [id: number]
  'update:keyword': [value: string]
  'update:degree': [value: string]
  'update:page': [page: number]
}>()
</script>

<style scoped>
.student-list {
  position: sticky;
  top: 96px;
  max-height: calc(100vh - 120px);
  overflow: auto;
  padding: 16px;
}

.student-list:hover {
  transform: none;
}

.side-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
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
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  padding: 9px 11px;
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

.student-pager {
  border-top: 1px solid var(--color-line);
  margin-top: 10px;
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

.student-pager button {
  width: 72px;
  min-height: 30px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-text);
  cursor: pointer;
  font-size: 12px;
}

.student-pager button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
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
