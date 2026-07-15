<template>
  <PortalLayout>
    <section class="news-detail-head">
      <div class="container detail-head-grid">
        <RouterLink class="back-link portal-back-link" :to="returnTo">返回新闻活动</RouterLink>
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

    <section v-if="article" class="page-section">
      <div class="container article-layout">
        <main class="card article-card">
          <img v-if="article.cover_image" class="cover-image" :src="article.cover_image" :alt="article.title" />
          <p v-if="article?.summary" class="lead">{{ article.summary }}</p>
          <div v-if="hasRichBody" class="article-body rich-body" v-html="articleHtml"></div>
          <div v-else class="article-body plain-body">
            <p v-for="paragraph in paragraphs" :key="paragraph">{{ paragraph }}</p>
          </div>
          <div v-if="detailGalleryImages.length" class="image-gallery">
            <figure v-for="image in detailGalleryImages" :key="image.id">
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
    <section v-else class="page-section">
      <div class="container">
        <div class="card empty-panel">未找到这条新闻，可能已删除或尚未发布。</div>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchNewsArticle, type NewsArticle } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'

const route = useRoute()
const returnTo = usePortalReturn('/news')
const article = ref<NewsArticle | null>(null)

const detailGalleryImages = computed(() => {
  const images = article.value?.images || []
  return images.filter((image) => !image.caption?.startsWith('Word') && image.caption !== '正文插图')
})

const articleHtml = computed(() => article.value?.word_html || article.value?.content || '')
const hasRichBody = computed(() => /<[a-z][\s\S]*>/i.test(articleHtml.value))

const paragraphs = computed(() => {
  const content = articleHtml.value || article.value?.summary || ''
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
    article.value = null
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

.empty-panel {
  padding: 28px;
  color: var(--color-muted);
  box-shadow: none;
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

.rich-body :deep(p) {
  margin: 0 0 18px;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.95;
  white-space: pre-wrap;
}

.rich-body :deep(h2) {
  margin: 32px 0 14px;
  color: var(--color-deep-green);
  font-size: 26px;
  line-height: 1.45;
}

.rich-body :deep(h3) {
  margin: 26px 0 12px;
  color: var(--color-deep-green);
  font-size: 21px;
  line-height: 1.5;
}

.rich-body :deep(ul),
.rich-body :deep(ol) {
  margin: 0 0 20px;
  padding-left: 1.7em;
  line-height: 1.9;
}

.rich-body :deep(blockquote) {
  margin: 24px 0;
  border-left: 3px solid var(--color-cau-green);
  padding: 5px 0 5px 20px;
  color: var(--color-muted);
}

.rich-body :deep(a) {
  color: var(--color-cau-green);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.rich-body :deep(figure) {
  margin: 24px 0;
}

.rich-body :deep(img) {
  display: block;
  max-width: min(100%, 920px);
  height: auto;
  margin: 24px auto;
  border-radius: var(--radius-md);
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
