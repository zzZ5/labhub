<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <p class="section-kicker">News</p>
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
          <article v-for="item in displayNews" :key="item.title" class="card news-card">
            <img :src="item.cover_image || fallbackImage" :alt="item.title" />
            <div>
              <span>{{ item.event_date || '近期' }} · {{ item.category?.name || '新闻活动' }}</span>
              <h2>{{ item.title }}</h2>
              <p>{{ item.summary || '新闻摘要待补充。' }}</p>
            </div>
          </article>
        </div>
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
const fallbackImage = 'https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=700&q=80'

const fallbackNews = [
  { id: 0, title: '课题组完成夏季堆肥产品田间施用试验采样', slug: 'field-sampling', summary: '围绕土壤养分变化、作物生长和环境风险指标开展连续监测。', cover_image: fallbackImage, event_date: '2026-06-18', category: { name: '田间试验' } },
  { id: 1, title: '实验室举办农业废弃物资源化专题组会', slug: 'seminar', summary: '师生围绕腐殖化过程调控和智能监测模型进行讨论。', cover_image: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=700&q=80', event_date: '2026-05-29', category: { name: '学术交流' } },
  { id: 2, title: '完成堆肥反应器与气体采样系统操作培训', slug: 'training', summary: '面向新进学生开展仪器安全、样品记录和数据归档培训。', cover_image: 'https://images.unsplash.com/photo-1581093588401-fbb62a02f120?auto=format&fit=crop&w=700&q=80', event_date: '2026-05-12', category: { name: '实验培训' } },
]

const displayNews = computed(() => (news.value.length ? news.value : fallbackNews))

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
    }),
  ])
})
</script>

<style scoped>
.portal-page-head {
  position: relative;
  border-bottom: 4px solid var(--color-cau-green);
  padding: 56px 0 42px;
  background:`n    linear-gradient(90deg, rgba(234, 245, 238, 0.96), rgba(255, 255, 255, 0.98) 56%, rgba(248, 247, 242, 0.96)),`n    radial-gradient(circle at 88% 26%, rgba(0, 135, 60, 0.08), transparent 28%),`n    var(--color-white);
}

.portal-page-head::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 34%;
  height: 4px;
  content: "";
  background: var(--color-soil);
}

.portal-page-head h1 {
  margin: 0 0 14px;
  color: var(--color-deep-green);
  font-size: clamp(38px, 4.5vw, 56px);
  font-weight: 650;
}

.portal-page-head p:last-child {
  max-width: 780px;
  margin: 0;
  color: var(--color-muted);
  font-size: 17px;
  line-height: 1.8;
}

.portal-page-head .section-kicker {
  color: var(--color-cau-green);
}

.page-section {
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

.news-card {
  overflow: hidden;
  border-color: rgba(31, 61, 43, 0.1);
  box-shadow: none;
}

.news-card img {
  width: 100%;
  aspect-ratio: 16 / 8.5;
  object-fit: cover;
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


