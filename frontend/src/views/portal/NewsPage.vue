<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <p class="section-kicker">新闻活动</p>
        <h1>新闻活动</h1>
        <p>记录组会、田间采样、学术交流、实验培训与学生答辩等课题组动态。</p>
      </div>
    </section>
    <section class="page-section">
      <div class="container">
        <div class="filter-row">
          <button :class="{ active: !activeCategory }" @click="activeCategory = ''">全部</button>
          <button
            v-for="category in categories"
            :key="category.slug"
            :class="{ active: activeCategory === category.slug }"
            @click="activeCategory = category.slug"
          >
            {{ category.name }}
          </button>
        </div>
        <div class="news-grid">
          <RouterLink v-for="item in displayNews" :key="item.title" class="card news-card" :to="`/news/${item.slug}`">
            <img v-if="item.cover_image" :src="item.cover_image" :alt="item.title" />
            <div v-else class="news-image-placeholder">暂无封面</div>
            <div>
              <span>{{ item.event_date || '近期' }} · {{ item.category?.name || '新闻活动' }}</span>
              <h2>{{ item.title }}</h2>
              <p>{{ item.summary || '新闻摘要待补充。' }}</p>
            </div>
          </RouterLink>
        </div>
        <div v-if="!displayNews.length" class="card empty-panel">暂无新闻活动，请在内部平台“门户内容”中维护。</div>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { fetchNews, fetchNewsCategories, type NewsArticle, type NewsCategory } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const news = ref<NewsArticle[]>([])
const categories = ref<NewsCategory[]>([])
const activeCategory = ref('')
const displayNews = computed(() => news.value)

async function loadNews() {
  try {
    news.value = await fetchNews({ category__slug: activeCategory.value || undefined })
  } catch {
    news.value = []
  }
}

watch(activeCategory, loadNews)

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
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 18px;
}

.filter-row button {
  border: 1px solid var(--color-border);
  border-radius: 999px;
  padding: 7px 14px;
  background: #fff;
  color: var(--color-muted);
  cursor: pointer;
}

.filter-row button.active,
.filter-row button:hover {
  border-color: var(--color-cau-green);
  color: var(--color-cau-green);
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

.news-card img {
  width: 100%;
  aspect-ratio: 16 / 8.5;
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

.news-card div {
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


