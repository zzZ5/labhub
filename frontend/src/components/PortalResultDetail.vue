<template>
  <PortalDetailLayout :return-to="returnTo" return-label="返回科研成果" :kicker="typeLabel" :title="title" :aside-title="infoTitle">
    <template v-if="$slots.meta" #meta><slot name="meta" /></template>
    <div class="result-detail-content"><slot /></div>
    <template #aside><slot name="info" /></template>
    <template v-if="$slots.actions" #actions><slot name="actions" /></template>
  </PortalDetailLayout>
</template>

<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'

import PortalDetailLayout from './PortalDetailLayout.vue'

defineProps<{
  returnTo: RouteLocationRaw
  typeLabel: string
  title: string
  infoTitle: string
}>()
</script>

<style scoped>
.result-detail-content {
  display: grid;
  gap: 26px;
  min-width: 0;
  padding: 28px 32px;
}

.result-detail-content :deep(section + section) {
  border-top: 1px solid var(--color-line);
  padding-top: 24px;
}

.result-detail-content :deep(h2) {
  margin: 0 0 12px;
  color: var(--color-deep-green);
  font-size: 21px;
  font-weight: 650;
}

.result-detail-content :deep(p) {
  margin: 0;
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.85;
}

.result-detail-content :deep(.muted) {
  color: var(--color-muted);
}

@media (max-width: 640px) {
  .result-detail-content {
    gap: 22px;
    padding: 22px 20px;
  }
}
</style>
