<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <p class="section-kicker">科研成果</p>
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
            <div class="block-heading">
              <h2>最新论文</h2>
              <span>{{ filteredPapers.length }} 篇论文，可按题名、作者、期刊检索</span>
            </div>
            <div class="paper-tools">
              <input v-model="paperKeyword" type="search" placeholder="搜索论文题名、作者或期刊" />
              <select v-model="paperYear">
                <option value="">全部年份</option>
                <option v-for="year in paperYears" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>
            <RouterLink v-for="paper in pagedPapers" :key="paper.id || paper.title" class="paper-row" :to="`/publications/${paper.id}`">
              <time>{{ paper.year }}</time>
              <div>
                <h3>{{ paper.title }}</h3>
                <div class="paper-meta">
                  <span>{{ paper.journal || '期刊信息待补充' }}</span>
                  <em>查看详情</em>
                </div>
                <p>{{ paper.authors }}</p>
              </div>
            </RouterLink>
            <div v-if="!pagedPapers.length" class="empty-note">没有找到匹配的论文。</div>
            <div v-if="paperTotalPages > 1" class="pager">
              <button type="button" :disabled="paperPage === 1" @click="paperPage -= 1">上一页</button>
              <span>第 {{ paperPage }} / {{ paperTotalPages }} 页</span>
              <button type="button" :disabled="paperPage === paperTotalPages" @click="paperPage += 1">下一页</button>
            </div>
          </article>
          <article class="card output-block">
            <h2>科研项目</h2>
            <div v-for="project in displayProjects" :key="project.title" class="simple-row">
              <strong>{{ project.title }}</strong>
              <span>{{ project.funding_source || project.principal_investigator || '科研项目' }}</span>
            </div>
            <div v-if="!displayProjects.length" class="empty-note">项目内容待补充。</div>
          </article>
          <article class="card output-block">
            <h2>专利成果</h2>
            <div v-for="patent in displayPatents" :key="patent.title" class="simple-row">
              <strong>{{ patent.title }}</strong>
              <span>{{ patent.patent_number || patent.status || '专利成果' }}</span>
            </div>
            <div v-if="!displayPatents.length" class="empty-note">专利内容待补充。</div>
          </article>
        </main>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

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
const papersReady = ref(false)
const paperKeyword = ref('')
const paperYear = ref<number | ''>('')
const paperPage = ref(1)
const paperPageSize = 8

const fallbackPapers = [
  { id: 0, year: 2026, title: 'Microbial Necromass Accelerates Humic Acid Formation by Reshaping DOM Transformation Pathways During Composting', authors: '中农雨磷团队', journal: 'Environmental Research', is_representative: false },
  { id: 1, year: 2026, title: 'Effect of Different Organic-to-inorganic Phosphorus Ratios on Organic Phosphorus Mineralization and Microbial Functions During Composting', authors: '中农雨磷团队', journal: 'Journal of Environmental Chemical Engineering', is_representative: false },
  { id: 2, year: 2026, title: 'A Compost-Derived Functional Microbial Consortium Fortifies Humification During Bio-Organic Fertilizer Production', authors: '中农雨磷团队', journal: 'Journal of Environmental Chemical Engineering', is_representative: false },
]

const looksLikeSeedPaper = (paper: Publication) =>
  /LabHub|Agricultural organic waste recycling study/i.test(`${paper.title} ${paper.authors} ${paper.journal || ''}`)

const displayPapers = computed(() => {
  if (!papersReady.value && !papers.value.length) return []
  if (!papers.value.length || papers.value.some(looksLikeSeedPaper)) return fallbackPapers
  return papers.value
})
const paperYears = computed(() => [...new Set(displayPapers.value.map((paper) => paper.year).filter(Boolean))].sort((a, b) => b - a))
const filteredPapers = computed(() => {
  const keyword = paperKeyword.value.trim().toLowerCase()
  return displayPapers.value.filter((paper) => {
    const matchesYear = !paperYear.value || paper.year === Number(paperYear.value)
    const haystack = `${paper.title} ${paper.authors} ${paper.journal || ''}`.toLowerCase()
    return matchesYear && (!keyword || haystack.includes(keyword))
  })
})
const paperTotalPages = computed(() => Math.max(1, Math.ceil(filteredPapers.value.length / paperPageSize)))
const pagedPapers = computed(() => filteredPapers.value.slice((paperPage.value - 1) * paperPageSize, paperPage.value * paperPageSize))
const displayProjects = computed(() => projects.value.slice(0, 6))
const displayPatents = computed(() => patents.value.slice(0, 6))
const statsItems = computed(() => [
  { value: stats.value?.publications ?? displayPapers.value.length, label: '公开论文' },
  { value: stats.value?.projects ?? displayProjects.value.length, label: '科研项目' },
  { value: stats.value?.patents ?? displayPatents.value.length, label: '专利成果' },
  { value: stats.value?.awards ?? 0, label: '获奖成果' },
])

watch([paperKeyword, paperYear], () => {
  paperPage.value = 1
})

watch(paperTotalPages, (total) => {
  if (paperPage.value > total) paperPage.value = total
})

onMounted(async () => {
  const [paperData, projectData, patentData, statData] = await Promise.allSettled([
    fetchPublications(),
    fetchProjects(),
    fetchPatents(),
    fetchPublicationStats(),
  ])
  if (paperData.status === 'fulfilled') papers.value = paperData.value
  papersReady.value = true
  if (projectData.status === 'fulfilled') projects.value = projectData.value
  if (patentData.status === 'fulfilled') patents.value = patentData.value
  if (statData.status === 'fulfilled') stats.value = statData.value
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
  background:
    linear-gradient(180deg, rgba(234, 245, 238, 0.7), rgba(255, 255, 255, 0.96)),
    #fff;
}

.stats-panel strong {
  display: block;
  color: var(--color-cau-green);
  font-size: 28px;
}

.stats-panel span,
.paper-row p,
.simple-row span {
  color: var(--color-muted);
}

.stats-panel span {
  color: var(--color-muted);
}

.output-main {
  display: grid;
  gap: 18px;
}

.output-block h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 24px;
}

.block-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 8px;
}

.block-heading > span {
  color: var(--color-muted);
  font-size: 13px;
}

.paper-tools {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 150px;
  gap: 10px;
  margin: 14px 0 4px;
}

.paper-tools input,
.paper-tools select {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 40px;
  padding: 0 12px;
  background: #fff;
  color: var(--color-text);
  font: inherit;
}

.paper-tools input:focus,
.paper-tools select:focus {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

.paper-row {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 18px;
  padding: 18px 0;
  border-top: 1px solid var(--color-border);
  color: inherit;
  cursor: pointer;
}

.paper-row:hover h3 {
  color: var(--color-cau-green);
}

.paper-row time {
  align-self: start;
  border-radius: 999px;
  padding: 5px 10px;
  background: var(--color-eco-green);
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
  text-align: center;
}

.paper-row h3 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 18px;
  font-weight: 650;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.paper-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.paper-meta span {
  border-radius: 999px;
  padding: 4px 9px;
  background: rgba(78, 110, 126, 0.1);
  color: var(--color-blue-gray);
  font-size: 13px;
  font-weight: 600;
}


.paper-meta em {
  color: var(--color-cau-green);
  font-size: 13px;
  font-style: normal;
  font-weight: 700;
}

.paper-row p,
.simple-row span {
  margin: 0;
  font-size: 14px;
}

.paper-row p {
  display: -webkit-box;
  margin-top: 8px;
  overflow: hidden;
  color: var(--color-muted);
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.simple-row {
  display: grid;
  gap: 4px;
  padding: 12px 0;
  border-top: 1px solid var(--color-border);
}

.pager {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  border-top: 1px solid var(--color-border);
  padding-top: 16px;
}

.pager button {
  border: 1px solid rgba(0, 135, 60, 0.22);
  border-radius: var(--radius-sm);
  min-height: 34px;
  padding: 0 12px;
  background: #fff;
  color: var(--color-cau-green);
  cursor: pointer;
  font-weight: 700;
}

.pager button:disabled {
  border-color: var(--color-border);
  color: var(--color-muted);
  cursor: not-allowed;
  opacity: 0.65;
}

.pager span,
.empty-note {
  color: var(--color-muted);
  font-size: 14px;
}

@media (max-width: 860px) {
  .output-layout {
    grid-template-columns: 1fr;
  }

  .paper-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .paper-tools {
    grid-template-columns: 1fr;
  }

  .paper-row time {
    width: fit-content;
  }
}

@media (max-width: 640px) {
  .block-heading {
    align-items: flex-start;
    flex-direction: column;
    gap: 4px;
  }

  .paper-row h3 {
    font-size: 17px;
  }
}
</style>






