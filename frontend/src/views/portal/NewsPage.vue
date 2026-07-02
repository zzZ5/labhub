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
            <img :src="item.cover_image || fallbackImage" :alt="item.title" />
            <div>
              <span>{{ item.event_date || '近期' }} · {{ item.category?.name || '新闻活动' }}</span>
              <h2>{{ item.title }}</h2>
              <p>{{ item.summary || '新闻摘要待补充。' }}</p>
            </div>
          </RouterLink>
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
const fallbackImage = 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=700&q=80'
const fallbackCategories = [
  { id: 1, name: '组内动态', slug: 'lab-news', description: '', sort_order: 1 },
  { id: 2, name: '学术交流', slug: 'academic-exchange', description: '', sort_order: 2 },
  { id: 3, name: '科研进展', slug: 'research-progress', description: '', sort_order: 3 },
  { id: 4, name: '项目相关', slug: 'projects', description: '', sort_order: 4 },
  { id: 5, name: '田间试验', slug: 'field-work', description: '', sort_order: 5 },
  { id: 6, name: '实验培训', slug: 'training', description: '', sort_order: 6 },
  { id: 7, name: '学生培养', slug: 'student-development', description: '', sort_order: 7 },
  { id: 8, name: '获奖成果', slug: 'awards', description: '', sort_order: 8 },
  { id: 9, name: '招生招聘', slug: 'recruitment', description: '', sort_order: 9 },
]

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
      categories.value = data.length ? data : fallbackCategories
    }).catch(() => {
      categories.value = fallbackCategories
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


