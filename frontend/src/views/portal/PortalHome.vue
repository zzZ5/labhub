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
          kicker="About"
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
        <SectionHeader kicker="Research" title="研究方向" description="从微生物生态机制到有机废弃物转化，再到高值产品开发与田间生态评价，形成完整研究链条。" />
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
          <SectionHeader kicker="Outputs" title="代表成果" description="以论文成果、科研项目、专利转化和学术交流支撑农业资源环境领域的长期积累。" />
          <div class="stats-row">
            <div v-for="item in displayStats" :key="item.label">
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>
        <div class="timeline card">
          <article v-for="paper in displayPapers" :key="paper.title">
            <time>{{ paper.year }}</time>
            <div>
              <h3>{{ paper.title }}</h3>
              <p>{{ paper.source }}</p>
            </div>
          </article>
          <RouterLink class="section-link compact" to="/publications">更多成果</RouterLink>
        </div>
      </div>
    </section>

    <section class="page-section team-section">
      <div class="container">
        <SectionHeader kicker="Team" title="团队成员" description="课题组由导师、博士研究生、硕士研究生和毕业学生共同组成，围绕资源环境与生态过程开展协同研究。" />
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
        <SectionHeader kicker="News" title="新闻活动" description="记录田间采样、学术交流、实验培训与组内科研动态。" />
        <div class="news-grid">
          <article v-for="item in displayNews" :key="item.title" class="card news-card">
            <img :src="item.image" :alt="item.title" />
            <div>
              <span>{{ item.date }} · {{ item.category }}</span>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
            </div>
          </article>
        </div>
        <RouterLink class="section-link" to="/news">查看新闻活动</RouterLink>
      </div>
    </section>

    <section class="join-section">
      <div class="container join-card">
        <div>
          <p class="section-kicker">Join Us</p>
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
  fetchRepresentativePublications,
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
  { year: '方向一', title: '微生物生态与有机废弃物资源化机制研究', source: '围绕功能菌群、物质转化和生态过程开展长期研究' },
  { year: '方向二', title: '农业废弃物低碳转化技术与装备', source: '支撑堆肥、臭气减排、腐殖化和产品品质提升' },
  { year: '方向三', title: '高值产品开发与农业生态应用评价', source: '服务有机肥、水溶肥和资源循环利用场景' },
]

const fallbackMembers = [
  { name: '团队负责人', role: '硕博导师', focus: '统筹微生物生态、有机废弃物资源转化与高值产品开发方向', avatar: '/favicon.svg' },
  { name: '博士研究生', role: '博士生', focus: '围绕功能微生物、堆肥腐殖化与低碳转化机制开展研究', avatar: '/favicon.svg' },
  { name: '硕士研究生', role: '硕士生', focus: '参与有机肥产品开发、养分循环与土壤生态评价', avatar: '/favicon.svg' },
  { name: '毕业学生与合作成员', role: '团队网络', focus: '共同支撑资源利用、生态环境工程和农业应用场景研究', avatar: '/favicon.svg' },
]

const fallbackNews = [
  { date: '2026-06-18', category: '田间试验', title: '课题组完成夏季堆肥产品田间施用试验采样', summary: '围绕土壤养分变化、作物生长和环境风险指标开展连续监测。', image: 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=700&q=80' },
  { date: '2026-05-29', category: '学术交流', title: '实验室举办农业废弃物资源化专题组会', summary: '师生围绕腐殖化过程调控和智能监测模型进行讨论。', image: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=700&q=80' },
  { date: '2026-05-12', category: '实验培训', title: '完成堆肥反应器与气体采样系统操作培训', summary: '面向新进学生开展仪器安全、样品记录和数据归档培训。', image: 'https://images.unsplash.com/photo-1581093588401-fbb62a02f120?auto=format&fit=crop&w=700&q=80' },
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
  if (!apiPapers.value.length) return fallbackPapers
  return apiPapers.value.slice(0, 3).map((paper) => ({
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
    date: item.event_date || '近期',
    category: item.category?.name || '新闻活动',
    title: item.title,
    summary: item.summary || '新闻摘要待补充。',
    image: item.cover_image || 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=700&q=80',
  }))
})

onMounted(async () => {
  const [research, members, news, papers, stats] = await Promise.allSettled([
    fetchResearchDirections(),
    fetchMembers(),
    fetchNews(),
    fetchRepresentativePublications(),
    fetchPublicationStats(),
  ])
  if (research.status === 'fulfilled') apiResearchDirections.value = research.value
  if (members.status === 'fulfilled') apiMembers.value = members.value
  if (news.status === 'fulfilled') apiNews.value = news.value
  if (papers.status === 'fulfilled') apiPapers.value = papers.value
  if (stats.status === 'fulfilled') apiStats.value = stats.value
})
</script>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-text);
  background:
    linear-gradient(180deg, rgba(234, 245, 238, 0.62), rgba(248, 247, 242, 0.96) 58%, rgba(255, 255, 255, 0.98)),
    var(--color-rice);
}

.hero::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  content: "";
  background: var(--color-cau-green);
}

.hero::after {
  position: absolute;
  inset: 4px 0 0 auto;
  display: block;
  width: min(58vw, 860px);
  content: "";
  background: url("https://images.unsplash.com/photo-1492496913980-501348b61469?auto=format&fit=crop&w=1800&q=84") center / cover no-repeat;
  mask-image: linear-gradient(90deg, transparent 0%, rgba(0, 0, 0, 0.35) 28%, #000 72%);
  opacity: 0.38;
}

.hero-inner {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: minmax(0, 760px);
  align-items: center;
  gap: 70px;
  min-height: 430px;
  padding: 70px 0 58px;
}

.hero-copy {
  position: relative;
  z-index: 2;
  max-width: 660px;
  border-left: 4px solid var(--color-cau-green);
  padding-left: 24px;
}

.hero-copy::before {
  display: none;
}

.hero-copy h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(40px, 4.7vw, 58px);
  font-weight: 650;
  line-height: 1.08;
}

.hero-lead {
  max-width: 650px;
  margin: 18px 0 0;
  color: var(--color-deep-green);
  font-size: clamp(20px, 2vw, 25px);
  font-weight: 600;
  line-height: 1.42;
}

.hero-text {
  max-width: 620px;
  margin: 16px 0 0;
  color: var(--color-muted);
  font-size: 17px;
  line-height: 1.85;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 26px;
}

.hero-strip {
  position: relative;
  z-index: 2;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  background: rgba(255, 255, 255, 0.94);
}

.hero-strip-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0;
  margin-top: 0;
  border: 0;
}

.hero-strip-grid span {
  display: block;
  min-height: auto;
  border-right: 1px solid var(--color-border);
  padding: 13px 20px;
  background: transparent;
  color: var(--color-muted);
  box-shadow: none;
}

.hero-strip-grid strong {
  display: block;
  margin-bottom: 4px;
  color: var(--color-cau-green);
  font-size: 16px;
  font-weight: 700;
}

.hero-strip-grid span {
  color: var(--color-muted);
}

.primary-action,
.secondary-action {
  padding: 11px 22px;
}

.hero .secondary-action {
  border-color: rgba(0, 135, 60, 0.34);
  background: #fff;
  color: var(--color-cau-green);
  backdrop-filter: none;
}

.hero .secondary-action:hover {
  border-color: var(--color-cau-green);
  background: var(--color-eco-green);
}

.hero .section-kicker {
  color: var(--color-cau-green);
}

.intro-grid,
.publication-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.48fr);
  gap: 52px;
  align-items: start;
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
  gap: 18px;
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
  margin: -8px 0 20px;
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
.timeline,
.member-card {
  border: 0;
  border-radius: 0;
  padding: 22px;
  box-shadow: none;
}

.timeline {
  border-top: 1px solid rgba(31, 61, 43, 0.14);
  border-bottom: 1px solid rgba(31, 61, 43, 0.14);
  background: transparent;
}

.research-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: #fff;
}

.research-card:hover,
.timeline:hover,
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
.timeline h3,
.member-card h3,
.news-card h3 {
  margin: 12px 0 7px;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.research-card p,
.timeline p,
.member-card p,
.news-card p {
  margin: 0;
  color: var(--color-muted);
}

.timeline article {
  display: grid;
  grid-template-columns: 72px 1fr;
  gap: 20px;
  padding: 18px 0;
  border-bottom: 1px solid rgba(31, 61, 43, 0.12);
}

.timeline time {
  color: var(--color-cau-green);
  font-weight: 700;
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
      linear-gradient(90deg, rgba(255, 255, 255, 0.98), rgba(234, 245, 238, 0.94)),
      var(--color-white);
  }

  .hero::before {
    opacity: 0.18;
  }

  .hero-inner,
  .intro-grid,
  .publication-grid {
    grid-template-columns: 1fr;
  }

  .hero-inner {
    min-height: auto;
  }

  .hero-strip-grid {
    margin-top: 0;
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
