<template>
  <PortalLayout>
    <PortalPageHeader title="科研成果" description="展示团队发表论文、承担项目、授权专利与获奖成果，支持检索和分页浏览。" />

    <section class="page-section">
      <div class="container output-layout">
        <aside class="stats-panel card">
          <div v-for="(item, index) in statsItems" :key="item.label" :class="`result-stat result-stat-${index + 1}`">
            <strong>{{ item.value }}</strong>
            <span>{{ item.label }}</span>
          </div>
        </aside>

        <main class="output-main card">
          <div class="result-tabs" role="tablist" aria-label="科研成果类型" @keydown="handleTabKeydown">
            <button id="result-tab-papers" class="tab-papers" role="tab" aria-controls="result-panel-papers" :aria-selected="activeTab === 'papers'" :tabindex="activeTab === 'papers' ? 0 : -1" :class="{ active: activeTab === 'papers' }" type="button" @click="activeTab = 'papers'">论文</button>
            <button id="result-tab-projects" class="tab-projects" role="tab" aria-controls="result-panel-projects" :aria-selected="activeTab === 'projects'" :tabindex="activeTab === 'projects' ? 0 : -1" :class="{ active: activeTab === 'projects' }" type="button" @click="activeTab = 'projects'">项目</button>
            <button id="result-tab-patents" class="tab-patents" role="tab" aria-controls="result-panel-patents" :aria-selected="activeTab === 'patents'" :tabindex="activeTab === 'patents' ? 0 : -1" :class="{ active: activeTab === 'patents' }" type="button" @click="activeTab = 'patents'">专利</button>
            <button id="result-tab-awards" class="tab-awards" role="tab" aria-controls="result-panel-awards" :aria-selected="activeTab === 'awards'" :tabindex="activeTab === 'awards' ? 0 : -1" :class="{ active: activeTab === 'awards' }" type="button" @click="activeTab = 'awards'">获奖</button>
          </div>

          <section v-if="activeTab === 'papers'" id="result-panel-papers" role="tabpanel" aria-labelledby="result-tab-papers" class="result-block">
            <div class="block-heading">
              <div>
                <h2>论文发表</h2>
                <p>{{ paperTotal }} 篇公开论文，可按题名、作者、期刊、DOI 检索</p>
              </div>
              <button class="mobile-filter-toggle" type="button" :aria-expanded="filtersExpanded" @click="filtersExpanded = !filtersExpanded">{{ filtersExpanded ? '收起筛选' : '筛选论文' }}</button>
            </div>
            <div class="result-tools" :class="{ 'mobile-collapsed': !filtersExpanded }">
              <input v-model="paperKeyword" type="search" placeholder="搜索论文题名、作者、期刊或 DOI" @keyup.enter="loadPapers(1)" />
              <select v-model="paperYear" @change="loadPapers(1)">
                <option value="">全部年份</option>
                <option v-for="year in paperYears" :key="year" :value="year">{{ year }}</option>
              </select>
              <button type="button" @click="loadPapers(1)">检索</button>
            </div>
            <RouterLink v-for="paper in papers" :key="paper.id" class="paper-row" :to="{ path: `/publications/${paper.id}`, query: { from: route.fullPath } }">
              <time>{{ paper.year }}</time>
              <div>
                <h3>{{ paper.title }}</h3>
                <p class="authors">{{ paper.authors }}</p>
                <div class="meta-line">
                  <span>{{ paper.journal || '期刊信息待补充' }}</span>
                  <span v-if="paper.doi">DOI: {{ paper.doi }}</span>
                </div>
                <p v-if="paper.abstract" class="abstract">{{ paper.abstract }}</p>
              </div>
            </RouterLink>
            <div v-if="!papers.length" class="empty-note">没有找到匹配的论文。</div>
            <AppPagination :page="paperPage" :total-pages="Math.max(1, Math.ceil(paperTotal / pageSize))" @change="loadPapers" />
          </section>

          <section v-else-if="activeTab === 'projects'" id="result-panel-projects" role="tabpanel" aria-labelledby="result-tab-projects" class="result-block">
            <div class="block-heading">
              <div>
                <h2>科研项目</h2>
                <p>{{ projectTotal }} 项公开项目，可按项目名称、编号、来源或负责人检索</p>
              </div>
              <button class="mobile-filter-toggle" type="button" :aria-expanded="filtersExpanded" @click="filtersExpanded = !filtersExpanded">{{ filtersExpanded ? '收起筛选' : '筛选项目' }}</button>
            </div>
            <div class="result-tools two" :class="{ 'mobile-collapsed': !filtersExpanded }">
              <input v-model="projectKeyword" type="search" placeholder="搜索项目名称、编号、来源或负责人" @keyup.enter="loadProjects(1)" />
              <button type="button" @click="loadProjects(1)">检索</button>
            </div>
            <RouterLink v-for="project in projects" :key="project.id" class="simple-card project-card" :to="{ path: `/publications/projects/${project.id}`, query: { from: route.fullPath } }">
              <div>
                <h3>{{ project.title }}</h3>
                <p>{{ project.description || project.funding_source || '项目说明待补充' }}</p>
              </div>
              <dl>
                <div>
                  <dt>编号</dt>
                  <dd>{{ project.project_number || '未公开' }}</dd>
                </div>
                <div>
                  <dt>来源</dt>
                  <dd>{{ project.funding_source || '-' }}</dd>
                </div>
                <div>
                  <dt>状态</dt>
                  <dd>{{ project.status || '-' }}</dd>
                </div>
              </dl>
            </RouterLink>
            <div v-if="!projects.length" class="empty-note">没有找到匹配的项目。</div>
            <AppPagination :page="projectPage" :total-pages="Math.max(1, Math.ceil(projectTotal / pageSize))" @change="loadProjects" />
          </section>

          <section v-else-if="activeTab === 'patents'" id="result-panel-patents" role="tabpanel" aria-labelledby="result-tab-patents" class="result-block">
            <div class="block-heading">
              <div>
                <h2>专利成果</h2>
                <p>{{ patentTotal }} 项公开专利，可按专利名称、专利号、发明人检索</p>
              </div>
              <button class="mobile-filter-toggle" type="button" :aria-expanded="filtersExpanded" @click="filtersExpanded = !filtersExpanded">{{ filtersExpanded ? '收起筛选' : '筛选专利' }}</button>
            </div>
            <div class="result-tools two" :class="{ 'mobile-collapsed': !filtersExpanded }">
              <input v-model="patentKeyword" type="search" placeholder="搜索专利名称、专利号或发明人" @keyup.enter="loadPatents(1)" />
              <button type="button" @click="loadPatents(1)">检索</button>
            </div>
            <RouterLink v-for="patent in patents" :key="patent.id" class="simple-card patent-card" :to="{ path: `/publications/patents/${patent.id}`, query: { from: route.fullPath } }">
              <div>
                <h3>{{ patent.title }}</h3>
                <p>{{ patent.inventors || '发明人待补充' }}</p>
              </div>
              <dl>
                <div>
                  <dt>专利号</dt>
                  <dd>{{ patent.patent_number || '-' }}</dd>
                </div>
                <div>
                  <dt>状态</dt>
                  <dd>{{ patent.status || '-' }}</dd>
                </div>
                <div v-if="patent.application_date">
                  <dt>申请日期</dt>
                  <dd>{{ patent.application_date }}</dd>
                </div>
              </dl>
            </RouterLink>
            <div v-if="!patents.length" class="empty-note">没有找到匹配的专利。</div>
            <AppPagination :page="patentPage" :total-pages="Math.max(1, Math.ceil(patentTotal / pageSize))" @change="loadPatents" />
          </section>

          <section v-else id="result-panel-awards" role="tabpanel" aria-labelledby="result-tab-awards" class="result-block">
            <div class="block-heading">
              <div>
                <h2>获奖成果</h2>
                <p>{{ awardTotal }} 项公开获奖，可按奖项名称、等级或参与人员检索</p>
              </div>
              <button class="mobile-filter-toggle" type="button" :aria-expanded="filtersExpanded" @click="filtersExpanded = !filtersExpanded">{{ filtersExpanded ? '收起筛选' : '筛选获奖' }}</button>
            </div>
            <div class="result-tools two" :class="{ 'mobile-collapsed': !filtersExpanded }">
              <input v-model="awardKeyword" type="search" placeholder="搜索奖项名称、等级或参与人员" @keyup.enter="loadAwards(1)" />
              <button type="button" @click="loadAwards(1)">检索</button>
            </div>
            <RouterLink v-for="award in awards" :key="award.id" class="simple-card award-card" :to="{ path: `/publications/awards/${award.id}`, query: { from: route.fullPath } }">
              <div>
                <h3>{{ award.title }}</h3>
                <p>{{ award.description || award.participants || '奖项说明待补充' }}</p>
              </div>
              <dl>
                <div>
                  <dt>等级</dt>
                  <dd>{{ award.award_level || '-' }}</dd>
                </div>
                <div>
                  <dt>日期</dt>
                  <dd>{{ award.award_date || '-' }}</dd>
                </div>
              </dl>
            </RouterLink>
            <div v-if="!awards.length" class="empty-note">没有找到匹配的获奖成果。</div>
            <AppPagination :page="awardPage" :total-pages="Math.max(1, Math.ceil(awardTotal / pageSize))" @change="loadAwards" />
          </section>
        </main>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  fetchPatentPage,
  fetchProjectPage,
  fetchPublicationPage,
  fetchAwardPage,
  fetchPublicationStats,
  type Award,
  type Patent,
  type Project,
  type Publication,
  type PublicationStats,
} from '../../api/publicPortal'
import AppPagination from '../../components/AppPagination.vue'
import PortalPageHeader from '../../components/PortalPageHeader.vue'
import PortalLayout from '../../layouts/PortalLayout.vue'

type TabKey = 'papers' | 'projects' | 'patents' | 'awards'

const pageSize = 10
const route = useRoute()
const router = useRouter()
const tabKeys: TabKey[] = ['papers', 'projects', 'patents', 'awards']
const queryTab = typeof route.query.tab === 'string' && tabKeys.includes(route.query.tab as TabKey) ? route.query.tab as TabKey : 'papers'
const queryPage = Math.max(1, Number.parseInt(typeof route.query.page === 'string' ? route.query.page : '', 10) || 1)

async function handleTabKeydown(event: KeyboardEvent) {
  if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
  event.preventDefault()
  const current = tabKeys.indexOf(activeTab.value)
  const next = event.key === 'Home'
    ? 0
    : event.key === 'End'
      ? tabKeys.length - 1
      : (current + (event.key === 'ArrowRight' ? 1 : -1) + tabKeys.length) % tabKeys.length
  activeTab.value = tabKeys[next]
  await nextTick()
  document.getElementById(`result-tab-${activeTab.value}`)?.focus()
}
const queryKeyword = typeof route.query.q === 'string' ? route.query.q : ''
const activeTab = ref<TabKey>(queryTab)
const stats = ref<PublicationStats | null>(null)
const filtersExpanded = ref(false)

const papers = ref<Publication[]>([])
const projects = ref<Project[]>([])
const patents = ref<Patent[]>([])
const awards = ref<Award[]>([])

const paperKeyword = ref(queryTab === 'papers' ? queryKeyword : '')
const projectKeyword = ref(queryTab === 'projects' ? queryKeyword : '')
const patentKeyword = ref(queryTab === 'patents' ? queryKeyword : '')
const awardKeyword = ref(queryTab === 'awards' ? queryKeyword : '')
const paperYear = ref<number | ''>(queryTab === 'papers' && typeof route.query.year === 'string' ? Number(route.query.year) || '' : '')

const paperPage = ref(queryTab === 'papers' ? queryPage : 1)
const projectPage = ref(queryTab === 'projects' ? queryPage : 1)
const patentPage = ref(queryTab === 'patents' ? queryPage : 1)
const awardPage = ref(queryTab === 'awards' ? queryPage : 1)
const paperTotal = ref(0)
const projectTotal = ref(0)
const patentTotal = ref(0)
const awardTotal = ref(0)

const paperYears = computed(() => {
  const current = new Date().getFullYear()
  return Array.from({ length: 12 }, (_, index) => current - index)
})

const statsItems = computed(() => [
  { value: stats.value?.publications ?? paperTotal.value, label: '公开论文' },
  { value: stats.value?.projects ?? projectTotal.value, label: '科研项目' },
  { value: stats.value?.patents ?? patentTotal.value, label: '专利成果' },
  { value: stats.value?.awards ?? awardTotal.value, label: '获奖成果' },
])

function syncActiveQuery() {
  const pages = { papers: paperPage.value, projects: projectPage.value, patents: patentPage.value, awards: awardPage.value }
  const keywords = { papers: paperKeyword.value, projects: projectKeyword.value, patents: patentKeyword.value, awards: awardKeyword.value }
  const query: Record<string, string> = {}
  if (activeTab.value !== 'papers') query.tab = activeTab.value
  if (pages[activeTab.value] > 1) query.page = String(pages[activeTab.value])
  if (keywords[activeTab.value].trim()) query.q = keywords[activeTab.value].trim()
  if (activeTab.value === 'papers' && paperYear.value) query.year = String(paperYear.value)
  void router.replace({ path: '/publications', query })
}

async function loadPapers(page = paperPage.value) {
  paperPage.value = page
  const data = await fetchPublicationPage({
    page,
    page_size: pageSize,
    search: paperKeyword.value.trim() || undefined,
    year: paperYear.value ? Number(paperYear.value) : undefined,
  })
  papers.value = data.results
  paperTotal.value = data.count
  if (activeTab.value === 'papers') syncActiveQuery()
}

async function loadProjects(page = projectPage.value) {
  projectPage.value = page
  const data = await fetchProjectPage({ page, page_size: pageSize, search: projectKeyword.value.trim() || undefined })
  projects.value = data.results
  projectTotal.value = data.count
  if (activeTab.value === 'projects') syncActiveQuery()
}

async function loadPatents(page = patentPage.value) {
  patentPage.value = page
  const data = await fetchPatentPage({ page, page_size: pageSize, search: patentKeyword.value.trim() || undefined })
  patents.value = data.results
  patentTotal.value = data.count
  if (activeTab.value === 'patents') syncActiveQuery()
}

async function loadAwards(page = awardPage.value) {
  awardPage.value = page
  const data = await fetchAwardPage({ page, page_size: pageSize, search: awardKeyword.value.trim() || undefined })
  awards.value = data.results
  awardTotal.value = data.count
  if (activeTab.value === 'awards') syncActiveQuery()
}

watch(activeTab, async (tab) => {
  filtersExpanded.value = false
  syncActiveQuery()
  if (tab === 'projects' && !projects.value.length) await loadProjects(1)
  if (tab === 'patents' && !patents.value.length) await loadPatents(1)
  if (tab === 'awards' && !awards.value.length) await loadAwards(1)
})

onMounted(async () => {
  const [paperData, projectData, patentData, awardData, statData] = await Promise.allSettled([
    loadPapers(paperPage.value),
    loadProjects(projectPage.value),
    loadPatents(patentPage.value),
    loadAwards(awardPage.value),
    fetchPublicationStats(),
  ])
  if (statData.status === 'fulfilled') stats.value = statData.value
  void paperData
  void projectData
  void patentData
  void awardData
})
</script>

<style scoped>
.page-section {
  padding-top: 34px;
  background: var(--surface-portal);
}

.output-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.stats-panel,
.output-main {
  border-color: rgba(31, 61, 43, 0.1);
  box-shadow: none;
}

.stats-panel {
  position: relative;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  align-self: start;
  gap: 0;
  overflow: hidden;
  padding: 16px 18px 13px;
  background: linear-gradient(90deg, #fff, rgba(245, 239, 227, 0.38));
}

.stats-panel::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 88px;
  height: 3px;
  background: linear-gradient(90deg, var(--color-cau-green) 0 72%, var(--color-cau-gold) 72% 100%);
  content: "";
}

.stats-panel > div {
  border-left: 1px solid var(--color-line);
  padding: 2px 18px;
}

.stats-panel > div:first-child {
  border-left: 0;
  padding-left: 0;
}

.stats-panel strong,
.stats-panel span {
  display: block;
}

.stats-panel strong {
  color: var(--color-cau-green);
  font-size: 22px;
}

.stats-panel .result-stat-2 strong { color: var(--color-cau-wisdom-blue); }
.stats-panel .result-stat-3 strong { color: var(--color-cau-green-dark); }
.stats-panel .result-stat-4 strong { color: var(--color-cau-gold); }

.stats-panel span {
  color: var(--color-muted);
  font-size: 13px;
}

@media (max-width: 640px) {
  .stats-panel {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px 0;
  }

  .stats-panel > div:nth-child(3) {
    border-left: 0;
    padding-left: 0;
  }
}

.output-main {
  padding: 0;
  overflow: hidden;
}

.result-tabs {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  border-bottom: 1px solid var(--color-line);
  padding: 12px 16px 0;
  scrollbar-width: none;
}

.result-tabs button {
  flex: 0 0 auto;
  border: 0;
  border-bottom: 2px solid transparent;
  padding: 12px 16px;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
  font-weight: 700;
}

.result-tabs button.active {
  color: var(--color-cau-green);
}

.result-tabs .tab-papers.active { border-bottom-color: var(--color-cau-green); }
.result-tabs .tab-projects.active { border-bottom-color: var(--color-cau-wisdom-blue); color: var(--color-cau-wisdom-blue); }
.result-tabs .tab-patents.active { border-bottom-color: var(--color-cau-green-dark); color: var(--color-cau-green-dark); }
.result-tabs .tab-awards.active { border-bottom-color: var(--color-cau-gold); color: var(--color-cau-gold); }

.result-block {
  padding: 24px;
}

.block-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 14px;
}

.block-heading h2 {
  margin: 0 0 5px;
  color: var(--color-deep-green);
  font-size: 24px;
}

.block-heading p {
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.mobile-filter-toggle {
  display: none;
}

.result-tools {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 150px 82px;
  gap: 10px;
  margin-bottom: 14px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  padding: 10px;
  background: var(--color-panel);
}

.result-tools.two {
  grid-template-columns: minmax(0, 1fr) 82px;
}

.result-tools input,
.result-tools select,
.result-tools button {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 40px;
  padding: 0 12px;
  background: #fff;
  color: var(--color-text);
  font: inherit;
}

.result-tools button {
  border-color: var(--color-cau-green);
  background: var(--color-cau-green);
  color: #fff;
  cursor: pointer;
  font-weight: 700;
}

.paper-row {
  display: grid;
  grid-template-columns: 62px minmax(0, 1fr);
  gap: 16px;
  border-top: 1px solid var(--color-line);
  padding: 16px 0;
  color: inherit;
}

.paper-row time {
  align-self: start;
  border-left: 2px solid var(--color-cau-gold);
  border-radius: 2px;
  padding: 5px 10px;
  background: var(--color-eco-green);
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
  text-align: center;
}

.paper-row h3,
.simple-card h3 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 650;
  line-height: 1.45;
  overflow-wrap: anywhere;
}

.paper-row > div,
.simple-card > div { min-width: 0; }

.paper-row:hover h3,
.simple-card:hover h3 {
  color: var(--color-cau-green);
}

.authors,
.abstract,
.simple-card p {
  margin: 7px 0 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

.abstract {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.meta-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.meta-line span {
  padding: 0;
  color: var(--color-blue-gray);
  font-size: 12px;
  font-weight: 500;
}

.simple-card p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.meta-line span + span::before {
  margin-right: 8px;
  color: var(--color-border);
  content: "·";
}

.simple-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 290px;
  gap: 20px;
  border-top: 1px solid var(--color-line);
  padding: 16px 0;
  color: inherit;
}

.project-card,
.patent-card,
.award-card {
  position: relative;
  padding-left: 14px;
}

.project-card::before,
.patent-card::before,
.award-card::before {
  position: absolute;
  top: 20px;
  bottom: 20px;
  left: 0;
  width: 2px;
  border-radius: 2px;
  content: "";
}

.project-card::before { background: var(--color-cau-wisdom-blue); }
.patent-card::before { background: var(--color-cau-green-dark); }
.award-card::before { background: var(--color-cau-gold); }

.simple-card dl {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 0;
}

.project-card dl {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.simple-card dt,
.simple-card dd {
  margin: 0;
}

.simple-card dt {
  color: var(--color-muted);
  font-size: 12px;
}

.simple-card dd {
  margin-top: 3px;
  color: var(--color-text);
  font-size: 13px;
  font-weight: 650;
  line-height: 1.45;
}

.empty-note {
  color: var(--color-muted);
  font-size: 14px;
}

@media (max-width: 900px) {
  .output-layout,
  .simple-card {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stats-panel {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0;
    padding: 10px 8px;
  }

  .stats-panel > div,
  .stats-panel > div:nth-child(3) {
    border-left: 1px solid var(--color-line);
    padding: 0 8px;
  }

  .stats-panel > div:first-child {
    border-left: 0;
  }

  .stats-panel strong {
    font-size: 19px;
  }

  .stats-panel span {
    font-size: 11px;
    white-space: nowrap;
  }

  .result-tabs {
    padding-right: 10px;
    padding-left: 10px;
  }

  .result-tabs button {
    min-height: var(--control-touch);
    padding: 10px 13px;
  }

  .result-block {
    padding: 18px 16px;
  }

  .block-heading {
    align-items: center;
  }

  .block-heading h2 {
    font-size: 21px;
  }

  .mobile-filter-toggle {
    display: inline-flex;
    min-height: 38px;
    flex: 0 0 auto;
    align-items: center;
    border: 1px solid rgba(0, 135, 60, 0.25);
    border-radius: var(--radius-sm);
    padding: 0 11px;
    background: #fff;
    color: var(--color-cau-green);
    font-size: 13px;
    font-weight: 650;
  }

  .result-tools.mobile-collapsed {
    display: none;
  }

  .result-tools,
  .result-tools.two,
  .paper-row {
    grid-template-columns: 1fr;
  }

  .paper-row time {
    width: fit-content;
  }

  .simple-card dl,
  .project-card dl {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
