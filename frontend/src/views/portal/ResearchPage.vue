<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <p class="section-kicker">研究方向</p>
        <h1>研究方向</h1>
        <p>围绕农业废弃物资源化、生态环境过程调控、微生物生态机制和智能堆肥技术，形成从基础机制到工程应用的研究链条。</p>
      </div>
    </section>
    <section class="page-section">
      <div class="container research-grid">
        <RouterLink v-for="item in displayDirections" :key="item.title" class="card research-card" :to="item.to">
          <span>{{ item.index }}</span>
          <h2>{{ item.title }}</h2>
          <p>{{ item.summary }}</p>
          <div class="tag-row">
            <em v-for="tag in item.tags" :key="tag">{{ tag }}</em>
          </div>
        </RouterLink>
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
  { title: '微生物生态', summary: '解析有机废弃物转化、土壤生态过程中的关键微生物群落与功能机制。' },
  { title: '有机废弃物资源转化', summary: '面向农业和食品加工废弃物，研究低碳转化、稳定化和资源化利用路径。' },
  { title: '高值产品开发', summary: '围绕有机肥、水溶肥和生态产品，推进从工艺优化到应用评价的转化研究。' },
  { title: '堆肥腐殖化调控', summary: '研究堆肥过程中腐殖酸形成、臭气减排和品质提升的过程调控机制。' },
  { title: '养分循环与土壤健康', summary: '评价有机物料还田、养分循环利用及其对土壤生态功能的影响。' },
  { title: '农业低碳生态转化', summary: '服务农业废弃物低碳处理和绿色农业场景，探索可推广的技术模式。' },
]

const displayDirections = computed(() =>
  (directions.value.length ? directions.value : fallback).map((item: any, index) => ({
    index: `0${index + 1}`,
    title: item.title,
    summary: item.summary,
    to: item.slug ? `/research/${item.slug}` : '/research',
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
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 28px 0 24px;
  background:
    linear-gradient(90deg, rgba(234, 245, 238, 0.76), rgba(255, 255, 255, 0.96) 48%, rgba(248, 247, 242, 0.92)),
    var(--color-white);
}

.portal-page-head::before {
  position: absolute;
  top: 30px;
  bottom: 26px;
  left: max(20px, calc((100vw - var(--container)) / 2));
  width: 3px;
  border-radius: 999px;
  content: "";
  background: var(--color-cau-green);
}

.portal-page-head .container {
  padding-left: 22px;
}

.portal-page-head h1 {
  margin: 0 0 9px;
  color: var(--color-deep-green);
  font-size: clamp(28px, 3.1vw, 38px);
  font-weight: 650;
  line-height: 1.18;
}

.portal-page-head p:last-child {
  max-width: 820px;
  margin: 0;
  color: var(--color-muted);
  font-size: 15px;
  line-height: 1.65;
}

.portal-page-head .section-kicker {
  color: var(--color-cau-green);
}

.page-section {
  padding-top: 30px;
  background: var(--color-rice);
}

.research-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.research-card {
  display: block;
  border-color: rgba(31, 61, 43, 0.1);
  padding: 22px;
  color: inherit;
  text-decoration: none;
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


