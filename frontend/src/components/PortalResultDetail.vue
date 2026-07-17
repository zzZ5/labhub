<template>
  <section class="result-detail-head">
    <div class="container">
      <ReturnLink :to="returnTo">返回科研成果</ReturnLink>
      <p class="section-kicker">{{ typeLabel }}</p>
      <h1>{{ title }}</h1>
      <div v-if="$slots.meta" class="result-detail-meta"><slot name="meta" /></div>
    </div>
  </section>

  <section class="result-detail-section">
    <div class="container result-detail-layout">
      <main class="card result-detail-main"><slot /></main>
      <aside class="card result-detail-side">
        <strong>{{ infoTitle }}</strong>
        <div class="result-detail-info"><slot name="info" /></div>
        <div v-if="$slots.actions" class="result-detail-actions"><slot name="actions" /></div>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'

import ReturnLink from './ReturnLink.vue'

defineProps<{
  returnTo: RouteLocationRaw
  typeLabel: string
  title: string
  infoTitle: string
}>()
</script>

<style scoped>
.result-detail-head {
  border-bottom: 1px solid rgba(31, 61, 43, 0.1);
  padding: 30px 0 28px;
  background: rgba(255, 255, 255, 0.74);
}

.result-detail-head .container {
  max-width: 1080px;
}

.section-kicker {
  margin: 18px 0 6px;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.result-detail-head h1 {
  max-width: 980px;
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(26px, 3.2vw, 38px);
  font-weight: 650;
  line-height: 1.28;
}

.result-detail-meta {
  margin-top: 14px;
}

.result-detail-meta :deep(.meta-list) {
  display: flex;
  flex-wrap: wrap;
  gap: 7px 16px;
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
}

.result-detail-section {
  padding: var(--space-8) 0 var(--space-16);
  background: var(--color-rice);
}

.result-detail-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  align-items: start;
  gap: 22px;
  max-width: 1080px;
}

.result-detail-main,
.result-detail-side {
  border-color: rgba(31, 61, 43, 0.1);
  box-shadow: none;
}

.result-detail-main {
  display: grid;
  gap: 26px;
  min-width: 0;
  padding: 28px 32px;
}

.result-detail-main :deep(section + section) {
  border-top: 1px solid var(--color-line);
  padding-top: 24px;
}

.result-detail-main :deep(h2) {
  margin: 0 0 12px;
  color: var(--color-deep-green);
  font-size: 21px;
  font-weight: 650;
}

.result-detail-main :deep(p) {
  margin: 0;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.85;
}

.result-detail-main :deep(.muted) {
  color: var(--color-muted);
}

.result-detail-side {
  padding: 21px;
}

.result-detail-side > strong {
  color: var(--color-deep-green);
  font-size: 17px;
}

.result-detail-info :deep(dl) {
  display: grid;
  gap: 13px;
  margin: 17px 0 0;
}

.result-detail-info :deep(dt),
.result-detail-info :deep(dd) {
  margin: 0;
}

.result-detail-info :deep(dt) {
  color: var(--color-muted);
  font-size: 12px;
}

.result-detail-info :deep(dd) {
  margin-top: 3px;
  color: var(--color-text);
  font-size: 14px;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.result-detail-actions {
  display: grid;
  gap: 12px;
  margin-top: 18px;
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

@media (max-width: 900px) {
  .result-detail-layout {
    grid-template-columns: 1fr;
  }

  .result-detail-side {
    order: -1;
  }
}

@media (max-width: 640px) {
  .result-detail-head {
    padding: 22px 0 20px;
  }

  .section-kicker {
    margin-top: 14px;
  }

  .result-detail-head h1 {
    font-size: 26px;
  }

  .result-detail-section {
    padding-top: 18px;
  }

  .result-detail-main {
    gap: 22px;
    padding: 22px 20px;
  }

  .result-detail-side {
    padding: 18px 20px;
  }
}
</style>
