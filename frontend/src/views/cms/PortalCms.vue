<template>
  <InternalLayout title="门户内容管理">
    <section class="cms-page">
      <div class="cms-heading">
        <div>
          <h1>门户内容</h1>
        </div>
        <div class="heading-actions">
          <div class="cms-stat-strip">
            <span v-for="item in cmsOverview" :key="item.label">{{ item.label }} {{ item.value }}</span>
          </div>
          <RouterLink class="preview-link" to="/">预览官网</RouterLink>
        </div>
      </div>

      <el-tabs v-model="activeTab" class="cms-tabs">
        <el-tab-pane label="站点首页" name="site">
          <CmsSiteEditor :site-form="siteForm" :contact-form="contactForm" :saving="saving" :progress="cmsUploadProgress" @save="saveHomeContent" />
        </el-tab-pane>

        <el-tab-pane label="页脚设置" name="footer">
          <CmsFooterEditor
            :site-form="siteForm"
            :external-links="externalLinks"
            :logo="editingSiteLogo"
            :favicon="editingSiteFavicon"
            :hero-image="editingSiteHeroImage"
            :saving="saving"
            :progress="cmsUploadProgress"
            :display-file-label="displayFileLabel"
            @file="(event, field) => setFile(event, siteForm, field)"
            @save="saveFooterContent"
          />
        </el-tab-pane>

        <el-tab-pane label="首页横幅" name="banners">
          <CmsBannerEditor
            :rows="bannerRows"
            :editing-id="editingBannerId"
            :form="bannerForm"
            :site-form="siteForm"
            :default-hero="editingSiteHeroImage"
            :current-image="editingBannerImage"
            :saving="saving"
            :progress="cmsUploadProgress"
            :display-file-label="displayFileLabel"
            @create="resetBanner"
            @edit="editBanner"
            @file="setFile($event, bannerForm, 'image')"
            @save="saveBanner"
            @delete="deleteBanner"
          />
        </el-tab-pane>

        <el-tab-pane label="研究方向" name="research">
          <CmsResearchEditor
            :rows="researchRows"
            :editing-slug="editingResearchSlug"
            :form="researchForm"
            :current-cover="editingResearchCover"
            :saving="saving"
            :progress="cmsUploadProgress"
            :display-file-label="displayFileLabel"
            @create="resetResearch"
            @edit="editResearch"
            @file="setFile($event, researchForm, 'cover_image')"
            @save="saveResearch"
            @delete="deleteResearch"
          />
        </el-tab-pane>

        <el-tab-pane label="团队成员" name="members">
          <CmsMemberEditor
            :rows="memberRows" :editing-id="editingMemberId" :form="memberForm"
            :avatar-preview="memberAvatarPreviewUrl" :selected-avatar="selectedMemberAvatar" :current-avatar="editingMemberAvatar"
            :avatar-input-key="memberAvatarInputKey" :saving="saving" :progress="cmsUploadProgress"
            :importing="importingKind === 'members'" :import-progress="importProgress"
            :display-file-label="displayFileLabel" :format-file-size="formatFileSize"
            @create="resetMember" @edit="editMember" @file="setFile($event, memberForm, 'avatar')"
            @import="importCmsFile($event, 'members')" @save="saveMember" @delete="deleteMember"
          />
        </el-tab-pane>

        <el-tab-pane label="新闻活动" name="news">
          <CmsNewsEditor
            ref="newsEditorRef" :rows="newsRows" :editing-slug="editingNewsSlug" :form="newsForm" :categories="newsCategories"
            v-model:content="newsContent" :uploading-image="uploadingNewsImage" :image-upload-progress="newsImageUploadProgress"
            :file-input-key="newsFileInputKey" :selected-word-file="selectedNewsWordFile" :current-word-file="editingNewsWordFile"
            :current-cover="editingNewsCover" :upload-progress="newsUploadProgress" :saving="saving"
            :display-file-label="displayFileLabel" :format-file-size="formatFileSize"
            @create="resetNews" @edit="editNews" @image-selected="insertNewsBodyImage"
            @word-file="setFile($event, newsForm, 'word_file')" @cover-file="setFile($event, newsForm, 'cover_image')"
            @save="saveNews" @delete="deleteNews"
          />
        </el-tab-pane>

        <el-tab-pane label="论文成果" name="publications">
          <CmsPublicationEditor
            :rows="publicationRows" :editing-id="editingPublicationId" :form="publicationForm" :preview="publicationPreview"
            :has-preview="hasPublicationPreview" :volume-preview="publicationVolumePreview" :current-pdf="editingPublicationPdf"
            :saving="saving" :progress="cmsUploadProgress" :importing="importingKind === 'publications'" :import-progress="importProgress"
            :display-file-label="displayFileLabel" @create="resetPublication" @edit="editPublication" @parse="parsePublicationCitation"
            @file="setFile($event, publicationForm, 'pdf_file')" @import="importCmsFile($event, 'publications')"
            @save="savePublication" @delete="deletePublication"
          />
        </el-tab-pane>

        <el-tab-pane label="科研项目" name="projects">
          <CmsProjectEditor
            :rows="projectRows" :editing-id="editingProjectId" :form="projectForm" :saving="saving" :progress="cmsUploadProgress"
            :importing="importingKind === 'projects'" :import-progress="importProgress"
            @create="resetProject" @edit="editProject" @import="importCmsFile($event, 'projects')" @save="saveProject" @delete="deleteProject"
          />
        </el-tab-pane>

        <el-tab-pane label="专利成果" name="patents">
          <CmsPatentEditor
            :rows="patentRows" :editing-id="editingPatentId" :form="patentForm" :current-pdf="editingPatentPdf"
            :saving="saving" :progress="cmsUploadProgress" :importing="importingKind === 'patents'" :import-progress="importProgress"
            :display-file-label="displayFileLabel" @create="resetPatent" @edit="editPatent"
            @file="setFile($event, patentForm, 'pdf_file')" @import="importCmsFile($event, 'patents')" @save="savePatent" @delete="deletePatent"
          />
        </el-tab-pane>

        <el-tab-pane label="获奖成果" name="awards">
          <CmsAwardEditor
            :rows="awardRows" :editing-id="editingAwardId" :form="awardForm" :current-image="editingAwardImage"
            :current-attachment="editingAwardAttachment" :saving="saving" :progress="cmsUploadProgress"
            :importing="importingKind === 'awards'" :import-progress="importProgress" :display-file-label="displayFileLabel"
            @create="resetAward" @edit="editAward" @image-file="setFile($event, awardForm, 'image')"
            @attachment-file="setFile($event, awardForm, 'attachment')" @import="importCmsFile($event, 'awards')"
            @save="saveAward" @delete="deleteAward"
          />
        </el-tab-pane>


      </el-tabs>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { cmsApi, type CmsNewsArticle } from '../../api/cms'
import type { Award, ContactInfo, HomeBanner, Member, NewsCategory, Patent, Project, Publication, ResearchDirection, SiteSetting } from '../../api/publicPortal'
import InternalLayout from '../../layouts/InternalLayout.vue'
import { useSiteBrandStore } from '../../stores/siteBrand'
import CmsBannerEditor from './components/CmsBannerEditor.vue'
import CmsAwardEditor from './components/CmsAwardEditor.vue'
import CmsFooterEditor from './components/CmsFooterEditor.vue'
import CmsMemberEditor from './components/CmsMemberEditor.vue'
import CmsNewsEditor from './components/CmsNewsEditor.vue'
import CmsPatentEditor from './components/CmsPatentEditor.vue'
import CmsProjectEditor from './components/CmsProjectEditor.vue'
import CmsPublicationEditor from './components/CmsPublicationEditor.vue'
import CmsResearchEditor from './components/CmsResearchEditor.vue'
import CmsSiteEditor from './components/CmsSiteEditor.vue'
import { useCmsImport } from './composables/useCmsImport'

type FileField = 'cover_image' | 'avatar' | 'pdf_file' | 'image' | 'attachment' | 'word_file' | 'logo' | 'favicon' | 'hero_image'
type CmsForm = Record<string, unknown>
type Row<T> = {
  key: string | number
  title: string
  meta: string
  source: T
}
type PublicationPreview = {
  authors: string
  title: string
  journal: string
  year: number | string
  volume: string
  issue: string
  pages: string
  doi: string
}


const activeTab = ref('site')
const saving = ref(false)
const uploadingNewsImage = ref(false)
const siteBrand = useSiteBrandStore()
const cmsUploadProgress = ref(0)
const newsUploadProgress = ref(0)
const newsImageUploadProgress = ref(0)
const newsFileInputKey = ref(0)
const newsEditorRef = ref<{ insertImage: (src: string, alt?: string) => void } | null>(null)
const memberAvatarInputKey = ref(0)
const memberAvatarObjectUrl = ref('')
const { importProgress, importingKind, importFile: importCmsFile } = useCmsImport(loadAll)

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

const editingResearchSlug = ref('')
const editingSiteId = ref<number | null>(null)
const editingContactId = ref<number | null>(null)
const editingSiteLogo = ref('')
const editingSiteFavicon = ref('')
const editingSiteHeroImage = ref('')
const editingBannerId = ref<number | null>(null)
const editingBannerImage = ref('')
const editingResearchCover = ref('')
const editingMemberId = ref<number | null>(null)
const editingMemberAvatar = ref('')
const editingNewsSlug = ref('')
const editingNewsId = ref<number | null>(null)
const editingNewsCover = ref('')
const editingNewsWordFile = ref('')
const editingPublicationId = ref<number | null>(null)
const editingPublicationPdf = ref('')
const editingProjectId = ref<number | null>(null)
const editingPatentId = ref<number | null>(null)
const editingAwardId = ref<number | null>(null)
const editingPatentPdf = ref('')
const editingAwardImage = ref('')
const editingAwardAttachment = ref('')

const researchForm = reactive<CmsForm>({ title: '', summary: '', content: '', cover_image: undefined, sort_order: 0 })
const siteForm = reactive<CmsForm>({
  site_name: '中农雨磷',
  site_subtitle: '中国农业大学资源与环境学院',
  keywords: '聚焦微生物生态、有机废弃物资源转化与高值产品开发',
  banner_interval_seconds: 6,
  description: '',
  footer_text: '',
  contact_email: '',
  contact_phone: '',
  address: '',
  logo: undefined,
  favicon: undefined,
  hero_image: undefined,
})
const externalLinks = reactive([
  { label: '中国农业大学', url: 'https://www.cau.edu.cn/' },
  { label: '资源与环境学院', url: 'https://zihuan.cau.edu.cn/' },
  { label: '教师个人主页', url: 'https://faculty.cau.edu.cn/' },
])
const contactForm = reactive<CmsForm>({
  title: '欢迎对微生物生态与农业资源循环感兴趣的同学加入',
  content: '',
  email: '',
  phone: '',
  address: '',
  map_url: '',
})
const bannerForm = reactive<CmsForm>({
  title: '',
  subtitle: '',
  image: undefined,
  link: '',
  sort_order: 0,
  is_active: true,
})
const memberForm = reactive<CmsForm>({
  name: '',
  role_type: '',
  research_direction: '',
  email: '',
  avatar: undefined,
  profile: '',
  sort_order: 0,
})
const newsForm = reactive<CmsForm>({
  title: '',
  summary: '',
  content: '',
  cover_image: undefined,
  word_file: undefined,
  event_date: '',
  location: '',
  category_id: null,
  status: 'published',
  visibility: 'public',
  is_pinned: false,
})
const publicationForm = reactive<CmsForm>({
  citation_text: '',
  title: '',
  authors: '',
  journal: '',
  year: new Date().getFullYear(),
  volume: '',
  issue: '',
  pages: '',
  doi: '',
  impact_factor: '',
  jcr_partition: '',
  cas_partition: '',
  abstract: '',
  pdf_file: undefined,
  visibility: 'public',
  sort_order: 0,
})
const publicationPreview = reactive<PublicationPreview>({
  authors: '',
  title: '',
  journal: '',
  year: '',
  volume: '',
  issue: '',
  pages: '',
  doi: '',
})
const hasPublicationPreview = computed(() => Boolean(
  publicationPreview.title
  || publicationPreview.authors
  || publicationPreview.journal
  || publicationPreview.year
  || publicationPreview.doi,
))
const publicationVolumePreview = computed(() => {
  const volumeIssue = [publicationPreview.volume, publicationPreview.issue ? `(${publicationPreview.issue})` : ''].filter(Boolean).join('')
  return [volumeIssue, publicationPreview.pages].filter(Boolean).join(': ')
})
const projectForm = reactive<CmsForm>({
  title: '',
  project_number: '',
  funding_source: '',
  principal_investigator: '',
  start_date: '',
  end_date: '',
  amount: '',
  status: '',
  visibility: 'public',
  description: '',
  sort_order: 0,
})
const patentForm = reactive<CmsForm>({
  title: '',
  patent_number: '',
  inventors: '',
  application_date: '',
  authorization_date: '',
  status: '',
  pdf_file: undefined,
  visibility: 'public',
  sort_order: 0,
})
const awardForm = reactive<CmsForm>({
  title: '',
  award_level: '',
  award_date: '',
  participants: '',
  description: '',
  image: undefined,
  attachment: undefined,
  visibility: 'public',
  sort_order: 0,
})

const researchRows = computed<Row<ResearchDirection>[]>(() =>
  researchItems.value.map((item) => ({ key: item.slug, title: item.title, meta: item.summary || item.slug, source: item })),
)
const bannerRows = computed<Row<HomeBanner>[]>(() =>
  bannerItems.value.map((item) => ({
    key: item.id,
    title: item.title || '未命名横幅',
    meta: `${item.is_active === false ? '停用' : '启用'} · 排序 ${item.sort_order || 0} · ${displayFileLabel(item.image) || '未上传图片'}`,
    source: item,
  })),
)
const memberRows = computed<Row<Member>[]>(() =>
  memberItems.value.map((item) => ({
    key: item.id,
    title: item.name,
    meta: `${item.sort_order ? `排序 ${item.sort_order}` : '不展示'} · ${roleText(item.role_type) || '身份头衔待补充'} · ${item.research_direction || '研究方向待补充'}`,
    source: item,
  })),
)
const newsRows = computed<Row<CmsNewsArticle>[]>(() =>
  newsItems.value.map((item) => ({
    key: item.slug,
    title: item.title,
    meta: `${item.event_date || '未设置日期'} · ${statusText(item.status)}`,
    source: item,
  })),
)
const selectedNewsWordFile = computed(() => (newsForm.word_file instanceof File ? newsForm.word_file : null))
const newsContent = computed({
  get: () => String(newsForm.content || ''),
  set: (value: string) => {
    newsForm.content = value
  },
})
const selectedMemberAvatar = computed(() => (memberForm.avatar instanceof File ? memberForm.avatar : null))
const memberAvatarPreviewUrl = computed(() => memberAvatarObjectUrl.value || editingMemberAvatar.value)
const publicationRows = computed<Row<Publication>[]>(() =>
  publicationItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${visibilityText(item.visibility)} · ${item.year} · ${item.journal || '期刊待补充'}`, source: item })),
)
const projectRows = computed<Row<Project>[]>(() =>
  projectItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${visibilityText(item.visibility)} · ${item.funding_source || '资助来源待补充'} · ${item.status || '状态待补充'}`, source: item })),
)
const patentRows = computed<Row<Patent>[]>(() =>
  patentItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${visibilityText(item.visibility)} · ${item.patent_number || '专利号待补充'} · ${item.status || '状态待补充'}`, source: item })),
)
const awardRows = computed<Row<Award>[]>(() =>
  awardItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${visibilityText(item.visibility)} · ${item.award_level || '等级待补充'} · ${item.award_date || '日期待补充'}`, source: item })),
)
const cmsOverview = computed(() => [
  { label: '首页设置', value: siteSettings.value.length ? 1 : 0, note: '基础文案与联系信息' },
  { label: '首页横幅', value: bannerItems.value.length, note: '轮播图片' },
  { label: '研究方向', value: researchItems.value.length, note: '公开门户展示' },
  { label: '团队成员', value: memberItems.value.length, note: '师生与校友信息' },
  { label: '新闻活动', value: newsItems.value.length, note: '组内动态与活动' },
  { label: '论文成果', value: publicationItems.value.length, note: '科研成果维护' },
  { label: '科研项目', value: projectItems.value.length, note: '项目维护' },
  { label: '专利成果', value: patentItems.value.length, note: '专利维护' },
  { label: '获奖成果', value: awardItems.value.length, note: '获奖维护' },
])

async function loadAll() {
  const [settings, contacts, banners, research, members, categories, news, publications, projects, patents, awards] = await Promise.allSettled([
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
  const settingsValue = resultValue(settings, siteSettings.value)
  const contactsValue = resultValue(contacts, contactInfoItems.value)
  siteSettings.value = settingsValue
  contactInfoItems.value = contactsValue
  fillSiteForms(settingsValue[0], contactsValue[0])
  bannerItems.value = resultValue(banners, bannerItems.value)
  researchItems.value = resultValue(research, researchItems.value)
  memberItems.value = resultValue(members, memberItems.value)
  newsCategories.value = resultValue(categories, newsCategories.value)
  newsItems.value = resultValue(news, newsItems.value)
  publicationItems.value = resultValue(publications, publicationItems.value)
  projectItems.value = resultValue(projects, projectItems.value)
  patentItems.value = resultValue(patents, patentItems.value)
  awardItems.value = resultValue(awards, awardItems.value)

  if ([settings, contacts, banners, research, members, categories, news, publications, projects, patents, awards].some((item) => item.status === 'rejected')) {
    ElMessage.warning('部分门户内容加载失败，请刷新或检查当前账号是否有门户编辑权限。')
  }
}

function resultValue<T>(result: PromiseSettledResult<T[]>, fallback: T[]) {
  return result.status === 'fulfilled' ? result.value : fallback
}

function fillSiteForms(setting?: SiteSetting, contact?: ContactInfo) {
  editingSiteId.value = setting?.id || null
  editingContactId.value = contact?.id || null
  editingSiteLogo.value = setting?.logo || ''
  editingSiteFavicon.value = setting?.favicon || ''
  editingSiteHeroImage.value = setting?.hero_image || ''
  Object.assign(siteForm, {
    site_name: setting?.site_name || '中农雨磷',
    site_subtitle: setting?.site_subtitle || '中国农业大学资源与环境学院',
    keywords: setting?.keywords || '聚焦微生物生态、有机废弃物资源转化与高值产品开发',
    banner_interval_seconds: setting?.banner_interval_seconds || 6,
    description: setting?.description || '',
    footer_text: setting?.footer_text || '',
    contact_email: setting?.contact_email || '',
    contact_phone: setting?.contact_phone || '',
    address: setting?.address || '',
    logo: undefined,
    favicon: undefined,
    hero_image: undefined,
  })
  fillExternalLinks(setting?.external_links)
  Object.assign(contactForm, {
    title: contact?.title || '欢迎对微生物生态与农业资源循环感兴趣的同学加入',
    content: contact?.content || '',
    email: contact?.email || setting?.contact_email || '',
    phone: contact?.phone || setting?.contact_phone || '',
    address: contact?.address || setting?.address || '',
    map_url: contact?.map_url || '',
  })
}

function applyExternalLinksToSiteForm() {
  siteForm.external_links = externalLinks
    .map((link) => ({ label: link.label.trim(), url: link.url.trim() }))
    .filter((link) => link.label && link.url)
}

function fillExternalLinks(links?: SiteSetting['external_links']) {
  const defaults = [
    { label: '中国农业大学', url: 'https://www.cau.edu.cn/' },
    { label: '资源与环境学院', url: 'https://zihuan.cau.edu.cn/' },
    { label: '教师个人主页', url: 'https://faculty.cau.edu.cn/' },
  ]
  const nextLinks = links?.length ? links : defaults
  externalLinks.splice(0, externalLinks.length, ...nextLinks.slice(0, 5).map((link) => ({
    label: link.label || '',
    url: link.url || '',
  })))
  while (externalLinks.length < 3) externalLinks.push({ label: '', url: '' })
}

async function saveHomeContent() {
  saving.value = true
  cmsUploadProgress.value = 0
  const onUploadProgress = createCmsUploadProgressHandler()
  try {
    siteForm.contact_email = contactForm.email || siteForm.contact_email || ''
    contactForm.title = '加入我们'
    contactForm.phone = ''
    contactForm.address = siteForm.address || ''
    contactForm.map_url = ''
    applyExternalLinksToSiteForm()
    await Promise.all([
      editingContactId.value ? cmsApi.updateContactInfo(editingContactId.value, contactForm, onUploadProgress) : cmsApi.createContactInfo(contactForm, onUploadProgress),
      editingSiteId.value ? cmsApi.updateSiteSetting(editingSiteId.value, siteForm, onUploadProgress) : cmsApi.createSiteSetting(siteForm, onUploadProgress),
    ])
    if (cmsUploadProgress.value > 0) cmsUploadProgress.value = 100
    await loadAll()
    await siteBrand.load(true)
    ElMessage.success('内容已保存')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败，请检查权限和表单内容')
  } finally {
    saving.value = false
    resetCmsUploadProgressSoon()
  }
}

async function saveFooterContent() {
  applyExternalLinksToSiteForm()
  await save((onUploadProgress) =>
    editingSiteId.value ? cmsApi.updateSiteSetting(editingSiteId.value, siteForm, onUploadProgress) : cmsApi.createSiteSetting(siteForm, onUploadProgress),
  )
  await siteBrand.load(true)
}

function setFile(event: Event, form: CmsForm, field: FileField) {
  const input = event.target as HTMLInputElement
  form[field] = input.files?.[0]
  if (form === memberForm && field === 'avatar') {
    releaseMemberAvatarPreview()
    const file = input.files?.[0]
    if (file) memberAvatarObjectUrl.value = URL.createObjectURL(file)
  }
  if (form === newsForm && (field === 'word_file' || field === 'cover_image')) newsUploadProgress.value = 0
}

function releaseMemberAvatarPreview() {
  if (memberAvatarObjectUrl.value) URL.revokeObjectURL(memberAvatarObjectUrl.value)
  memberAvatarObjectUrl.value = ''
}

function displayFileName(value?: string | null) {
  if (!value) return ''
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

function displayFileLabel(value?: string | null) {
  if (!value) return ''
  const size = findUploadedFileSize(value)
  return size ? `${displayFileName(value)}（${formatFileSize(size)}）` : displayFileName(value)
}

function findUploadedFileSize(value: string) {
  const match = (url?: string | null) => Boolean(url && value && (url === value || url.split('?')[0] === value.split('?')[0]))
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

function formatFileSize(size: number) {
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

function createCmsUploadProgressHandler() {
  return (event: { loaded: number; total?: number }) => {
    if (!event.total) return
    cmsUploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
  }
}

function resetCmsUploadProgressSoon() {
  setTimeout(() => {
    if (!saving.value) cmsUploadProgress.value = 0
  }, 800)
}

function uploadErrorMessage(error: any, fallback: string) {
  const data = error?.response?.data
  if (data?.detail) return data.detail
  if (data?.word_file?.length) return data.word_file[0]
  if (data?.image?.length) return data.image[0]
  if (data?.cover_image?.length) return data.cover_image[0]
  if (error?.code === 'ECONNABORTED') return '上传超时，请检查网络后重试。'
  if (!error?.response) return '上传连接失败，请检查网络或服务器上传限制。'
  return fallback
}

function resetBanner() {
  editingBannerId.value = null
  editingBannerImage.value = ''
  Object.assign(bannerForm, {
    title: '',
    subtitle: '',
    image: undefined,
    link: '',
    sort_order: 0,
    is_active: true,
  })
}

function editBanner(item: HomeBanner) {
  editingBannerId.value = item.id
  editingBannerImage.value = item.image || ''
  Object.assign(bannerForm, {
    title: item.title || '',
    subtitle: item.subtitle || '',
    image: undefined,
    link: item.link || '',
    sort_order: item.sort_order || 0,
    is_active: item.is_active !== false,
  })
}

async function saveBanner() {
  await save((onUploadProgress) =>
    editingBannerId.value ? cmsApi.updateHomeBanner(editingBannerId.value, bannerForm, onUploadProgress) : cmsApi.createHomeBanner(bannerForm, onUploadProgress),
  )
  resetBanner()
}

async function deleteBanner() {
  if (!editingBannerId.value) return
  await removeAfterConfirm('确定删除这张首页横幅吗？', () => cmsApi.deleteHomeBanner(editingBannerId.value as number), resetBanner)
}

function resetResearch() {
  editingResearchSlug.value = ''
  editingResearchCover.value = ''
  Object.assign(researchForm, { title: '', summary: '', content: '', cover_image: undefined, sort_order: 0 })
}

function editResearch(item: ResearchDirection) {
  editingResearchSlug.value = item.slug
  editingResearchCover.value = item.cover_image || ''
  Object.assign(researchForm, {
    title: item.title,
    summary: item.summary,
    content: item.content || '',
    cover_image: undefined,
    sort_order: item.sort_order || 0,
  })
}

async function saveResearch() {
  await save((onUploadProgress) => (editingResearchSlug.value ? cmsApi.updateResearch(editingResearchSlug.value, researchForm, onUploadProgress) : cmsApi.createResearch(researchForm, onUploadProgress)))
  resetResearch()
}

async function deleteResearch() {
  await removeAfterConfirm('确定删除这个研究方向吗？', () => cmsApi.deleteResearch(editingResearchSlug.value), resetResearch)
}

function resetMember() {
  releaseMemberAvatarPreview()
  editingMemberId.value = null
  editingMemberAvatar.value = ''
  memberAvatarInputKey.value += 1
  Object.assign(memberForm, {
    name: '',
    role_type: '',
    research_direction: '',
    email: '',
    avatar: undefined,
    profile: '',
    sort_order: 0,
  })
}

function editMember(item: Member) {
  releaseMemberAvatarPreview()
  editingMemberId.value = item.id
  editingMemberAvatar.value = item.avatar || ''
  memberAvatarInputKey.value += 1
  Object.assign(memberForm, {
    name: item.name,
    role_type: item.role_label || item.role_type || '',
    research_direction: item.research_direction || '',
    email: item.email || '',
    avatar: undefined,
    profile: item.profile || '',
    sort_order: (item as Member & { sort_order?: number }).sort_order || 0,
  })
}

async function saveMember() {
  await save((onUploadProgress) => (editingMemberId.value ? cmsApi.updateMember(editingMemberId.value, memberForm, onUploadProgress) : cmsApi.createMember(memberForm, onUploadProgress)))
  resetMember()
}

async function deleteMember() {
  if (!editingMemberId.value) return
  await removeAfterConfirm('确定删除这个团队成员吗？', () => cmsApi.deleteMember(editingMemberId.value as number), resetMember)
}

function resetNews() {
  editingNewsSlug.value = ''
  editingNewsId.value = null
  editingNewsCover.value = ''
  editingNewsWordFile.value = ''
  newsFileInputKey.value += 1
  newsUploadProgress.value = 0
  Object.assign(newsForm, {
    title: '',
    summary: '',
    content: '',
    cover_image: undefined,
    word_file: undefined,
    event_date: '',
    location: '',
    category_id: null,
    status: 'published',
    visibility: 'public',
    is_pinned: false,
  })
}

function editNews(item: CmsNewsArticle) {
  editingNewsSlug.value = item.slug
  editingNewsId.value = item.id
  editingNewsCover.value = item.cover_image || ''
  editingNewsWordFile.value = item.word_file || ''
  newsFileInputKey.value += 1
  newsUploadProgress.value = 0
  Object.assign(newsForm, {
    title: item.title,
    summary: item.summary || '',
    content: item.word_html || item.content || '',
    cover_image: undefined,
    word_file: undefined,
    event_date: item.event_date || '',
    location: item.location || '',
    category_id: item.category?.id || null,
    status: item.status || 'published',
    visibility: item.visibility || 'public',
    is_pinned: item.is_pinned || false,
  })
}

async function saveNews() {
  saving.value = true
  newsUploadProgress.value = 0
  try {
    const onUploadProgress = (event: { loaded: number; total?: number }) => {
      if (!event.total) return
      newsUploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    }
    const saved = editingNewsSlug.value
      ? await cmsApi.updateNews(editingNewsSlug.value, newsForm, onUploadProgress)
      : await cmsApi.createNews(newsForm, onUploadProgress)
    newsUploadProgress.value = 100
    newsFileInputKey.value += 1
    await loadAll()
    editNews(saved)
    ElMessage.success('新闻已保存')
  } catch (error: any) {
    ElMessage.error(uploadErrorMessage(error, '保存失败，请检查权限和表单内容。'))
  } finally {
    saving.value = false
    setTimeout(() => {
      if (!saving.value) newsUploadProgress.value = 0
    }, 800)
  }
}

async function deleteNews() {
  await removeAfterConfirm('确定删除这条新闻吗？', () => cmsApi.deleteNews(editingNewsSlug.value), resetNews)
}

async function ensureNewsDraft() {
  if (editingNewsId.value) return editingNewsId.value
  const title = String(newsForm.title || '').trim()
  if (!title) {
    ElMessage.warning('请先填写新闻标题，再插入图片。')
    return null
  }
  const saved = await cmsApi.createNews({
    title,
    summary: newsForm.summary || '',
    content: newsForm.content || '',
    event_date: newsForm.event_date || '',
    location: newsForm.location || '',
    category_id: newsForm.category_id,
    status: 'draft',
    visibility: newsForm.visibility || 'public',
    is_pinned: false,
  })
  editingNewsId.value = saved.id
  editingNewsSlug.value = saved.slug
  newsForm.status = 'draft'
  await loadAll()
  return saved.id
}

async function insertNewsBodyImage(file: File) {
  uploadingNewsImage.value = true
  newsImageUploadProgress.value = 0
  try {
    const articleId = await ensureNewsDraft()
    if (!articleId) return
    const uploaded = await cmsApi.createNewsImage({
      article_id: articleId,
      image: file,
      caption: '正文插图',
      sort_order: 0,
    }, (event) => {
      if (!event.total) return
      newsImageUploadProgress.value = Math.min(99, Math.round((event.loaded / event.total) * 100))
    })
    newsImageUploadProgress.value = 100
    newsEditorRef.value?.insertImage(uploaded.image, file.name)
    ElMessage.success('图片已插入正文，请保存新闻。')
  } catch (error: any) {
    ElMessage.error(uploadErrorMessage(error, '图片上传失败'))
  } finally {
    uploadingNewsImage.value = false
    setTimeout(() => {
      if (!uploadingNewsImage.value) newsImageUploadProgress.value = 0
    }, 800)
  }
}

function resetPublication() {
  editingPublicationId.value = null
  editingPublicationPdf.value = ''
  Object.assign(publicationForm, {
    citation_text: '',
    title: '',
    authors: '',
    journal: '',
    year: new Date().getFullYear(),
    volume: '',
    issue: '',
    pages: '',
    doi: '',
    impact_factor: '',
    jcr_partition: '',
    cas_partition: '',
    abstract: '',
    pdf_file: undefined,
    visibility: 'public',
    sort_order: 0,
  })
  clearPublicationPreview()
}

function editPublication(item: Publication) {
  editingPublicationId.value = item.id
  editingPublicationPdf.value = item.pdf_file || ''
  Object.assign(publicationForm, {
    citation_text: formatPublicationCitation(item),
    title: item.title,
    authors: item.authors,
    journal: item.journal || '',
    year: item.year,
    volume: item.volume || '',
    issue: item.issue || '',
    pages: item.pages || '',
    doi: item.doi || '',
    impact_factor: item.impact_factor || '',
    jcr_partition: item.jcr_partition || '',
    cas_partition: item.cas_partition || '',
    abstract: item.abstract || '',
    pdf_file: undefined,
    visibility: item.visibility || 'public',
    sort_order: (item as Publication & { sort_order?: number }).sort_order || 0,
  })
  applyPublicationPreview({
    title: item.title || '',
    authors: item.authors || '',
    journal: item.journal || '',
    year: item.year || '',
    volume: item.volume || '',
    issue: item.issue || '',
    pages: item.pages || '',
    doi: item.doi || '',
  }, false)
}

function clearPublicationPreview() {
  Object.assign(publicationPreview, {
    authors: '',
    title: '',
    journal: '',
    year: '',
    volume: '',
    issue: '',
    pages: '',
    doi: '',
  })
}

function applyPublicationPreview(parsed: Partial<PublicationPreview>, writeForm = true) {
  Object.assign(publicationPreview, {
    authors: parsed.authors || '',
    title: parsed.title || '',
    journal: parsed.journal || '',
    year: parsed.year || '',
    volume: parsed.volume || '',
    issue: parsed.issue || '',
    pages: parsed.pages || '',
    doi: parsed.doi || '',
  })
  if (!writeForm) return
  Object.entries(publicationPreview).forEach(([key, value]) => {
    publicationForm[key] = value
  })
}

async function parsePublicationCitation(showMessage = true) {
  const citation = String(publicationForm.citation_text || '').replace(/\s+/g, ' ').trim()
  if (!citation) {
    clearPublicationPreview()
    if (showMessage) ElMessage.warning('请先填写 GB/T 7714-2025 格式引文。')
    return false
  }
  let parsed
  try {
    parsed = await cmsApi.parsePublicationCitation(citation)
  } catch (error: any) {
    if (showMessage) ElMessage.error(uploadErrorMessage(error, '引文拆分失败，请稍后重试。'))
    return false
  }
  applyPublicationPreview(parsed)
  if (!parsed.complete) {
    if (showMessage) ElMessage.warning('拆分结果不完整，请检查预览后补充缺失信息。')
    return false
  }
  if (showMessage) ElMessage.success('已拆分，请检查预览结果后保存。')
  return true
}

function formatPublicationCitation(item: Publication) {
  const volumeIssue = [item.volume, item.issue ? `(${item.issue})` : ''].filter(Boolean).join('')
  const pages = item.pages ? `: ${item.pages}` : ''
  const meta = [item.year, [volumeIssue, pages].filter(Boolean).join('')].filter(Boolean).join(', ')
  const doi = item.doi ? ` DOI: ${item.doi}` : ''
  return [item.authors, item.title, item.journal, meta].filter(Boolean).join('. ') + doi
}

function publicationPayload() {
  const { citation_text: _citationText, ...payload } = publicationForm
  return payload
}

async function savePublication() {
  const parsed = await parsePublicationCitation(false)
  if (!parsed) {
    ElMessage.warning('请先点击“拆分并预览”，确认结果后再保存。')
    return
  }
  const payload = publicationPayload()
  await save((onUploadProgress) =>
    editingPublicationId.value ? cmsApi.updatePublication(editingPublicationId.value, payload, onUploadProgress) : cmsApi.createPublication(payload, onUploadProgress),
  )
  resetPublication()
}

async function deletePublication() {
  if (!editingPublicationId.value) return
  await removeAfterConfirm('确定删除这篇论文吗？', () => cmsApi.deletePublication(editingPublicationId.value as number), resetPublication)
}

function resetProject() {
  editingProjectId.value = null
  Object.assign(projectForm, {
    title: '',
    project_number: '',
    funding_source: '',
    principal_investigator: '',
    start_date: '',
    end_date: '',
    amount: '',
    status: '',
    visibility: 'public',
    description: '',
    sort_order: 0,
  })
}

function editProject(item: Project) {
  editingProjectId.value = item.id
  Object.assign(projectForm, {
    title: item.title,
    project_number: item.project_number || '',
    funding_source: item.funding_source || '',
    principal_investigator: item.principal_investigator || '',
    start_date: item.start_date || '',
    end_date: item.end_date || '',
    amount: item.amount || '',
    status: item.status || '',
    visibility: (item as Project & { visibility?: string }).visibility || 'public',
    description: item.description || '',
    sort_order: item.sort_order || 0,
  })
}

async function saveProject() {
  await save((onUploadProgress) => (editingProjectId.value ? cmsApi.updateProject(editingProjectId.value, projectForm, onUploadProgress) : cmsApi.createProject(projectForm, onUploadProgress)))
  resetProject()
}

async function deleteProject() {
  if (!editingProjectId.value) return
  await removeAfterConfirm('确定删除这个科研项目吗？', () => cmsApi.deleteProject(editingProjectId.value as number), resetProject)
}

function resetPatent() {
  editingPatentId.value = null
  editingPatentPdf.value = ''
  Object.assign(patentForm, {
    title: '',
    patent_number: '',
    inventors: '',
    application_date: '',
    authorization_date: '',
    status: '',
    pdf_file: undefined,
    visibility: 'public',
    sort_order: 0,
  })
}

function editPatent(item: Patent) {
  editingPatentId.value = item.id
  editingPatentPdf.value = item.pdf_file || ''
  Object.assign(patentForm, {
    title: item.title,
    patent_number: item.patent_number || '',
    inventors: item.inventors || '',
    application_date: item.application_date || '',
    authorization_date: item.authorization_date || '',
    status: item.status || '',
    pdf_file: undefined,
    visibility: (item as Patent & { visibility?: string }).visibility || 'public',
    sort_order: item.sort_order || 0,
  })
}

async function savePatent() {
  await save((onUploadProgress) => (editingPatentId.value ? cmsApi.updatePatent(editingPatentId.value, patentForm, onUploadProgress) : cmsApi.createPatent(patentForm, onUploadProgress)))
  resetPatent()
}

async function deletePatent() {
  if (!editingPatentId.value) return
  await removeAfterConfirm('确定删除这个专利成果吗？', () => cmsApi.deletePatent(editingPatentId.value as number), resetPatent)
}

function resetAward() {
  editingAwardId.value = null
  editingAwardImage.value = ''
  editingAwardAttachment.value = ''
  Object.assign(awardForm, {
    title: '',
    award_level: '',
    award_date: '',
    participants: '',
    description: '',
    image: undefined,
    attachment: undefined,
    visibility: 'public',
    sort_order: 0,
  })
}

function editAward(item: Award) {
  editingAwardId.value = item.id
  editingAwardImage.value = item.image || ''
  editingAwardAttachment.value = item.attachment || ''
  Object.assign(awardForm, {
    title: item.title,
    award_level: item.award_level || '',
    award_date: item.award_date || '',
    participants: item.participants || '',
    description: item.description || '',
    image: undefined,
    attachment: undefined,
    visibility: item.visibility || 'public',
    sort_order: item.sort_order || 0,
  })
}

async function saveAward() {
  await save((onUploadProgress) => (editingAwardId.value ? cmsApi.updateAward(editingAwardId.value, awardForm, onUploadProgress) : cmsApi.createAward(awardForm, onUploadProgress)))
  resetAward()
}

async function deleteAward() {
  if (!editingAwardId.value) return
  await removeAfterConfirm('确定删除这个获奖成果吗？', () => cmsApi.deleteAward(editingAwardId.value as number), resetAward)
}

async function save(action: (onUploadProgress?: (event: { loaded: number; total?: number }) => void) => Promise<unknown>) {
  saving.value = true
  cmsUploadProgress.value = 0
  const onUploadProgress = createCmsUploadProgressHandler()
  try {
    await action(onUploadProgress)
    if (cmsUploadProgress.value > 0) cmsUploadProgress.value = 100
    await loadAll()
    ElMessage.success('内容已保存')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败，请检查权限和表单内容')
  } finally {
    saving.value = false
    resetCmsUploadProgressSoon()
  }
}

async function removeAfterConfirm(message: string, action: () => Promise<unknown>, reset: () => void) {
  try {
    await ElMessageBox.confirm(message, '删除确认', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' })
    await save(action)
    reset()
  } catch (error: any) {
    if (error !== 'cancel') ElMessage.error('删除失败')
  }
}

function roleText(role: string) {
  return (
    {
      PI: '硕博导师',
      teacher: '教师',
      postdoc: '博士后',
      phd: '博士生',
      master: '硕士生',
      undergraduate: '本科生',
      alumni: '已毕业学生',
      visitor: '访问学生',
    }[role] || role
  )
}

function statusText(status: string) {
  return ({ draft: '草稿', published: '已发布', archived: '已归档' }[status] || status)
}

function visibilityText(visibility?: string) {
  return ({ public: '公开', members: '成员可见', admins: '管理员可见' }[visibility || ''] || '未设置')
}

onMounted(loadAll)
onBeforeUnmount(releaseMemberAvatarPreview)
</script>

<style>
.cms-page {
  display: grid;
  gap: 12px;
}

.cms-heading {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  background: #fff;
  box-shadow: none;
}

.cms-heading h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 24px;
  font-weight: 650;
  line-height: 1.2;
  white-space: nowrap;
}

.heading-actions {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: 12px;
}

.cms-stat-strip {
  display: flex;
  flex: 1 1 auto;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}

.cms-stat-strip span {
  border: 1px solid var(--color-line);
  border-radius: 999px;
  padding: 5px 9px;
  background: var(--color-panel);
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 600;
}

.preview-link {
  border: 1px solid rgba(0, 135, 60, 0.28);
  border-radius: var(--radius-sm);
  padding: 8px 13px;
  background: #fff;
  color: var(--color-cau-green);
  font-weight: 700;
  white-space: nowrap;
}

.preview-link.subtle {
  border-color: var(--color-border);
  color: var(--color-muted);
}

.cms-tabs {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 10px 14px 16px;
  background: #fff;
  box-shadow: none;
}

.cms-tabs .el-tabs__header {
  margin-bottom: 12px;
}

.cms-tabs .el-tabs__nav-wrap::after {
  height: 1px;
  background: var(--color-line);
}

.editor-grid {
  display: grid;
  grid-template-columns: minmax(340px, 400px) minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
}

.editor-single {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.list-panel,
.form-panel {
  border-radius: var(--radius-md);
}

.list-panel {
  position: relative;
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) auto;
  height: 100%;
  overflow: hidden;
  padding: 18px;
  box-shadow: none;
}

.form-panel {
  padding: 18px 20px;
  box-shadow: none;
}

.site-form-panel {
  min-height: 100%;
}

.form-section {
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  margin-bottom: 14px;
  padding: 14px;
  background: rgba(251, 252, 251, 0.72);
}

.list-panel:hover,
.form-panel:hover {
  transform: none;
}

.panel-heading,
.list-toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 10px;
}

.list-panel .list-toolbar {
  align-items: flex-start;
  border-bottom: 1px solid var(--color-line);
  margin-bottom: 12px;
  min-height: 58px;
  padding-bottom: 12px;
}

.list-panel .list-toolbar strong,
.list-panel .list-toolbar span {
  display: block;
}

.list-panel .list-toolbar > div {
  min-width: 0;
}

.list-panel .list-toolbar strong {
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.list-panel .list-toolbar span {
  margin-top: 2px;
  color: var(--color-muted);
  font-size: 12px;
}

.list-panel .list-toolbar .el-button {
  --el-button-size: 32px;
  flex: 0 0 auto;
  min-height: 32px;
  padding: 7px 12px;
  color: #fff !important;
}

.cms-page .el-button--primary,
.cms-page .el-button--primary span {
  color: #fff !important;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.list-panel .list-search {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 36px;
  margin-bottom: 10px;
  padding: 0 11px;
  background: #fff;
  color: var(--color-text);
  font: inherit;
}

.list-panel .list-search:focus {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

.list-panel .content-list-scroll {
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 6px;
}

.list-panel .content-row {
  display: block;
  width: 100%;
  border: 1px solid var(--color-line);
  border-radius: 8px;
  margin-bottom: 10px;
  padding: 12px 13px;
  background: #fff;
  cursor: pointer;
  text-align: left;
}

.list-panel .content-row:hover,
.list-panel .content-row.active {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
}

.list-panel .content-row:hover strong,
.list-panel .content-row.active strong {
  color: var(--color-cau-green);
}

.list-panel .content-row strong,
.list-panel .content-row span,
.form-panel small {
  display: block;
}

.list-panel .content-row strong {
  display: block;
  overflow: hidden;
  color: var(--color-text);
  font-size: 14px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel .content-row span,
.form-panel small,
.empty-list {
  color: var(--color-muted);
  font-size: 13px;
}

.list-panel .content-row span {
  margin-top: 7px;
  overflow: hidden;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel .empty-list {
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

.list-panel .list-pager {
  display: grid;
  justify-items: center;
  align-items: center;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  margin-top: 10px;
  padding-top: 10px;
  background: #fff;
}

.list-panel .pager-summary {
  flex: 0 0 auto;
  color: var(--color-text);
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.list-panel .pager-controls {
  display: grid;
  grid-template-columns: 68px minmax(54px, 1fr) 68px;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
}

.news-editor-grid {
  grid-template-columns: minmax(290px, 340px) minmax(0, 1fr);
  align-items: start;
}

.news-form-panel {
  min-width: 0;
}

.news-body-field .el-form-item__content {
  display: block;
}

.news-body-field .rich-editor {
  width: 100%;
}

.news-assets-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin: 2px 0 14px;
}

.news-asset-field {
  display: grid;
  align-content: start;
  gap: 7px;
  min-width: 0;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: #fafcfb;
}

.news-asset-field strong {
  color: var(--color-deep-green);
  font-size: 14px;
}

.news-asset-field small {
  overflow: hidden;
  color: var(--color-muted);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.news-save-progress {
  margin-top: 0;
}

.member-avatar-field {
  display: grid;
  grid-template-columns: 104px minmax(0, 1fr);
  align-items: center;
  gap: 16px;
  width: 100%;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  padding: 12px;
  background: #fafcfb;
}

.member-avatar-preview {
  display: grid;
  place-items: center;
  width: 104px;
  aspect-ratio: 4 / 5;
  overflow: hidden;
  border: 1px solid rgba(31, 61, 43, 0.12);
  border-radius: 7px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 22px;
  font-weight: 650;
}

.member-avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}

.member-avatar-control {
  display: grid;
  min-width: 0;
  gap: 7px;
}

.member-avatar-control small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel .page-size-select {
  flex: 0 0 108px;
  width: 116px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  min-height: 30px;
  padding: 0 8px;
  background: #fff;
  color: var(--color-text);
  font-size: 13px;
}

.list-panel .list-pager button {
  border: 1px solid rgba(0, 135, 60, 0.22);
  border-radius: var(--radius-sm);
  min-height: 30px;
  padding: 0 10px;
  background: #fff;
  color: var(--color-cau-green);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.list-panel .list-pager button:disabled {
  border-color: var(--color-border);
  color: var(--color-muted);
  cursor: not-allowed;
  opacity: 0.6;
}

.list-panel .pager-controls span {
  color: var(--color-muted);
  font-size: 13px;
  font-variant-numeric: tabular-nums;
  text-align: center;
}

.editor-hint {
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-sm);
  margin: -4px 0 18px;
  padding: 12px 14px;
  background: var(--color-eco-green);
}

.editor-hint strong {
  color: var(--color-deep-green);
  font-size: 14px;
}

.editor-hint p {
  margin: 4px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.65;
}

.import-strip {
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-sm);
  padding: 10px 12px;
  background: var(--color-panel);
}

.cms-import-block {
  grid-column: 1 / -1;
}

.import-progress {
  grid-column: 1 / -1;
  margin: -4px 0 0;
}

.import-strip span {
  min-width: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.import-strip input {
  display: none;
}

.import-strip a,
.import-strip button {
  flex: 0 0 auto;
  border: 1px solid rgba(0, 135, 60, 0.22);
  border-radius: 999px;
  padding: 5px 12px;
  background: #fff;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
  line-height: 1.4;
  text-decoration: none;
  white-space: nowrap;
}

.import-strip a:hover,
.import-strip button:hover {
  border-color: var(--color-primary);
  background: rgba(0, 135, 60, 0.06);
}

.news-gallery-manager {
  display: grid;
  gap: 12px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  margin: 0 0 18px;
  padding: 14px;
  background: var(--color-panel);
}

.gallery-heading {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.gallery-heading strong {
  color: var(--color-deep-green);
}

.gallery-heading p {
  margin: 3px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
}

.gallery-heading span {
  flex: 0 0 auto;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}

.gallery-grid article {
  overflow: hidden;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-sm);
  background: #fff;
}

.gallery-grid img {
  display: block;
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

.gallery-grid article > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 9px;
}

.gallery-grid article span {
  min-width: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.gallery-grid article button {
  border: 0;
  background: transparent;
  color: #9f312f;
  cursor: pointer;
  font-size: 12px;
  font-weight: 700;
}

.gallery-upload {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr) auto auto;
  gap: 10px;
  align-items: center;
}

.form-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--color-line);
  margin-bottom: 14px;
  padding-bottom: 12px;
}

.form-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.form-heading h2 {
  margin: 4px 0 0;
  color: var(--color-deep-green);
  font-size: 20px;
  font-weight: 650;
  line-height: 1.3;
}

.form-heading p {
  max-width: 620px;
  margin: 8px 0 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
}

.legacy-banner-note {
  display: grid;
  grid-template-columns: 132px minmax(0, 1fr);
  gap: 12px;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  padding: 12px;
  background: rgba(234, 245, 238, 0.62);
}

.legacy-banner-note img {
  width: 132px;
  height: 78px;
  border-radius: 8px;
  background: var(--color-line);
  object-fit: cover;
}

.legacy-banner-note div {
  display: grid;
  align-content: center;
  gap: 3px;
  min-width: 0;
}

.legacy-banner-note strong {
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 650;
}

.legacy-banner-note span,
.legacy-banner-note small {
  overflow: hidden;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.55;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.form-panel .el-form-item {
  margin-bottom: 14px;
}

.form-panel .el-textarea__inner {
  line-height: 1.7;
}

.form-two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.form-three-col {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.secondary-inline-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 135, 60, 0.24);
  border-radius: var(--radius-xs);
  margin: -4px 0 14px;
  padding: 6px 12px;
  background: #fff;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
}

.secondary-inline-action:hover {
  border-color: var(--color-primary);
  background: rgba(0, 135, 60, 0.06);
}

.list-panel .list-pager .pager-nav {
  display: inline-grid;
  place-items: center;
  width: 68px;
  padding: 0;
  line-height: 1;
  text-align: center;
}

.citation-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: -4px 0 12px;
}

.citation-actions .secondary-inline-action {
  margin: 0;
}

.citation-actions span {
  color: var(--color-muted);
  font-size: 13px;
}

.citation-preview {
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  padding: 12px 14px;
  background: rgba(234, 245, 238, 0.52);
}

.citation-preview__title {
  margin-bottom: 10px;
  color: var(--color-deep-green);
  font-size: 14px;
  font-weight: 700;
}

.citation-preview dl {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px 16px;
  margin: 0;
}

.citation-preview div {
  min-width: 0;
}

.citation-preview dt {
  margin-bottom: 2px;
  color: var(--color-muted);
  font-size: 12px;
}

.citation-preview dd {
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--color-text);
  font-size: 13px;
  line-height: 1.55;
}

.external-link-editor {
  display: grid;
  gap: 8px;
  border: 1px solid var(--color-line);
  border-radius: var(--radius-md);
  margin-bottom: 14px;
  padding: 14px;
  background: rgba(245, 247, 246, 0.72);
}

.subsection-heading {
  display: grid;
  gap: 4px;
  margin-bottom: 2px;
}

.subsection-heading strong {
  color: var(--color-deep-green);
  font-size: 15px;
}

.subsection-heading span {
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
}

.file-input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 10px 11px;
  background: #fff;
}

.upload-progress {
  display: grid;
  gap: 6px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  margin-bottom: 14px;
  padding: 12px;
  background: var(--color-soft-gray);
}

.upload-progress span {
  color: var(--color-muted);
  font-size: 13px;
}

.form-actions {
  position: sticky;
  bottom: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  margin: 18px -20px -18px;
  padding: 12px 20px;
  background: rgba(251, 252, 251, 0.96);
  backdrop-filter: blur(8px);
}

.inline-upload-progress {
  width: 100%;
  margin-bottom: 2px;
}

@media (max-width: 980px) {
  .editor-grid,
  .editor-single,
  .form-two-col,
  .form-three-col,
  .gallery-upload {
    grid-template-columns: 1fr;
  }

  .news-assets-grid {
    grid-template-columns: 1fr;
  }

  .member-avatar-field {
    grid-template-columns: 84px minmax(0, 1fr);
  }

  .member-avatar-preview {
    width: 84px;
  }

  .cms-heading {
    align-items: flex-start;
    grid-template-columns: 1fr;
  }

  .heading-actions {
    width: 100%;
  }

  .list-panel {
    max-height: none;
  }

  .list-panel .content-list-scroll {
    max-height: 420px;
  }
}

@media (max-width: 720px) {
  .cms-page {
    gap: 10px;
  }

  .cms-heading {
    display: grid;
    gap: 10px;
    padding: 12px 14px;
  }

  .cms-heading h1 {
    font-size: 21px;
  }

  .heading-actions,
  .cms-stat-strip {
    display: grid;
    grid-template-columns: 1fr;
    width: 100%;
    justify-content: stretch;
  }

  .cms-stat-strip {
    max-height: 78px;
    overflow: auto;
  }

  .cms-stat-strip span,
  .preview-link {
    width: 100%;
    text-align: center;
  }

  .cms-tabs {
    border-radius: var(--radius-sm);
    padding: 6px;
  }

  .cms-tabs .el-tabs__header {
    margin-bottom: 8px;
  }

  .cms-tabs .el-tabs__nav-wrap {
    padding: 0;
  }

  .cms-tabs .el-tabs__nav-prev,
  .cms-tabs .el-tabs__nav-next,
  .cms-tabs .el-tabs__active-bar {
    display: none;
  }

  .cms-tabs .el-tabs__nav-scroll {
    overflow: visible;
  }

  .cms-tabs .el-tabs__nav {
    display: grid;
    width: 100%;
    float: none;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
    transform: none !important;
    white-space: normal;
  }

  .cms-tabs .el-tabs__item {
    justify-content: center;
    width: 100%;
    height: 36px;
    border: 1px solid var(--color-line);
    border-radius: var(--radius-sm);
    padding: 0 8px;
    background: var(--color-panel);
    font-size: 13px;
  }

  .cms-tabs .el-tabs__item.is-active {
    border-color: rgba(0, 135, 60, 0.2);
    background: var(--color-eco-green);
  }

  .editor-grid,
  .editor-single {
    gap: 10px;
  }

  .list-panel,
  .form-panel {
    border-radius: var(--radius-sm);
    padding: 12px;
  }

  .list-panel {
    display: block;
    height: auto;
    overflow: visible;
  }

  .list-panel .list-toolbar {
    display: grid;
    grid-template-columns: 1fr;
    gap: 9px;
    min-height: 0;
    margin-bottom: 10px;
    padding-bottom: 10px;
  }

  .list-panel .list-toolbar strong {
    font-size: 17px;
  }

  .list-panel .list-toolbar .el-button {
    width: 100%;
    min-height: 36px;
  }

  .list-panel .list-search {
    min-height: 38px;
    margin-bottom: 10px;
  }

  .list-panel .content-list-scroll {
    max-height: 48vh;
    overflow-y: auto;
    padding-right: 2px;
  }

  .list-panel .content-row {
    margin-bottom: 8px;
    padding: 10px 11px;
  }

  .list-panel .content-row strong,
  .list-panel .content-row span {
    white-space: normal;
  }

  .list-panel .content-row strong {
    display: -webkit-box;
    overflow: hidden;
    line-height: 1.45;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .list-panel .content-row span {
    display: -webkit-box;
    margin-top: 5px;
    overflow: hidden;
    line-height: 1.45;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }

  .list-panel .list-pager {
    gap: 8px;
  }

  .list-panel .list-pager button {
    min-height: 34px;
    padding: 0 8px;
  }

  .list-panel .list-pager span {
    align-self: center;
    white-space: nowrap;
  }

  .import-strip {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 10px;
  }

  .import-strip span {
    white-space: normal;
  }

  .import-strip a,
  .import-strip button {
    width: 100%;
    flex: none;
  }

  .form-heading {
    display: grid;
    gap: 8px;
  }

  .form-heading h2 {
    font-size: 18px;
  }

  .citation-actions {
    align-items: flex-start;
    flex-direction: column;
  }

  .citation-preview dl {
    grid-template-columns: 1fr;
  }

  .form-three-col {
    grid-template-columns: 1fr;
    gap: 0;
  }

  .form-actions {
    position: static;
    display: grid;
    grid-template-columns: 1fr;
    margin: 14px 0 0;
    padding: 12px 0 0;
  }

  .form-actions .el-button {
    width: 100%;
    margin: 0;
  }
}
</style>
