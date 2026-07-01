<template>
  <InternalLayout title="门户内容管理">
    <section class="cms-page">
      <div class="cms-heading">
        <div>
          <span>门户内容</span>
          <h1>官网内容维护</h1>
        </div>
        <div class="heading-actions">
          <div class="cms-stat-strip">
            <span v-for="item in cmsOverview" :key="item.label">{{ item.label }} {{ item.value }}</span>
          </div>
          <RouterLink class="preview-link" to="/">预览官网</RouterLink>
        </div>
      </div>

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
                <el-form-item label="姓名"><el-input v-model="memberForm.name" /></el-form-item>
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
                  <el-form-item label="邮箱"><el-input v-model="memberForm.email" /></el-form-item>
                </div>
                <el-form-item label="研究方向"><el-input v-model="memberForm.research_direction" /></el-form-item>
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
                <el-form-item label="Word 稿件">
                  <input class="file-input" type="file" accept=".docx" @change="setFile($event, newsForm, 'word_file')" />
                  <small>上传 .docx 后保存，新闻详情页会优先展示 Word 转 HTML 的内容；下方正文可作为不用 Word 时的备用正文。</small>
                </el-form-item>
                <el-form-item label="正文"><el-input v-model="newsForm.content" type="textarea" :rows="8" /></el-form-item>
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

        <el-tab-pane label="论文成果" name="publications">
          <section class="editor-grid">
            <ContentList title="论文成果" action-label="新增论文" :items="publicationRows" :active-key="editingPublicationId || ''" @create="resetPublication" @edit="editPublication" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingPublicationId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ publicationForm.title || '论文成果' }}</h2>
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
                  <el-form-item label="排序"><el-input-number v-model="publicationForm.sort_order" :min="0" /></el-form-item>
                </div>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingPublicationId)" @save="savePublication" @delete="deletePublication" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="科研项目" name="projects">
          <section class="editor-grid">
            <ContentList title="科研项目" action-label="新增项目" :items="projectRows" :active-key="editingProjectId || ''" @create="resetProject" @edit="editProject" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingProjectId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ projectForm.title || '科研项目' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="项目名称"><el-input v-model="projectForm.title" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="项目编号"><el-input v-model="projectForm.project_number" /></el-form-item>
                  <el-form-item label="资助来源"><el-input v-model="projectForm.funding_source" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="负责人"><el-input v-model="projectForm.principal_investigator" /></el-form-item>
                  <el-form-item label="状态"><el-input v-model="projectForm.status" /></el-form-item>
                </div>
                <div class="form-two-col">
                  <el-form-item label="开始日期"><el-date-picker v-model="projectForm.start_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                  <el-form-item label="结束日期"><el-date-picker v-model="projectForm.end_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                </div>
                <el-form-item label="可见范围">
                  <el-select v-model="projectForm.visibility">
                    <el-option label="公开" value="public" />
                    <el-option label="成员可见" value="members" />
                    <el-option label="管理员可见" value="admins" />
                  </el-select>
                </el-form-item>
                <el-form-item label="说明"><el-input v-model="projectForm.description" type="textarea" :rows="4" /></el-form-item>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingProjectId)" @save="saveProject" @delete="deleteProject" />
            </article>
          </section>
        </el-tab-pane>

        <el-tab-pane label="专利成果" name="patents">
          <section class="editor-grid">
            <ContentList title="专利成果" action-label="新增专利" :items="patentRows" :active-key="editingPatentId || ''" @create="resetPatent" @edit="editPatent" />
            <article class="card form-panel">
              <div class="form-heading">
                <div>
                  <span>{{ editingPatentId ? '正在编辑' : '新增内容' }}</span>
                  <h2>{{ patentForm.title || '专利成果' }}</h2>
                </div>
              </div>
              <el-form label-position="top">
                <el-form-item label="专利名称"><el-input v-model="patentForm.title" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="专利号"><el-input v-model="patentForm.patent_number" /></el-form-item>
                  <el-form-item label="状态"><el-input v-model="patentForm.status" /></el-form-item>
                </div>
                <el-form-item label="发明人"><el-input v-model="patentForm.inventors" type="textarea" :rows="2" /></el-form-item>
                <div class="form-two-col">
                  <el-form-item label="申请日期"><el-date-picker v-model="patentForm.application_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                  <el-form-item label="授权日期"><el-date-picker v-model="patentForm.authorization_date" type="date" value-format="YYYY-MM-DD" clearable /></el-form-item>
                </div>
                <el-form-item label="可见范围">
                  <el-select v-model="patentForm.visibility">
                    <el-option label="公开" value="public" />
                    <el-option label="成员可见" value="members" />
                    <el-option label="管理员可见" value="admins" />
                  </el-select>
                </el-form-item>
              </el-form>
              <FormActions :saving="saving" :deletable="Boolean(editingPatentId)" @save="savePatent" @delete="deletePatent" />
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

import { cmsApi, type CmsNewsArticle, type CmsNewsImage } from '../../api/cms'
import type { Member, NewsCategory, Patent, Project, Publication, ResearchDirection } from '../../api/publicPortal'
import InternalLayout from '../../layouts/InternalLayout.vue'

type FileField = 'cover_image' | 'avatar' | 'pdf_file' | 'image' | 'word_file'
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
    const keyword = ref('')
    const page = ref(1)
    const pageSize = 12
    const filteredItems = computed(() => {
      const q = keyword.value.trim().toLowerCase()
      if (!q) return props.items
      return props.items.filter((item) => `${item.title} ${item.meta}`.toLowerCase().includes(q))
    })
    const totalPages = computed(() => Math.max(1, Math.ceil(filteredItems.value.length / pageSize)))
    const pagedItems = computed(() => filteredItems.value.slice((page.value - 1) * pageSize, page.value * pageSize))
    const setPage = (nextPage: number) => {
      page.value = Math.min(totalPages.value, Math.max(1, nextPage))
    }
    return () =>
      h('article', { class: 'card list-panel' }, [
        h('div', { class: 'list-toolbar' }, [
          h('div', [h('strong', props.title), h('span', `${filteredItems.value.length} / ${props.items.length}`)]),
          h(ElButton, { type: 'primary', onClick: () => emit('create') }, () => props.actionLabel),
        ]),
        h('input', {
          class: 'list-search',
          value: keyword.value,
          placeholder: `搜索${props.title}`,
          onInput: (event: Event) => {
            keyword.value = (event.target as HTMLInputElement).value
            page.value = 1
          },
        }),
        filteredItems.value.length
          ? h('div', { class: 'content-list-scroll' }, pagedItems.value.map((item) =>
              h('button', { key: item.key, class: ['content-row', { active: item.key === props.activeKey }], type: 'button', onClick: () => emit('edit', item.source) }, [
                h('strong', item.title),
                h('span', item.meta),
              ]),
            ))
          : h('div', { class: 'empty-list' }, keyword.value ? '没有找到匹配内容。' : '暂无内容，点击右上角新增。'),
        filteredItems.value.length > pageSize
          ? h('div', { class: 'list-pager' }, [
              h('button', { type: 'button', disabled: page.value === 1, onClick: () => setPage(page.value - 1) }, '上一页'),
              h('span', `第 ${page.value} / ${totalPages.value} 页`),
              h('button', { type: 'button', disabled: page.value === totalPages.value, onClick: () => setPage(page.value + 1) }, '下一页'),
            ])
          : null,
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
const uploadingNewsImage = ref(false)

const researchItems = ref<ResearchDirection[]>([])
const memberItems = ref<Member[]>([])
const newsItems = ref<CmsNewsArticle[]>([])
const newsCategories = ref<NewsCategory[]>([])
const publicationItems = ref<Publication[]>([])
const projectItems = ref<Project[]>([])
const patentItems = ref<Patent[]>([])

const editingResearchSlug = ref('')
const editingResearchCover = ref('')
const editingMemberId = ref<number | null>(null)
const editingMemberAvatar = ref('')
const editingNewsSlug = ref('')
const editingNewsId = ref<number | null>(null)
const editingNewsCover = ref('')
const editingNewsImages = ref<CmsNewsImage[]>([])
const editingPublicationId = ref<number | null>(null)
const editingPublicationPdf = ref('')
const editingProjectId = ref<number | null>(null)
const editingPatentId = ref<number | null>(null)

const researchForm = reactive<CmsForm>({ title: '', summary: '', content: '', cover_image: undefined, sort_order: 0 })
const memberForm = reactive<CmsForm>({
  name: '',
  role_type: 'master',
  research_direction: '',
  email: '',
  avatar: undefined,
  profile: '',
  sort_order: 0,
  is_public: true,
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
const newsImageForm = reactive({
  file: undefined as File | undefined,
  caption: '',
  sort_order: 0,
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
  sort_order: 0,
})
const projectForm = reactive<CmsForm>({
  title: '',
  project_number: '',
  funding_source: '',
  principal_investigator: '',
  start_date: '',
  end_date: '',
  status: '',
  visibility: 'public',
  description: '',
})
const patentForm = reactive<CmsForm>({
  title: '',
  patent_number: '',
  inventors: '',
  application_date: '',
  authorization_date: '',
  status: '',
  visibility: 'public',
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
const projectRows = computed<Row<Project>[]>(() =>
  projectItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${item.funding_source || '资助来源待补充'} · ${item.status || '状态待补充'}`, source: item })),
)
const patentRows = computed<Row<Patent>[]>(() =>
  patentItems.value.map((item) => ({ key: item.id, title: item.title, meta: `${item.patent_number || '专利号待补充'} · ${item.status || '状态待补充'}`, source: item })),
)
const cmsOverview = computed(() => [
  { label: '研究方向', value: researchItems.value.length, note: '公开门户展示' },
  { label: '团队成员', value: memberItems.value.length, note: '师生与校友信息' },
  { label: '新闻活动', value: newsItems.value.length, note: '组内动态与活动' },
  { label: '论文成果', value: publicationItems.value.length, note: '科研成果维护' },
  { label: '科研项目', value: projectItems.value.length, note: '项目维护' },
  { label: '专利成果', value: patentItems.value.length, note: '专利维护' },
])

async function loadAll() {
  const [research, members, categories, news, publications, projects, patents] = await Promise.all([
    cmsApi.listResearch(),
    cmsApi.listMembers(),
    cmsApi.listNewsCategories(),
    cmsApi.listNews(),
    cmsApi.listPublications(),
    cmsApi.listProjects(),
    cmsApi.listPatents(),
  ])
  researchItems.value = research
  memberItems.value = members
  newsCategories.value = categories
  newsItems.value = news
  publicationItems.value = publications
  projectItems.value = projects
  patentItems.value = patents
}

function setFile(event: Event, form: CmsForm, field: FileField) {
  const input = event.target as HTMLInputElement
  form[field] = input.files?.[0]
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
    role_type: 'master',
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
    role_type: item.role_type || 'master',
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
  editingNewsId.value = null
  editingNewsCover.value = ''
  editingNewsImages.value = []
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
  resetNewsImageForm()
}

function editNews(item: CmsNewsArticle) {
  editingNewsSlug.value = item.slug
  editingNewsId.value = item.id
  editingNewsCover.value = item.cover_image || ''
  editingNewsImages.value = (item.images || []) as CmsNewsImage[]
  Object.assign(newsForm, {
    title: item.title,
    summary: item.summary || '',
    content: item.content || '',
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
  try {
    const saved = editingNewsSlug.value ? await cmsApi.updateNews(editingNewsSlug.value, newsForm) : await cmsApi.createNews(newsForm)
    await loadAll()
    editNews(saved)
    ElMessage.success('新闻已保存')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败，请检查权限和表单内容')
  } finally {
    saving.value = false
  }
}

async function deleteNews() {
  await removeAfterConfirm('确定删除这条新闻吗？', () => cmsApi.deleteNews(editingNewsSlug.value), resetNews)
}

function setNewsImageFile(event: Event) {
  const input = event.target as HTMLInputElement
  newsImageForm.file = input.files?.[0]
}

function resetNewsImageForm() {
  newsImageForm.file = undefined
  newsImageForm.caption = ''
  newsImageForm.sort_order = 0
}

async function uploadNewsImage() {
  if (!editingNewsId.value) {
    ElMessage.warning('请先保存新闻正文，再添加活动图片。')
    return
  }
  if (!newsImageForm.file) {
    ElMessage.warning('请选择要上传的图片。')
    return
  }
  uploadingNewsImage.value = true
  try {
    await cmsApi.createNewsImage({
      article_id: editingNewsId.value,
      image: newsImageForm.file,
      caption: newsImageForm.caption,
      sort_order: newsImageForm.sort_order,
    })
    resetNewsImageForm()
    await loadAll()
    const updated = newsItems.value.find((item) => item.id === editingNewsId.value)
    if (updated) editNews(updated)
    ElMessage.success('活动图片已添加')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '图片上传失败')
  } finally {
    uploadingNewsImage.value = false
  }
}

async function deleteNewsImage(id: number) {
  try {
    await cmsApi.deleteNewsImage(id)
    await loadAll()
    const updated = newsItems.value.find((item) => item.id === editingNewsId.value)
    if (updated) editNews(updated)
    ElMessage.success('图片已删除')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '图片删除失败')
  }
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

function resetProject() {
  editingProjectId.value = null
  Object.assign(projectForm, {
    title: '',
    project_number: '',
    funding_source: '',
    principal_investigator: '',
    start_date: '',
    end_date: '',
    status: '',
    visibility: 'public',
    description: '',
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
    status: item.status || '',
    visibility: (item as Project & { visibility?: string }).visibility || 'public',
    description: item.description || '',
  })
}

async function saveProject() {
  await save(() => (editingProjectId.value ? cmsApi.updateProject(editingProjectId.value, projectForm) : cmsApi.createProject(projectForm)))
  resetProject()
}

async function deleteProject() {
  if (!editingProjectId.value) return
  await removeAfterConfirm('确定删除这个科研项目吗？', () => cmsApi.deleteProject(editingProjectId.value as number), resetProject)
}

function resetPatent() {
  editingPatentId.value = null
  Object.assign(patentForm, {
    title: '',
    patent_number: '',
    inventors: '',
    application_date: '',
    authorization_date: '',
    status: '',
    visibility: 'public',
  })
}

function editPatent(item: Patent) {
  editingPatentId.value = item.id
  Object.assign(patentForm, {
    title: item.title,
    patent_number: item.patent_number || '',
    inventors: item.inventors || '',
    application_date: item.application_date || '',
    authorization_date: item.authorization_date || '',
    status: item.status || '',
    visibility: (item as Patent & { visibility?: string }).visibility || 'public',
  })
}

async function savePatent() {
  await save(() => (editingPatentId.value ? cmsApi.updatePatent(editingPatentId.value, patentForm) : cmsApi.createPatent(patentForm)))
  resetPatent()
}

async function deletePatent() {
  if (!editingPatentId.value) return
  await removeAfterConfirm('确定删除这个专利成果吗？', () => cmsApi.deletePatent(editingPatentId.value as number), resetPatent)
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

onMounted(loadAll)
</script>

<style scoped>
.cms-page {
  display: grid;
  gap: 12px;
}

.cms-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid rgba(0, 135, 60, 0.12);
  border-radius: var(--radius-md);
  padding: 14px 18px;
  background: #fff;
  box-shadow: none;
}

.cms-heading span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.cms-heading h1 {
  margin: 3px 0 0;
  color: var(--color-deep-green);
  font-size: 24px;
  font-weight: 650;
  line-height: 1.2;
}

.heading-actions {
  display: flex;
  align-items: center;
  flex: 0 0 auto;
  gap: 12px;
}

.cms-stat-strip {
  display: flex;
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

.cms-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.cms-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: var(--color-line);
}

.editor-grid {
  display: grid;
  grid-template-columns: minmax(340px, 400px) minmax(0, 1fr);
  gap: 16px;
  align-items: stretch;
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

.list-panel :deep(.list-toolbar) {
  align-items: flex-start;
  border-bottom: 1px solid var(--color-line);
  margin-bottom: 12px;
  min-height: 58px;
  padding-bottom: 12px;
}

.list-panel :deep(.list-toolbar strong),
.list-panel :deep(.list-toolbar span) {
  display: block;
}

.list-panel :deep(.list-toolbar > div) {
  min-width: 0;
}

.list-panel :deep(.list-toolbar strong) {
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.list-panel :deep(.list-toolbar span) {
  margin-top: 2px;
  color: var(--color-muted);
  font-size: 12px;
}

.list-panel :deep(.list-toolbar .el-button) {
  --el-button-size: 32px;
  flex: 0 0 auto;
  min-height: 32px;
  padding: 7px 12px;
  color: #fff !important;
}

.cms-page :deep(.el-button--primary),
.cms-page :deep(.el-button--primary span) {
  color: #fff !important;
}

.panel-heading h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: 19px;
  font-weight: 650;
}

.list-panel :deep(.list-search) {
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

.list-panel :deep(.list-search:focus) {
  border-color: rgba(0, 135, 60, 0.35);
  outline: none;
  box-shadow: 0 0 0 3px rgba(0, 135, 60, 0.08);
}

.list-panel :deep(.content-list-scroll) {
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 6px;
}

.list-panel :deep(.content-row) {
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

.list-panel :deep(.content-row:hover),
.list-panel :deep(.content-row.active) {
  border-color: rgba(0, 135, 60, 0.14);
  background: var(--color-eco-green);
}

.list-panel :deep(.content-row:hover strong),
.list-panel :deep(.content-row.active strong) {
  color: var(--color-cau-green);
}

.list-panel :deep(.content-row strong),
.list-panel :deep(.content-row span),
.form-panel small {
  display: block;
}

.list-panel :deep(.content-row strong) {
  display: block;
  overflow: hidden;
  color: var(--color-text);
  font-size: 14px;
  line-height: 1.45;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel :deep(.content-row span),
.form-panel small,
.empty-list {
  color: var(--color-muted);
  font-size: 13px;
}

.list-panel :deep(.content-row span) {
  margin-top: 7px;
  overflow: hidden;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-panel :deep(.empty-list) {
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

.list-panel :deep(.list-pager) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid var(--color-line);
  margin-top: 10px;
  padding-top: 10px;
  background: #fff;
}

.list-panel :deep(.list-pager button) {
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

.list-panel :deep(.list-pager button:disabled) {
  border-color: var(--color-border);
  color: var(--color-muted);
  cursor: not-allowed;
  opacity: 0.6;
}

.list-panel :deep(.list-pager span) {
  color: var(--color-muted);
  font-size: 13px;
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

.form-panel :deep(.el-form-item) {
  margin-bottom: 14px;
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
  margin: 18px -20px -18px;
  padding: 12px 20px;
  background: rgba(251, 252, 251, 0.96);
  backdrop-filter: blur(8px);
}

@media (max-width: 980px) {
  .editor-grid,
  .form-two-col,
  .gallery-upload {
    grid-template-columns: 1fr;
  }

  .cms-heading {
    align-items: flex-start;
    flex-direction: column;
  }

  .list-panel {
    max-height: none;
  }

  .list-panel :deep(.content-list-scroll) {
    max-height: 420px;
  }
}
</style>
