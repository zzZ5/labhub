import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { cmsApi, type CmsNewsArticle } from '../../../api/cms'
import type {
  Award,
  ContactInfo,
  HomeBanner,
  Member,
  NewsCategory,
  Patent,
  Project,
  Publication,
  ResearchDirection,
  SiteSetting,
} from '../../../api/publicPortal'
import { formatFileSize } from '../../../utils/files'

export type CmsListRow<T> = {
  key: string | number
  title: string
  meta: string
  source: T
}

type BaseContentLoaded = (setting?: SiteSetting, contact?: ContactInfo) => void

export function useCmsContentData(onBaseContentLoaded?: BaseContentLoaded) {
  const loading = ref(false)
  const loadError = ref('')
  const researchItems = ref<ResearchDirection[]>([])
  const siteSettings = ref<SiteSetting[]>([])
  const contactInfoItems = ref<ContactInfo[]>([])
  const bannerItems = ref<HomeBanner[]>([])
  const memberItems = ref<Member[]>([])
  const newsItems = ref<CmsNewsArticle[]>([])
  const newsCategories = ref<NewsCategory[]>([])
  const publicationItems = ref<Publication[]>([])
  const projectItems = ref<Project[]>([])
  const patentItems = ref<Patent[]>([])
  const awardItems = ref<Award[]>([])

  const researchRows = computed<CmsListRow<ResearchDirection>[]>(() =>
    prioritizeSortedItems(researchItems.value).map((item) => ({
      key: item.slug,
      title: item.title,
      meta: compactMeta([homepageSortText(item.sort_order), item.summary || item.slug]),
      source: item,
    })),
  )
  const bannerRows = computed<CmsListRow<HomeBanner>[]>(() =>
    prioritizeSortedItems(bannerItems.value).map((item) => ({
      key: item.id,
      title: item.title || '未命名横幅',
      meta: `${item.is_active === false ? '停用' : '启用'} · 排序 ${item.sort_order || 0} · ${displayFileLabel(item.image) || '未上传图片'}`,
      source: item,
    })),
  )
  const memberRows = computed<CmsListRow<Member>[]>(() =>
    memberItems.value.map((item) => ({
      key: item.id,
      title: item.name,
      meta: compactMeta([item.sort_order ? `排序 ${item.sort_order}` : '不展示', roleText(item.role_type), item.research_direction]),
      source: item,
    })),
  )
  const newsRows = computed<CmsListRow<CmsNewsArticle>[]>(() =>
    newsItems.value.map((item) => ({
      key: item.slug,
      title: item.title,
      meta: `${item.event_date || '未设置日期'} · ${statusText(item.status)}`,
      source: item,
    })),
  )
  const publicationRows = computed<CmsListRow<Publication>[]>(() =>
    prioritizeSortedItems(publicationItems.value).map((item) => ({ key: item.id, title: item.title, meta: compactMeta([homepageSortText(item.sort_order), visibilityText(item.visibility), item.year, item.journal]), source: item })),
  )
  const projectRows = computed<CmsListRow<Project>[]>(() =>
    prioritizeSortedItems(projectItems.value).map((item) => ({ key: item.id, title: item.title, meta: compactMeta([homepageSortText(item.sort_order), visibilityText(item.visibility), item.funding_source, item.status]), source: item })),
  )
  const patentRows = computed<CmsListRow<Patent>[]>(() =>
    prioritizeSortedItems(patentItems.value).map((item) => ({ key: item.id, title: item.title, meta: compactMeta([homepageSortText(item.sort_order), visibilityText(item.visibility), item.patent_number, item.status]), source: item })),
  )
  const awardRows = computed<CmsListRow<Award>[]>(() =>
    prioritizeSortedItems(awardItems.value).map((item) => ({ key: item.id, title: item.title, meta: compactMeta([homepageSortText(item.sort_order), visibilityText(item.visibility), item.award_level, item.award_date]), source: item })),
  )

  const cmsOverview = computed(() => [
    { label: '首页设置', value: siteSettings.value.length ? 1 : 0 },
    { label: '首页横幅', value: bannerItems.value.length },
    { label: '研究方向', value: researchItems.value.length },
    { label: '团队成员', value: memberItems.value.length },
    { label: '新闻活动', value: newsItems.value.length },
    { label: '论文成果', value: publicationItems.value.length },
    { label: '科研项目', value: projectItems.value.length },
    { label: '专利成果', value: patentItems.value.length },
    { label: '获奖成果', value: awardItems.value.length },
  ])

  async function loadAll() {
    loading.value = true
    loadError.value = ''
    try {
      const results = await Promise.allSettled([
        cmsApi.listSiteSettings(),
        cmsApi.listContactInfo(),
        cmsApi.listHomeBanners(),
        cmsApi.listResearch(),
        cmsApi.listMembers(),
        cmsApi.listNewsCategories(),
        cmsApi.listNews(),
        cmsApi.listPublications(),
        cmsApi.listProjects(),
        cmsApi.listPatents(),
        cmsApi.listAwards(),
      ])
      const [settings, contacts, banners, research, members, categories, news, publications, projects, patents, awards] = results
      siteSettings.value = resultValue(settings, siteSettings.value)
      contactInfoItems.value = resultValue(contacts, contactInfoItems.value)
      bannerItems.value = resultValue(banners, bannerItems.value)
      researchItems.value = resultValue(research, researchItems.value)
      memberItems.value = resultValue(members, memberItems.value)
      newsCategories.value = resultValue(categories, newsCategories.value)
      newsItems.value = resultValue(news, newsItems.value)
      publicationItems.value = resultValue(publications, publicationItems.value)
      projectItems.value = resultValue(projects, projectItems.value)
      patentItems.value = resultValue(patents, patentItems.value)
      awardItems.value = resultValue(awards, awardItems.value)
      onBaseContentLoaded?.(siteSettings.value[0], contactInfoItems.value[0])

      const failedCount = results.filter((item) => item.status === 'rejected').length
      if (failedCount) {
        loadError.value = `${failedCount} 项门户内容未能加载，现有内容已保留。请检查网络或权限后重试。`
        ElMessage.warning('部分门户内容加载失败，请刷新或检查当前账号是否有门户编辑权限。')
      }
    } finally {
      loading.value = false
    }
  }

  function displayFileLabel(value?: string | null) {
    if (!value) return ''
    const size = findUploadedFileSize(value)
    return size ? `${displayFileName(value)}（${formatFileSize(size)}）` : displayFileName(value)
  }

  function findUploadedFileSize(value: string) {
    const match = (url?: string | null) => Boolean(url && (url === value || url.split('?')[0] === value.split('?')[0]))
    const site = siteSettings.value.find((item) => match(item.logo) || match(item.favicon) || match(item.hero_image))
    if (site) {
      if (match(site.logo)) return site.logo_size || 0
      if (match(site.favicon)) return site.favicon_size || 0
      if (match(site.hero_image)) return site.hero_image_size || 0
    }
    const banner = bannerItems.value.find((item) => match(item.image))
    if (banner) return banner.image_size || 0
    const research = researchItems.value.find((item) => match(item.cover_image))
    if (research) return research.cover_image_size || 0
    const member = memberItems.value.find((item) => match(item.avatar))
    if (member) return member.avatar_size || 0
    const news = newsItems.value.find((item) => match(item.cover_image) || match(item.word_file))
    if (news) {
      if (match(news.cover_image)) return news.cover_image_size || 0
      if (match(news.word_file)) return news.word_file_size || 0
    }
    const publication = publicationItems.value.find((item) => match(item.pdf_file))
    if (publication) return publication.pdf_file_size || 0
    const patent = patentItems.value.find((item) => match(item.pdf_file))
    if (patent) return patent.pdf_file_size || 0
    const award = awardItems.value.find((item) => match(item.image) || match(item.attachment))
    if (award) {
      if (match(award.image)) return award.image_size || 0
      if (match(award.attachment)) return award.attachment_size || 0
    }
    return 0
  }

  return {
    loading,
    loadError,
    researchItems,
    siteSettings,
    contactInfoItems,
    bannerItems,
    memberItems,
    newsItems,
    newsCategories,
    publicationItems,
    projectItems,
    patentItems,
    awardItems,
    researchRows,
    bannerRows,
    memberRows,
    newsRows,
    publicationRows,
    projectRows,
    patentRows,
    awardRows,
    cmsOverview,
    displayFileLabel,
    loadAll,
  }
}

function resultValue<T>(result: PromiseSettledResult<T[]>, fallback: T[]) {
  return result.status === 'fulfilled' ? result.value : fallback
}

function displayFileName(value: string) {
  const withoutQuery = value.split('?')[0]
  const filename = withoutQuery.split('/').filter(Boolean).pop() || value
  let decoded = filename
  try {
    decoded = decodeURIComponent(filename)
  } catch {
    decoded = filename
  }
  return decoded.length > 42 ? `${decoded.slice(0, 18)}...${decoded.slice(-18)}` : decoded
}

function roleText(role: string) {
  const labels: Record<string, string> = {
    pi: '硕博导师',
    postdoc: '博士后',
    phd: '博士生',
    master: '硕士生',
    undergraduate: '本科生',
    other: '其他成员',
    graduate: '已毕业成员',
  }
  return labels[role] || role
}

function statusText(status: string) {
  return status === 'published' ? '已发布' : status === 'draft' ? '草稿' : status === 'archived' ? '已归档' : status
}

function visibilityText(visibility?: string) {
  const labels: Record<string, string> = {
    public: '公开',
    members: '成员可见',
    admins: '管理员可见',
  }
  return visibility ? labels[visibility] || visibility : ''
}

function compactMeta(values: Array<string | number | null | undefined>) {
  return values.filter((value) => value !== '' && value !== null && value !== undefined).join(' · ')
}

function homepageSortText(value?: number | null) {
  const order = Number(value) || 0
  return order > 0 ? `首页排序 ${order}` : '首页默认'
}

function prioritizeSortedItems<T extends { sort_order?: number | null }>(items: T[]) {
  return items
    .map((item, index) => ({ item, index, order: Number(item.sort_order) || 0 }))
    .sort((a, b) => {
      const aPrioritized = a.order > 0
      const bPrioritized = b.order > 0
      if (aPrioritized !== bPrioritized) return aPrioritized ? -1 : 1
      if (aPrioritized && a.order !== b.order) return a.order - b.order
      return a.index - b.index
    })
    .map(({ item }) => item)
}
