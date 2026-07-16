<template>
  <div class="instrument-list">
    <div class="instrument-grid">
      <article
        v-for="instrument in instruments"
        :key="instrument.id"
        class="card instrument-card"
        @click="$emit('detail', instrument.id)"
      >
        <img v-if="instrument.image" :src="instrument.image" :alt="instrument.name" />
        <div v-else class="instrument-image-placeholder">暂无图片</div>
        <div class="instrument-body">
          <div class="instrument-title">
            <h2>{{ instrument.name }}</h2>
            <span :class="['status-tag', statusClass(instrument.status)]">{{ statusText(instrument.status) }}</span>
          </div>
          <p>{{ instrument.model || '型号待补充' }}</p>
          <dl>
            <div>
              <dt>位置</dt>
              <dd>{{ instrument.location_detail || '未填写位置' }}</dd>
            </div>
            <div v-if="instrument.manager_name">
              <dt>负责人</dt>
              <dd>{{ instrument.manager_name }}</dd>
            </div>
            <div>
              <dt>说明</dt>
              <dd class="instrument-note-preview">{{ shortNote(instrument.notes) }}</dd>
            </div>
          </dl>
          <div class="instrument-actions">
            <span class="detail-link">查看设备详情</span>
            <button v-if="canManage && instrument.id > 0" type="button" class="edit-action" @click.stop="$emit('edit', instrument)">编辑</button>
          </div>
        </div>
      </article>
    </div>

    <div v-if="!instruments.length" class="card empty-panel">没有找到匹配的仪器设备。</div>

    <div v-if="total > 12" class="list-pager">
      <span class="pager-summary">共 {{ total }} 台设备</span>
      <div class="pager-controls">
        <button class="pager-nav" type="button" :disabled="page === 1" @click="$emit('update:page', page - 1)">上一页</button>
        <PageJump compact inline :page="page" :total-pages="totalPages" @change="$emit('update:page', $event)" />
        <button class="pager-nav" type="button" :disabled="page === totalPages" @click="$emit('update:page', page + 1)">下一页</button>
      </div>
      <el-select :model-value="pageSize" size="small" class="page-size-select" placeholder="分页" @update:model-value="$emit('update:pageSize', Number($event))">
        <el-option label="12 台/页" :value="12" />
        <el-option label="24 台/页" :value="24" />
        <el-option label="48 台/页" :value="48" />
      </el-select>
    </div>
  </div>
</template>

<script setup lang="ts">
import PageJump from '../../../components/PageJump.vue'
import type { Instrument } from '../../../api/instruments'

defineProps<{
  instruments: Instrument[]
  total: number
  page: number
  totalPages: number
  pageSize: number
  canManage: boolean
}>()

defineEmits<{
  detail: [id: number]
  edit: [instrument: Instrument]
  'update:page': [page: number]
  'update:pageSize': [size: number]
}>()

function shortNote(note: string) {
  const text = (note || '').replace(/\s+/g, ' ').trim()
  if (!text) return '暂无详细说明，可在设备详情中补充。'
  return text.length > 58 ? `${text.slice(0, 58)}...` : text
}

function statusClass(status: string) {
  if (status === 'normal') return 'normal'
  if (status === 'maintenance') return 'maintenance'
  return 'archived'
}

function statusText(status: string) {
  return ({ normal: '正常', maintenance: '维护中', disabled: '停用' } as Record<string, string>)[status] || '待确认'
}
</script>

<style scoped>
.instrument-list {
  display: grid;
  gap: 14px;
}

.instrument-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.instrument-card {
  overflow: hidden;
  border-radius: var(--radius-lg);
  cursor: pointer;
}

.instrument-card:hover {
  border-color: rgba(0, 135, 60, 0.24);
  transform: translateY(-1px);
}

.instrument-card img,
.instrument-image-placeholder {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  background: #f7f9f7;
}

.instrument-card img {
  object-fit: contain;
  filter: saturate(0.96);
}

.instrument-image-placeholder {
  display: grid;
  place-items: center;
  background: var(--color-eco-green);
  color: var(--color-muted);
  font-size: 14px;
}

.instrument-body {
  padding: 22px;
}

.instrument-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 8px;
}

.instrument-title h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.instrument-card p {
  margin: 0;
  color: var(--color-muted);
}

.instrument-card dl {
  display: grid;
  gap: 8px;
  margin: 18px 0 0;
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

.instrument-card dl div {
  display: grid;
  grid-template-columns: 56px 1fr;
  gap: 12px;
  font-size: 14px;
}

.instrument-card dt {
  color: var(--color-text);
}

.instrument-card dd {
  margin: 0;
  color: var(--color-muted);
}

.instrument-note-preview {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.instrument-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-top: 18px;
  border-top: 1px solid var(--color-line);
  padding-top: 14px;
}

.detail-link {
  margin-right: auto;
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}

.edit-action,
.list-pager button {
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: var(--radius-sm);
  background: #fff;
  color: var(--color-cau-green);
  cursor: pointer;
  font-weight: 700;
}

.edit-action {
  min-height: 30px;
  padding: 0 10px;
  font-size: 13px;
}

.edit-action:hover {
  background: var(--color-eco-green);
}

.empty-panel {
  padding: 24px;
  color: var(--color-muted);
  text-align: center;
}

.list-pager {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  background: #fff;
  color: var(--color-muted);
  font-size: 14px;
}

.pager-summary {
  color: var(--color-text);
  font-weight: 700;
  white-space: nowrap;
}

.pager-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.page-size-select {
  width: 128px;
}

.list-pager button {
  min-height: 32px;
  padding: 0 12px;
}

.list-pager .pager-nav {
  width: 72px;
  padding: 0;
}

.list-pager button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}

@media (max-width: 1080px) {
  .instrument-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .instrument-grid {
    grid-template-columns: 1fr;
  }

  .list-pager {
    justify-content: center;
    flex-wrap: wrap;
  }

  .pager-summary {
    width: 100%;
    text-align: center;
  }
}
</style>
