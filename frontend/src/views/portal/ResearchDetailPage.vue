<template>
  <PortalLayout>
    <section class="portal-page-head">
      <div class="container">
        <RouterLink class="back-link portal-back-link" to="/research">返回研究方向</RouterLink>
        <p class="section-kicker">研究方向</p>
        <h1>{{ direction?.title || '研究方向' }}</h1>
        <p>{{ direction?.summary || '研究方向简介待补充。' }}</p>
      </div>
    </section>

    <section class="page-section">
      <div class="container detail-layout">
        <article class="card detail-card">
          <img v-if="direction?.cover_image" :src="direction.cover_image" :alt="direction.title" />
          <div class="detail-body">
            <h2>研究内容</h2>
            <p v-for="paragraph in contentParagraphs" :key="paragraph">{{ paragraph }}</p>
            <p v-if="!contentParagraphs.length" class="muted">详细内容可在内部平台“门户内容-研究方向”中维护。</p>
          </div>
        </article>
        <aside class="card side-card">
          <span>Research</span>
          <strong>{{ direction?.title || '研究方向' }}</strong>
          <p>{{ direction?.summary || '围绕农业资源环境问题开展机制解析与应用研究。' }}</p>
        </aside>
      </div>
    </section>
  </PortalLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { fetchResearchDirection, type ResearchDirection } from '../../api/publicPortal'
import PortalLayout from '../../layouts/PortalLayout.vue'

const route = useRoute()
const direction = ref<ResearchDirection | null>(null)

const contentParagraphs = computed(() =>
  (direction.value?.content || '')
    .split(/\n+/)
    .map((item) => item.trim())
    .filter(Boolean),
)

onMounted(async () => {
  try {
    direction.value = await fetchResearchDirection(String(route.params.slug))
  } catch {
    direction.value = null
  }
})
</script>

<style scoped>
.portal-page-head {
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 30px 0 26px;
  background: linear-gradient(90deg, rgba(234, 245, 238, 0.78), rgba(255, 255, 255, 0.96) 52%, rgba(248, 247, 242, 0.92));
}

.portal-page-head h1 {
  margin: 0 0 10px;
  color: var(--color-deep-green);
  font-size: clamp(30px, 3.4vw, 42px);
  font-weight: 650;
}

.portal-page-head p:last-child {
  max-width: 860px;
  margin: 0;
  color: var(--color-muted);
  line-height: 1.75;
}

.back-link {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  border: 1px solid rgba(0, 135, 60, 0.24);
  border-radius: var(--radius-sm);
  margin-bottom: 14px;
  padding: 0 13px;
  background: rgba(255, 255, 255, 0.72);
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
}

.back-link::before {
  margin-right: 7px;
  content: "←";
}

.back-link:hover {
  border-color: var(--color-cau-green);
  background: var(--color-eco-green);
}

.page-section {
  background: var(--color-rice);
}

.detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 20px;
}

.detail-card,
.side-card {
  box-shadow: none;
}

.detail-card {
  overflow: hidden;
  padding: 0;
}

.detail-card img {
  width: 100%;
  max-height: 360px;
  object-fit: cover;
}

.detail-body {
  padding: 28px;
}

.detail-body h2 {
  margin: 0 0 18px;
  color: var(--color-deep-green);
  font-size: 24px;
}

.detail-body p {
  margin: 0 0 16px;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.85;
}

.muted {
  color: var(--color-muted) !important;
}

.side-card {
  position: sticky;
  top: 96px;
  align-self: start;
  padding: 22px;
}

.side-card span {
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.side-card strong {
  display: block;
  margin-top: 8px;
  color: var(--color-deep-green);
  font-size: 20px;
}

.side-card p {
  color: var(--color-muted);
  line-height: 1.7;
}

@media (max-width: 860px) {
  .detail-layout {
    grid-template-columns: 1fr;
  }

  .side-card {
    position: static;
  }
}
</style>
