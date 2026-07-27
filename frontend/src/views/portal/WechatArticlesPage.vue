<template>
  <PortalLayout>
    <PortalPageHeader title="公众号速递" description="汇集关注公众号发布的科研资讯与文献解读，点击条目可前往微信原文。" />
    <section class="digest-section">
      <div class="container digest-layout">
        <div class="digest-toolbar">
          <label class="digest-search">
            <el-icon><Search /></el-icon>
            <input v-model="keyword" type="search" placeholder="搜索文章标题" aria-label="搜索文章标题" />
          </label>
          <label class="digest-filter">
            <span>公众号</span>
            <select v-model="accountFilter" aria-label="按公众号筛选">
              <option value="">全部公众号</option>
              <option v-for="account in accounts" :key="account.id" :value="String(account.id)">{{ account.name }}</option>
            </select>
          </label>
        </div>

        <LoadErrorNotice v-if="loadError" :description="loadError" :retrying="loading" @retry="loadArticles" />
        <ListSkeleton v-if="loading" :rows="6" thumbnail />
        <div v-else-if="articles.length" class="digest-list">
          <a
            v-for="article in articles"
            :key="article.id"
            class="digest-item"
            :href="article.source_url"
            target="_blank"
            rel="noopener noreferrer"
          >
            <div class="digest-cover">
              <img
                v-if="article.cover_url && !imageErrors.has(article.id)"
                :src="article.cover_url"
                :alt="article.title"
                referrerpolicy="no-referrer"
                @error="imageErrors.add(article.id)"
              />
              <ImagePlaceholder v-else :label="article.account.name" text="暂无封面" />
            </div>
            <div class="digest-copy">
              <div class="digest-meta">
                <span>{{ article.account.name }}</span>
                <time :datetime="article.published_at">{{ formatPortalDateTime(article.published_at) }}</time>
              </div>
              <h2>{{ article.title }}</h2>
              <p>{{ article.summary || '暂无摘要，点击查看微信原文。' }}</p>
              <span class="digest-link">查看微信原文 <el-icon><TopRight /></el-icon></span>
            </div>
          </a>
        </div>
        <EmptyState v-else title="暂无文章" description="当前筛选条件下没有可展示的公众号文章。" />
        <AppPagination :page="page" :total-pages="totalPages" @change="page = $event" />
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { Search, TopRight } from '@element-plus/icons-vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchWechatAccounts, fetchWechatArticles, type WechatAccount, type WechatArticle } from '../../api/wechatArticles'
import AppPagination from '../../components/AppPagination.vue'
import EmptyState from '../../components/EmptyState.vue'
import ImagePlaceholder from '../../components/ImagePlaceholder.vue'
import ListSkeleton from '../../components/ListSkeleton.vue'
import LoadErrorNotice from '../../components/LoadErrorNotice.vue'
import PortalPageHeader from '../../components/PortalPageHeader.vue'
import { useDebouncedValue } from '../../composables/useDebouncedValue'
import PortalLayout from '../../layouts/PortalLayout.vue'
import { formatPortalDateTime } from '../../utils/date'
import { requestErrorMessage } from '../../utils/requestErrors'

const route = useRoute()
const router = useRouter()
const accounts = ref<WechatAccount[]>([])
const articles = ref<WechatArticle[]>([])
const loading = ref(false)
const loadError = ref('')
const total = ref(0)
const keyword = ref(typeof route.query.q === 'string' ? route.query.q : '')
const debouncedKeyword = useDebouncedValue(keyword)
const accountFilter = ref(typeof route.query.account === 'string' ? route.query.account : '')
const page = ref(Math.max(1, Number.parseInt(typeof route.query.page === 'string' ? route.query.page : '', 10) || 1))
const pageSize = 12
const imageErrors = reactive(new Set<number>())
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

async function loadArticles() {
  loading.value = true
  loadError.value = ''
  try {
    const result = await fetchWechatArticles({
      account: accountFilter.value ? Number(accountFilter.value) : undefined,
      search: debouncedKeyword.value.trim() || undefined,
      page: page.value,
      page_size: pageSize,
    })
    articles.value = result.results
    total.value = result.count
  } catch (error) {
    articles.value = []
    total.value = 0
    loadError.value = requestErrorMessage(error, '文章列表加载失败，请稍后重试。')
  } finally {
    loading.value = false
  }
}

function syncQuery() {
  const query: Record<string, string> = {}
  if (keyword.value.trim()) query.q = keyword.value.trim()
  if (accountFilter.value) query.account = accountFilter.value
  if (page.value > 1) query.page = String(page.value)
  void router.replace({ name: 'wechat-articles', query })
}

watch([debouncedKeyword, accountFilter], () => {
  page.value = 1
  syncQuery()
  void loadArticles()
})
watch(page, () => {
  syncQuery()
  void loadArticles()
})
watch(totalPages, (value) => {
  if (page.value > value) page.value = value
})

onMounted(async () => {
  await Promise.allSettled([
    fetchWechatAccounts().then((data) => {
      accounts.value = data
    }),
    loadArticles(),
  ])
})
</script>

<style scoped>
.digest-section {
  min-height: 520px;
  padding: 34px 0 72px;
  background: var(--surface-portal);
}

.digest-layout {
  display: grid;
  gap: 18px;
}

.digest-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 1px solid var(--color-line);
  padding-bottom: 14px;
}

.digest-search {
  display: flex;
  align-items: center;
  width: min(440px, 100%);
  min-height: 42px;
  gap: 9px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0 13px;
  background: var(--color-white);
  color: var(--color-muted);
}

.digest-search:focus-within {
  border-color: var(--color-cau-green);
  box-shadow: 0 0 0 3px var(--color-focus);
}

.digest-search input {
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--color-text);
  font: inherit;
}

.digest-filter {
  display: flex;
  align-items: center;
  gap: 9px;
  color: var(--color-muted);
  font-size: 14px;
}

.digest-filter select {
  min-width: 180px;
  min-height: 42px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0 34px 0 12px;
  background: var(--color-white);
  color: var(--color-text);
}

.digest-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px 18px;
}

.digest-item {
  display: grid;
  grid-template-columns: 270px minmax(0, 1fr);
  height: 168px;
  min-height: 168px;
  overflow: hidden;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-white);
  color: inherit;
  text-decoration: none;
  transition: border-color 160ms ease, box-shadow 160ms ease, transform 160ms ease;
}

.digest-item:hover {
  border-color: var(--color-border-accent);
  box-shadow: var(--shadow-hover);
  transform: translateY(-1px);
}

.digest-cover {
  align-self: stretch;
  overflow: hidden;
  background: var(--color-panel);
}

.digest-cover img,
.digest-cover :deep(.image-placeholder) {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.digest-copy {
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr) auto;
  min-width: 0;
  overflow: hidden;
  padding: 12px 14px;
}

.digest-meta {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  color: var(--color-muted);
  font-size: 12px;
}

.digest-meta span {
  color: var(--color-cau-green);
  font-weight: 650;
}

.digest-item h2 {
  display: -webkit-box;
  margin: 5px 0 3px;
  overflow: hidden;
  color: var(--color-deep-green);
  font-size: 17px;
  line-height: 1.45;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.digest-item p {
  display: -webkit-box;
  min-height: 0;
  margin: 0;
  overflow: hidden;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.65;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.digest-link {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  align-self: end;
  margin-top: 0;
  padding-top: 4px;
  color: var(--color-cau-green);
  font-size: 12px;
  font-weight: 650;
}

@media (max-width: 1120px) {
  .digest-list {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .digest-section {
    padding-top: 22px;
  }

  .digest-toolbar {
    align-items: stretch;
    flex-direction: column;
  }

  .digest-filter {
    justify-content: space-between;
  }

  .digest-filter select {
    min-width: 0;
    flex: 1;
  }

  .digest-item {
    grid-template-columns: 132px minmax(0, 1fr);
    height: 132px;
    min-height: 132px;
  }

  .digest-cover,
  .digest-cover img,
  .digest-cover :deep(.image-placeholder) {
    min-height: 0;
  }

  .digest-copy {
    padding: 11px 12px;
  }

  .digest-meta {
    display: grid;
    gap: 2px;
  }

  .digest-item h2 {
    margin-top: 5px;
    font-size: 15px;
  }

  .digest-item p {
    display: none;
  }
}
</style>
