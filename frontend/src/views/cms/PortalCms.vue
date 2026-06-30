<template>
  <InternalLayout title="门户内容管理">
    <section class="cms-page">
      <div class="cms-heading">
        <div>
          <span>Portal CMS</span>
          <h1>官网内容维护</h1>
          <p>维护公开门户的研究方向、团队成员、新闻活动和代表论文；内部仪器信息也在这里统一更新。保存后，相关页面会读取最新内容。</p>
        </div>
        <div class="heading-actions">
          <RouterLink class="preview-link" to="/">预览官网</RouterLink>
          <RouterLink class="preview-link subtle" to="/instruments">查看内部仪器</RouterLink>
        </div>
      </div>

      <section class="cms-overview">
        <article v-for="item in cmsOverview" :key="item.label" class="card overview-card">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <p>{{ item.note }}</p>
        </article>
      </section>

      <el-tabs v-model="activeTab" class="cms-tabs">
        <el-tab-pane label="研究方向" name="research">
          <section class="editor-grid">
            <ContentList title="研究方向" action-label="新增方向" :items="researchRows" :active-key="editingResearchSlug" @create="resetResearch" @edit="editResearch" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingResearchSlug ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ researchForm.title || '研究方向' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="标题"><el-input v-model="researchForm.title" /></el-form-item>
                <el-form-item label="URL 标识"><el-input v-model="researchForm.slug" placeholder="organic-waste-recycling" /></el-form-item>
                <el-form-item label="摘要"><el-input v-model="researchForm.summary" type="textarea" :rows="3" /></el-form-item>
                <el-form-item label="详细内容"><el-input v-model="researchForm.content" type="textarea" :rows="5" /></el-form-item>
                <el-form-item label="封面图">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, researchForm, 'cover_image')" />
                  <small v-if="editingResearchCover">当前图片：{{ editingResearchCover }}</small>
                </el-form-item>
                <el-form-item label="排序"><el-input-number v-model="researchForm.sort_order" :min="0" /></el-form-item>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingResearchSlug)" @save="saveResearch" @delete="deleteResearch" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="团队成员" name="members">
          <section class="editor-grid">
            <ContentList title="团队成员" action-label="新增成员" :items="memberRows" :active-key="editingMemberId || ''" @create="resetMember" @edit="editMember" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingMemberId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ memberForm.name || '团队成员' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <div class="form-two-col">
                  <el-form-item label="姓名"><el-input v-model="memberForm.name" /></el-form-item>
                  <el-form-item label="英文名"><el-input v-model="memberForm.name_en" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="成员类型">
                    <el-select v-model="memberForm.role_type">
                      <el-option label="硕博导师" value="PI" />
                      <el-option label="教师" value="teacher" />
                      <el-option label="博士后" value="postdoc" />
                      <el-option label="博士生" value="phd" />
                      <el-option label="硕士生" value="master" />
                      <el-option label="本科生" value="undergraduate" />
                      <el-option label="已毕业学生" value="alumni" />
                      <el-option label="访问学生" value="visitor" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="年级"><el-input v-model="memberForm.grade" /></el-form-item>
                </div>
                <el-form-item label="研究方向"><el-input v-model="memberForm.research_direction" /></el-form-item>
                <el-form-item label="邮箱"><el-input v-model="memberForm.email" /></el-form-item>
                <el-form-item label="头像">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, memberForm, 'avatar')" />
                  <small v-if="editingMemberAvatar">当前头像：{{ editingMemberAvatar }}</small>
                </el-form-item>
                <el-form-item label="简介"><el-input v-model="memberForm.profile" type="textarea" :rows="4" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="排序"><el-input-number v-model="memberForm.sort_order" :min="0" /></el-form-item>
                  <el-form-item label="公开展示"><el-switch v-model="memberForm.is_public" /></el-form-item>
                </div>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingMemberId)" @save="saveMember" @delete="deleteMember" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="新闻活动" name="news">
          <section class="editor-grid">
            <ContentList title="新闻活动" action-label="新增新闻" :items="newsRows" :active-key="editingNewsSlug" @create="resetNews" @edit="editNews" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingNewsSlug ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ newsForm.title || '新闻活动' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="标题"><el-input v-model="newsForm.title" /></el-form-item>
                <el-form-item label="URL 标识"><el-input v-model="newsForm.slug" placeholder="field-sampling-2026" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="活动日期"><el-date-picker v-model="newsForm.event_date" type="date" value-format="YYYY-MM-DD" /></el-form-item>
                  <el-form-item label="地点"><el-input v-model="newsForm.location" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="分类">
                    <el-select v-model="newsForm.category_id" clearable placeholder="选择分类">
                      <el-option v-for="category in newsCategories" :key="category.id" :label="category.name" :value="category.id" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="状态">
                    <el-select v-model="newsForm.status">
                      <el-option label="草稿" value="draft" />
                      <el-option label="发布" value="published" />
                      <el-option label="归档" value="archived" />
                    </el-select>
                  </el-form-item>
                </div>
                <el-form-item label="摘要"><el-input v-model="newsForm.summary" type="textarea" :rows="3" /></el-form-item>
                <el-form-item label="正文"><el-input v-model="newsForm.content" type="textarea" :rows="7" /></el-form-item>
                <el-form-item label="封面图">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, newsForm, 'cover_image')" />
                  <small v-if="editingNewsCover">当前封面：{{ editingNewsCover }}</small>
                </el-form-item>
                <div class="form-two-col">
                  <el-form-item label="可见范围">
                    <el-select v-model="newsForm.visibility">
                      <el-option label="公开" value="public" />
                      <el-option label="成员可见" value="members" />
                      <el-option label="管理员可见" value="admins" />
                    </el-select>
                  </el-form-item>
                  <el-form-item label="置顶"><el-switch v-model="newsForm.is_pinned" /></el-form-item>
                </div>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingNewsSlug)" @save="saveNews" @delete="deleteNews" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="代表论文" name="publications">
          <section class="editor-grid">
            <ContentList title="论文成果" action-label="新增论文" :items="publicationRows" :active-key="editingPublicationId || ''" @create="resetPublication" @edit="editPublication" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingPublicationId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ publicationForm.title || '代表论文' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="论文题目"><el-input v-model="publicationForm.title" /></el-form-item>
                <el-form-item label="作者"><el-input v-model="publicationForm.authors" type="textarea" :rows="2" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="期刊"><el-input v-model="publicationForm.journal" /></el-form-item>
                  <el-form-item label="年份"><el-input-number v-model="publicationForm.year" :min="1990" :max="2100" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="DOI"><el-input v-model="publicationForm.doi" /></el-form-item>
                  <el-form-item label="可见范围">
                    <el-select v-model="publicationForm.visibility">
                      <el-option label="公开" value="public" />
                      <el-option label="成员可见" value="members" />
                      <el-option label="管理员可见" value="admins" />
                    </el-select>
                  </el-form-item>
                </div>
                <el-form-item label="摘要"><el-input v-model="publicationForm.abstract" type="textarea" :rows="4" /></el-form-item>
                <el-form-item label="PDF 附件">
                  <input class="file-input" type="file" accept="application/pdf" @change="setFile($event, publicationForm, 'pdf_file')" />
                  <small v-if="editingPublicationPdf">当前 PDF：{{ editingPublicationPdf }}</small>
                </el-form-item>
                <div class="form-two-col">
                  <el-form-item label="代表成果"><el-switch v-model="publicationForm.is_representative" /></el-form-item>
                  <el-form-item label="排序"><el-input-number v-model="publicationForm.sort_order" :min="0" /></el-form-item>
                </div>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingPublicationId)" @save="savePublication" @delete="deletePublication" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="仪器台账" name="instruments">
          <section class="editor-grid">
            <ContentList title="仪器设备" action-label="新增仪器" :items="instrumentRows" :active-key="editingInstrumentId || ''" @create="resetInstrument" @edit="editInstrument" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingInstrumentId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ instrumentForm.name || '仪器设备' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="仪器名称"><el-input v-model="instrumentForm.name" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="型号"><el-input v-model="instrumentForm.model" /></el-form-item>
                  <el-form-item label="状态">
                    <el-select v-model="instrumentForm.status">
                      <el-option label="正常" value="normal" />
                      <el-option label="维护中" value="maintenance" />
                      <el-option label="停用" value="disabled" />
                    </el-select>
                  </el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="房间"><el-input v-model="instrumentForm.room" /></el-form-item>
                  <el-form-item label="详细位置"><el-input v-model="instrumentForm.location_detail" /></el-form-item>
                </div>
                <el-form-item label="设备图片">
                  <input class="file-input" type="file" accept="image/*" @change="setFile($event, instrumentForm, 'image')" />
                  <small v-if="editingInstrumentImage">当前图片：{{ editingInstrumentImage }}</small>
                </el-form-item>
                <el-form-item label="使用说明"><el-input v-model="instrumentForm.notes" type="textarea" :rows="4" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="排序"><el-input-number v-model="instrumentForm.sort_order" :min="0" /></el-form-item>
                </div>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingInstrumentId)" @save="saveInstrument" @delete="deleteInstrument" />
            </article>
          </section>
        </el-tab-pane>
      </el-tabs>
    </section>
  </InternalLayout>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, reactive, ref } from 'vue'
import { ElButton, ElMessage, ElMessageBox } from 'element-plus'

import { cmsApi, type CmsNewsArticle, type InstrumentCategory } from '../../api/cms'
import type { Instrument } from '../../api/instruments'
import type { Member, NewsCategory, Publication, ResearchDirection } from '../../api/publicPortal'
import InternalLayout from '../../layouts/InternalLayout.vue'

type FileField = 'cover_image' | 'avatar' | 'pdf_file' | 'image'
type CmsForm = Record<string, unknown>
type Row<T> = {
  key: string | number
  title: string
  meta: string
  source: T
}

const ContentList = defineComponent({
  props: {
    title: { type: String, required: true },
    actionLabel: { type: String, required: true },
    items: { type: Array as () => Row<unknown>[], required: true },
    activeKey: { type: [String, Number], default: '' },
  },
  emits: ['create', 'edit'],
  setup(props, { emit }) {
    return () =>
      h('article', { class: 'card list-panel' }, [
        h('div', { class: 'panel-heading' }, [
          h('div', [h('span', { class: 'panel-kicker' }, `${props.items.length} 条内容`), h('h2', props.title)]),
          h(ElButton, { plain: true, onClick: () => emit('create') }, () => props.actionLabel),
        ]),
        props.items.length
          ? props.items.map((item) =>
              h('button', { key: item.key, class: ['content-row', { active: item.key === props.activeKey }], type: 'button', onClick: () => emit('edit', item.source) }, [
                h('strong', item.title),
                h('span', item.meta),
              ]),
            )
          : h('div', { class: 'empty-list' }, '暂无内容，点击右上角新增。'),
      ])
  },
})

const FormActions = defineComponent({
  props: {
    saving: { type: Boolean, default: false },
    deletable: { type: Boolean, default: false },
  },
  emits: ['save', 'delete'],
  setup(props, { emit }) {
    return () =>
      h('div', { class: 'form-actions' }, [
        h(ElButton, { type: 'primary', loading: props.saving, onClick: () => emit('save') }, () => '保存'),
        props.deletable ? h(ElButton, { plain: true, onClick: () => emit('delete') }, () => '删除') : null,
      ])
  },
})

const activeTab = ref('research')
const saving = ref(false)

const researchItems = ref<ResearchDirection[]>([])
const memberItems = ref<Member[]>([])
const newsItems = ref<CmsNewsArticle[]>([])
const newsCategories = ref<NewsCategory[]>([])
const publicationItems = ref<Publication[]>([])
const instrumentItems = ref<Instrument[]>([])
const instrumentCategories = ref<InstrumentCategory[]>([])

const editingResearchSlug = ref('')
const editingResearchCover = ref('')
const editingMemberId = ref<number | null>(null)
const editingMemberAvatar = ref('')
const editingNewsSlug = ref('')
const editingNewsCover = ref('')
const editingPublicationId = ref<number | null>(null)
const editingPublicationPdf = ref('')
const editingInstrumentId = ref<number | null>(null)
const editingInstrumentImage = ref('')

const researchForm = reactive<CmsForm>({ title: '', slug: '', summary: '', content: '', cover_image: undefined, sort_order: 0 })
const memberForm = reactive<CmsForm>({
  name: '',
  name_en: '',
  role_type: 'master',
  grade: '',
  research_direction: '',
  email: '',
  avatar: undefined,
  profile: '',
  sort_order: 0,
  is_public: true,
})
const newsForm = reactive<CmsForm>({
  title: '',
  slug: '',
  summary: '',
  content: '',
  cover_image: undefined,
  event_date: '',
  location: '',
  category_id: null,
  status: 'published',
  visibility: 'public',
  is_pinned: false,
})
const publicationForm = reactive<CmsForm>({
  title: '',
  authors: '',
  journal: '',
  year: new Date().getFullYear(),
  doi: '',
  abstract: '',
  pdf_file: undefined,
  visibility: 'public',
  is_representative: true,
  sort_order: 0,
})
const instrumentForm = reactive<CmsForm>({
  name: '',
  model: '',
  room: '',
  location_detail: '',
  image: undefined,
  status: 'normal',
  need_training: false,
  notes: '',
  sort_order: 0,
})

const researchRows = computed<Row<ResearchDirection>[]>(() =>
  researchItems.value.map((item) => ({ key: item.slug, title: item.title, meta: item.slug, source: item })),
)
const memberRows = computed<Row<Member>[]>(() =>
  memberItems.value.map((item) => ({
    key: item.id,
    title: item.name,
    meta: `${roleText(item.role_type)} · ${item.research_direction || '研究方向待补充'}`,
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
const publicationRows = computed<Row<Publication>[]>(() =>
  publicationItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${item.year} · ${item.journal || '期刊待补充'}`, source: item })),
)
const instrumentRows = computed<Row<Instrument>[]>(() =>
  instrumentItems.value.map((item) => ({
    key: item.id,
    title: item.name,
    meta: `${instrumentStatusText(item.status)} · ${item.room || '位置待补充'}`,
    source: item,
  })),
)

const cmsOverview = computed(() => [
  { label: '研究方向', value: researchItems.value.length, note: '公开门户展示' },
  { label: '团队成员', value: memberItems.value.length, note: '师生与校友信息' },
  { label: '新闻活动', value: newsItems.value.length, note: '组内动态与活动' },
  { label: '代表论文', value: publicationItems.value.length, note: '科研成果维护' },
  { label: '内部仪器', value: instrumentItems.value.length, note: '内部平台展示' },
])

async function loadAll() {
  const [research, members, categories, news, publications, instrumentCategoryData, instruments] = await Promise.all([
    cmsApi.listResearch(),
    cmsApi.listMembers(),
    cmsApi.listNewsCategories(),
    cmsApi.listNews(),
    cmsApi.listPublications(),
    cmsApi.listInstrumentCategories(),
    cmsApi.listInstruments(),
  ])
  researchItems.value = research
  memberItems.value = members
  newsCategories.value = categories
  newsItems.value = news
  publicationItems.value = publications
  instrumentCategories.value = instrumentCategoryData
  instrumentItems.value = instruments
}

function setFile(event: Event, form: CmsForm, field: FileField) {
  const input = event.target as HTMLInputElement
  form[field] = input.files?.[0]
}

function resetResearch() {
  editingResearchSlug.value = ''
  editingResearchCover.value = ''
  Object.assign(researchForm, { title: '', slug: '', summary: '', content: '', cover_image: undefined, sort_order: 0 })
}

function editResearch(item: ResearchDirection) {
  editingResearchSlug.value = item.slug
  editingResearchCover.value = item.cover_image || ''
  Object.assign(researchForm, {
    title: item.title,
    slug: item.slug,
    summary: item.summary,
    content: item.content || '',
    cover_image: undefined,
    sort_order: item.sort_order || 0,
  })
}

async function saveResearch() {
  await save(() => (editingResearchSlug.value ? cmsApi.updateResearch(editingResearchSlug.value, researchForm) : cmsApi.createResearch(researchForm)))
  resetResearch()
}

async function deleteResearch() {
  await removeAfterConfirm('确定删除这个研究方向吗？', () => cmsApi.deleteResearch(editingResearchSlug.value), resetResearch)
}

function resetMember() {
  editingMemberId.value = null
  editingMemberAvatar.value = ''
  Object.assign(memberForm, {
    name: '',
    name_en: '',
    role_type: 'master',
    grade: '',
    research_direction: '',
    email: '',
    avatar: undefined,
    profile: '',
    sort_order: 0,
    is_public: true,
  })
}

function editMember(item: Member) {
  editingMemberId.value = item.id
  editingMemberAvatar.value = item.avatar || ''
  Object.assign(memberForm, {
    name: item.name,
    name_en: item.name_en || '',
    role_type: item.role_type || 'master',
    grade: item.grade || '',
    research_direction: item.research_direction || '',
    email: item.email || '',
    avatar: undefined,
    profile: item.profile || '',
    sort_order: (item as Member & { sort_order?: number }).sort_order || 0,
    is_public: true,
  })
}

async function saveMember() {
  await save(() => (editingMemberId.value ? cmsApi.updateMember(editingMemberId.value, memberForm) : cmsApi.createMember(memberForm)))
  resetMember()
}

async function deleteMember() {
  if (!editingMemberId.value) return
  await removeAfterConfirm('确定删除这个团队成员吗？', () => cmsApi.deleteMember(editingMemberId.value as number), resetMember)
}

function resetNews() {
  editingNewsSlug.value = ''
  editingNewsCover.value = ''
  Object.assign(newsForm, {
    title: '',
    slug: '',
    summary: '',
    content: '',
    cover_image: undefined,
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
  editingNewsCover.value = item.cover_image || ''
  Object.assign(newsForm, {
    title: item.title,
    slug: item.slug,
    summary: item.summary || '',
    content: item.content || '',
    cover_image: undefined,
    event_date: item.event_date || '',
    location: item.location || '',
    category_id: item.category?.id || null,
    status: item.status || 'published',
    visibility: item.visibility || 'public',
    is_pinned: item.is_pinned || false,
  })
}

async function saveNews() {
  await save(() => (editingNewsSlug.value ? cmsApi.updateNews(editingNewsSlug.value, newsForm) : cmsApi.createNews(newsForm)))
  resetNews()
}

async function deleteNews() {
  await removeAfterConfirm('确定删除这条新闻吗？', () => cmsApi.deleteNews(editingNewsSlug.value), resetNews)
}

function resetPublication() {
  editingPublicationId.value = null
  editingPublicationPdf.value = ''
  Object.assign(publicationForm, {
    title: '',
    authors: '',
    journal: '',
    year: new Date().getFullYear(),
    doi: '',
    abstract: '',
    pdf_file: undefined,
    visibility: 'public',
    is_representative: true,
    sort_order: 0,
  })
}

function editPublication(item: Publication) {
  editingPublicationId.value = item.id
  editingPublicationPdf.value = item.pdf_file || ''
  Object.assign(publicationForm, {
    title: item.title,
    authors: item.authors,
    journal: item.journal || '',
    year: item.year,
    doi: item.doi || '',
    abstract: item.abstract || '',
    pdf_file: undefined,
    visibility: item.visibility || 'public',
    is_representative: item.is_representative,
    sort_order: (item as Publication & { sort_order?: number }).sort_order || 0,
  })
}

async function savePublication() {
  await save(() =>
    editingPublicationId.value ? cmsApi.updatePublication(editingPublicationId.value, publicationForm) : cmsApi.createPublication(publicationForm),
  )
  resetPublication()
}

async function deletePublication() {
  if (!editingPublicationId.value) return
  await removeAfterConfirm('确定删除这篇论文吗？', () => cmsApi.deletePublication(editingPublicationId.value as number), resetPublication)
}

function resetInstrument() {
  editingInstrumentId.value = null
  editingInstrumentImage.value = ''
  Object.assign(instrumentForm, {
    name: '',
    model: '',
    room: '',
    location_detail: '',
    image: undefined,
    status: 'normal',
    need_training: false,
    notes: '',
    sort_order: 0,
  })
}

function editInstrument(item: Instrument) {
  editingInstrumentId.value = item.id
  editingInstrumentImage.value = item.image || ''
  Object.assign(instrumentForm, {
    name: item.name,
    model: item.model || '',
    room: item.room || '',
    location_detail: item.location_detail || '',
    image: undefined,
    status: item.status || 'normal',
    need_training: item.need_training,
    notes: item.notes || '',
    sort_order: item.sort_order || 0,
  })
}

async function saveInstrument() {
  await save(() => (editingInstrumentId.value ? cmsApi.updateInstrument(editingInstrumentId.value, instrumentForm) : cmsApi.createInstrument(instrumentForm)))
  resetInstrument()
}

async function deleteInstrument() {
  if (!editingInstrumentId.value) return
  await removeAfterConfirm('确定删除这台仪器吗？', () => cmsApi.deleteInstrument(editingInstrumentId.value as number), resetInstrument)
}

async function save(action: () => Promise<unknown>) {
  saving.value = true
  try {
    await action()
    await loadAll()
    ElMessage.success('内容已保存')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败，请检查权限和表单内容')
  } finally {
    saving.value = false
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

function instrumentStatusText(status: string) {
  return ({ normal: '正常', maintenance: '维护中', disabled: '停用' }[status] || status)
}

onMounted(loadAll)
</script>

<style scoped>
.cms-page {
  display: grid;
  gap: 20px;
}

.cms-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-lg);
  padding: 30px 32px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(251, 253, 251, 0.94) 60%, rgba(234, 245, 238, 0.84)),
    #fff;
  box-shadow: var(--shadow-flat);
}

.cms-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.cms-heading h1 {
  margin: 6px 0 8px;
  color: var(--color-deep-green);
  font-size: clamp(27px, 3vw, 34px);
  font-weight: 650;
  line-height: 1.2;
}

.cms-heading p {
  margin: 0;
  max-width: 720px;
  color: var(--color-muted);
}

.heading-actions {
  display: flex;
  flex: 0 0 auto;
  gap: 10px;
}

.preview-link {
  border: 1px solid rgba(0, 135, 60, 0.28);
  border-radius: var(--radius-sm);
  padding: 9px 16px;
  background: #fff;
  color: var(--color-cau-green);
  font-weight: 700;
}

.preview-link.subtle {
  border-color: var(--color-border);
  color: var(--color-muted);
}

.cms-overview {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.overview-card {
  padding: 18px;
}

.overview-card:hover {
  transform: none;
}

.overview-card span {
  color: var(--color-muted);
  font-size: 13px;
  font-weight: 600;
}

.overview-card strong {
  display: block;
  margin: 8px 0 5px;
  color: var(--color-deep-green);
  font-size: 28px;
  line-height: 1;
}

.overview-card p {
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
}

.cms-tabs {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px 24px 26px;
  background: #fff;
  box-shadow: var(--shadow-soft);
}

.cms-tabs :deep(.el-tabs__header) {
  margin-bottom: 22px;
}

.cms-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--color-line);
}

.editor-grid {
  display: grid;
  grid-template-columns: minmax(300px, 380px) minmax(0, 1fr);
  gap: 22px;
  align-items: start;
}

.list-panel,
.form-panel {
  padding: 24px;
  border-radius: var(--radius-lg);
}

.list-panel {
  position: sticky;
  top: 96px;
  max-height: calc(100vh - 128px);
  overflow: auto;
}

.list-panel:hover,
.form-panel:hover {
  transform: none;
}

.panel-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 12px;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.panel-kicker {
  display: block;
  margin-bottom: 3px;
  color: var(--color-cau-green);
  font-size: 12px;
  font-weight: 700;
}

.content-row {
  display: block;
  width: 100%;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  margin-bottom: 7px;
  padding: 13px 14px;
  background: transparent;
  cursor: pointer;
  text-align: left;
}

.content-row:hover,
.content-row.active {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
}

.content-row:hover strong,
.content-row.active strong {
  color: var(--color-cau-green);
}

.content-row strong,
.content-row span,
.form-panel small {
  display: block;
}

.content-row strong {
  color: var(--color-text);
  font-size: 15px;
}

.content-row span,
.form-panel small,
.empty-list {
  color: var(--color-muted);
  font-size: 14px;
}

.empty-list {
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

.form-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 18px;
  border-bottom: 1px solid var(--color-line);
  margin-bottom: 20px;
  padding-bottom: 16px;
}

.form-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.form-heading h2 {
  margin: 4px 0 0;
  color: var(--color-deep-green);
  font-size: 22px;
  font-weight: 650;
  line-height: 1.3;
}

.form-panel :deep(.el-form-item) {
  margin-bottom: 18px;
}

.form-panel :deep(.el-textarea__inner) {
  line-height: 1.7;
}

.form-two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.file-input {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 10px 11px;
  background: #fff;
}

.form-actions {
  position: sticky;
  bottom: 0;
  display: flex;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  margin: 22px -24px -24px;
  padding: 14px 24px;
  background: rgba(251, 252, 251, 0.96);
  backdrop-filter: blur(8px);
}

@media (max-width: 980px) {
  .editor-grid,
  .form-two-col,
  .cms-overview {
    grid-template-columns: 1fr;
  }

  .cms-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .list-panel {
    position: static;
    max-height: none;
  }
}
</style>
