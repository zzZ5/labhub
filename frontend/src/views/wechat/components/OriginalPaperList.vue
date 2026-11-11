<template>
    <section class="papers-page" aria-label="论文原文">
      <form class="papers-search" @submit.prevent="search">
        <label class="search-field">
          <span>查找论文</span>
          <input v-model="keyword" type="search" placeholder="中文标题、英文标题、DOI、作者或期刊" />
        </label>
        <label>
          <span>研究专题</span>
          <select v-model="topic" @change="search">
            <option value="">全部专题</option>
            <option v-for="item in paperTopics" :key="item.value" :value="item.value">{{ item.label }}</option>
          </select>
        </label>
        <button type="submit" class="search-button">搜索</button>
      </form>
      <div class="papers-toolbar">
        <p class="papers-count" aria-live="polite">{{ loading ? '正在查找…' : `共 ${total} 篇论文` }}<span v-if="total && !loading"> · 第 {{ page }} / {{ Math.ceil(total / 12) }} 页</span></p>
        <label class="sort-field">排序
          <select v-model="sort" @change="search">
            <option value="added">收录时间：从新到旧</option>
            <option value="year_desc">发表年份：从新到旧</option>
            <option value="year_asc">发表年份：从旧到新</option>
            <option value="title">原文标题 A–Z</option>
          </select>
        </label>
      </div>
      <LoadErrorNotice v-if="loadError" :description="loadError" :retrying="loading" @retry="load" />
      <ListSkeleton v-if="loading" :rows="4" />
      <div v-else-if="papers.length" class="papers-list">
        <article v-for="paper in papers" :key="paper.id" class="paper-row">
          <div class="paper-meta">
            <span class="paper-year">{{ paper.year || '年份未录入' }}</span>
            <span class="paper-journal">{{ paper.journal }}</span>
            <button v-if="paper.topic" type="button" class="paper-topic" @click="topic = paper.topic; search()">{{ paper.topic_label }}</button>
          </div>
          <h2><a :href="paperFileUrl(paper.preview_url) || paperSourceUrl(paper) || undefined" :target="paper.preview_url || paperSourceUrl(paper) ? '_blank' : undefined" rel="noopener noreferrer">{{ paper.title }}</a></h2>
          <p v-if="paper.chinese_title" class="paper-translation">{{ paper.chinese_title }}</p>
          <details v-if="paper.authors" class="paper-authors">
            <summary><span>{{ authorPreview(paper.authors) }}</span><span class="authors-toggle">作者详情</span></summary>
            <p>{{ paper.authors }}</p>
          </details>
          <p v-if="paper.doi" class="paper-doi">DOI: {{ paper.doi }}</p>
          <div class="paper-actions">
            <a v-if="paper.preview_url" class="paper-read" :href="paperFileUrl(paper.preview_url)" target="_blank" rel="noopener noreferrer">阅读 PDF</a>
            <a v-if="paper.download_url" :href="paperFileUrl(paper.download_url)" target="_blank" rel="noopener noreferrer">下载 PDF</a>
            <a v-if="paperSourceUrl(paper)" :href="paperSourceUrl(paper)" target="_blank" rel="noopener noreferrer">原文入口 ↗</a>
            <a v-if="paper.wechat_url" :href="paper.wechat_url" target="_blank" rel="noopener noreferrer">公众号解读 ↗</a>
            <span v-if="!paper.preview_url" class="paper-note">本站未提供 PDF</span>
          </div>
        </article>
      </div>
      <EmptyState v-else-if="!loadError" title="暂无匹配的论文" description="可尝试缩短关键词，或选择全部专题。" />
      <AppPagination :page="page" :total-pages="Math.max(1, Math.ceil(total / 12))" @change="changePage" />
      <p class="papers-footnote">本站仅提供许可允许分享的 PDF；其余论文请通过原文入口访问。</p>
    </section>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchOriginalPapers, paperFileUrl, paperSourceUrl, paperTopics, type OriginalPaper } from '../../../api/originalPapers'
import AppPagination from '../../../components/AppPagination.vue'
import EmptyState from '../../../components/EmptyState.vue'
import ListSkeleton from '../../../components/ListSkeleton.vue'
import LoadErrorNotice from '../../../components/LoadErrorNotice.vue'
import { requestErrorMessage } from '../../../utils/requestErrors'

const route = useRoute()
const router = useRouter()
const keyword = ref(String(route.query.q || ''))
const topic = ref(paperTopics.some(item => item.value === route.query.topic) ? String(route.query.topic) : '')
const page = ref(Math.max(1, Number(route.query.page) || 1))
const validSorts = ['year_desc', 'year_asc', 'added', 'title']
const sort = ref(validSorts.includes(String(route.query.sort)) ? String(route.query.sort) : 'added')
const papers = ref<OriginalPaper[]>([])
const total = ref(0)
const loading = ref(false)
const loadError = ref('')
let requestId = 0

async function load() {
  const current = ++requestId
  loading.value = true
  loadError.value = ''
  try {
    const result = await fetchOriginalPapers({ search: keyword.value.trim() || undefined, topic: topic.value || undefined, page: page.value, sort: sort.value })
    if (current !== requestId) return
    papers.value = result.results
    total.value = result.count
  } catch (error) {
    if (current !== requestId) return
    papers.value = []
    total.value = 0
    loadError.value = requestErrorMessage(error, '原文列表加载失败，请重试。')
  } finally {
    if (current === requestId) loading.value = false
  }
}

function updateQuery() {
  const query = { tab: 'papers', q: keyword.value.trim() || undefined, topic: topic.value || undefined, sort: sort.value === 'added' ? undefined : sort.value, page: page.value > 1 ? String(page.value) : undefined }
  if (router.resolve({ name: 'wechat-articles', query }).fullPath === route.fullPath) void load()
  else void router.push({ name: 'wechat-articles', query })
}
function search() { page.value = 1; updateQuery() }
function changePage(value: number) { page.value = value; updateQuery() }
function authorPreview(authors: string) {
  const names = authors.split(';').map(name => name.trim()).filter(Boolean)
  return names.length > 3 ? `${names.slice(0, 3).join('; ')}; et al.` : authors
}
watch(() => route.query, () => {
  if (route.query.tab !== 'papers') return
  // Route hydration must not trigger a second request or reset the restored page.
  keyword.value = String(route.query.q || '')
  topic.value = paperTopics.some(item => item.value === route.query.topic) ? String(route.query.topic) : ''
  sort.value = validSorts.includes(String(route.query.sort)) ? String(route.query.sort) : 'added'
  page.value = Math.max(1, Math.floor(Number(route.query.page) || 1))
  void load()
}, { immediate: true })
</script>

<style scoped>
.papers-page { min-width: 0; padding-bottom: 12px; }
.papers-search { display: flex; align-items: end; gap: 12px; padding-bottom: 20px; border-bottom: 1px solid var(--color-border); }
.papers-search label { display: grid; gap: 6px; min-width: 0; font-size: 13px; color: var(--color-muted); }
.search-field { flex: 1; }
.papers-search input, .papers-search select { width: 100%; min-height: 44px; padding: 9px 12px; border: 1px solid var(--color-border); border-radius: 4px; background: var(--color-white); color: var(--color-text); font: inherit; font-size: 15px; }
.search-button { min-height: 44px; padding: 8px 24px; background: var(--color-cau-green); color: var(--color-white); border: 0; border-radius: 4px; cursor: pointer; font: inherit; }
.papers-toolbar { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px 16px; padding: 16px 0; }
.papers-count { margin: 0; color: var(--color-text); font-size: 14px; }
.papers-count span { color: var(--color-muted); font-size: 13px; }
.sort-field { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--color-muted); }
.sort-field select { min-height: 40px; max-width: 100%; border: 1px solid var(--color-border); border-radius: 4px; padding: 6px 8px; background: var(--color-white); color: var(--color-text); font: inherit; }
.papers-list { border-top: 1px solid var(--color-border); }
.paper-row { padding: 20px 0 18px; border-bottom: 1px solid var(--color-border); overflow-wrap: anywhere; }
.paper-meta { display: flex; flex-wrap: wrap; align-items: center; gap: 6px 12px; color: var(--color-muted); font-size: 13px; margin: 0 0 9px; }
.paper-year { color: var(--color-deep-green); font-weight: 700; font-variant-numeric: tabular-nums; }
.paper-journal { color: var(--color-text); font-weight: 600; }
.paper-topic { margin-left: auto; border: 1px solid var(--color-border); background: var(--surface-hover); border-radius: 4px; padding: 3px 8px; color: var(--color-muted); font: inherit; cursor: pointer; }
.paper-topic:hover { color: var(--color-cau-green-dark); border-color: var(--color-cau-green); }
.paper-row h2 { margin: 0 0 7px; color: var(--color-deep-green); font-size: 19px; line-height: 1.45; font-weight: 600; }
.paper-row h2 a { color: inherit; text-decoration: none; }
.paper-row h2 a[href]:hover { color: var(--color-cau-green); text-decoration: underline; text-underline-offset: 3px; }
.paper-translation { margin: 0 0 8px; color: var(--color-muted); font-size: 14px; }
.paper-authors, .paper-doi { margin: 5px 0; font-size: 12px; color: var(--color-muted); }
.paper-authors summary { cursor: pointer; display: flex; align-items: baseline; gap: 10px; list-style: none; }
.paper-authors summary::-webkit-details-marker { display: none; }
.paper-authors summary > span:first-child { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.authors-toggle { flex-shrink: 0; text-decoration: underline; text-underline-offset: 3px; }
.paper-authors p { margin: 8px 0; line-height: 1.7; }
.paper-actions { display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: center; margin-top: 10px; font-size: 13px; }
.paper-actions a { min-height: 36px; display: inline-flex; align-items: center; color: var(--color-cau-green-dark); text-decoration: none; }
.paper-actions a:hover { text-decoration: underline; text-underline-offset: 4px; }
.paper-actions .paper-read { padding: 0 12px; border: 1px solid var(--color-border-accent); border-radius: 4px; font-weight: 600; background: var(--surface-hover); }
.papers-page :is(a, button, select, input, summary):focus-visible { outline: 2px solid var(--color-cau-green); outline-offset: 3px; }
.paper-note, .papers-footnote { color: var(--color-muted); font-size: 12px; }
.papers-footnote { margin-top: 24px; }
@media (max-width: 640px) {
  .papers-search { flex-wrap: wrap; }
  .search-field { flex-basis: 100%; }
  .papers-search label:not(.search-field) { flex: 1; }
  .paper-row h2 { font-size: 18px; }
  .paper-topic { margin-left: 0; }
  .sort-field { width: 100%; justify-content: space-between; }
  .sort-field select { flex: 1; }
  .paper-actions a, .paper-topic { min-height: 44px; }
}
</style>
