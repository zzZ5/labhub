<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <h1>研究方向</h1>
        <p>{{ pageDescription }}</p>
      </div>
    </section>
    <section class="page-section">
      <div class="container research-grid">
        <RouterLink v-for="item in displayDirections" :key="item.title" class="card research-card" :to="item.to">
          <span>{{ item.index }}</span>
          <h2>{{ item.title }}</h2>
          <p>{{ item.summary }}</p>
        </RouterLink>
      </div>
      <div v-if="!displayDirections.length" class="container">
        <div class="card empty-panel">暂无公开研究方向，请在内部平台“门户内容”中维护。</div>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchResearchDirections, type ResearchDirection } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const directions = ref<ResearchDirection[]>([])
const route = useRoute()

const displayDirections = computed(() =>
  directions.value.map((item, index) => ({
    index: `0${index + 1}`,
    title: item.title,
    summary: item.summary || '研究方向简介待补充。',
    to: { path: `/research/${item.slug}`, query: { from: route.fullPath } },
  })),
)

const pageDescription = computed(() => {
  const firstSummary = directions.value.find((item) => item.summary)?.summary
  return firstSummary || '研究方向内容可在内部平台“门户内容”中维护，保存后会同步展示到公开网站。'
})

onMounted(async () => {
  try {
    directions.value = await fetchResearchDirections()
  } catch {
    directions.value = []
  }
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

.research-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}

.research-card {
  display: block;
  border-color: rgba(31, 61, 43, 0.1);
  padding: 22px;
  color: inherit;
  text-decoration: none;
  box-shadow: none;
}

.empty-panel {
  padding: 28px;
  color: var(--color-muted);
  box-shadow: none;
}

.research-card > span {
  color: var(--color-cau-green);
  font-weight: 700;
}

.research-card h2 {
  margin: 12px 0 10px;
  color: var(--color-deep-green);
  font-size: 20px;
}

.research-card p {
  margin: 0;
  color: var(--color-muted);
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
}
</style>


