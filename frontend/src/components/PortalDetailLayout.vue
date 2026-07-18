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
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--color-border-quiet);
  padding: 32px 0 28px;
  background:
    linear-gradient(100deg, rgba(234, 245, 238, 0.74), rgba(255, 255, 255, 0.94) 55%, rgba(245, 239, 227, 0.62)),
    #fff;
}

.portal-detail-head::after {
  position: absolute;
  right: max(20px, calc((100vw - var(--container)) / 2));
  bottom: -42px;
  width: 320px;
  height: 90px;
  border-top: 1px solid rgba(0, 135, 60, 0.13);
  border-radius: 50%;
  content: "";
  transform: rotate(-7deg);
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
  font-weight: 680;
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
  background: var(--surface-portal);
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
  position: relative;
  overflow: hidden;
  padding: 0;
}

.portal-detail-side {
  align-self: start;
  border-top: 3px solid var(--color-cau-green);
  padding: 20px 22px 22px;
}

.portal-detail-main {
  padding-top: 3px;
}

.portal-detail-main::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 92px;
  height: 3px;
  background: linear-gradient(90deg, var(--color-cau-green) 0 72px, var(--color-cau-gold) 72px 92px);
  content: "";
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
