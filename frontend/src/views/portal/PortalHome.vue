<template>
  <PortalLayout>
    <section class="hero">
      <div class="hero-carousel">
        <div
          v-for="(banner, index) in heroBanners"
          :key="`${banner.image}-${index}`"
          class="hero-slide"
          :class="{ active: index === activeBannerIndex }"
          :style="{
            backgroundImage: `url('${banner.image}')`,
            transform: `translateX(${(index - activeBannerIndex) * 100}%)`,
          }"
        ></div>
        <div class="hero-caption">
          <h1>{{ activeHeroTitle }}</h1>
          <span v-if="activeHeroSubtitle">{{ activeHeroSubtitle }}</span>
        </div>
        <div v-if="heroBanners.length > 1" class="hero-controls" aria-label="首页横幅切换">
          <div class="hero-dots">
            <button
              v-for="(_, index) in heroBanners"
              :key="index"
              type="button"
              :aria-label="`切换到第 ${index + 1} 张横幅`"
              :class="{ active: index === activeBannerIndex }"
              @click="activeBannerIndex = index"
            ></button>
          </div>
        </div>
      </div>
    </section>
    <section class="page-section intro-section">
      <div class="container intro-grid">
        <div class="intro-main">
          <div class="intro-heading">
            <span>{{ siteName }}</span>
            <h2>课题组简介</h2>
          </div>
          <div class="intro-body">
            <p>{{ introDescription }}</p>
          </div>
          <div class="intro-actions">
            <RouterLink class="primary-action" to="/research">研究方向</RouterLink>
            <RouterLink class="secondary-action" to="/dashboard">进入内部平台</RouterLink>
          </div>
        </div>
      </div>
    </section>

    <section class="page-section research-section">
      <div class="container">
        <SectionHeader :title="researchSectionTitle" :description="researchSectionDescription" />
        <div v-if="displayResearchDirections.length" class="research-grid">
          <RouterLink v-for="item in displayResearchDirections" :key="item.title" class="card research-card" :to="item.to">
            <component :is="item.icon" />
            <h3>{{ item.title }}</h3>
            <p>{{ item.description }}</p>
          </RouterLink>
        </div>
        <RouterLink v-if="displayResearchDirections.length" class="section-link" to="/research">查看全部研究方向</RouterLink>
      </div>
    </section>

    <section class="page-section publication-section">
      <div class="container publication-grid">
        <div>
          <SectionHeader title="科研成果" description="展示课题组近期公开发表和授权、立项、获奖等成果动态；完整论文、项目、专利与获奖信息可进入科研成果页查看。" />
          <div class="stats-row compact-stats">
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
        <SectionHeader title="团队成员" description="课题组由不同阶段的师生和合作成员共同组成，在日常科研训练、学术交流和项目实践中推进团队协作。" />
        <div class="member-grid">
          <RouterLink v-for="member in displayMembers" :key="member.name" class="card member-card" :to="member.to">
            <img :src="member.avatar" :alt="member.name" />
            <div class="member-info">
              <h3>{{ member.name }}</h3>
              <span>{{ member.role }}</span>
              <p>{{ member.focus }}</p>
            </div>
          </RouterLink>
        </div>
        <div v-if="!displayMembers.length" class="empty-inline">暂无公开团队成员。</div>
        <RouterLink class="section-link" to="/team">查看团队成员</RouterLink>
      </div>
    </section>

    <section class="page-section news-section">
      <div class="container">
        <SectionHeader title="新闻活动" description="发布组内动态、学术交流、科研进展、成果荣誉与招生招聘信息。" />
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
          <h2>加入我们</h2>
          <p>{{ contactDescription }}</p>
        </div>
        <a :href="`mailto:${contactEmail}`">联系实验室</a>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { Cpu, DataAnalysis, MostlyCloudy, Orange, SetUp, WindPower } from '@element-plus/icons-vue'

import SectionHeader from '../../components/SectionHeader.vue'
import PortalLayout from '../../layouts/PortalLayout.vue'
import {
  fetchMembers,
  fetchContactInfo,
  fetchHomeBanners,
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
  type HomeBanner,
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
const apiBanners = ref<HomeBanner[]>([])
const apiPapers = ref<Publication[]>([])
const apiProjects = ref<Project[]>([])
const apiPatents = ref<Patent[]>([])
const apiAwards = ref<Award[]>([])
const apiStats = ref<PublicationStats | null>(null)
const siteSetting = ref<Partial<SiteSetting>>({})
const contactInfo = ref<Partial<ContactInfo>>({})
const achievementsReady = ref(false)
const activeBannerIndex = ref(0)
let bannerTimer: number | undefined

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
const introDescription = computed(() => siteDescription.value)
const contactDescription = computed(() => contactInfo.value.content || '长期欢迎具有环境科学、生态学、农学、微生物学、资源利用等背景的同学参与科研训练、硕士和博士研究。')
const contactEmail = computed(() => contactInfo.value.email || siteSetting.value.contact_email || 'weiyq2019@cau.edu.cn')
const researchSectionTitle = computed(() => (apiResearchDirections.value.length ? '研究方向' : '研究方向待维护'))
const researchSectionDescription = computed(() =>
  apiResearchDirections.value.length
    ? '展示课题组当前公开维护的研究方向，详细内容可进入对应页面查看。'
    : '研究方向内容可在内部平台“门户内容”中维护，首页会实时同步公开展示。',
)
const heroBanners = computed(() => {
  const banners = apiBanners.value
    .filter((item) => item.image)
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
  if (banners.length) return banners
  return [{
    id: 0,
    title: siteName.value,
    subtitle: heroLead.value,
    image: siteSetting.value.hero_image || '/default-hero.svg',
    link: '',
    sort_order: 0,
  }]
})
const activeHeroBanner = computed(() => heroBanners.value[activeBannerIndex.value] || heroBanners.value[0] || {
  title: siteName.value,
  subtitle: heroLead.value,
  image: '',
})
const activeHeroTitle = computed(() => activeHeroBanner.value.title || siteName.value)
const activeHeroSubtitle = computed(() => activeHeroBanner.value.subtitle || heroLead.value)

function startBannerTimer() {
  if (bannerTimer) window.clearInterval(bannerTimer)
  if (heroBanners.value.length <= 1) return
  bannerTimer = window.setInterval(() => {
    showNextBanner()
  }, 5200)
}

function showNextBanner() {
  const length = heroBanners.value.length
  if (length <= 1) return
  activeBannerIndex.value = (activeBannerIndex.value + 1) % length
}

const displayStats = computed(() => {
  if (!apiStats.value) {
    return [
      { value: '0', label: '论文' },
      { value: '0', label: '项目' },
      { value: '0', label: '专利' },
      { value: '0', label: '获奖' },
    ]
  }
  return [
    { value: `${apiStats.value.publications}`, label: '论文' },
    { value: `${apiStats.value.projects}`, label: '项目' },
    { value: `${apiStats.value.patents}`, label: '专利' },
    { value: `${apiStats.value.awards}`, label: '获奖' },
  ]
})

const displayResearchDirections = computed(() => {
  if (!apiResearchDirections.value.length) return []
  const icons = [Orange, WindPower, MostlyCloudy, DataAnalysis, Cpu, SetUp]
  return apiResearchDirections.value.slice(0, 6).map((item, index) => ({
    title: item.title,
    description: item.summary || '研究方向简介待补充。',
    to: `/research/${item.slug}`,
    icon: icons[index % icons.length],
  }))
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
    role: memberIdentity(member),
    focus: member.research_direction || '农业生态环境过程',
    avatar: member.avatar || '/site-icon.png',
    to: `/team/${member.id}`,
  }))
})

function memberIdentity(member: Member) {
  return member.role_label || member.role_type || '团队成员'
}

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
  const [setting, contact, banners, research, members, news, papers, projects, patents, awards, stats] = await Promise.allSettled([
    fetchSiteSetting(),
    fetchContactInfo(),
    fetchHomeBanners(),
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
  if (banners.status === 'fulfilled') apiBanners.value = banners.value
  if (research.status === 'fulfilled') apiResearchDirections.value = research.value
  if (members.status === 'fulfilled') apiMembers.value = members.value
  if (news.status === 'fulfilled') apiNews.value = news.value
  if (papers.status === 'fulfilled') apiPapers.value = papers.value
  if (projects.status === 'fulfilled') apiProjects.value = projects.value
  if (patents.status === 'fulfilled') apiPatents.value = patents.value
  if (awards.status === 'fulfilled') apiAwards.value = awards.value
  achievementsReady.value = true
  if (stats.status === 'fulfilled') apiStats.value = stats.value
  startBannerTimer()
})

watch(
  () => heroBanners.value.length,
  () => {
    activeBannerIndex.value = 0
    startBannerTimer()
  },
)

onUnmounted(() => {
  if (bannerTimer) window.clearInterval(bannerTimer)
})
</script>

<style scoped>
.hero {
  position: relative;
  overflow: hidden;
  padding: 12px 0 22px;
  background: var(--color-rice);
}

.hero-carousel {
  position: relative;
  width: min(var(--container), calc(100% - 40px));
  height: clamp(380px, 39vw, 540px);
  margin: 0 auto;
  overflow: hidden;
  border-radius: 8px;
  background: #eef2ee;
}

.hero-slide {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  opacity: 1;
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  transition: transform 760ms cubic-bezier(0.22, 1, 0.36, 1);
}

.hero-slide::after {
  position: absolute;
  inset: 0;
  content: "";
  background: linear-gradient(180deg, transparent 62%, rgba(31, 61, 43, 0.16));
}

.hero-slide.active {
  z-index: 1;
}

.hero-caption {
  position: absolute;
  bottom: 30px;
  left: clamp(16px, 3vw, 38px);
  z-index: 4;
  max-width: min(360px, calc(100% - 56px));
  color: #fff;
  text-shadow: 0 2px 10px rgba(18, 38, 26, 0.38);
}

.hero-caption h1 {
  margin: 0;
  font-size: clamp(15px, 1.35vw, 21px);
  font-weight: 650;
  line-height: 1.22;
}

.hero-caption span {
  display: block;
  max-width: 340px;
  margin-top: 5px;
  font-size: clamp(10px, 0.75vw, 12px);
  font-weight: 500;
  line-height: 1.55;
}

.hero-controls {
  position: absolute;
  bottom: 14px;
  left: 50%;
  z-index: 4;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translateX(-50%);
}

.hero-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
}

.hero-dots button {
  width: 6px;
  height: 6px;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.58);
  cursor: pointer;
  transition: width 0.2s ease, background 0.2s ease;
}

.hero-dots button.active {
  width: 18px;
  background: #fff;
}

.primary-action,
.secondary-action {
  min-height: 42px;
  padding: 10px 20px;
}

.intro-actions .primary-action {
  box-shadow: none;
}

.intro-actions .secondary-action {
  background: rgba(255, 255, 255, 0.72);
}

.intro-grid,
.publication-grid {
  display: grid;
  grid-template-columns: minmax(260px, 0.34fr) minmax(0, 1fr);
  gap: 42px;
  align-items: start;
}

.intro-grid {
  position: relative;
  display: block;
  width: min(var(--container), calc(100% - 40px));
}

.intro-main {
  position: relative;
  display: grid;
  grid-template-columns: minmax(200px, 0.32fr) minmax(0, 1fr);
  gap: 42px;
  min-width: 0;
  border-top: 1px solid rgba(31, 61, 43, 0.12);
  border-bottom: 1px solid rgba(31, 61, 43, 0.08);
  padding: 34px 0 32px;
}

.intro-heading span {
  display: block;
  width: fit-content;
  border-top: 3px solid var(--color-cau-green);
  padding-top: 12px;
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
}

.intro-heading h2 {
  margin: 16px 0 0;
  color: var(--color-deep-green);
  font-size: clamp(30px, 3vw, 40px);
  font-weight: 650;
  line-height: 1.18;
}

.intro-body {
  min-width: 0;
}

.intro-body p {
  max-width: 820px;
  margin: 0;
  color: rgba(47, 52, 55, 0.82);
  font-size: 17px;
  line-height: 1.9;
}

.intro-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  grid-column: 2;
  margin-top: -4px;
}

.intro-detail {
  max-width: 980px;
  margin: 12px 0 0;
  color: rgba(47, 52, 55, 0.78);
  font-size: 16px;
  line-height: 1.8;
}

.publication-section,
.news-section {
  background: var(--color-rice);
}

.page-section {
  position: relative;
  border-top: 1px solid rgba(31, 61, 43, 0.08);
}

.intro-section {
  position: relative;
  margin-top: -1px;
  padding-top: 54px;
  padding-bottom: 58px;
  background:
    linear-gradient(180deg, #fff 0%, rgba(248, 247, 242, 0.72) 100%),
    var(--color-rice);
}

.intro-section::before {
  display: none;
}

.intro-section :deep(.section-header h2) {
  color: var(--color-deep-green);
}

.intro-section :deep(.section-header p:last-child) {
  color: var(--color-muted);
}

.stats-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
}

.stats-row {
  grid-template-columns: repeat(4, 1fr);
  border-top-color: rgba(31, 61, 43, 0.14);
}

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

.compact-stats {
  max-width: 520px;
  margin-top: 22px;
}

.compact-stats div {
  padding: 8px 0 8px 14px;
}

.stats-row strong {
  display: block;
  color: var(--color-cau-green);
  font-size: 32px;
  font-weight: 650;
  line-height: 1;
}

.compact-stats strong {
  font-size: 24px;
}

.stats-row span {
  color: var(--color-muted);
  font-size: 14px;
}

.research-section,
.team-section {
  background: var(--color-soft-gray);
}

.research-section {
  position: relative;
  overflow: hidden;
  padding-top: 78px;
  padding-bottom: 82px;
  background:
    linear-gradient(180deg, rgba(248, 247, 242, 0.82), rgba(245, 247, 246, 0.98)),
    var(--color-soft-gray);
}

.research-section::before {
  position: absolute;
  top: 44px;
  right: max(20px, calc((100vw - var(--container)) / 2));
  width: 172px;
  height: 118px;
  pointer-events: none;
  content: "";
  opacity: 0.34;
  background:
    radial-gradient(circle at 42px 76px, rgba(0, 135, 60, 0.12) 0 8px, transparent 9px),
    radial-gradient(circle at 72px 54px, rgba(0, 135, 60, 0.1) 0 7px, transparent 8px),
    radial-gradient(circle at 106px 36px, rgba(166, 120, 78, 0.12) 0 7px, transparent 8px),
    radial-gradient(circle at 128px 66px, rgba(0, 135, 60, 0.09) 0 6px, transparent 7px),
    linear-gradient(150deg, transparent 0 31%, rgba(31, 61, 43, 0.36) 32% 33%, transparent 34%),
    linear-gradient(112deg, transparent 0 43%, rgba(31, 61, 43, 0.28) 44% 45%, transparent 46%);
}

.publication-section {
  background:
    linear-gradient(180deg, #fff 0%, rgba(248, 247, 242, 0.5) 100%),
    #fff;
}

.team-section {
  background:
    linear-gradient(180deg, rgba(245, 247, 246, 0.98), rgba(234, 245, 238, 0.78)),
    var(--color-soft-gray);
}

.news-section {
  background:
    radial-gradient(circle at 12% 16%, rgba(234, 245, 238, 0.86), transparent 260px),
    var(--color-rice);
}

.research-grid,
.news-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  border: 0;
  background: transparent;
}

.research-grid {
  margin-top: 22px;
}

.research-card,
.latest-paper-panel,
.member-card {
  border: 0;
  border-radius: 0;
  padding: 20px;
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
  border: 1px solid rgba(31, 61, 43, 0.1);
  border-radius: var(--radius-md);
  min-height: 154px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.92)),
    #fff;
  box-shadow: var(--shadow-soft);
}

.research-card:hover,
.news-card:hover {
  transform: translateY(-2px);
}

.member-card:hover {
  transform: translateY(-2px);
}

.latest-paper-panel:hover {
  transform: none;
}

.research-card svg {
  width: 25px;
  height: 25px;
  border: 0;
  border-radius: 0;
  padding: 0;
  background: transparent;
  color: var(--color-cau-green);
}

.research-card h3,
.member-card h3,
.news-card h3 {
  margin: 11px 0 7px;
  color: var(--color-deep-green);
  font-size: 18px;
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
  grid-template-columns: 52px 1fr;
  gap: 14px;
  padding: 13px 0;
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
  font-size: 16px;
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

.paper-compact span {
  display: inline-flex;
  margin-top: 6px;
  color: var(--color-cau-green);
  font-size: 12px;
  font-weight: 700;
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  border: 0;
}

.member-card {
  display: grid;
  grid-template-columns: 62px minmax(0, 1fr);
  align-items: center;
  min-height: 128px;
  border: 1px solid rgba(31, 61, 43, 0.1);
  border-radius: var(--radius-md);
  padding: 15px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 247, 242, 0.72)),
    #fff;
  color: inherit;
  text-decoration: none;
  box-shadow: var(--shadow-soft);
}

.member-card img {
  width: 58px;
  height: 58px;
  border: 1px solid var(--color-line);
  border-radius: 50%;
  background: var(--color-eco-green);
  object-fit: cover;
}

.member-info {
  display: grid;
  gap: 5px;
  min-width: 0;
  margin-top: 0;
}

.member-info h3 {
  min-width: 0;
  margin: 0;
  overflow: hidden;
  color: var(--color-deep-green);
  font-size: 17px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.member-info span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 650;
  line-height: 1.45;
}

.member-card p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.65;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.news-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #fff;
  color: inherit;
  box-shadow: var(--shadow-soft);
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
  padding: 14px 15px 16px;
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
  align-items: center;
  min-height: 34px;
  border-bottom: 1px solid rgba(0, 135, 60, 0.32);
  margin-top: 22px;
  color: var(--color-cau-green);
  font-weight: 700;
}

.section-link:hover {
  border-bottom-color: var(--color-cau-green);
  color: #0a7638;
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
  padding: 8px 0 72px;
  border-top: 1px solid rgba(31, 61, 43, 0.08);
  background: var(--color-rice);
}

.join-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  border: 1px solid rgba(0, 135, 60, 0.18);
  border-radius: var(--radius-lg);
  padding: 34px 38px;
  background:
    linear-gradient(90deg, var(--color-deep-green), #0a7638),
    var(--color-deep-green);
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

@media (max-width: 980px) {
  .hero {
    padding: 10px 0 16px;
  }

  .hero-carousel {
    width: min(var(--container), calc(100% - 28px));
    height: clamp(300px, 50vw, 430px);
    border-radius: 8px;
  }

  .intro-grid,
  .publication-grid {
    grid-template-columns: 1fr;
  }

  .intro-grid {
    max-width: none;
  }

  .intro-main {
    grid-template-columns: 1fr;
    gap: 22px;
  }

  .intro-actions {
    grid-column: auto;
    margin-top: 0;
  }

  .research-grid,
  .news-grid,
  .member-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .hero-carousel {
    width: calc(100% - 20px);
    height: 240px;
    border-radius: 7px;
  }

  .hero-caption {
    bottom: 34px;
    left: 18px;
    max-width: calc(100% - 36px);
  }

  .hero-caption h1 {
    font-size: 15px;
  }

  .hero-caption span {
    margin-top: 5px;
    font-size: 10px;
    line-height: 1.45;
  }

  .hero-controls {
    bottom: 12px;
  }

  .hero-dots button {
    width: 6px;
    height: 6px;
  }

  .hero-dots button.active {
    width: 20px;
  }

  .intro-grid {
    width: min(var(--container), calc(100% - 28px));
  }

  .primary-action,
  .secondary-action {
    flex: 1 1 140px;
    min-height: 42px;
    padding: 10px 14px;
  }

  .research-grid,
  .news-grid,
  .member-grid,
  .stats-row {
    grid-template-columns: 1fr;
  }

  .member-card {
    grid-template-columns: 56px minmax(0, 1fr);
    min-height: 112px;
  }

  .member-card img {
    width: 56px;
    height: 56px;
  }

  .join-card {
    align-items: flex-start;
    flex-direction: column;
    gap: 18px;
    padding: 24px;
  }

  .join-card h2 {
    font-size: 24px;
  }

  .join-card a {
    width: 100%;
  }
}
</style>


