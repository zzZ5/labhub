<template>
  <PortalLayout>
    <section class="hero">
      <div class="container hero-inner">
        <div class="hero-copy">
          <p class="section-kicker">中国农业大学资源与环境学院</p>
          <h1>中农雨磷</h1>
          <p class="hero-lead">聚焦微生物生态、有机废弃物资源转化与高值产品开发</p>
          <p class="hero-text">
            课题组面向农业绿色发展与资源环境治理需求，围绕有机废弃物资源化、养分循环和土壤生态过程开展基础研究、技术研发与应用评价。
          </p>
          <div class="hero-actions">
            <RouterLink class="primary-action" to="/research">研究方向</RouterLink>
            <RouterLink class="secondary-action" to="/dashboard">进入内部平台</RouterLink>
          </div>
        </div>
      </div>
    </section>
    <section class="hero-strip" aria-label="研究链条">
      <div class="container hero-strip-grid">
        <span v-for="item in heroScenes" :key="item.title">
          <strong>{{ item.title }}</strong>
          {{ item.value }}
        </span>
      </div>
    </section>

    <section class="page-section intro-section">
      <div class="container intro-grid">
        <SectionHeader
          kicker="课题组简介"
          title="把农业废弃物转化为可持续生态资源"
          description="中农雨磷以团队协作为基础，连接微生物生态机制、有机废弃物转化、产品开发和田间应用评价，推动农业废弃物从环境负担转化为生态资源。"
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
        <SectionHeader kicker="研究方向" title="从过程机制到资源化应用" description="围绕农业有机废弃物转化，连接微生物机制、堆肥腐殖化、养分循环、产品开发和田间生态评价。" />
        <div class="research-flow" aria-label="研究链条">
          <span>农业有机废弃物</span>
          <span>微生物过程</span>
          <span>养分循环</span>
          <span>高值产品</span>
          <span>田间生态评价</span>
        </div>
        <div class="research-grid">
          <article v-for="item in displayResearchDirections" :key="item.title" class="card research-card">
            <component :is="item.icon" />
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </article>
        </div>
        <RouterLink class="section-link" to="/research">查看全部研究方向</RouterLink>
      </div>
    </section>

    <section class="page-section publication-section">
      <div class="container publication-grid">
        <div>
          <SectionHeader kicker="科研成果" title="近期发表" description="组内论文统一纳入成果统计，首页展示近期发表的研究进展。" />
          <div class="stats-row">
            <div v-for="item in displayStats" :key="item.label">
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>
        <div class="latest-paper-panel">
          <RouterLink v-for="paper in displayPapers" :key="paper.title" class="paper-compact" :to="`/publications/${paper.id}`">
            <time>{{ paper.year }}</time>
            <div>
              <h3>{{ paper.title }}</h3>
              <p>{{ paper.source }}</p>
              <span>查看详情</span>
            </div>
          </RouterLink>
          <RouterLink class="section-link compact" to="/publications">查看全部论文</RouterLink>
        </div>
      </div>
    </section>

    <section class="page-section team-section">
      <div class="container">
        <SectionHeader kicker="团队成员" title="团队成员" description="课题组由导师、博士研究生、硕士研究生和毕业学生共同组成，围绕资源环境与生态过程开展协同研究。" />
        <div class="member-grid">
          <article v-for="member in displayMembers" :key="member.name" class="card member-card">
            <img :src="member.avatar" :alt="member.name" />
            <h3>{{ member.name }}</h3>
            <span class="status-tag normal">{{ member.role }}</span>
            <p>{{ member.focus }}</p>
          </article>
        </div>
        <RouterLink class="section-link" to="/team">查看团队成员</RouterLink>
      </div>
    </section>

    <section class="page-section news-section">
      <div class="container">
        <SectionHeader kicker="新闻活动" title="新闻活动" description="记录田间采样、学术交流、实验培训与组内科研动态。" />
        <div class="news-grid">
          <RouterLink v-for="item in displayNews" :key="item.title" class="card news-card" :to="`/news/${item.slug}`">
            <img :src="item.image" :alt="item.title" />
            <div>
              <span>{{ item.date }} · {{ item.category }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
            </div>
          </RouterLink>
        </div>
        <RouterLink class="section-link" to="/news">查看新闻活动</RouterLink>
      </div>
    </section>

    <section class="join-section">
      <div class="container join-card">
        <div>
          <p class="section-kicker">加入我们</p>
          <h2>欢迎对微生物生态与农业资源循环感兴趣的同学加入</h2>
          <p>长期欢迎具有环境科学、生态学、农学、微生物学、资源利用等背景的同学参与科研训练、硕士和博士研究。</p>
        </div>
        <a href="mailto:weiyq2019@cau.edu.cn">联系实验室</a>
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
  fetchNews,
  fetchPublicationStats,
  fetchPublications,
  fetchResearchDirections,
  type Member,
  type NewsArticle,
  type Publication,
  type PublicationStats,
  type ResearchDirection,
} from '../../api/publicPortal'

const facts = [
  { value: '3', label: '核心研究主线' },
  { value: '6', label: '长期研究方向' },
  { value: '多类', label: '论文项目与专利成果' },
]

const heroScenes = [
  { title: '田间', value: '土壤健康与生态效应' },
  { title: '过程', value: '堆肥转化与腐殖化调控' },
  { title: '机制', value: '功能微生物与养分循环' },
]

const apiResearchDirections = ref<ResearchDirection[]>([])
const apiMembers = ref<Member[]>([])
const apiNews = ref<NewsArticle[]>([])
const apiPapers = ref<Publication[]>([])
const apiStats = ref<PublicationStats | null>(null)
const papersReady = ref(false)

const fallbackResearchDirections = [
  { title: '微生物生态', description: '解析有机废弃物转化、土壤生态过程中的关键微生物群落与功能机制。', icon: DataAnalysis },
  { title: '有机废弃物资源转化', description: '面向农业和食品加工废弃物，研究低碳转化、稳定化和资源化利用路径。', icon: Orange },
  { title: '高值产品开发', description: '围绕有机肥、水溶肥和生态产品，推进从工艺优化到应用评价的转化研究。', icon: SetUp },
  { title: '堆肥腐殖化调控', description: '研究堆肥过程中腐殖酸形成、臭气减排和品质提升的过程调控机制。', icon: WindPower },
  { title: '养分循环与土壤健康', description: '评价有机物料还田、养分循环利用及其对土壤生态功能的影响。', icon: MostlyCloudy },
  { title: '农业低碳生态转化', description: '服务农业废弃物低碳处理和绿色农业场景，探索可推广的技术模式。', icon: Cpu },
]

const fallbackStats = [
  { value: '论文', label: '研究成果持续积累' },
  { value: '项目', label: '支撑团队稳定开展研究' },
  { value: '专利', label: '推动技术转化与应用' },
]

const fallbackPapers = [
  { id: 0, year: '2026', title: 'Microbial Necromass Accelerates Humic Acid Formation by Reshaping DOM Transformation Pathways During Composting', source: 'Environmental Research' },
  { id: 1, year: '2026', title: 'Effect of Different Organic-to-inorganic Phosphorus Ratios on Organic Phosphorus Mineralization and Microbial Functions During Composting', source: 'Journal of Environmental Chemical Engineering' },
  { id: 2, year: '2026', title: 'A Compost-Derived Functional Microbial Consortium Fortifies Humification During Bio-Organic Fertilizer Production', source: 'Journal of Environmental Chemical Engineering' },
]

const fallbackMembers = [
  { name: '团队负责人', role: '硕博导师', focus: '统筹微生物生态、有机废弃物资源转化与高值产品开发方向', avatar: '/favicon.svg' },
  { name: '博士研究生', role: '博士生', focus: '围绕功能微生物、堆肥腐殖化与低碳转化机制开展研究', avatar: '/favicon.svg' },
  { name: '硕士研究生', role: '硕士生', focus: '参与有机肥产品开发、养分循环与土壤生态评价', avatar: '/favicon.svg' },
  { name: '毕业学生与合作成员', role: '团队网络', focus: '共同支撑资源利用、生态环境工程和农业应用场景研究', avatar: '/favicon.svg' },
]

const fallbackNews = [
  { slug: 'field-sampling', date: '2026-06-18', category: '田间试验', title: '课题组完成夏季堆肥产品田间施用试验采样', summary: '围绕土壤养分变化、作物生长和环境风险指标开展连续监测。', image: 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=700&q=80' },
  { slug: 'seminar', date: '2026-05-29', category: '学术交流', title: '实验室举办农业废弃物资源化专题组会', summary: '师生围绕腐殖化过程调控和智能监测模型进行讨论。', image: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=700&q=80' },
  { slug: 'training', date: '2026-05-12', category: '实验培训', title: '完成堆肥反应器与气体采样系统操作培训', summary: '面向新进学生开展仪器安全、样品记录和数据归档培训。', image: 'https://images.unsplash.com/photo-1581093588401-fbb62a02f120?auto=format&fit=crop&w=700&q=80' },
]

const displayResearchDirections = computed(() => {
  if (!apiResearchDirections.value.length) return fallbackResearchDirections
  const icons = [Orange, WindPower, MostlyCloudy, DataAnalysis, Cpu, SetUp]
  return apiResearchDirections.value.slice(0, 6).map((item, index) => ({
    title: item.title,
    description: item.summary || '研究方向简介待补充。',
    icon: icons[index % icons.length],
  }))
})

const displayStats = computed(() => {
  if (!apiStats.value) return fallbackStats
  const looksLikeSeedData = apiStats.value.publications < 20 && apiStats.value.patents < 10
  if (looksLikeSeedData) return fallbackStats
  return [
    { value: `${apiStats.value.publications}`, label: '公开论文' },
    { value: `${apiStats.value.projects}`, label: '科研项目' },
    { value: `${apiStats.value.patents}`, label: '专利成果' },
  ]
})

const displayPapers = computed(() => {
  if (!papersReady.value && !apiPapers.value.length) return []
  if (!apiPapers.value.length) return fallbackPapers
  return apiPapers.value.slice(0, 3).map((paper) => ({
    id: paper.id,
    year: `${paper.year}`,
    title: paper.title,
    source: paper.journal || paper.authors,
  }))
})

const displayMembers = computed(() => {
  if (apiMembers.value.length < 2) return fallbackMembers
  return apiMembers.value.slice(0, 4).map((member) => ({
    name: member.name,
    role: member.role_label,
    focus: member.research_direction || '农业生态环境过程',
    avatar: member.avatar || 'https://images.unsplash.com/photo-1560250097-0b93528c311a?auto=format&fit=crop&w=220&q=80',
  }))
})

const displayNews = computed(() => {
  if (!apiNews.value.length) return fallbackNews
  return apiNews.value.slice(0, 3).map((item) => ({
    slug: item.slug,
    date: item.event_date || '近期',
    category: item.category?.name || '新闻活动',
    title: item.title,
    summary: item.summary || '新闻摘要待补充。',
    image: item.cover_image || 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=700&q=80',
  }))
})

onMounted(async () => {
  const [research, members, news, papers, stats] = await Promise.allSettled([
    fetchResearchDirections(),
    fetchMembers(),
    fetchNews(),
    fetchPublications(),
    fetchPublicationStats(),
  ])
  if (research.status === 'fulfilled') apiResearchDirections.value = research.value
  if (members.status === 'fulfilled') apiMembers.value = members.value
  if (news.status === 'fulfilled') apiNews.value = news.value
  if (papers.status === 'fulfilled') apiPapers.value = papers.value
  papersReady.value = true
  if (stats.status === 'fulfilled') apiStats.value = stats.value
})
</script>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid rgba(31, 61, 43, 0.08);
  color: var(--color-text);
  background:
    linear-gradient(90deg, #f8f7f2 0%, #f8f7f2 38%, rgba(248, 247, 242, 0.86) 50%, rgba(248, 247, 242, 0.24) 72%, rgba(248, 247, 242, 0.02) 100%),
    linear-gradient(180deg, rgba(234, 245, 238, 0.34), rgba(255, 255, 255, 0.08)),
    url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1900&q=88") center right / cover no-repeat;
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

.hero-strip {
  position: relative;
  z-index: 2;
  border-top: 0;
  border-bottom: 1px solid var(--color-border);
  background: #fff;
}

.hero-strip-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  margin-top: 0;
  border: 0;
  padding: 15px 0;
}

.hero-strip-grid span {
  display: block;
  min-height: auto;
  border-left: 2px solid rgba(0, 135, 60, 0.28);
  border-right: 0;
  padding: 2px 0 2px 14px;
  background: transparent;
  color: var(--color-muted);
  box-shadow: none;
}

.hero-strip-grid strong {
  display: block;
  margin-bottom: 2px;
  color: var(--color-cau-green);
  font-size: 15px;
  font-weight: 700;
}

.hero-strip-grid span {
  color: var(--color-muted);
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
    background:
      linear-gradient(180deg, rgba(248, 247, 242, 0.98), rgba(234, 245, 238, 0.88)),
      url("https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=86") center / cover no-repeat;
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

  .hero-strip-grid {
    margin-top: 0;
    gap: 10px;
  }

  .hero-strip-grid span:nth-child(2),
  .hero-strip-grid span:nth-child(3) {
    transform: none;
  }

  .hero-strip-grid {
    grid-template-columns: 1fr;
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

