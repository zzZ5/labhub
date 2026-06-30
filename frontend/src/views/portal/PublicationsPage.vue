<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <p class="section-kicker">Outputs</p>
        <h1>科研成果</h1>
        <p>以论文、项目、专利和奖励为支撑，沉淀农业生态环境领域的可复用方法和工程经验。</p>
      </div>
    </section>
    <section class="page-section">
      <div class="container output-layout">
        <aside class="stats-panel card">
          <div v-for="item in statsItems" :key="item.label">
            <strong>{{ item.value }}</strong>
            <span>{{ item.label }}</span>
          </div>
        </aside>
        <main class="output-main">
          <article class="card output-block">
            <h2>代表论文</h2>
            <div v-for="paper in displayPapers" :key="paper.title" class="paper-row">
              <time>{{ paper.year }}</time>
              <div>
                <h3>{{ paper.title }}</h3>
                <p>{{ paper.authors }}</p>
                <span>{{ paper.journal || '期刊信息待补充' }}</span>
              </div>
            </div>
          </article>
          <article class="card output-block">
            <h2>项目与专利</h2>
            <div v-for="project in displayProjects" :key="project.title" class="simple-row">
              <strong>{{ project.title }}</strong>
              <span>{{ project.funding_source || project.principal_investigator || '科研项目' }}</span>
            </div>
            <div v-for="patent in displayPatents" :key="patent.title" class="simple-row">
              <strong>{{ patent.title }}</strong>
              <span>{{ patent.patent_number || patent.status || '专利成果' }}</span>
            </div>
          </article>
        </main>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  fetchPatents,
  fetchProjects,
  fetchPublicationStats,
  fetchPublications,
  type Patent,
  type Project,
  type Publication,
  type PublicationStats,
} from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const papers = ref<Publication[]>([])
const projects = ref<Project[]>([])
const patents = ref<Patent[]>([])
const stats = ref<PublicationStats | null>(null)

const fallbackPapers = [
  { id: 0, year: 2026, title: 'Composting process regulation for agricultural organic waste recycling', authors: '中农雨磷团队', journal: 'Journal of Cleaner Production', is_representative: true },
  { id: 1, year: 2025, title: 'Microbial mechanisms of humification in aerobic composting systems', authors: '中农雨磷团队', journal: 'Bioresource Technology', is_representative: true },
]

const displayPapers = computed(() => (papers.value.length ? papers.value : fallbackPapers))
const displayProjects = computed(() => projects.value.slice(0, 4))
const displayPatents = computed(() => patents.value.slice(0, 4))
const statsItems = computed(() => [
  { value: stats.value?.publications ?? displayPapers.value.length, label: '公开论文' },
  { value: stats.value?.projects ?? displayProjects.value.length, label: '科研项目' },
  { value: stats.value?.patents ?? displayPatents.value.length, label: '专利成果' },
  { value: stats.value?.awards ?? 0, label: '获奖成果' },
])

onMounted(async () => {
  const [paperData, projectData, patentData, statData] = await Promise.allSettled([
    fetchPublications(),
    fetchProjects(),
    fetchPatents(),
    fetchPublicationStats(),
  ])
  if (paperData.status === 'fulfilled') papers.value = paperData.value
  if (projectData.status === 'fulfilled') projects.value = projectData.value
  if (patentData.status === 'fulfilled') patents.value = patentData.value
  if (statData.status === 'fulfilled') stats.value = statData.value
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

.output-layout {
  display: grid;
  grid-template-columns: 230px 1fr;
  gap: 22px;
}

.stats-panel,
.output-block {
  border-color: rgba(31, 61, 43, 0.1);
  padding: 22px;
  box-shadow: none;
}

.stats-panel {
  display: grid;
  gap: 14px;
  align-self: start;
  background: var(--color-deep-green);
}

.stats-panel strong {
  display: block;
  color: #fff;
  font-size: 30px;
}

.stats-panel span,
.paper-row p,
.paper-row span,
.simple-row span {
  color: var(--color-muted);
}

.stats-panel span {
  color: rgba(255, 255, 255, 0.7);
}

.output-main {
  display: grid;
  gap: 18px;
}

.output-block h2 {
  margin: 0 0 16px;
  color: var(--color-deep-green);
  font-size: 24px;
}

.paper-row {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 16px;
  padding: 14px 0;
  border-top: 1px solid var(--color-border);
}

.paper-row time {
  color: var(--color-cau-green);
  font-weight: 700;
}

.paper-row h3 {
  margin: 0 0 6px;
  color: var(--color-deep-green);
  font-size: 18px;
}

.paper-row p,
.simple-row span {
  margin: 0;
  font-size: 14px;
}

.simple-row {
  display: grid;
  gap: 4px;
  padding: 12px 0;
  border-top: 1px solid var(--color-border);
}

@media (max-width: 860px) {
  .output-layout {
    grid-template-columns: 1fr;
  }
}
</style>


