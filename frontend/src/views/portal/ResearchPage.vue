<template>
  <PortalLayout>
    <PortalPageHeader title="研究方向" description="聚焦课题组持续开展的核心研究领域与技术方向。" />
    <section class="page-section">
      <div class="container research-grid">
        <RouterLink v-for="item in displayDirections" :key="item.title" class="card research-card" :to="item.to">
          <div class="research-media" :class="{ 'is-empty': !item.coverImage || imageErrors.has(item.slug) }">
            <img
              v-if="item.coverImage && !imageErrors.has(item.slug)"
              :src="item.coverImage"
              :alt="item.title"
              @error="imageErrors.add(item.slug)"
            />
            <ImagePlaceholder v-else :label="`${item.title}暂无配图`" text="" />
            <span>{{ item.index }}</span>
          </div>
          <div class="research-content">
            <h2>{{ item.title }}</h2>
            <p>{{ item.summary }}</p>
            <small>查看研究内容 <ArrowRight /></small>
          </div>
        </RouterLink>
      </div>
      <div v-if="!displayDirections.length" class="container">
        <div class="card empty-panel">暂无公开研究方向，请在内部平台“门户内容”中维护。</div>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'

import { fetchResearchDirections, type ResearchDirection } from '../../api/publicPortal'
import ImagePlaceholder from '../../components/ImagePlaceholder.vue'
import PortalPageHeader from '../../components/PortalPageHeader.vue'
import PortalLayout from '../../layouts/PortalLayout.vue'

const directions = ref<ResearchDirection[]>([])
const route = useRoute()
const imageErrors = reactive(new Set<string>())

const displayDirections = computed(() =>
  directions.value.map((item, index) => ({
    index: `0${index + 1}`,
    slug: item.slug,
    title: item.title,
    summary: item.summary || '研究方向简介待补充。',
    coverImage: item.cover_image || '',
    to: { path: `/research/${item.slug}`, query: { from: route.fullPath } },
  })),
)

onMounted(async () => {
  try {
    directions.value = await fetchResearchDirections()
  } catch {
    directions.value = []
  }
})
</script>

<style scoped>
.page-section {
  padding-top: 34px;
  background: var(--surface-portal);
}

.research-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.research-card {
  display: grid;
  grid-template-rows: auto 1fr;
  overflow: hidden;
  border-color: rgba(31, 61, 43, 0.1);
  padding: 0;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
  transition: border-color 180ms ease, transform 180ms ease;
}

.empty-panel {
  padding: 28px;
  color: var(--color-muted);
  box-shadow: none;
}

.research-media {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: var(--color-panel-strong);
}

.research-media img,
.research-media :deep(.image-placeholder) {
  width: 100%;
  height: 100%;
}

.research-media img {
  display: block;
  object-fit: cover;
  transition: transform 220ms ease;
}

.research-media > span {
  position: absolute;
  right: 14px;
  bottom: 12px;
  border-left: 2px solid var(--color-cau-gold);
  padding-left: 7px;
  color: rgba(255, 255, 255, 0.94);
  font-size: 13px;
  font-weight: 700;
  text-shadow: 0 1px 6px rgba(17, 31, 23, 0.55);
}

.research-content {
  display: flex;
  min-width: 0;
  flex-direction: column;
  border-top: 2px solid rgba(0, 135, 60, 0.08);
  padding: 19px 20px 18px;
}

.research-card h2 {
  margin: 0 0 9px;
  color: var(--color-deep-green);
  font-size: 20px;
}

.research-card p {
  display: -webkit-box;
  margin: 0;
  overflow: hidden;
  color: var(--color-muted);
  line-height: 1.7;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}

.research-card small {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: auto;
  padding-top: 16px;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 650;
}

.research-card small svg {
  width: 14px;
  height: 14px;
}

.research-card:hover .research-media img {
  transform: scale(1.025);
}

.research-card:hover {
  border-color: rgba(0, 135, 60, 0.28);
  transform: translateY(-2px);
}

@media (max-width: 980px) {
  .research-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .research-grid {
    grid-template-columns: 1fr;
  }

  .research-card {
    grid-template-columns: 116px minmax(0, 1fr);
    grid-template-rows: 1fr;
  }

  .research-media {
    min-height: 148px;
    aspect-ratio: auto;
  }

  .research-content {
    padding: 16px;
  }

  .research-card h2 {
    font-size: 18px;
  }

  .research-card p {
    -webkit-line-clamp: 2;
  }
}
</style>


