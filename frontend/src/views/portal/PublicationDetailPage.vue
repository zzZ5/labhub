<template>
  <PortalLayout>
    <section class="publication-head">
      <div class="container">
        <RouterLink class="back-link" to="/publications">返回科研成果</RouterLink>
        <p class="section-kicker">论文详情</p>
        <h1>{{ paper?.title || '论文详情' }}</h1>
        <div class="paper-tags">
          <span>{{ paper?.year || '年份待补充' }}</span>
          <span v-if="paper?.journal">{{ paper.journal }}</span>
          <span v-if="paper?.doi">DOI: {{ paper.doi }}</span>
        </div>
      </div>
    </section>

    <section class="page-section">
      <div class="container publication-layout">
        <main class="card paper-card">
          <section>
            <h2>作者</h2>
            <p class="authors">{{ paper?.authors || '作者信息待补充' }}</p>
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
            <div v-if="paper?.volume || paper?.issue || paper?.pages">
              <dt>卷期页</dt>
              <dd>{{ volumeIssuePages }}</dd>
            </div>
            <div v-if="paper?.jcr_partition || paper?.cas_partition">
              <dt>分区</dt>
              <dd>{{ [paper?.jcr_partition, paper?.cas_partition].filter(Boolean).join(' / ') }}</dd>
            </div>
            <div v-if="paper?.impact_factor">
              <dt>影响因子</dt>
              <dd>{{ paper.impact_factor }}</dd>
            </div>
          </dl>
          <a v-if="paper?.doi" class="outline-link" :href="doiUrl" target="_blank" rel="noreferrer">打开 DOI</a>
          <a v-if="paper?.pdf_file" class="primary-link" :href="paper.pdf_file" target="_blank" rel="noreferrer">查看 PDF</a>
        </aside>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchPublication, type Publication } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const route = useRoute()
const paper = ref<Publication | null>(null)

const fallbackPapers: Record<string, Publication> = {
  '0': {
    id: 0,
    year: 2026,
    title: 'Microbial Necromass Accelerates Humic Acid Formation by Reshaping DOM Transformation Pathways During Composting',
    authors: 'Su Chang; Yi Zheng; Baoju Liu; Wenjie Chen; Yuquan Wei; Long D. Nghiem; Mohan Bai; Guochun Ding; Huike Ye; Yan Xu; Ji Li',
    journal: 'Environmental Research',
    doi: '',
    abstract: 'AMiner 候选记录。后续可在后台补充完整摘要、DOI 和 PDF 附件。',
    pdf_file: '',
    visibility: 'public',
    is_representative: false,
  },
  '1': {
    id: 1,
    year: 2026,
    title: 'Effect of Different Organic-to-inorganic Phosphorus Ratios on Organic Phosphorus Mineralization and Microbial Functions During Composting',
    authors: 'Zhen Wu; Yuquan Wei; Tong Guo; Long D. Nghiem; Zimin Wei; Yue Zhao',
    journal: 'Journal of Environmental Chemical Engineering',
    doi: '',
    abstract: 'AMiner 候选记录。后续可在后台补充完整摘要、DOI 和 PDF 附件。',
    pdf_file: '',
    visibility: 'public',
    is_representative: false,
  },
  '2': {
    id: 2,
    year: 2026,
    title: 'A Compost-Derived Functional Microbial Consortium Fortifies Humification During Bio-Organic Fertilizer Production',
    authors: 'Yang Yang; Yuxin Sun; Jiaqi Liu; Xueqing Jia; Tao Wang; Qing Chen; Yanming Li; Yuyun Wang; Zhi Xu; Yuquan Wei; Ruixue Chang',
    journal: 'Journal of Environmental Chemical Engineering',
    doi: '',
    abstract: 'AMiner 候选记录。后续可在后台补充完整摘要、DOI 和 PDF 附件。',
    pdf_file: '',
    visibility: 'public',
    is_representative: false,
  },
}

const doiUrl = computed(() => {
  if (!paper.value?.doi) return ''
  return paper.value.doi.startsWith('http') ? paper.value.doi : `https://doi.org/${paper.value.doi}`
})

const volumeIssuePages = computed(() => {
  if (!paper.value) return ''
  return [paper.value.volume, paper.value.issue, paper.value.pages].filter(Boolean).join(', ')
})

onMounted(async () => {
  const id = String(route.params.id || '')
  try {
    paper.value = await fetchPublication(id)
  } catch {
    paper.value = fallbackPapers[id] || null
  }
})
</script>

<style scoped>
.publication-head {
  border-bottom: 4px solid var(--color-cau-green);
  padding: 46px 0 38px;
  background:
    linear-gradient(90deg, rgba(234, 245, 238, 0.96), rgba(255, 255, 255, 0.98) 58%, rgba(248, 247, 242, 0.96)),
    var(--color-white);
}

.back-link {
  display: inline-flex;
  margin-bottom: 18px;
  color: var(--color-cau-green);
  font-weight: 700;
}

.publication-head h1 {
  max-width: 980px;
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(30px, 4vw, 48px);
  font-weight: 650;
  line-height: 1.24;
}

.paper-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.paper-tags span {
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

.publication-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 24px;
}

.paper-card,
.side-card {
  border-color: rgba(31, 61, 43, 0.1);
  box-shadow: none;
}

.paper-card {
  display: grid;
  gap: 26px;
  padding: 30px 34px;
}

.paper-card h2 {
  margin: 0 0 12px;
  color: var(--color-deep-green);
  font-size: 22px;
}

.paper-card p {
  margin: 0;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.85;
}

.paper-card .authors {
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
  .publication-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .paper-card {
    padding: 24px 22px;
  }
}
</style>
