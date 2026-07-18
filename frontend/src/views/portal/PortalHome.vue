<template>
  <PortalLayout>
    <section class="hero">
      <div
        class="hero-carousel"
        @pointerdown="handleBannerPointerDown"
        @pointerup="handleBannerPointerUp"
        @pointercancel="handleBannerPointerCancel"
      >
        <div
          v-for="(banner, index) in heroBanners"
          :key="`${banner.image}-${index}`"
          class="hero-slide"
          :class="{ active: index === activeBannerIndex }"
          :style="{ transform: `translateX(${(index - activeBannerIndex) * 100}%)` }"
        >
          <div v-if="!heroImageStates[heroStateKey(banner.image, index)]" class="hero-skeleton" aria-hidden="true"></div>
          <img
            v-if="heroImageStates[heroStateKey(banner.image, index)] !== 'failed'"
            :src="banner.image"
            :alt="banner.title || siteName"
            @load="heroImageStates[heroStateKey(banner.image, index)] = 'loaded'"
            @error="heroImageStates[heroStateKey(banner.image, index)] = 'failed'"
          />
          <ImagePlaceholder v-else class="hero-fallback" label="横幅图片暂不可用" text="横幅图片暂不可用" />
        </div>
        <div v-if="activeHeroTitle || activeHeroSubtitle" class="hero-caption">
          <h1>{{ activeHeroTitle }}</h1>
          <span v-if="activeHeroSubtitle">{{ activeHeroSubtitle }}</span>
        </div>
        <button v-if="heroBanners.length > 1" class="hero-arrow hero-arrow-left" type="button" aria-label="上一张横幅" @click="showPrevBanner">
          ‹
        </button>
        <button v-if="heroBanners.length > 1" class="hero-arrow hero-arrow-right" type="button" aria-label="下一张横幅" @click="showNextBannerManually">
          ›
        </button>
        <div v-if="heroBanners.length > 1" class="hero-controls" aria-label="首页横幅切换">
          <div class="hero-dots">
            <button
              v-for="(_, index) in heroBanners"
              :key="index"
              type="button"
              :aria-label="`切换到第 ${index + 1} 张横幅`"
              :class="{ active: index === activeBannerIndex }"
              @click="setActiveBanner(index)"
            ></button>
          </div>
        </div>
      </div>
    </section>
    <section class="page-section intro-section">
      <div class="container intro-grid">
        <div :class="['intro-main', { 'is-empty': !introDescription }]">
          <div class="intro-heading">
            <h2>课题组简介</h2>
          </div>
          <div v-if="introDescription" class="intro-body">
            <p v-if="introDescription">{{ introDescription }}</p>
          </div>
        </div>
      </div>
    </section>

    <section v-if="displayResearchDirections.length" class="page-section research-section">
      <div class="container">
        <SectionHeader title="研究方向" />
        <div class="research-grid">
          <RouterLink v-for="item in displayResearchDirections" :key="item.title" class="card research-card" :to="{ path: item.to, query: { from: route.fullPath } }">
            <span class="research-card-icon"><component :is="item.icon" /></span>
            <div><h3>{{ item.title }}</h3><p v-if="item.description">{{ item.description }}</p></div>
          </RouterLink>
        </div>
        <RouterLink class="section-link" to="/research">查看全部研究方向</RouterLink>
      </div>
    </section>

    <section class="page-section publication-section">
      <div class="container publication-grid">
        <div class="publication-summary">
          <SectionHeader title="科研成果" description="展示课题组近期公开发表和授权、立项、获奖等成果动态；完整论文、项目、专利与获奖信息可进入科研成果页查看。" />
          <div class="stats-row compact-stats">
            <div v-for="item in displayStats" :key="item.label">
              <strong>{{ item.value }}</strong>
              <span>{{ item.label }}</span>
            </div>
          </div>
        </div>
        <div class="latest-paper-panel">
          <RouterLink v-for="item in displayAchievements" :key="`${item.type}-${item.id}`" class="paper-compact" :to="{ path: item.to, query: { from: route.fullPath } }">
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

    <section v-if="displayMembers.length" class="page-section team-section">
      <div class="container">
        <div class="team-heading-row">
          <SectionHeader title="团队成员" />
          <RouterLink v-if="displayMembers.length" class="team-all-link" to="/team">
            查看全部成员
            <ArrowRight />
          </RouterLink>
        </div>
        <div class="member-grid">
          <RouterLink v-for="member in displayMembers" :key="member.name" class="card member-card" :to="{ path: member.to, query: { from: route.fullPath } }">
            <div class="member-photo">
              <img
                v-if="member.avatar && !memberImageErrors.has(member.name)"
                :src="member.avatar"
                :alt="member.name"
                @error="memberImageErrors.add(member.name)"
              />
              <ImagePlaceholder v-else :label="`${member.name}暂无头像`" :initial="member.name" />
            </div>
            <div class="member-info">
              <div class="member-name-row">
                <h3>{{ member.name }}</h3>
                <ArrowRight class="member-arrow" />
              </div>
              <span v-if="member.role" class="member-role">{{ member.role }}</span>
              <p v-if="member.focus">{{ member.focus }}</p>
            </div>
          </RouterLink>
        </div>
      </div>
    </section>

    <section v-if="displayNews.length" class="page-section news-section">
      <div class="container">
        <SectionHeader title="新闻活动" />
        <div class="news-grid">
          <RouterLink v-for="item in displayNews" :key="item.title" class="card news-card" :to="{ path: `/news/${item.slug}`, query: { from: route.fullPath } }">
            <div class="news-media">
              <img
                v-if="item.image && !newsImageErrors.has(item.slug)"
                :src="item.image"
                :alt="item.title"
                @error="newsImageErrors.add(item.slug)"
              />
              <ImagePlaceholder v-else class="news-image-placeholder" :label="`${item.title}暂无封面`" text="暂无封面" />
            </div>
            <div class="news-card-content">
              <span v-if="item.meta">{{ item.meta }}</span>
              <h3>{{ item.title }}</h3>
              <p v-if="item.summary">{{ item.summary }}</p>
            </div>
          </RouterLink>
        </div>
        <RouterLink class="section-link" to="/news">查看新闻活动</RouterLink>
      </div>
    </section>

    <section v-if="contactDescription || contactEmail" class="join-section">
      <div class="container join-card">
        <div>
          <h2 v-if="contactTitle">{{ contactTitle }}</h2>
          <p>{{ contactDescription }}</p>
        </div>
        <a v-if="contactEmail" :href="`mailto:${contactEmail}`">联系实验室</a>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { ArrowRight, Cpu, DataAnalysis, MostlyCloudy, Orange, SetUp, WindPower } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'

import SectionHeader from '../../components/SectionHeader.vue'
import ImagePlaceholder from '../../components/ImagePlaceholder.vue'
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

const route = useRoute()
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
const heroImageStates = reactive<Record<string, 'loaded' | 'failed'>>({})
const newsImageErrors = reactive(new Set<string>())
const memberImageErrors = reactive(new Set<string>())
let bannerTimer: number | undefined
let bannerPointer: { id: number; x: number; y: number } | null = null

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

const HOME_SECTION_DEFAULT_COUNT = 4
const HOME_SECTION_MAX_COUNT = 10

const siteName = computed(() => siteSetting.value.site_name || '')
const heroSubtitle = computed(() => siteSetting.value.hero_subtitle || '')
const siteDescription = computed(() => siteSetting.value.description || '')
const introDescription = computed(() => siteDescription.value)
const contactDescription = computed(() => contactInfo.value.content || '')
const contactTitle = computed(() => contactInfo.value.title || '')
const contactEmail = computed(() => contactInfo.value.email || siteSetting.value.contact_email || '')
const bannerIntervalMs = computed(() => {
  const seconds = Number(siteSetting.value.banner_interval_seconds || 6)
  return Math.min(30, Math.max(3, Number.isFinite(seconds) ? seconds : 6)) * 1000
})
const heroBanners = computed(() => {
  const banners = apiBanners.value
    .filter((item) => item.image)
    .map((item) => ({ ...item, image: item.image as string }))
    .sort((a, b) => (a.sort_order || 0) - (b.sort_order || 0))
  if (banners.length) return banners
  return [{
    id: 0,
    title: siteName.value,
    subtitle: heroSubtitle.value,
    image: siteSetting.value.hero_image || '/default-hero.svg',
    link: '',
    sort_order: 0,
  }]
})
const activeHeroBanner = computed(() => heroBanners.value[activeBannerIndex.value] || heroBanners.value[0] || {
  title: siteName.value,
  subtitle: heroSubtitle.value,
  image: '',
})
const activeHeroTitle = computed(() => activeHeroBanner.value.title || siteName.value)
const activeHeroSubtitle = computed(() => activeHeroBanner.value.subtitle || heroSubtitle.value)

function heroStateKey(image: string, index: number) {
  return `${index}:${image}`
}

function startBannerTimer() {
  if (bannerTimer) window.clearInterval(bannerTimer)
  if (heroBanners.value.length <= 1) return
  bannerTimer = window.setInterval(() => {
    showNextBanner()
  }, bannerIntervalMs.value)
}

function stopBannerTimer() {
  if (!bannerTimer) return
  window.clearInterval(bannerTimer)
  bannerTimer = undefined
}

function showPrevBanner() {
  const length = heroBanners.value.length
  if (length <= 1) return
  activeBannerIndex.value = (activeBannerIndex.value - 1 + length) % length
  startBannerTimer()
}

function showNextBanner() {
  const length = heroBanners.value.length
  if (length <= 1) return
  activeBannerIndex.value = (activeBannerIndex.value + 1) % length
}

function showNextBannerManually() {
  showNextBanner()
  startBannerTimer()
}

function setActiveBanner(index: number) {
  activeBannerIndex.value = index
  startBannerTimer()
}

function handleBannerPointerDown(event: PointerEvent) {
  if (!event.isPrimary || heroBanners.value.length <= 1) return
  bannerPointer = { id: event.pointerId, x: event.clientX, y: event.clientY }
  if (event.currentTarget instanceof HTMLElement) event.currentTarget.setPointerCapture(event.pointerId)
  stopBannerTimer()
}

function handleBannerPointerUp(event: PointerEvent) {
  if (!bannerPointer || event.pointerId !== bannerPointer.id) return
  const deltaX = event.clientX - bannerPointer.x
  const deltaY = event.clientY - bannerPointer.y
  bannerPointer = null

  if (Math.abs(deltaX) >= 36 && Math.abs(deltaX) > Math.abs(deltaY) * 1.2) {
    if (deltaX < 0) showNextBannerManually()
    else showPrevBanner()
    return
  }
  startBannerTimer()
}

function handleBannerPointerCancel(event: PointerEvent) {
  if (!bannerPointer || event.pointerId !== bannerPointer.id) return
  bannerPointer = null
  startBannerTimer()
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
  const ranked = apiResearchDirections.value
    .filter((item) => (item.sort_order ?? 0) > 0)
    .sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0))
  const selected = ranked.length
    ? ranked.slice(0, HOME_SECTION_MAX_COUNT)
    : apiResearchDirections.value.slice(0, HOME_SECTION_DEFAULT_COUNT)
  return selected.map((item, index) => ({
    title: item.title,
    description: item.summary || '',
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
      source: [project.funding_source, project.status].filter(Boolean).join(' · '),
      to: `/publications/projects/${project.id}`,
      sortOrder: project.sort_order ?? 0,
      dateRank: dateRank(project.start_date),
    })),
    ...apiPatents.value.map((patent) => ({
      id: patent.id,
      type: 'patent' as const,
      badge: '专利',
      title: patent.title,
      source: [patent.patent_number, patent.status].filter(Boolean).join(' · '),
      to: `/publications/patents/${patent.id}`,
      sortOrder: patent.sort_order ?? 0,
      dateRank: dateRank(patent.authorization_date || patent.application_date),
    })),
    ...apiAwards.value.map((award) => ({
      id: award.id,
      type: 'award' as const,
      badge: '获奖',
      title: award.title,
      source: [award.award_level, award.award_date].filter(Boolean).join(' · '),
      to: `/publications/awards/${award.id}`,
      sortOrder: award.sort_order ?? 0,
      dateRank: dateRank(award.award_date),
    })),
  ]
  if (!items.length) return []
  const visibleItems = items.filter((item) => item.sortOrder > 0)
  if (!visibleItems.length) {
    return items
      .sort((a, b) => b.dateRank - a.dateRank || b.id - a.id)
      .slice(0, HOME_SECTION_DEFAULT_COUNT)
  }
  return visibleItems
    .sort((a, b) => a.sortOrder - b.sortOrder || b.dateRank - a.dateRank || b.id - a.id)
    .slice(0, HOME_SECTION_MAX_COUNT)
})

const displayMembers = computed(() => {
  return apiMembers.value.slice(0, 6).map((member) => ({
    name: member.name,
    role: memberIdentity(member),
    focus: member.research_direction || '',
    avatar: member.avatar || '',
    to: `/team/${member.id}`,
  }))
})

function memberIdentity(member: Member) {
  return member.role_label || member.role_type || ''
}

const displayNews = computed(() => {
  return apiNews.value.slice(0, 3).map((item) => ({
    slug: item.slug,
    meta: [item.event_date, item.category?.name].filter(Boolean).join(' · '),
    title: item.title,
    summary: item.summary || '',
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
    fetchPublications({ page_size: 100, ordering: '-sort_order,-year' }),
    fetchProjects({ page_size: 100, ordering: '-sort_order,-start_date' }),
    fetchPatents({ page_size: 100, ordering: '-sort_order,-application_date' }),
    fetchAwards({ page_size: 100, ordering: '-sort_order,-award_date' }),
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
  () => [heroBanners.value.length, bannerIntervalMs.value],
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
  touch-action: pan-y;
  user-select: none;
}

.hero-slide {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  opacity: 1;
  overflow: hidden;
  transition: transform 760ms cubic-bezier(0.22, 1, 0.36, 1);
}

.hero-slide > img,
.hero-skeleton,
.hero-fallback {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.hero-slide > img {
  display: block;
  object-fit: cover;
  object-position: center;
  -webkit-user-drag: none;
}

.hero-skeleton {
  background: linear-gradient(100deg, var(--color-panel-strong) 30%, #f8faf8 46%, var(--color-panel-strong) 62%);
  background-size: 220% 100%;
  animation: hero-loading 1.5s ease-in-out infinite;
}

.hero-fallback {
  background: var(--color-panel-strong);
}

@keyframes hero-loading {
  to { background-position: -220% 0; }
}

.hero-slide::after {
  position: absolute;
  inset: 0;
  content: "";
  z-index: 2;
  background: linear-gradient(180deg, transparent 58%, rgba(16, 38, 24, 0.28));
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

.hero-arrow {
  position: absolute;
  top: 50%;
  z-index: 4;
  display: grid;
  width: 34px;
  height: 48px;
  place-items: center;
  border: 0;
  background: transparent;
  color: rgba(255, 255, 255, 0.68);
  cursor: pointer;
  font-family: Georgia, "Times New Roman", serif;
  font-size: 42px;
  font-weight: 400;
  line-height: 1;
  transform: translateY(-50%);
  text-shadow: 0 2px 10px rgba(18, 38, 26, 0.34);
  transition: color 0.18s ease, opacity 0.18s ease, transform 0.22s ease;
}

.hero-arrow:hover {
  color: rgba(255, 255, 255, 0.96);
}

.hero-arrow-left {
  left: 12px;
}

.hero-arrow-left:hover {
  transform: translate(-3px, -50%) scale(1.08);
}

.hero-arrow-right {
  right: 12px;
}

.hero-arrow-right:hover {
  transform: translate(3px, -50%) scale(1.08);
}

.hero-dots {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
}

.hero-dots button {
  display: grid;
  width: 22px;
  min-width: 0;
  height: 22px;
  min-height: 0;
  place-items: center;
  border: 0;
  padding: 0;
  background: transparent;
  cursor: pointer;
}

.hero-dots button::before {
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.52);
  content: "";
  transition: width 0.2s ease, background 0.2s ease;
}

.hero-dots button.active::before {
  width: 14px;
  background: rgba(255, 255, 255, 0.82);
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
  gap: 34px;
  min-width: 0;
  border-top: 1px solid rgba(31, 61, 43, 0.12);
  border-bottom: 1px solid rgba(31, 61, 43, 0.08);
  padding: 28px 0 26px;
}

.intro-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(28px, 3vw, 34px);
  font-weight: 650;
  line-height: 1.18;
}

.intro-heading::before {
  display: block;
  width: 44px;
  height: 3px;
  margin-bottom: 12px;
  background: var(--color-cau-green);
  content: "";
}

.intro-body {
  min-width: 0;
}

.intro-body p {
  max-width: 820px;
  margin: 0;
  color: rgba(47, 52, 55, 0.82);
  font-size: 16px;
  line-height: 1.8;
}

.intro-lead {
  display: block;
  max-width: 820px;
  margin-bottom: 12px;
  color: var(--color-deep-green);
  font-size: 18px;
  font-weight: 650;
  line-height: 1.6;
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
  padding-top: 38px;
  padding-bottom: 44px;
  background: #fff;
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
  padding-top: 68px;
  padding-bottom: 72px;
  background: var(--color-soft-gray);
}

.intro-main.is-empty {
  grid-template-columns: 1fr;
  align-items: center;
  padding-top: 20px;
  padding-bottom: 20px;
}

.research-section::before {
  display: none;
}

.publication-section {
  background: #fff;
}

.publication-grid {
  grid-template-columns: minmax(0, 1fr);
  gap: 24px;
}

.publication-summary {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 0.72fr);
  align-items: end;
  gap: 36px;
}

.publication-summary :deep(.section-header) {
  margin-bottom: 0;
}

.publication-summary .compact-stats {
  width: 100%;
  max-width: none;
  margin-top: 0;
}

.team-section {
  background: var(--color-eco-green);
}

.news-section {
  background: var(--color-rice);
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
  column-gap: 28px;
  gap: 8px;
  border-left: 0;
  padding: 0;
  background: transparent;
}

.research-card {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  align-items: start;
  gap: 14px;
  border: 1px solid rgba(31, 61, 43, 0.1);
  border-radius: var(--radius-md);
  min-height: 126px;
  padding: 18px 20px;
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

.research-card-icon {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 1px solid rgba(0, 135, 60, 0.14);
  border-radius: 50%;
  background: var(--color-eco-green);
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

.research-card h3 {
  margin-top: 1px;
}

.research-card p {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  border: 0;
}

.team-heading-row {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 32px;
  margin-bottom: 32px;
}

.team-heading-row :deep(.section-header) {
  margin-bottom: 0;
}

.team-all-link {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 7px;
  margin-bottom: 4px;
  border-bottom: 1px solid rgba(0, 135, 60, 0.36);
  padding: 6px 0;
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 650;
  text-decoration: none;
  transition: gap 180ms ease, border-color 180ms ease;
}

.team-all-link svg {
  width: 16px;
  height: 16px;
}

.team-all-link:hover {
  gap: 11px;
  border-color: var(--color-cau-green);
}

.member-card {
  display: grid;
  grid-template-columns: 116px minmax(0, 1fr);
  align-items: stretch;
  min-height: 156px;
  border: 1px solid rgba(31, 61, 43, 0.1);
  border-radius: var(--radius-md);
  overflow: hidden;
  padding: 0;
  background: rgba(255, 255, 255, 0.96);
  color: inherit;
  text-decoration: none;
  box-shadow: var(--shadow-soft);
}

.member-photo {
  min-height: 156px;
  overflow: hidden;
  background: var(--color-panel-strong);
}

.member-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
  transition: transform 260ms ease;
}

.member-info {
  display: grid;
  align-content: center;
  gap: 8px;
  min-width: 0;
  padding: 20px 18px;
}

.member-name-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.member-info h3 {
  min-width: 0;
  margin: 0;
  overflow: hidden;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.member-role {
  display: -webkit-box;
  overflow: hidden;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 650;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.member-arrow {
  width: 17px;
  height: 17px;
  flex: 0 0 auto;
  color: rgba(0, 135, 60, 0.56);
  transition: transform 180ms ease, color 180ms ease;
}

.member-card p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.member-card:hover {
  border-color: rgba(0, 135, 60, 0.24);
  box-shadow: var(--shadow-hover);
}

.member-card:hover .member-photo img {
  transform: scale(1.025);
}

.member-card:hover .member-arrow {
  color: var(--color-cau-green);
  transform: translateX(3px);
}

.news-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: #fff;
  color: inherit;
  box-shadow: var(--shadow-soft);
}

.news-media,
.news-card img,
.news-image-placeholder {
  width: 100%;
  aspect-ratio: 16 / 8.5;
}

.news-media {
  overflow: hidden;
  padding: 0;
  background: var(--color-panel-strong);
}

.news-card img {
  display: block;
  object-fit: cover;
  filter: saturate(0.92);
}

.news-image-placeholder {
  display: grid;
  place-items: center;
  width: 100%;
  aspect-ratio: 16 / 8.5;
  background: var(--color-panel-strong);
  color: rgba(78, 110, 126, 0.62);
  font-size: 12px;
}

.news-card-content {
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
  grid-column: 1 / -1;
  justify-self: start;
  margin-top: 14px;
}

.empty-inline {
  grid-column: 1 / -1;
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
  padding: 28px 32px;
  background: #fff;
  box-shadow: none;
}

.join-card h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 27px;
  font-weight: 650;
}

.join-card p:last-child {
  max-width: 760px;
  margin: 12px 0 0;
  color: var(--color-muted);
}

.join-card a {
  flex: 0 0 auto;
  border-radius: var(--radius-sm);
  padding: 11px 20px;
  background: var(--color-cau-green);
  color: #fff;
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

  .publication-summary {
    grid-template-columns: 1fr;
    gap: 18px;
  }

  .intro-grid {
    max-width: none;
  }

  .intro-main {
    grid-template-columns: 1fr;
    gap: 22px;
  }

  .research-grid,
  .news-grid,
  .member-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .member-card {
    grid-template-columns: 110px minmax(0, 1fr);
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
    bottom: 9px;
  }

  .hero-arrow {
    width: 28px;
    height: 40px;
    font-size: 34px;
  }

  .hero-arrow-left {
    left: 8px;
  }

  .hero-arrow-right {
    right: 8px;
  }

  .hero-dots button {
    width: 18px;
    height: 18px;
  }

  .hero-dots button::before {
    width: 4px;
    height: 4px;
    background: rgba(255, 255, 255, 0.4);
  }

  .hero-dots button.active::before {
    width: 10px;
    background: rgba(255, 255, 255, 0.7);
  }

  .intro-grid {
    width: min(var(--container), calc(100% - 28px));
  }

  .research-grid,
  .news-grid,
  .member-grid {
    grid-template-columns: 1fr;
  }

  .latest-paper-panel {
    grid-template-columns: 1fr;
  }

  .stats-row {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .compact-stats {
    max-width: none;
  }

  .compact-stats div {
    padding-left: 10px;
  }

  .compact-stats strong {
    font-size: 21px;
  }

  .research-card {
    min-height: 0;
    padding: 15px;
  }

  .team-heading-row {
    display: block;
    margin-bottom: 24px;
  }

  .team-all-link {
    margin-top: 16px;
    margin-bottom: 0;
  }

  .member-card {
    grid-template-columns: 92px minmax(0, 1fr);
    min-height: 126px;
  }

  .member-photo {
    min-height: 126px;
  }

  .member-info {
    gap: 6px;
    padding: 15px 14px;
  }

  .member-info h3 {
    font-size: 17px;
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


