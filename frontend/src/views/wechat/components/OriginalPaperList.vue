<template>
    <section class="papers-page" aria-label="论文原文">
      <form class="papers-search" @submit.prevent="search">
        <label class="search-field">
          <span>查找论文</span>
          <input v-model="keyword" type="search" placeholder="中文标题、英文标题、DOI、作者或期刊" />
        </label>
        <label>
          <span>研究专题</span>
          <select v-model="topic">
            <option value="">全部专题</option>
            <option v-for="item in paperTopics" :key="item.value" :value="item.value">{{ item.label }}</option>
          </select>
        </label>
        <button type="submit" class="search-button">搜索</button>
      </form>
      <p class="papers-count">共 {{ total }} 篇论文</p>
      <LoadErrorNotice v-if="loadError" :description="loadError" :retrying="loading" @retry="load" />
      <ListSkeleton v-if="loading" :rows="4" />
      <div v-else-if="papers.length" class="papers-list">
        <article v-for="paper in papers" :key="paper.id" class="paper-row">
          <p class="paper-meta">{{ [paper.topic_label, paper.journal, paper.year].filter(Boolean).join(' · ') }}</p>
          <h2>{{ paper.chinese_title || paper.title }}</h2>
          <p v-if="paper.chinese_title" class="paper-english">{{ paper.title }}</p>
          <p v-if="paper.authors" class="paper-authors">{{ paper.authors }}</p>
          <p v-if="paper.doi" class="paper-doi">DOI: {{ paper.doi }}</p>
          <div class="paper-actions">
            <a v-if="paper.preview_url" :href="paperFileUrl(paper.preview_url)" target="_blank" rel="noopener noreferrer">在线阅读 PDF</a>
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
import { onMounted, ref, watch } from 'vue'
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
    const result = await fetchOriginalPapers({ search: keyword.value.trim() || undefined, topic: topic.value || undefined, page: page.value })
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
  void router.replace({ name: 'wechat-articles', query: { tab: 'papers', q: keyword.value.trim() || undefined, topic: topic.value || undefined, page: page.value > 1 ? String(page.value) : undefined } })
  void load()
}
function search() { page.value = 1; updateQuery() }
function changePage(value: number) { page.value = value; updateQuery() }
watch(topic, search)
onMounted(load)
</script>

<style scoped>
.papers-page { min-width: 0; padding-bottom: 12px; }
.papers-search { display: flex; align-items: end; gap: 12px; padding-bottom: 20px; border-bottom: 1px solid var(--color-border); }
.papers-search label { display: grid; gap: 6px; min-width: 0; font-size: 13px; color: var(--color-muted); }
.search-field { flex: 1; }
.papers-search input, .papers-search select { width: 100%; min-height: 44px; padding: 9px 12px; border: 1px solid var(--color-border); border-radius: 4px; background: var(--color-white); color: var(--color-text); font: inherit; font-size: 15px; }
.search-button { min-height: 44px; padding: 8px 24px; background: var(--color-cau-green); color: var(--color-white); border: 0; border-radius: 4px; cursor: pointer; font: inherit; }
.papers-count { display: flex; justify-content: space-between; gap: 12px; color: var(--color-muted); font-size: 13px; }
.papers-list { border-top: 1px solid var(--color-border); }
.paper-row { padding: 22px 0; border-bottom: 1px solid var(--color-border); overflow-wrap: anywhere; }
.paper-meta { color: var(--color-muted); font-size: 13px; margin: 0 0 8px; }
.paper-row h2 { margin: 0 0 8px; color: var(--color-deep-green); font-size: 20px; line-height: 1.5; }
.paper-english { margin: 0 0 8px; font-size: 16px; }
.paper-authors, .paper-doi { margin: 5px 0; font-size: 13px; color: var(--color-muted); }
.paper-actions { display: flex; flex-wrap: wrap; gap: 10px 20px; align-items: center; margin-top: 14px; font-size: 14px; }
.paper-actions a { min-height: 36px; display: inline-flex; align-items: center; color: var(--color-cau-green-dark); text-decoration: underline; text-underline-offset: 4px; }
.paper-note, .papers-footnote { color: var(--color-muted); font-size: 12px; }
.papers-footnote { margin-top: 24px; }
@media (max-width: 640px) {
  .papers-search { flex-wrap: wrap; }
  .search-field { flex-basis: 100%; }
  .papers-search label:not(.search-field) { flex: 1; }
  .paper-row h2 { font-size: 18px; }
}
</style>
