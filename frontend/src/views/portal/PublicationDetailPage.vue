<template>
  <PortalLayout>
    <section class="detail-head">
      <div class="container">
        <ReturnLink class="back-link portal-back-link" :to="returnTo">返回科研成果</ReturnLink>
        <p class="section-kicker">论文详情</p>
        <h1>{{ paper?.title || '论文详情' }}</h1>
        <div class="tags">
          <span>{{ paper?.year || '年份待补充' }}</span>
          <span v-if="paper?.journal">{{ paper.journal }}</span>
          <span v-if="paper?.doi">DOI: {{ paper.doi }}</span>
        </div>
      </div>
    </section>

    <section class="page-section">
      <div class="container detail-layout">
        <main class="card detail-card">
          <section>
            <h2>作者</h2>
            <p class="muted">{{ paper?.authors || '作者信息待补充' }}</p>
          </section>
          <section>
            <h2>摘要</h2>
            <p>{{ paper?.abstract || '摘要待补充。' }}</p>
          </section>
        </main>

        <aside class="card side-card">
          <strong>论文信息</strong>
          <dl>
            <div>
              <dt>年份</dt>
              <dd>{{ paper?.year || '-' }}</dd>
            </div>
            <div>
              <dt>期刊</dt>
              <dd>{{ paper?.journal || '待补充' }}</dd>
            </div>
            <div v-if="volumeIssuePages">
              <dt>卷期页</dt>
              <dd>{{ volumeIssuePages }}</dd>
            </div>
            <div v-if="paper?.jcr_partition || paper?.cas_partition">
              <dt>分区</dt>
              <dd>{{ [paper?.jcr_partition, paper?.cas_partition].filter(Boolean).join(' / ') }}</dd>
            </div>
            <div v-if="Number(paper?.impact_factor) > 0">
              <dt>影响因子</dt>
              <dd>{{ paper?.impact_factor }}</dd>
            </div>
            <div v-if="paper?.pdf_file">
              <dt>PDF 大小</dt>
              <dd>{{ pdfSizeLabel }}</dd>
            </div>
          </dl>
          <a v-if="paper?.doi" class="outline-link" :href="doiUrl" target="_blank" rel="noreferrer">打开 DOI</a>
          <a v-if="paper?.pdf_file" class="primary-link" :href="paper.pdf_file" target="_blank" rel="noreferrer">查看 PDF</a>
          <a v-if="paper?.pdf_file" class="outline-link" :href="paper.pdf_file" download>下载 PDF</a>
        </aside>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchPublication, type Publication } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import ReturnLink from '../../components/ReturnLink.vue'
import { formatOptionalFileSize } from '../../utils/files'

const route = useRoute()
const returnTo = usePortalReturn('/publications')
const paper = ref<Publication | null>(null)

const doiUrl = computed(() => {
  if (!paper.value?.doi) return ''
  return paper.value.doi.startsWith('http') ? paper.value.doi : `https://doi.org/${paper.value.doi}`
})

const volumeIssuePages = computed(() => {
  if (!paper.value) return ''
  return [paper.value.volume, paper.value.issue, paper.value.pages].filter(Boolean).join(', ')
})

const pdfSizeLabel = computed(() => formatOptionalFileSize(paper.value?.pdf_file_size))

onMounted(async () => {
  paper.value = await fetchPublication(String(route.params.id || ''))
})
</script>

<style scoped>
.detail-head {
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 34px 0 30px;
  background: rgba(255, 255, 255, 0.72);
}

.back-link {
  display: inline-flex;
  margin-bottom: 14px;
  color: var(--color-cau-green);
  font-weight: 700;
}

.detail-head h1 {
  max-width: 1000px;
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(26px, 3.2vw, 38px);
  font-weight: 650;
  line-height: 1.25;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.tags span {
  border-radius: 999px;
  padding: 6px 11px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 13px;
  font-weight: 650;
}

.page-section {
  background: var(--color-rice);
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 24px;
}

.detail-card,
.side-card {
  border-color: rgba(31, 61, 43, 0.1);
  box-shadow: none;
}

.detail-card {
  display: grid;
  gap: 26px;
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

.detail-card .muted {
  color: var(--color-muted);
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
  margin: 18px 0;
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
  margin-top: 10px;
  background: var(--color-cau-green);
  color: #fff;
}

.outline-link {
  border: 1px solid rgba(0, 135, 60, 0.28);
  color: var(--color-cau-green);
}

@media (max-width: 900px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }
}
</style>
