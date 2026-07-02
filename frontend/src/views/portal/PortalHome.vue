<template>
  <PortalLayout>
    <section class="hero" :style="heroBackgroundStyle">
      <div class="container hero-inner">
        <div class="hero-copy">
          <p class="section-kicker">{{ siteSubtitle }}</p>
          <h1>{{ siteName }}</h1>
          <p class="hero-lead">{{ heroLead }}</p>
          <p class="hero-text">
            {{ siteDescription }}
          </p>
          <div class="hero-actions">
            <RouterLink class="primary-action" to="/research">研究方向</RouterLink>
            <RouterLink class="secondary-action" to="/dashboard">进入内部平台</RouterLink>
          </div>
        </div>
      </div>
    </section>
    <section class="page-section intro-section">
      <div class="container intro-grid">
        <SectionHeader
          kicker="课题组简介"
          :title="introTitle"
          :description="introDescription"
        />
        <div class="intro-facts">
          <div v-for="item in facts" :key="item.label">
            <strong>{{ item.value }}</strong>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-section research-section">
      <div class="container">
        <SectionHeader kicker="研究方向" :title="researchSectionTitle" :description="researchSectionDescription" />
        <div v-if="researchFlowItems.length" class="research-flow" aria-label="研究关键词">
          <span v-for="item in researchFlowItems" :key="item">{{ item }}</span>
        </div>
        <div v-if="displayResearchDirections.length" class="research-grid">
          <RouterLink v-for="item in displayResearchDirections" :key="item.title" class="card research-card" :to="item.to">
            <component :is="item.icon" />
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
            <div v-if="item.tags.length" class="research-tags">
              <span v-for="tag in item.tags" :key="tag">{{ tag }}</span>
            </div>
          </RouterLink>
        </div>
        <RouterLink v-if="displayResearchDirections.length" class="section-link" to="/research">查看全部研究方向</RouterLink>
      </div>
    </section>

    <section class="page-section publication-section">
      <div class="container publication-grid">
        <div>
          <SectionHeader kicker="科研成果" title="近期进展" description="论文、项目、专利和获奖成果统一纳入门户展示，首页按门户内容排序展示近期代表进展。" />
          <div class="stats-row">
            <div v-for="item in displayStats" :key="item.label">
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>
        <div class="latest-paper-panel">
          <RouterLink v-for="item in displayAchievements" :key="`${item.type}-${item.id}`" class="paper-compact" :to="item.to">
            <time>{{ item.badge }}</time>
            <div>
              <h3>{{ item.title }}</h3>
              <p>{{ item.source }}</p>
              <span>查看详情</span>
            </div>
          </RouterLink>
          <div v-if="!displayAchievements.length" class="empty-inline">暂无公开成果。</div>
          <RouterLink class="section-link compact" to="/publications">查看全部成果</RouterLink>
        </div>
      </div>
    </section>

    <section class="page-section team-section">
      <div class="container">
        <SectionHeader kicker="团队成员" title="团队成员" description="课题组由导师、博士研究生、硕士研究生和毕业学生共同组成，围绕资源环境与生态过程开展协同研究。" />
        <div class="member-grid">
          <RouterLink v-for="member in displayMembers" :key="member.name" class="card member-card" :to="member.to">
            <img :src="member.avatar" :alt="member.name" />
            <h3>{{ member.name }}</h3>
            <span class="status-tag normal">{{ member.role }}</span>
            <p>{{ member.focus }}</p>
          </RouterLink>
        </div>
        <div v-if="!displayMembers.length" class="empty-inline">暂无公开团队成员。</div>
        <RouterLink class="section-link" to="/team">查看团队成员</RouterLink>
      </div>
    </section>

    <section class="page-section news-section">
      <div class="container">
        <SectionHeader kicker="新闻活动" title="新闻活动" description="记录田间采样、学术交流、实验培训与组内科研动态。" />
        <div class="news-grid">
          <RouterLink v-for="item in displayNews" :key="item.title" class="card news-card" :to="`/news/${item.slug}`">
            <img v-if="item.image" :src="item.image" :alt="item.title" />
            <div v-else class="news-image-placeholder">暂无封面</div>
            <div>
              <span>{{ item.date }} · {{ item.category }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
            </div>
          </RouterLink>
        </div>
        <div v-if="!displayNews.length" class="empty-inline">暂无新闻活动。</div>
        <RouterLink class="section-link" to="/news">查看新闻活动</RouterLink>
      </div>
    </section>

    <section class="join-section">
      <div class="container join-card">
        <div>
          <p class="section-kicker">加入我们</p>
          <h2>{{ contactTitle }}</h2>
          <p>{{ contactDescription }}</p>
        </div>
        <a :href="`mailto:${contactEmail}`">联系实验室</a>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Cpu, DataAnalysis, MostlyCloudy, Orange, SetUp, WindPower } from '@element-plus/icons-vue'

import SectionHeader from '../../components/SectionHeader.vue'
import PortalLayout from '../../layouts/PortalLayout.vue'
import {
  fetchMembers,
  fetchContactInfo,
  fetchNews,
  fetchAwards,
  fetchPatents,
  fetchPublicationStats,
  fetchPublications,
  fetchProjects,
  fetchResearchDirections,
  fetchSiteSetting,
  type Award,
  type ContactInfo,
  type Member,
  type NewsArticle,
  type Patent,
  type Publication,
  type PublicationStats,
  type Project,
  type ResearchDirection,
  type SiteSetting,
} from '../../api/publicPortal'

const apiResearchDirections = ref<ResearchDirection[]>([])
const apiMembers = ref<Member[]>([])
const apiNews = ref<NewsArticle[]>([])
const apiPapers = ref<Publication[]>([])
const apiProjects = ref<Project[]>([])
const apiPatents = ref<Patent[]>([])
const apiAwards = ref<Award[]>([])
const apiStats = ref<PublicationStats | null>(null)
const siteSetting = ref<Partial<SiteSetting>>({})
const contactInfo = ref<Partial<ContactInfo>>({})
const achievementsReady = ref(false)

type HomeAchievement = {
  id: number
  type: 'paper' | 'project' | 'patent' | 'award'
  title: string
  source: string
  badge: string
  to: string
  sortOrder: number
  dateRank: number
}

const siteName = computed(() => siteSetting.value.site_name || '中农雨磷')
const siteSubtitle = computed(() => siteSetting.value.site_subtitle || '中国农业大学资源与环境学院')
const heroLead = computed(() => siteSetting.value.keywords || '聚焦微生物生态、有机废弃物资源转化与高值产品开发')
const siteDescription = computed(() => siteSetting.value.description || '课题组面向农业绿色发展与资源环境治理需求，围绕有机废弃物资源化、养分循环和土壤生态过程开展基础研究、技术研发与应用评价。')
const introTitle = computed(() => siteSetting.value.footer_text ? '面向农业绿色发展与资源环境治理' : '把农业废弃物转化为可持续生态资源')
const introDescription = computed(() => siteSetting.value.footer_text || '中农雨磷以团队协作为基础，连接微生物生态机制、有机废弃物转化、产品开发和田间应用评价，推动农业废弃物从环境负担转化为生态资源。')
const contactTitle = computed(() => contactInfo.value.title || '欢迎对微生物生态与农业资源循环感兴趣的同学加入')
const contactDescription = computed(() => contactInfo.value.content || '长期欢迎具有环境科学、生态学、农学、微生物学、资源利用等背景的同学参与科研训练、硕士和博士研究。')
const contactEmail = computed(() => contactInfo.value.email || siteSetting.value.contact_email || 'weiyq2019@cau.edu.cn')
const researchSectionTitle = computed(() => (apiResearchDirections.value.length ? '研究方向' : '研究方向待维护'))
const researchSectionDescription = computed(() => {
  const summaries = apiResearchDirections.value
    .map((item) => item.summary)
    .filter(Boolean)
  return summaries[0] || '研究方向内容可在内部平台“门户内容”中维护，首页会实时同步公开展示。'
})
const heroBackgroundStyle = computed(() => {
  const layers = [
    'linear-gradient(90deg, #f8f7f2 0%, #f8f7f2 38%, rgba(248, 247, 242, 0.86) 50%, rgba(248, 247, 242, 0.24) 72%, rgba(248, 247, 242, 0.02) 100%)',
    'linear-gradient(180deg, rgba(234, 245, 238, 0.34), rgba(255, 255, 255, 0.08))',
  ]
  layers.push(`url("${siteSetting.value.hero_image || '/default-hero.svg'}")`)
  return {
    backgroundImage: layers.join(', '),
  }
})

const facts = computed(() => [
  { value: `${apiResearchDirections.value.length}`, label: '研究方向' },
  { value: apiStats.value ? `${apiStats.value.publications}` : '论文', label: '论文成果' },
  { value: apiStats.value ? `${apiStats.value.projects + apiStats.value.patents}` : '项目/专利', label: '项目与专利' },
])

const displayResearchDirections = computed(() => {
  if (!apiResearchDirections.value.length) return []
  const icons = [Orange, WindPower, MostlyCloudy, DataAnalysis, Cpu, SetUp]
  return apiResearchDirections.value.slice(0, 6).map((item, index) => ({
    title: item.title,
    description: item.summary || '研究方向简介待补充。',
    to: `/research/${item.slug}`,
    icon: icons[index % icons.length],
    tags: splitKeywords(item.keywords).slice(0, 4),
  }))
})

const researchFlowItems = computed(() => {
  const keywords = apiResearchDirections.value.flatMap((item) => splitKeywords(item.keywords))
  return Array.from(new Set(keywords)).slice(0, 6)
})

function splitKeywords(value?: string) {
  return (value || '')
    .split(/[，,、\s/]+/)
    .map((item) => item.trim())
    .filter(Boolean)
}

const displayStats = computed(() => {
  if (!apiStats.value) {
    return [
      { value: '0', label: '公开论文' },
      { value: '0', label: '科研项目' },
      { value: '0', label: '专利成果' },
    ]
  }
  return [
    { value: `${apiStats.value.publications}`, label: '公开论文' },
    { value: `${apiStats.value.projects}`, label: '科研项目' },
    { value: `${apiStats.value.patents}`, label: '专利成果' },
  ]
})

function dateRank(value?: string | null, fallback = 0) {
  if (!value) return fallback
  const parsed = Date.parse(value)
  return Number.isNaN(parsed) ? fallback : parsed
}

function yearRank(year?: number | null) {
  return year ? Date.UTC(year, 0, 1) : 0
}

const displayAchievements = computed(() => {
  if (!achievementsReady.value && !apiPapers.value.length) return []
  const items: HomeAchievement[] = [
    ...apiPapers.value.map((paper) => ({
      id: paper.id,
      type: 'paper' as const,
      badge: '论文',
      title: paper.title,
      source: [paper.journal || paper.authors, paper.year].filter(Boolean).join(' · '),
      to: `/publications/${paper.id}`,
      sortOrder: paper.sort_order ?? 0,
      dateRank: yearRank(paper.year),
    })),
    ...apiProjects.value.map((project) => ({
      id: project.id,
      type: 'project' as const,
      badge: '项目',
      title: project.title,
      source: [project.funding_source || '科研项目', project.status].filter(Boolean).join(' · '),
      to: `/publications/projects/${project.id}`,
      sortOrder: project.sort_order ?? 0,
      dateRank: dateRank(project.start_date),
    })),
    ...apiPatents.value.map((patent) => ({
      id: patent.id,
      type: 'patent' as const,
      badge: '专利',
      title: patent.title,
      source: [patent.patent_number || '专利成果', patent.status].filter(Boolean).join(' · '),
      to: `/publications/patents/${patent.id}`,
      sortOrder: patent.sort_order ?? 0,
      dateRank: dateRank(patent.authorization_date || patent.application_date),
    })),
    ...apiAwards.value.map((award) => ({
      id: award.id,
      type: 'award' as const,
      badge: '获奖',
      title: award.title,
      source: [award.award_level || '获奖成果', award.award_date].filter(Boolean).join(' · '),
      to: `/publications/awards/${award.id}`,
      sortOrder: award.sort_order ?? 0,
      dateRank: dateRank(award.award_date),
    })),
  ]
  if (!items.length) return []
  const typeOrder: HomeAchievement['type'][] = ['paper', 'project', 'patent', 'award']
  const sortOrders = Array.from(new Set(items.map((item) => item.sortOrder))).sort((a, b) => a - b)
  const ordered: HomeAchievement[] = []

  sortOrders.forEach((sortOrder) => {
    const buckets = typeOrder.map((type) =>
      items
        .filter((item) => item.sortOrder === sortOrder && item.type === type)
        .sort((a, b) => b.dateRank - a.dateRank),
    )
    const maxLength = Math.max(...buckets.map((bucket) => bucket.length))
    for (let index = 0; index < maxLength; index += 1) {
      buckets.forEach((bucket) => {
        if (bucket[index]) ordered.push(bucket[index])
      })
    }
  })

  return ordered.slice(0, 4)
})

const displayMembers = computed(() => {
  return apiMembers.value.slice(0, 4).map((member) => ({
    name: member.name,
    role: member.role_label,
    focus: member.research_direction || '农业生态环境过程',
    avatar: member.avatar || '/site-icon.png',
    to: `/team/${member.id}`,
  }))
})

const displayNews = computed(() => {
  return apiNews.value.slice(0, 3).map((item) => ({
    slug: item.slug,
    date: item.event_date || '近期',
    category: item.category?.name || '新闻活动',
    title: item.title,
    summary: item.summary || '新闻摘要待补充。',
    image: item.cover_image || '',
  }))
})

onMounted(async () => {
  const [setting, contact, research, members, news, papers, projects, patents, awards, stats] = await Promise.allSettled([
    fetchSiteSetting(),
    fetchContactInfo(),
    fetchResearchDirections(),
    fetchMembers(),
    fetchNews(),
    fetchPublications({ page_size: 8, ordering: 'sort_order,-year' }),
    fetchProjects({ page_size: 6, ordering: 'sort_order,-start_date' }),
    fetchPatents({ page_size: 6, ordering: 'sort_order,-application_date' }),
    fetchAwards({ page_size: 6, ordering: 'sort_order,-award_date' }),
    fetchPublicationStats(),
  ])
  if (setting.status === 'fulfilled') siteSetting.value = setting.value
  if (contact.status === 'fulfilled') contactInfo.value = contact.value
  if (research.status === 'fulfilled') apiResearchDirections.value = research.value
  if (members.status === 'fulfilled') apiMembers.value = members.value
  if (news.status === 'fulfilled') apiNews.value = news.value
  if (papers.status === 'fulfilled') apiPapers.value = papers.value
  if (projects.status === 'fulfilled') apiProjects.value = projects.value
  if (patents.status === 'fulfilled') apiPatents.value = patents.value
  if (awards.status === 'fulfilled') apiAwards.value = awards.value
  achievementsReady.value = true
  if (stats.status === 'fulfilled') apiStats.value = stats.value
})
</script>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid rgba(31, 61, 43, 0.08);
  color: var(--color-text);
  background-color: var(--color-rice);
  background-position: center right;
  background-size: cover;
  background-repeat: no-repeat;
}

.hero::before {
  position: absolute;
  top: 0;
  bottom: 0;
  left: max(20px, calc((100vw - var(--container)) / 2));
  width: min(720px, calc(100vw - 40px));
  content: "";
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.34), rgba(255, 255, 255, 0)),
    repeating-linear-gradient(135deg, rgba(0, 135, 60, 0.045) 0 1px, transparent 1px 18px);
  opacity: 0.72;
  mask-image: linear-gradient(90deg, #000, transparent 78%);
}

.hero::after {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 5px;
  content: "";
  background: linear-gradient(90deg, var(--color-cau-green), rgba(0, 135, 60, 0.42), rgba(166, 120, 78, 0.28), transparent);
}

.hero-inner {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: minmax(0, 720px);
  align-items: center;
  gap: 70px;
  min-height: 438px;
  padding: 68px 0 58px;
}

.hero-copy {
  position: relative;
  z-index: 2;
  max-width: 680px;
  border-left: 0;
  padding-left: 0;
}

.hero-copy::before {
  display: block;
  width: 54px;
  height: 3px;
  margin-bottom: 22px;
  border-radius: 999px;
  background: var(--color-cau-green);
  content: "";
}

.hero-copy h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(42px, 4.6vw, 56px);
  font-weight: 650;
  line-height: 1.06;
  letter-spacing: 0;
}

.hero-lead {
  max-width: 650px;
  margin: 20px 0 0;
  color: var(--color-deep-green);
  font-size: clamp(20px, 2vw, 25px);
  font-weight: 600;
  line-height: 1.42;
}

.hero-text {
  max-width: 620px;
  margin: 15px 0 0;
  color: rgba(47, 52, 55, 0.72);
  font-size: 17px;
  line-height: 1.85;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 28px;
}

.primary-action,
.secondary-action {
  padding: 11px 22px;
}

.hero .section-kicker {
  color: var(--color-cau-green);
}

.intro-grid,
.publication-grid {
  display: grid;
  grid-template-columns: minmax(240px, 0.38fr) minmax(0, 1fr);
  gap: 34px;
  align-items: start;
}

.intro-grid {
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.48fr);
  gap: 52px;
}

.publication-section,
.news-section {
  background: var(--color-rice);
}

.page-section {
  border-top: 1px solid rgba(31, 61, 43, 0.08);
}

.intro-section {
  position: relative;
  margin-top: -1px;
  padding-top: 54px;
  padding-bottom: 54px;
  background: var(--color-white);
}

.intro-section::before {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 1px;
  content: "";
  background: var(--color-border);
}

.intro-section :deep(.section-header h2) {
  color: var(--color-deep-green);
}

.intro-section :deep(.section-header p:last-child) {
  color: var(--color-muted);
}

.intro-section .section-kicker {
  color: var(--color-cau-green);
}

.intro-facts,
.stats-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
  border-top: 1px solid var(--color-border);
}

.stats-row {
  grid-template-columns: repeat(3, 1fr);
  border-top-color: rgba(31, 61, 43, 0.14);
}

.intro-facts div,
.stats-row div {
  border-left: 0;
  border-bottom: 1px solid var(--color-border);
  padding: 12px 0;
  background: transparent;
}

.stats-row div {
  border-bottom: 0;
  border-left: 2px solid rgba(0, 135, 60, 0.52);
  padding: 12px 0 12px 18px;
}

.intro-facts strong,
.stats-row strong {
  display: block;
  color: var(--color-cau-green);
  font-size: 32px;
  font-weight: 650;
  line-height: 1;
}

.intro-facts strong {
  color: var(--color-cau-green);
}

.intro-facts span,
.stats-row span {
  color: var(--color-muted);
  font-size: 14px;
}

.intro-facts span {
  color: var(--color-muted);
}

.research-section,
.team-section {
  background: var(--color-soft-gray);
}

.research-section {
  padding-top: 64px;
}

.publication-section {
  background: var(--color-white);
}

.team-section {
  background:
    linear-gradient(180deg, rgba(234, 245, 238, 0.72), rgba(245, 247, 246, 0.96)),
    var(--color-eco-green);
}

.news-section {
  background: var(--color-rice);
}

.research-grid,
.news-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  border: 0;
  background: transparent;
}

.research-grid {
  margin-top: 22px;
}

.research-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: -2px 0 22px;
}

.research-flow span {
  position: relative;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: 999px;
  padding: 9px 14px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 600;
}

.research-flow span:not(:last-child)::after {
  margin-left: 10px;
  color: var(--color-cau-green);
  content: "→";
}

.research-card,
.latest-paper-panel,
.member-card {
  border: 0;
  border-radius: 0;
  padding: 22px;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}

.latest-paper-panel {
  display: grid;
  gap: 8px;
  border-left: 0;
  padding: 0;
  background: transparent;
}

.research-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  min-height: 172px;
  background: #fff;
}

.research-card:hover,
.latest-paper-panel:hover,
.member-card:hover,
.news-card:hover {
  transform: none;
}

.research-card svg {
  width: 28px;
  height: 28px;
  border: 0;
  border-radius: 0;
  padding: 0;
  background: transparent;
  color: var(--color-cau-green);
}

.research-card h3,
.member-card h3,
.news-card h3 {
  margin: 12px 0 7px;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.research-card p,
.member-card p,
.news-card p {
  margin: 0;
  color: var(--color-muted);
  line-height: 1.7;
}

.research-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
  margin-top: 16px;
}

.research-tags span {
  border: 1px solid rgba(0, 135, 60, 0.14);
  border-radius: 999px;
  padding: 4px 9px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 12px;
  font-weight: 650;
}

.paper-compact {
  display: grid;
  grid-template-columns: 58px 1fr;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  color: inherit;
  cursor: pointer;
}

.paper-compact:hover h3 {
  color: var(--color-cau-green);
}

.paper-compact time {
  align-self: start;
  border-radius: 999px;
  padding: 4px 9px;
  background: var(--color-eco-green);
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.paper-compact h3 {
  display: -webkit-box;
  margin: 0 0 6px;
  overflow: hidden;
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 650;
  line-height: 1.48;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.paper-compact p {
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  border: 0;
}

.member-card {
  display: grid;
  grid-template-columns: 58px 1fr;
  gap: 15px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: #fff;
}

.member-card img {
  width: 58px;
  height: 58px;
  border: 1px solid var(--color-line);
  border-radius: 16px;
  object-fit: cover;
}

.member-card p {
  margin-top: 8px;
  font-size: 14px;
}

.news-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #fff;
  color: inherit;
  box-shadow: none;
}

.news-card img {
  width: 100%;
  aspect-ratio: 16 / 8.5;
  object-fit: cover;
  filter: saturate(0.92);
}

.news-image-placeholder {
  display: grid;
  place-items: center;
  width: 100%;
  aspect-ratio: 16 / 8.5;
  background: var(--color-eco-green);
  color: var(--color-muted);
  font-size: 14px;
}

.news-card div {
  padding: 15px 16px 17px;
}

.news-card span {
  color: var(--color-muted);
  font-size: 13px;
}

.news-card h3 {
  min-height: auto;
}

.section-link {
  display: inline-flex;
  margin-top: 22px;
  color: var(--color-cau-green);
  font-weight: 700;
}

.section-link.compact {
  margin-top: 14px;
}

.empty-inline {
  border: 1px dashed rgba(31, 61, 43, 0.16);
  border-radius: var(--radius-sm);
  padding: 18px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--color-muted);
  font-size: 14px;
}

.join-section {
  padding: 0 0 72px;
  border-top: 1px solid rgba(31, 61, 43, 0.08);
  background: var(--color-rice);
}

.join-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: var(--radius-lg);
  padding: 40px;
  background:
    linear-gradient(90deg, var(--color-cau-green), #0a7638),
    var(--color-cau-green);
  box-shadow: none;
}

.join-card h2 {
  margin: 0;
  color: #fff;
  font-size: 30px;
  font-weight: 650;
}

.join-card p:last-child {
  max-width: 760px;
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.72);
}

.join-card a {
  flex: 0 0 auto;
  border-radius: var(--radius-sm);
  padding: 11px 20px;
  background: #fff;
  color: var(--color-deep-green);
  font-weight: 600;
}

.join-card .section-kicker {
  color: rgba(255, 255, 255, 0.74);
}

@media (max-width: 980px) {
  .hero {
    background-position: center;
  }

  .hero::before {
    left: 20px;
    width: calc(100vw - 40px);
    opacity: 0.36;
  }

  .hero-inner,
  .intro-grid,
  .publication-grid {
    grid-template-columns: 1fr;
  }

  .hero-inner {
    min-height: auto;
    padding: 58px 0 48px;
  }

  .research-grid,
  .news-grid,
  .member-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .research-grid,
  .news-grid,
  .member-grid,
  .intro-facts,
  .stats-row {
    grid-template-columns: 1fr;
  }

  .member-card {
    grid-template-columns: 56px 1fr;
  }

  .join-card {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>


