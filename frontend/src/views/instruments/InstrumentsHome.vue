<template>
  <InternalLayout title="仪器平台">
    <section class="instrument-page">
      <div class="page-heading">
        <div>
          <span>Instrument Platform</span>
          <h1>仪器设备台账</h1>
          <p>
            查看课题组仪器设备状态、位置、图片和使用说明。实际使用记录按实验室线下台账执行。
          </p>
        </div>
        <span class="heading-note">内部平台</span>
      </div>

      <section class="status-grid">
        <article v-for="item in statusSummary" :key="item.label" class="card status-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.note }}</p>
        </article>
      </section>

      <section class="content-grid">
        <div class="instrument-grid">
          <RouterLink
            v-for="instrument in displayInstruments"
            :key="instrument.id"
            class="card instrument-card"
            :to="{ name: 'instrument-detail', params: { id: instrument.id } }"
          >
            <img :src="instrument.image || fallbackImage(instrument.status)" :alt="instrument.name" />
            <div class="instrument-body">
              <div class="instrument-title">
                <h2>{{ instrument.name }}</h2>
                <span :class="['status-tag', statusClass(instrument.status)]">
                  {{ statusText(instrument.status) }}
                </span>
              </div>
              <p>{{ instrument.model || '型号待补充' }}</p>
              <dl>
                <div>
                  <dt>位置</dt>
                  <dd>{{ instrument.room || '未填写房间' }} {{ instrument.location_detail }}</dd>
                </div>
                <div>
                  <dt>说明</dt>
                  <dd>{{ instrument.notes || '请按实验室线下设备记录和安全规程使用。' }}</dd>
                </div>
              </dl>
              <span class="detail-link">查看设备详情</span>
            </div>
          </RouterLink>
        </div>
      </section>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import InternalLayout from '../../layouts/InternalLayout.vue'
import { fetchInstruments, type Instrument } from '../../api/instruments'

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
const statusSummary = computed(() => {
  const items = displayInstruments.value
  return [
    { label: '设备总数', value: items.length, note: '当前台账设备' },
    { label: '正常设备', value: items.filter((item) => item.status === 'normal').length, note: '可按线下台账使用' },
    { label: '维护/停用', value: items.filter((item) => item.status !== 'normal').length, note: '需联系负责人确认' },
  ]
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
  if (status === 'maintenance') return 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=700&q=80'
  return 'https://images.unsplash.com/photo-1581093588401-fbb62a02f120?auto=format&fit=crop&w=700&q=80'
}

onMounted(loadInstruments)
</script>

<style scoped>
.instrument-page {
  display: grid;
  gap: 24px;
}

.page-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-lg);
  padding: 30px 32px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(251, 253, 251, 0.94) 60%, rgba(234, 245, 238, 0.86)),
    #fff;
  box-shadow: var(--shadow-flat);
}

.page-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.page-heading h1 {
  margin: 6px 0 8px;
  color: var(--color-deep-green);
  font-size: clamp(27px, 3vw, 34px);
  font-weight: 650;
  line-height: 1.2;
}

.page-heading p,
.instrument-card p,
.detail-model,
.offline-note p {
  margin: 0;
  color: var(--color-muted);
}

.heading-note {
  flex: 0 0 auto;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: 999px;
  padding: 7px 12px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 700;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.status-card {
  padding: 22px;
}

.status-card:hover {
  transform: none;
}

.status-card span {
  color: var(--color-muted);
  font-size: 14px;
}

.status-card strong {
  display: block;
  margin: 8px 0;
  color: var(--color-deep-green);
  font-size: 32px;
  font-weight: 650;
  line-height: 1;
}

.status-card p {
  margin: 0;
  color: var(--color-muted);
}

.content-grid {
  display: block;
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

.instrument-card img {
  width: 100%;
  aspect-ratio: 16 / 8.5;
  object-fit: cover;
  filter: saturate(0.92);
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

.detail-link {
  display: block;
  margin-top: 18px;
  border-top: 1px solid var(--color-line);
  padding-top: 14px;
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}

@media (max-width: 1080px) {
  .instrument-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .page-heading {
    display: grid;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }

  .instrument-grid {
    grid-template-columns: 1fr;
  }
}
</style>
