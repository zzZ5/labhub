<template>
  <section class="portal-detail-head">
    <div class="container portal-detail-head__inner">
      <ReturnLink class="portal-back-link" :to="returnTo">{{ returnLabel }}</ReturnLink>
      <div>
        <p class="section-kicker">{{ kicker }}</p>
        <h1>{{ title }}</h1>
        <div v-if="$slots.meta" class="portal-detail-meta"><slot name="meta" /></div>
      </div>
    </div>
  </section>

  <section class="portal-detail-section">
    <div :class="['container portal-detail-layout', { 'is-single': !$slots.aside && !$slots.actions }]">
      <main class="card portal-detail-main"><slot /></main>
      <aside v-if="$slots.aside || $slots.actions" class="card portal-detail-side">
        <strong v-if="asideTitle">{{ asideTitle }}</strong>
        <div v-if="$slots.aside" class="portal-detail-info"><slot name="aside" /></div>
        <div v-if="$slots.actions" class="portal-detail-actions"><slot name="actions" /></div>
      </aside>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import ReturnLink from './ReturnLink.vue'

defineProps<{
  returnTo: RouteLocationRaw
  returnLabel: string
  kicker: string
  title: string
  asideTitle?: string
}>()
</script>

<style scoped>
.portal-detail-head {
  border-bottom: 1px solid var(--color-border-quiet);
  padding: 32px 0 28px;
  background: var(--surface-white-soft);
}

.portal-detail-head__inner {
  display: grid;
  max-width: 1120px;
  gap: 18px;
}

.section-kicker {
  margin: 0 0 7px;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.portal-detail-head h1 {
  max-width: 940px;
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(28px, 3.4vw, 40px);
  font-weight: 650;
  line-height: 1.2;
  overflow-wrap: anywhere;
}

.portal-detail-meta {
  margin-top: 15px;
  color: var(--color-muted);
}

.portal-detail-meta :deep(.meta-list) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 18px;
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
}

.portal-detail-section {
  padding: 32px 0 64px;
  background: var(--color-rice);
}

.portal-detail-layout {
  display: grid;
  max-width: 1120px;
  grid-template-columns: minmax(0, 1fr) 280px;
  align-items: start;
  gap: 24px;
}

.portal-detail-layout.is-single {
  max-width: 900px;
  grid-template-columns: minmax(0, 1fr);
}

.portal-detail-main,
.portal-detail-side {
  min-width: 0;
  border-color: var(--color-border-quiet);
  box-shadow: none;
}

.portal-detail-main {
  overflow: hidden;
  padding: 0;
}

.portal-detail-side {
  align-self: start;
  padding: 22px;
}

.portal-detail-side > strong {
  color: var(--color-deep-green);
  font-size: 18px;
}

.portal-detail-info :deep(dl) {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
}

.portal-detail-info :deep(dt),
.portal-detail-info :deep(dd) {
  margin: 0;
}

.portal-detail-info :deep(dt) {
  color: var(--color-muted);
  font-size: 13px;
}

.portal-detail-info :deep(dd) {
  margin-top: 4px;
  color: var(--color-text);
  font-size: 14px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}

.portal-detail-actions {
  display: grid;
  gap: 10px;
  margin-top: 18px;
  border-top: 1px solid var(--color-line);
  padding-top: 16px;
}

@media (max-width: 900px) {
  .portal-detail-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .portal-detail-head {
    padding: 24px 0 22px;
  }

  .portal-detail-head__inner {
    gap: 14px;
  }

  .portal-detail-head h1 {
    font-size: 27px;
  }

  .portal-detail-section {
    padding: 18px 0 42px;
  }

  .portal-detail-side {
    padding: 18px 20px;
  }
}
</style>
