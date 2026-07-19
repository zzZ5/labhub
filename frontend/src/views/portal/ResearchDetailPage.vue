<template>
  <PortalLayout>
    <PortalDetailLayout
      :return-to="returnTo"
      return-label="返回研究方向"
      kicker="研究方向"
      :title="direction?.title || '研究方向'"
      aside-title="方向信息"
    >
      <template v-if="direction?.summary" #meta><p class="meta-list"><span>{{ direction.summary }}</span></p></template>

      <div v-if="loading" class="detail-state" role="status" aria-label="正在加载研究方向">
        <ListSkeleton :rows="4" thumbnail />
      </div>
      <div v-else-if="loadError" class="detail-state">
        <LoadErrorNotice :description="loadError" @retry="loadDirection" />
      </div>
      <template v-else-if="direction">
        <div v-if="direction.cover_image" class="detail-media">
          <img v-if="!imageFailed" :src="direction.cover_image" :alt="direction.title" @error="imageFailed = true" />
          <ImagePlaceholder v-else :label="`${direction.title}暂无配图`" text="" />
        </div>
        <div class="detail-body">
          <h2>研究内容</h2>
          <p v-for="paragraph in contentParagraphs" :key="paragraph">{{ paragraph }}</p>
          <p v-if="!contentParagraphs.length" class="muted">详细内容暂未补充。</p>
        </div>
      </template>
      <EmptyState v-else title="未找到研究方向" description="该内容可能已调整或暂未公开。">
        <template #action><ReturnLink :to="returnTo">返回研究方向</ReturnLink></template>
      </EmptyState>

      <template v-if="direction" #aside>
        <dl>
          <div><dt>内容类型</dt><dd>研究方向</dd></div>
          <div v-if="direction.updated_at"><dt>更新时间</dt><dd>{{ direction.updated_at.slice(0, 10) }}</dd></div>
        </dl>
      </template>
    </PortalDetailLayout>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchResearchDirection, type ResearchDirection } from '../../api/publicPortal'
import { usePortalReturn } from '../../composables/usePortalReturn'
import PortalLayout from '../../layouts/PortalLayout.vue'
import PortalDetailLayout from '../../components/PortalDetailLayout.vue'
import ReturnLink from '../../components/ReturnLink.vue'
import EmptyState from '../../components/EmptyState.vue'
import ImagePlaceholder from '../../components/ImagePlaceholder.vue'
import ListSkeleton from '../../components/ListSkeleton.vue'
import LoadErrorNotice from '../../components/LoadErrorNotice.vue'

const route = useRoute()
const returnTo = usePortalReturn('/research')
const direction = ref<ResearchDirection | null>(null)
const loading = ref(true)
const loadError = ref('')
const imageFailed = ref(false)

const contentParagraphs = computed(() => (direction.value?.content || '').split(/\n+/).map((item) => item.trim()).filter(Boolean))

async function loadDirection() {
  loading.value = true
  loadError.value = ''
  imageFailed.value = false
  try {
    direction.value = await fetchResearchDirection(String(route.params.slug))
  } catch {
    direction.value = null
    loadError.value = '研究方向加载失败，请稍后重试。'
  } finally {
    loading.value = false
  }
}

onMounted(loadDirection)
</script>

<style scoped>
.detail-state { padding: 28px; }

.detail-media {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: var(--color-panel-strong);
}

.detail-media img,
.detail-media :deep(.image-placeholder) { width: 100%; height: 100%; }
.detail-media img { display: block; object-fit: cover; }

.detail-body { padding: 28px 34px 34px; }
.detail-body h2 { position: relative; margin: 0 0 18px; padding-left: 13px; color: var(--color-deep-green); font-size: 23px; }
.detail-body h2::before { position: absolute; top: 0.16em; bottom: 0.16em; left: 0; width: 3px; background: linear-gradient(180deg, var(--color-cau-green) 0 72%, var(--color-cau-gold) 72% 100%); content: ""; }
.detail-body p { margin: 0 0 16px; color: var(--color-text); font-size: 16px; line-height: 1.9; }
.muted { color: var(--color-muted) !important; }

@media (max-width: 640px) {
  .detail-body { padding: 24px 22px 28px; }
}
</style>
