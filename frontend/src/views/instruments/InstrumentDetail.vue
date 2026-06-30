<template>
  <InternalLayout title="仪器详情">
    <section v-if="instrument" class="instrument-detail-page">
      <RouterLink class="back-link" to="/instruments">返回仪器平台</RouterLink>

      <article class="card detail-card">
        <img :src="instrument.image || fallbackImage(instrument.status)" :alt="instrument.name" />
        <div class="detail-content">
          <div class="detail-heading">
            <div>
              <span>Instrument Detail</span>
              <h1>{{ instrument.name }}</h1>
              <p>{{ instrument.model || '型号待补充' }}</p>
            </div>
            <span :class="['status-tag', statusClass(instrument.status)]">{{ statusText(instrument.status) }}</span>
          </div>

          <section class="info-section">
            <h2>位置</h2>
            <p>{{ instrument.room || '未填写房间' }} {{ instrument.location_detail }}</p>
          </section>

          <section class="info-section">
            <h2>使用说明</h2>
            <p>{{ instrument.notes || '请按实验室线下设备记录和安全规程使用。' }}</p>
          </section>

          <section class="offline-note">
            <h2>线下记录</h2>
            <p>本系统不提供线上预约。仪器使用、样品交接、异常情况和维护记录以实验室线下登记表为准。</p>
          </section>
        </div>
      </article>
    </section>

    <EmptyState
      v-else
      title="未找到仪器"
      description="该仪器可能已删除，或当前账号没有查看权限。"
    />
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import EmptyState from '../../components/EmptyState.vue'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { fetchInstruments, type Instrument } from '../../api/instruments'

const route = useRoute()
const instruments = ref<Instrument[]>([])

const fallbackInstruments: Instrument[] = [
  {
    id: 0,
    name: '智能堆肥反应器',
    model: '中试反应器系统',
    room: '生态过程实验室 A201',
    location_detail: '',
    image: null,
    status: 'normal',
    status_label: '正常',
    notes: '用于堆肥过程调控、温度通风监测和腐殖化过程实验。',
  },
]

const displayInstruments = computed(() => (instruments.value.length ? instruments.value : fallbackInstruments))
const instrument = computed(() => {
  const id = Number(route.params.id)
  return displayInstruments.value.find((item) => item.id === id) || null
})

async function loadInstruments() {
  try {
    instruments.value = await fetchInstruments()
  } catch {
    instruments.value = []
  }
}

function statusClass(status: string) {
  if (status === 'normal') return 'normal'
  if (status === 'maintenance') return 'maintenance'
  return 'archived'
}

function statusText(status: string) {
  return (
    {
      normal: '正常',
      maintenance: '维护中',
      disabled: '停用',
    }[status] || '待确认'
  )
}

function fallbackImage(status: string) {
  if (status === 'maintenance') return 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1200&q=82'
  return 'https://images.unsplash.com/photo-1581093588401-fbb62a02f120?auto=format&fit=crop&w=1200&q=82'
}

onMounted(loadInstruments)
</script>

<style scoped>
.instrument-detail-page {
  display: grid;
  gap: 18px;
}

.back-link {
  width: fit-content;
  border: 1px solid rgba(0, 135, 60, 0.2);
  border-radius: var(--radius-sm);
  padding: 8px 13px;
  background: #fff;
  color: var(--color-cau-green);
  font-weight: 700;
}

.detail-card {
  overflow: hidden;
  border-radius: var(--radius-lg);
}

.detail-card:hover {
  transform: none;
}

.detail-card > img {
  width: 100%;
  max-height: 420px;
  object-fit: cover;
  filter: saturate(0.94);
}

.detail-content {
  padding: 30px;
}

.detail-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 20px;
}

.detail-heading span:first-child {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.detail-heading h1 {
  margin: 5px 0 8px;
  color: var(--color-deep-green);
  font-size: clamp(30px, 4vw, 40px);
  font-weight: 650;
  line-height: 1.2;
}

.detail-heading p,
.info-section p,
.offline-note p {
  margin: 0;
  color: var(--color-muted);
}

.info-section,
.offline-note {
  margin-top: 22px;
}

.info-section h2,
.offline-note h2 {
  margin: 0 0 8px;
  color: var(--color-deep-green);
  font-size: 20px;
  font-weight: 650;
}

.info-section p,
.offline-note p {
  line-height: 1.85;
}

.offline-note {
  border-left: 3px solid var(--color-cau-green);
  border-radius: var(--radius-sm);
  padding: 14px 16px;
  background: var(--color-eco-green);
}

@media (max-width: 760px) {
  .detail-heading {
    display: grid;
  }

  .detail-content {
    padding: 22px;
  }
}
</style>
