<template>
  <PortalLayout>
    <section class="detail-head">
      <div class="container">
        <RouterLink class="back-link portal-back-link" to="/publications">返回科研成果</RouterLink>
        <p class="section-kicker">专利成果</p>
        <h1>{{ patent?.title || '专利成果' }}</h1>
      </div>
    </section>
    <section class="page-section">
      <div class="container detail-layout">
        <main class="card detail-card">
          <h2>发明人</h2>
          <p>{{ patent?.inventors || '发明人信息待补充。' }}</p>
        </main>
        <aside class="card side-card">
          <strong>专利信息</strong>
          <dl>
            <div>
              <dt>专利号</dt>
              <dd>{{ patent?.patent_number || '-' }}</dd>
            </div>
            <div>
              <dt>状态</dt>
              <dd>{{ patent?.status || '-' }}</dd>
            </div>
            <div v-if="patent?.application_date">
              <dt>申请日期</dt>
              <dd>{{ patent.application_date }}</dd>
            </div>
            <div v-if="patent?.authorization_date">
              <dt>授权日期</dt>
              <dd>{{ patent.authorization_date }}</dd>
            </div>
            <div v-if="patent?.pdf_file">
              <dt>PDF 大小</dt>
              <dd>{{ pdfSizeLabel }}</dd>
            </div>
          </dl>
          <a v-if="patent?.pdf_file" class="primary-link" :href="patent.pdf_file" target="_blank" rel="noreferrer">查看 PDF</a>
          <a v-if="patent?.pdf_file" class="outline-link" :href="patent.pdf_file" download>下载 PDF</a>
        </aside>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchPatent, type Patent } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const route = useRoute()
const patent = ref<Patent | null>(null)

const pdfSizeLabel = computed(() => formatFileSize(patent.value?.pdf_file_size || 0))

function formatFileSize(size: number) {
  if (!size) return '大小未知'
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

onMounted(async () => {
  patent.value = await fetchPatent(String(route.params.id || ''))
})
</script>

<style scoped>
.detail-head {
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 34px 0 30px;
  background: linear-gradient(90deg, rgba(234, 245, 238, 0.9), rgba(255, 255, 255, 0.98) 58%, rgba(248, 247, 242, 0.92));
}

.back-link {
  display: inline-flex;
  margin-bottom: 14px;
  color: var(--color-cau-green);
  font-weight: 700;
}

.detail-head h1 {
  max-width: 980px;
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(28px, 3.4vw, 42px);
  font-weight: 650;
  line-height: 1.25;
}

.page-section {
  background: var(--color-rice);
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 310px;
  gap: 24px;
}

.detail-card,
.side-card {
  border-color: rgba(31, 61, 43, 0.1);
  box-shadow: none;
}

.detail-card {
  padding: 30px 34px;
}

.detail-card h2 {
  margin: 0 0 12px;
  color: var(--color-deep-green);
  font-size: 21px;
}

.detail-card p {
  margin: 0;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.85;
}

.side-card {
  align-self: start;
  padding: 22px;
}

.side-card strong {
  color: var(--color-deep-green);
  font-size: 18px;
}

.side-card dl {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
}

.side-card dt {
  color: var(--color-muted);
  font-size: 13px;
}

.side-card dd {
  margin: 4px 0 0;
  color: var(--color-text);
  line-height: 1.55;
}

.primary-link,
.outline-link {
  display: flex;
  justify-content: center;
  border-radius: var(--radius-sm);
  padding: 9px 14px;
  font-weight: 700;
}

.primary-link {
  background: var(--color-cau-green);
  color: #fff;
}

.outline-link {
  margin-top: 10px;
  border: 1px solid rgba(0, 135, 60, 0.28);
  color: var(--color-cau-green);
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
