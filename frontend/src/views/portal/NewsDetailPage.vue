<template>
  <PortalLayout>
    <PortalDetailLayout
      :return-to="returnTo"
      return-label="返回新闻活动"
      :kicker="article?.category?.name || '新闻活动'"
      :title="article?.title || '新闻活动'"
      aside-title="活动信息"
    >
      <template #meta>
        <p class="meta-list">
          <span>{{ article?.event_date || '近期' }}</span>
          <span v-if="article?.location">{{ article.location }}</span>
        </p>
      </template>

      <template v-if="article">
        <img v-if="article.cover_image" class="cover-image" :src="article.cover_image" :alt="article.title" />
        <p v-if="article.summary" class="lead">{{ article.summary }}</p>
        <RichContent v-if="hasRichBody" class="article-body" :html="articleHtml" />
        <div v-else class="article-body plain-body">
          <p v-for="paragraph in paragraphs" :key="paragraph">{{ paragraph }}</p>
        </div>
        <div v-if="detailGalleryImages.length" class="image-gallery">
          <figure v-for="image in detailGalleryImages" :key="image.id">
            <img :src="image.image" :alt="image.caption || article.title" />
            <figcaption v-if="image.caption">{{ image.caption }}</figcaption>
          </figure>
        </div>
      </template>
      <div v-else class="empty-panel">未找到这条新闻，可能已删除或尚未发布。</div>

      <template #aside>
        <dl>
          <div><dt>分类</dt><dd>{{ article?.category?.name || '新闻活动' }}</dd></div>
          <div><dt>日期</dt><dd>{{ article?.event_date || '近期' }}</dd></div>
          <div v-if="article?.location"><dt>地点</dt><dd>{{ article.location }}</dd></div>
        </dl>
        <div v-if="article?.tags?.length" class="tag-row">
          <span v-for="tag in article.tags" :key="tag.id">{{ tag.name }}</span>
        </div>
      </template>
    </PortalDetailLayout>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchNewsArticle, type NewsArticle } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import PortalDetailLayout from '../../components/PortalDetailLayout.vue'
import RichContent from '../../components/RichContent.vue'

const route = useRoute()
const returnTo = usePortalReturn('/news')
const article = ref<NewsArticle | null>(null)

const detailGalleryImages = computed(() => {
  const images = article.value?.images || []
  return images.filter((image) => !image.caption?.startsWith('Word') && image.caption !== '正文插图')
})

const articleHtml = computed(() => article.value?.word_html || article.value?.content || '')
const hasRichBody = computed(() => /<[a-z][\s\S]*>/i.test(articleHtml.value))
const paragraphs = computed(() => (articleHtml.value || article.value?.summary || '').split(/\n+/).map((line) => line.trim()).filter(Boolean))

onMounted(async () => {
  try {
    article.value = await fetchNewsArticle(String(route.params.slug || ''))
  } catch {
    article.value = null
  }
})
</script>

<style scoped>
.cover-image {
  display: block;
  width: 100%;
  max-height: 420px;
  object-fit: cover;
}

.lead {
  margin: 0;
  border-left: 3px solid var(--color-cau-green);
  margin: 28px 34px 0;
  padding: 2px 0 2px 18px;
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

.image-gallery {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  padding: 0 34px 34px;
}

.image-gallery figure { margin: 0; }
.image-gallery img { width: 100%; aspect-ratio: 16 / 10; border-radius: var(--radius-md); object-fit: cover; }
.image-gallery figcaption { margin-top: 6px; color: var(--color-muted); font-size: 13px; }
.empty-panel { padding: 28px; color: var(--color-muted); }

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 18px;
}

.tag-row span {
  border-left: 2px solid var(--color-cau-gold);
  border-radius: 3px;
  padding: 5px 10px;
  background: var(--color-eco-green);
  color: var(--color-deep-green);
  font-size: 13px;
}

@media (max-width: 640px) {
  .article-body,
  .image-gallery {
    padding-right: 22px;
    padding-left: 22px;
  }

  .lead {
    margin: 22px 22px 0;
    padding: 2px 0 2px 14px;
  }

  .image-gallery { grid-template-columns: 1fr; }
}
</style>
