<template>
  <PortalLayout>
    <PortalPageHeader title="新闻活动" description="汇集组内动态、学术交流、科研进展、成果荣誉与招生招聘信息。" />
    <section class="page-section">
      <div class="container">
        <div class="filter-row" role="group" aria-label="按新闻分类筛选">
          <button type="button" :class="{ active: !activeCategory }" :aria-pressed="!activeCategory" @click="activeCategory = ''">全部</button>
          <button
            v-for="category in categories"
            :key="category.slug"
            :class="{ active: activeCategory === category.slug }"
            :aria-pressed="activeCategory === category.slug"
            type="button"
            @click="activeCategory = category.slug"
          >
            {{ category.name }}
          </button>
        </div>
        <div class="news-grid">
          <RouterLink v-for="item in pagedNews" :key="item.title" class="card news-card" :to="{ path: `/news/${item.slug}`, query: { from: route.fullPath } }">
            <div class="news-media" :class="{ 'is-empty': !item.cover_image || imageErrors.has(item.slug) }">
              <img v-if="item.cover_image && !imageErrors.has(item.slug)" :src="item.cover_image" :alt="item.title" @error="imageErrors.add(item.slug)" />
              <ImagePlaceholder v-else class="news-image-placeholder" :label="`${item.title}暂无封面`" text="" />
            </div>
            <div class="news-card-content">
              <span>{{ item.event_date || '近期' }} · {{ item.category?.name || '新闻活动' }}</span>
              <h2>{{ item.title }}</h2>
              <p>{{ item.summary || '新闻摘要待补充。' }}</p>
            </div>
          </RouterLink>
        </div>
        <div v-if="!displayNews.length" class="card empty-panel">暂无新闻活动，请在内部平台“门户内容”中维护。</div>
        <AppPagination :page="page" :total-pages="totalPages" @change="page = $event" />
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { fetchNews, fetchNewsCategories, type NewsArticle, type NewsCategory } from '../../api/publicPortal'
import AppPagination from '../../components/AppPagination.vue'
import ImagePlaceholder from '../../components/ImagePlaceholder.vue'
import PortalPageHeader from '../../components/PortalPageHeader.vue'
import PortalLayout from '../../layouts/PortalLayout.vue'

const news = ref<NewsArticle[]>([])
const categories = ref<NewsCategory[]>([])
const route = useRoute()
const router = useRouter()
const initialPage = Math.max(1, Number.parseInt(typeof route.query.page === 'string' ? route.query.page : '', 10) || 1)
const activeCategory = ref(typeof route.query.category === 'string' ? route.query.category : '')
const page = ref(initialPage)
const pageSize = 9
const imageErrors = reactive(new Set<string>())
const displayNews = computed(() => news.value)
const totalPages = computed(() => Math.max(1, Math.ceil(displayNews.value.length / pageSize)))
const pagedNews = computed(() => displayNews.value.slice((page.value - 1) * pageSize, page.value * pageSize))

async function loadNews() {
  try {
    news.value = await fetchNews({ category__slug: activeCategory.value || undefined })
  } catch {
    news.value = []
  }
}

watch(activeCategory, () => {
  page.value = 1
  syncQuery()
  void loadNews()
})

watch(page, syncQuery)

function syncQuery() {
  const query: Record<string, string> = {}
  if (activeCategory.value) query.category = activeCategory.value
  if (page.value > 1) query.page = String(page.value)
  void router.replace({ path: '/news', query })
}

watch(totalPages, (total) => {
  if (page.value > total) page.value = total
  if (page.value < 1) page.value = 1
})

onMounted(async () => {
  await Promise.allSettled([
    loadNews(),
    fetchNewsCategories().then((data) => {
      categories.value = data
    }).catch(() => {
      categories.value = []
    }),
  ])
})
</script>

<style scoped>
.portal-page-head {
  position: relative;
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 28px 0 24px;
  background:
    linear-gradient(90deg, rgba(234, 245, 238, 0.76), rgba(255, 255, 255, 0.96) 48%, rgba(248, 247, 242, 0.92)),
    var(--color-white);
}

.portal-page-head::before {
  position: absolute;
  top: 30px;
  bottom: 26px;
  left: max(20px, calc((100vw - var(--container)) / 2));
  width: 3px;
  border-radius: 999px;
  content: "";
  background: var(--color-cau-green);
}

.portal-page-head .container {
  padding-left: 22px;
}

.portal-page-head h1 {
  margin: 0 0 9px;
  color: var(--color-deep-green);
  font-size: clamp(28px, 3.1vw, 38px);
  font-weight: 650;
  line-height: 1.18;
}

.portal-page-head p:last-child {
  max-width: 820px;
  margin: 0;
  color: var(--color-muted);
  font-size: 15px;
  line-height: 1.65;
}

.portal-page-head .section-kicker {
  color: var(--color-cau-green);
}

.page-section {
  padding-top: 30px;
  background: var(--color-rice);
}

.filter-row {
  display: flex;
  gap: 22px;
  margin-bottom: 18px;
  overflow-x: auto;
  border-bottom: 1px solid var(--color-line);
  scrollbar-width: none;
}

.filter-row::-webkit-scrollbar {
  display: none;
}

.filter-row button {
  min-height: 40px;
  flex: 0 0 auto;
  border: 0;
  border-bottom: 2px solid transparent;
  padding: 0 2px;
  background: transparent;
  color: var(--color-muted);
  cursor: pointer;
}

.filter-row button.active,
.filter-row button:hover {
  border-bottom-color: var(--color-cau-green);
  color: var(--color-cau-green);
  font-weight: 650;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.empty-panel {
  padding: 28px;
  color: var(--color-muted);
  box-shadow: none;
}

.news-card {
  overflow: hidden;
  border-color: rgba(31, 61, 43, 0.1);
  color: inherit;
  box-shadow: none;
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

.news-card-content {
  padding: 15px 16px 17px;
}

.news-card span {
  color: var(--color-muted);
  font-size: 13px;
}

.news-card h2 {
  display: -webkit-box;
  margin: 8px 0;
  overflow: hidden;
  color: var(--color-deep-green);
  font-size: 18px;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.news-card p {
  margin: 0;
  color: var(--color-muted);
}

@media (max-width: 980px) {
  .news-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .news-grid {
    grid-template-columns: 1fr;
  }
}
</style>


