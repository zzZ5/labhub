<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <p class="section-kicker">Research</p>
        <h1>研究方向</h1>
        <p>围绕农业废弃物资源化、生态环境过程调控、微生物生态机制和智能堆肥技术，形成从基础机制到工程应用的研究链条。</p>
      </div>
    </section>
    <section class="page-section">
      <div class="container research-grid">
        <article v-for="item in displayDirections" :key="item.title" class="card research-card">
          <span>{{ item.index }}</span>
          <h2>{{ item.title }}</h2>
          <p>{{ item.summary }}</p>
          <div class="tag-row">
            <em v-for="tag in item.tags" :key="tag">{{ tag }}</em>
          </div>
        </article>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { fetchResearchDirections, type ResearchDirection } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const directions = ref<ResearchDirection[]>([])

const fallback = [
  { title: '有机废弃物资源化利用', summary: '研究秸秆、畜禽粪污、园林废弃物等农业有机废弃物的高值转化路径。' },
  { title: '好氧堆肥与腐殖化调控', summary: '解析堆肥过程碳氮转化、腐殖质形成与臭气排放控制机制。' },
  { title: '农业生态环境过程', summary: '关注土壤、作物、微生物和污染风险之间的生态环境过程耦合。' },
  { title: '微生物生态与功能机制', summary: '识别关键功能菌群及其环境响应机制，支撑过程调控。' },
  { title: '智能堆肥与过程建模', summary: '构建堆肥过程监测、预测和调控模型，服务工程化应用。' },
  { title: '养分循环与污染风险控制', summary: '评估有机肥还田、氮磷循环和潜在环境风险。' },
]

const displayDirections = computed(() =>
  (directions.value.length ? directions.value : fallback).map((item, index) => ({
    index: `0${index + 1}`,
    title: item.title,
    summary: item.summary,
    tags: ['农业生态', '资源循环', '环境过程'],
  })),
)

onMounted(async () => {
  try {
    directions.value = await fetchResearchDirections()
  } catch {
    directions.value = []
  }
})
</script>

<style scoped>
.portal-page-head {
  position: relative;
  border-bottom: 4px solid var(--color-cau-green);
  padding: 56px 0 42px;
  background:`n    linear-gradient(90deg, rgba(234, 245, 238, 0.96), rgba(255, 255, 255, 0.98) 56%, rgba(248, 247, 242, 0.96)),`n    radial-gradient(circle at 88% 26%, rgba(0, 135, 60, 0.08), transparent 28%),`n    var(--color-white);
}

.portal-page-head::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 34%;
  height: 4px;
  content: "";
  background: var(--color-soil);
}

.portal-page-head h1 {
  margin: 0 0 14px;
  color: var(--color-deep-green);
  font-size: clamp(38px, 4.5vw, 56px);
  font-weight: 650;
}

.portal-page-head p:last-child {
  max-width: 780px;
  margin: 0;
  color: var(--color-muted);
  font-size: 17px;
  line-height: 1.8;
}

.portal-page-head .section-kicker {
  color: var(--color-cau-green);
}

.page-section {
  background: var(--color-rice);
}

.research-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.research-card {
  border-color: rgba(31, 61, 43, 0.1);
  padding: 22px;
  box-shadow: none;
}

.research-card > span {
  color: var(--color-cau-green);
  font-weight: 700;
}

.research-card h2 {
  margin: 12px 0 10px;
  color: var(--color-deep-green);
  font-size: 20px;
}

.research-card p {
  margin: 0;
  color: var(--color-muted);
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 14px;
}

.tag-row em {
  border-radius: 999px;
  padding: 4px 10px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 13px;
  font-style: normal;
}

@media (max-width: 980px) {
  .research-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .research-grid {
    grid-template-columns: 1fr;
  }
}
</style>


