<template>
  <section class="article-manager">
    <div class="article-toolbar">
      <el-input v-model="keyword" clearable placeholder="搜索文章标题" :prefix-icon="Search" />
      <el-select v-model="accountFilter" clearable placeholder="全部公众号">
        <el-option v-for="account in accounts" :key="account.id" :label="account.name" :value="account.id" />
      </el-select>
      <div class="toolbar-actions">
        <el-button :type="selectionMode ? 'primary' : 'default'" plain @click="toggleSelectionMode">
          {{ selectionMode ? '退出批量' : '批量管理' }}
        </el-button>
        <el-button type="primary" :icon="Plus" @click="openCreate">手动添加文章</el-button>
      </div>
    </div>

    <LoadErrorNotice v-if="loadError" :description="loadError" :retrying="loading" @retry="loadArticles" />
    <ListSkeleton v-if="loading" :rows="6" />
    <template v-else-if="articles.length">
      <div v-if="selectionMode" class="bulk-toolbar">
        <div class="bulk-selection">
          <el-checkbox
            :model-value="allPageSelected"
            :indeterminate="somePageSelected"
            @change="togglePageSelection"
          >
            本页全选
          </el-checkbox>
          <span>已选 {{ selectedIds.size }} 篇</span>
        </div>
        <div class="bulk-actions">
          <el-button size="small" :disabled="!selectedIds.size || Boolean(bulkOperation)" :loading="bulkOperation === 'show'" @click="handleBulk('show')">公开</el-button>
          <el-button size="small" :disabled="!selectedIds.size || Boolean(bulkOperation)" :loading="bulkOperation === 'hide'" @click="handleBulk('hide')">隐藏</el-button>
          <el-button size="small" type="danger" plain :disabled="!selectedIds.size || Boolean(bulkOperation)" :loading="bulkOperation === 'delete'" @click="handleBulk('delete')">
            删除
          </el-button>
        </div>
      </div>
      <div class="article-list">
        <article v-for="article in articles" :key="article.id" class="article-row" :class="{ 'is-selecting': selectionMode }">
          <el-checkbox
            v-if="selectionMode"
            class="article-select"
            :model-value="selectedIds.has(article.id)"
            :aria-label="`选择文章：${article.title}`"
            @change="(checked: boolean | string | number) => toggleSelection(article.id, Boolean(checked))"
          />
          <div class="article-copy">
            <div class="article-meta">
              <span>{{ article.account_name }}</span>
              <time>{{ formatPortalDateTime(article.published_at) }}</time>
              <span class="status-tag" :class="article.is_visible ? 'normal' : 'archived'">{{ article.is_visible ? '公开' : '隐藏' }}</span>
              <span v-if="article.is_manual" class="manual-tag">手动录入</span>
            </div>
            <h3>{{ article.title }}</h3>
            <p>{{ article.summary || '未填写摘要' }}</p>
          </div>
          <div class="article-actions">
            <a :href="article.source_url" target="_blank" rel="noopener noreferrer">原文</a>
            <el-button text @click="openEdit(article)">编辑</el-button>
            <el-dropdown trigger="click" @command="(command: string) => command === 'delete' && handleDelete(article)">
              <el-button text :icon="MoreFilled" aria-label="更多操作" />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="delete">删除文章</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </article>
      </div>
      <AppPagination :page="page" :total-pages="totalPages" @change="page = $event" />
    </template>
    <EmptyState v-else title="暂无文章" description="可手动添加文章，或为公众号配置 RSS、开放接口后触发同步。" />

    <el-dialog v-model="dialogOpen" :title="editing ? '编辑文章' : '手动添加文章'" width="min(680px, calc(100vw - 24px))" destroy-on-close>
      <el-form label-position="top">
        <div class="form-grid">
          <el-form-item label="公众号" required>
            <el-select v-model="form.account" filterable>
              <el-option v-for="account in accounts" :key="account.id" :label="account.name" :value="account.id" />
            </el-select>
          </el-form-item>
          <el-form-item label="发布时间" required>
            <el-date-picker v-model="form.published_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择发布时间" />
          </el-form-item>
        </div>
        <el-form-item label="文章标题" required>
          <el-input v-model="form.title" maxlength="300" show-word-limit />
        </el-form-item>
        <el-form-item label="微信原文链接" required>
          <el-input v-model="form.source_url" placeholder="https://mp.weixin.qq.com/..." />
        </el-form-item>
        <el-form-item label="封面图片地址">
          <el-input v-model="form.cover_url" placeholder="https://..." />
        </el-form-item>
        <el-form-item label="简短摘要">
          <el-input v-model="form.summary" type="textarea" :rows="4" maxlength="500" show-word-limit />
        </el-form-item>
        <el-form-item label="展示状态">
          <el-switch v-model="form.is_visible" active-text="公开展示" inactive-text="暂不展示" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogOpen = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MoreFilled, Plus, Search } from '@element-plus/icons-vue'

import {
  bulkUpdateWechatArticles,
  createWechatArticle,
  deleteWechatArticle,
  fetchManagedWechatArticles,
  updateWechatArticle,
  type ManagedWechatAccount,
  type ManagedWechatArticle,
  type WechatArticlePayload,
} from '../../../api/wechatArticles'
import AppPagination from '../../../components/AppPagination.vue'
import EmptyState from '../../../components/EmptyState.vue'
import ListSkeleton from '../../../components/ListSkeleton.vue'
import LoadErrorNotice from '../../../components/LoadErrorNotice.vue'
import { useDebouncedValue } from '../../../composables/useDebouncedValue'
import { formatPortalDateTime } from '../../../utils/date'
import { requestErrorMessage } from '../../../utils/requestErrors'

const props = defineProps<{ accounts: ManagedWechatAccount[] }>()
const articles = ref<ManagedWechatArticle[]>([])
const total = ref(0)
const loading = ref(false)
const loadError = ref('')
const keyword = ref('')
const debouncedKeyword = useDebouncedValue(keyword)
const accountFilter = ref<number | undefined>()
const page = ref(1)
const pageSize = 12
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))
const dialogOpen = ref(false)
const editing = ref<ManagedWechatArticle | null>(null)
const saving = ref(false)
const selectionMode = ref(false)
const bulkOperation = ref<'show' | 'hide' | 'delete' | null>(null)
const selectedIds = ref(new Set<number>())
const allPageSelected = computed(
  () => articles.value.length > 0 && articles.value.every((article) => selectedIds.value.has(article.id)),
)
const somePageSelected = computed(
  () => !allPageSelected.value && articles.value.some((article) => selectedIds.value.has(article.id)),
)

function nowValue() {
  const date = new Date()
  const offset = date.getTimezoneOffset() * 60000
  return new Date(date.getTime() - offset).toISOString().slice(0, 19)
}

const blankForm = (): WechatArticlePayload => ({
  account: props.accounts[0]?.id || 0,
  title: '',
  summary: '',
  cover_url: '',
  source_url: '',
  published_at: nowValue(),
  is_visible: true,
})
const form = reactive<WechatArticlePayload>(blankForm())

async function loadArticles() {
  selectedIds.value = new Set()
  loading.value = true
  loadError.value = ''
  try {
    const result = await fetchManagedWechatArticles({
      account: accountFilter.value,
      search: debouncedKeyword.value.trim() || undefined,
      page: page.value,
      page_size: pageSize,
    })
    articles.value = result.results
    total.value = result.count
  } catch (error) {
    articles.value = []
    total.value = 0
    loadError.value = requestErrorMessage(error, '文章列表加载失败。')
  } finally {
    loading.value = false
  }
}

function resetForm(payload = blankForm()) {
  Object.assign(form, payload)
}

function openCreate() {
  if (!props.accounts.length) {
    ElMessage.warning('请先添加公众号。')
    return
  }
  editing.value = null
  resetForm()
  dialogOpen.value = true
}

function openEdit(article: ManagedWechatArticle) {
  editing.value = article
  resetForm({
    account: article.account,
    title: article.title,
    summary: article.summary,
    cover_url: article.cover_url,
    source_url: article.source_url,
    published_at: article.published_at.slice(0, 19),
    is_visible: article.is_visible,
  })
  dialogOpen.value = true
}

async function save() {
  if (!form.account || !form.title.trim() || !form.source_url.trim() || !form.published_at) {
    ElMessage.warning('请填写公众号、标题、发布时间和原文链接。')
    return
  }
  saving.value = true
  try {
    if (editing.value) await updateWechatArticle(editing.value.id, form)
    else await createWechatArticle(form)
    ElMessage.success(editing.value ? '文章已更新。' : '文章已添加。')
    dialogOpen.value = false
    await loadArticles()
  } catch (error) {
    ElMessage.error(requestErrorMessage(error, '保存失败，请检查链接和表单内容。'))
  } finally {
    saving.value = false
  }
}

function toggleSelection(articleId: number, checked: boolean) {
  const next = new Set(selectedIds.value)
  if (checked) next.add(articleId)
  else next.delete(articleId)
  selectedIds.value = next
}

function toggleSelectionMode() {
  selectionMode.value = !selectionMode.value
  selectedIds.value = new Set()
}

function togglePageSelection(checked: boolean | string | number) {
  selectedIds.value = checked ? new Set(articles.value.map((article) => article.id)) : new Set()
}

async function handleBulk(operation: 'show' | 'hide' | 'delete') {
  const ids = [...selectedIds.value]
  if (!ids.length) return
  if (operation === 'delete') {
    try {
      await ElMessageBox.confirm(
        `确定删除选中的 ${ids.length} 篇文章吗？由 RSS 同步的文章后续可能再次被同步，长期不展示建议使用“隐藏”。`,
        '批量删除文章',
        {
          type: 'warning',
          confirmButtonText: '删除',
          cancelButtonText: '取消',
        },
      )
    } catch (error) {
      if (error !== 'cancel' && error !== 'close') ElMessage.error(requestErrorMessage(error, '操作未完成。'))
      return
    }
  }

  bulkOperation.value = operation
  try {
    const result = await bulkUpdateWechatArticles(ids, operation)
    const actionLabel = operation === 'show' ? '设为公开' : operation === 'hide' ? '隐藏' : '删除'
    ElMessage.success(`已${actionLabel} ${result.affected} 篇文章。`)
    await loadArticles()
  } catch (error) {
    ElMessage.error(requestErrorMessage(error, '批量操作失败。'))
  } finally {
    bulkOperation.value = null
  }
}

async function handleDelete(article: ManagedWechatArticle) {
  try {
    await ElMessageBox.confirm(`确定删除“${article.title}”吗？`, '删除文章', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteWechatArticle(article.id)
    ElMessage.success('文章已删除。')
    if (articles.value.length === 1 && page.value > 1) page.value -= 1
    else await loadArticles()
  } catch (error: any) {
    if (error !== 'cancel' && error !== 'close') ElMessage.error(requestErrorMessage(error, '删除失败。'))
  }
}

watch([debouncedKeyword, accountFilter], () => {
  page.value = 1
  void loadArticles()
})
watch(page, loadArticles)
watch(totalPages, (value) => {
  if (page.value > value) page.value = value
})
watch(
  () => props.accounts,
  () => {
    if (!form.account && props.accounts.length) form.account = props.accounts[0].id
  },
)

onMounted(loadArticles)
</script>

<style scoped>
.article-manager {
  display: grid;
  gap: 14px;
}

.article-toolbar {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) 210px auto;
  gap: 10px;
}

.toolbar-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.bulk-toolbar {
  display: flex;
  min-height: 44px;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-block: 1px solid var(--color-line);
  padding: 6px 4px;
}

.bulk-selection,
.bulk-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.bulk-selection > span {
  color: var(--color-muted);
  font-size: 12px;
}

.article-list {
  display: grid;
}

.article-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  min-height: 112px;
  border-bottom: 1px solid var(--color-line);
  padding: 13px 4px;
}

.article-select {
  align-self: start;
  padding-top: 2px;
}

.article-select + .article-copy {
  min-width: 0;
}

.article-row.is-selecting {
  grid-template-columns: auto minmax(0, 1fr) auto;
}

.article-meta,
.article-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  color: var(--color-muted);
  font-size: 12px;
}

.article-meta > span:first-child {
  color: var(--color-cau-green);
  font-weight: 650;
}

.manual-tag {
  color: var(--color-blue-gray);
}

.article-copy h3 {
  margin: 7px 0 5px;
  color: var(--color-deep-green);
  font-size: 16px;
  line-height: 1.45;
}

.article-copy p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.article-actions a {
  color: var(--color-cau-green);
  font-weight: 650;
  text-decoration: none;
}

.form-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 1fr);
  gap: 14px;
}

@media (max-width: 720px) {
  .article-toolbar {
    grid-template-columns: 1fr;
  }

  .toolbar-actions {
    justify-content: stretch;
  }

  .toolbar-actions :deep(.el-button) {
    flex: 1;
  }

  .bulk-toolbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .bulk-actions {
    width: 100%;
    flex-wrap: wrap;
  }

  .article-row {
    grid-template-columns: minmax(0, 1fr);
    gap: 8px 10px;
  }

  .article-row.is-selecting {
    grid-template-columns: auto minmax(0, 1fr);
  }

  .article-actions {
    grid-column: 1;
    justify-content: flex-end;
  }

  .article-row.is-selecting .article-actions {
    grid-column: 2;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
}
</style>

