<template>
  <PortalLayout>
    <section class="news-detail-head">
      <div class="container detail-head-grid">
        <RouterLink class="back-link" to="/news">返回新闻活动</RouterLink>
        <div>
          <p class="section-kicker">{{ article?.category?.name || '新闻活动' }}</p>
          <h1>{{ article?.title || '新闻活动' }}</h1>
          <div class="article-meta">
            <span>{{ article?.event_date || '近期' }}</span>
            <span v-if="article?.location">{{ article.location }}</span>
          </div>
        </div>
      </div>
    </section>

    <section class="page-section">
      <div class="container article-layout">
        <main class="card article-card">
          <img v-if="coverImage" class="cover-image" :src="coverImage" :alt="article?.title" />
          <p v-if="article?.summary" class="lead">{{ article.summary }}</p>
          <div v-if="article?.word_html" class="article-body word-body" v-html="article.word_html"></div>
          <div v-else class="article-body">
            <p v-for="paragraph in paragraphs" :key="paragraph">{{ paragraph }}</p>
          </div>
          <div v-if="article?.images?.length" class="image-gallery">
            <figure v-for="image in article.images" :key="image.id">
              <img :src="image.image" :alt="image.caption || article.title" />
              <figcaption v-if="image.caption">{{ image.caption }}</figcaption>
            </figure>
          </div>
        </main>

        <aside class="side-card card">
          <strong>活动信息</strong>
          <dl>
            <div>
              <dt>分类</dt>
              <dd>{{ article?.category?.name || '新闻活动' }}</dd>
            </div>
            <div>
              <dt>日期</dt>
              <dd>{{ article?.event_date || '近期' }}</dd>
            </div>
            <div v-if="article?.location">
              <dt>地点</dt>
              <dd>{{ article.location }}</dd>
            </div>
          </dl>
          <div v-if="article?.tags?.length" class="tag-row">
            <span v-for="tag in article.tags" :key="tag.id">{{ tag.name }}</span>
          </div>
        </aside>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchNewsArticle, type NewsArticle } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const route = useRoute()
const article = ref<NewsArticle | null>(null)

const fallbackImage = 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1200&q=82'
const fallbackArticles: Record<string, NewsArticle> = {
  'field-sampling': {
    id: 0,
    title: '课题组完成夏季堆肥产品田间施用试验采样',
    slug: 'field-sampling',
    summary: '围绕土壤养分变化、作物生长和环境风险指标开展连续监测。',
    content: '课题组近期完成夏季田间试验采样工作，重点关注堆肥产品施用后的土壤养分变化、作物生长状态和潜在环境风险指标。\n\n后续团队将结合室内分析、微生物群落测定和田间连续观测数据，评估有机物料还田对土壤生态功能和农业资源循环的综合影响。',
    cover_image: fallbackImage,
    event_date: '2026-06-18',
    location: '中国农业大学西校区',
    category: { name: '田间试验' },
  },
  seminar: {
    id: 1,
    title: '实验室举办农业废弃物资源化专题组会',
    slug: 'seminar',
    summary: '师生围绕腐殖化过程调控和智能监测模型进行讨论。',
    content: '本次组会围绕农业废弃物资源化、堆肥腐殖化调控和过程监测模型展开讨论。\n\n与会成员结合近期实验数据，对后续采样计划、指标体系和模型验证方案进行了梳理。',
    cover_image: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1200&q=82',
    event_date: '2026-05-29',
    location: '资源与环境学院',
    category: { name: '学术交流' },
  },
  training: {
    id: 2,
    title: '完成堆肥反应器与气体采样系统操作培训',
    slug: 'training',
    summary: '面向新进学生开展仪器安全、样品记录和数据归档培训。',
    content: '课题组面向新进学生开展堆肥反应器、气体采样系统和实验记录规范培训。\n\n培训内容覆盖仪器安全、样品编号、过程记录、数据归档和异常情况处理，帮助成员尽快熟悉组内实验规范。',
    cover_image: 'https://images.unsplash.com/photo-1581093588401-fbb62a02f120?auto=format&fit=crop&w=1200&q=82',
    event_date: '2026-05-12',
    location: '生态过程实验室',
    category: { name: '实验培训' },
  },
}

const coverImage = computed(() => article.value?.cover_image || fallbackImage)
const paragraphs = computed(() => {
  const content = article.value?.content || article.value?.summary || '新闻正文待补充。'
  return content
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean)
})

onMounted(async () => {
  const slug = String(route.params.slug || '')
  try {
    article.value = await fetchNewsArticle(slug)
  } catch {
    article.value = fallbackArticles[slug] || null
  }
})
</script>

<style scoped>
.news-detail-head {
  border-bottom: 4px solid var(--color-cau-green);
  padding: 46px 0 38px;
  background:
    linear-gradient(90deg, rgba(234, 245, 238, 0.96), rgba(255, 255, 255, 0.98) 56%, rgba(248, 247, 242, 0.96)),
    var(--color-white);
}

.detail-head-grid {
  display: grid;
  gap: 18px;
}

.back-link {
  width: fit-content;
  color: var(--color-cau-green);
  font-weight: 700;
}

.news-detail-head h1 {
  max-width: 860px;
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(34px, 4.2vw, 52px);
  font-weight: 650;
  line-height: 1.18;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-top: 16px;
  color: var(--color-muted);
}

.page-section {
  background: var(--color-rice);
}

.article-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
}

.article-card,
.side-card {
  border-color: rgba(31, 61, 43, 0.1);
  box-shadow: none;
}

.article-card {
  padding: 0;
  overflow: hidden;
}

.cover-image {
  display: block;
  width: 100%;
  max-height: 420px;
  object-fit: cover;
}

.lead {
  margin: 0;
  padding: 28px 34px 0;
  color: var(--color-deep-green);
  font-size: 20px;
  line-height: 1.75;
}

.article-body {
  padding: 24px 34px 36px;
}

.article-body p {
  margin: 0 0 18px;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.9;
}

.word-body :deep(p) {
  margin: 0 0 18px;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.95;
  white-space: pre-wrap;
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  padding: 0 34px 34px;
}

.image-gallery figure {
  margin: 0;
}

.image-gallery img {
  width: 100%;
  aspect-ratio: 16 / 10;
  border-radius: var(--radius-md);
  object-fit: cover;
}

.image-gallery figcaption {
  margin-top: 6px;
  color: var(--color-muted);
  font-size: 13px;
}

.side-card {
  align-self: start;
  padding: 22px;
}

.side-card strong {
  color: var(--color-deep-green);
  font-size: 18px;
}

.side-card dl {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
}

.side-card dt {
  color: var(--color-muted);
  font-size: 13px;
}

.side-card dd {
  margin: 4px 0 0;
  color: var(--color-text);
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.tag-row span {
  border-radius: 999px;
  padding: 5px 10px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 13px;
}

@media (max-width: 900px) {
  .article-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .lead,
  .article-body,
  .image-gallery {
    padding-right: 22px;
    padding-left: 22px;
  }

  .image-gallery {
    grid-template-columns: 1fr;
  }
}
</style>
