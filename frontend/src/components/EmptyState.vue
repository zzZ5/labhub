<template>
  <div :class="['empty-state', { compact }]" role="status">
    <component :is="icon" v-if="icon" />
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
    <div v-if="$slots.action" class="empty-state__action"><slot name="action" /></div>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  icon?: Component
  title: string
  description: string
  compact?: boolean
}>()
</script>

<style scoped>
.empty-state {
  display: grid;
  place-items: center;
  min-height: 180px;
  border: 1px dashed var(--color-border);
  border-radius: var(--radius-md);
  background: #fff;
  color: var(--color-muted);
  text-align: center;
}

.empty-state svg {
  width: 34px;
  height: 34px;
  color: var(--color-cau-green);
}

.empty-state h3 {
  margin: 8px 0 0;
  color: var(--color-deep-green);
  font-size: 18px;
}

.empty-state p {
  margin: 4px 0 0;
}

.empty-state__action { margin-top: 12px; }

.empty-state.compact {
  min-height: 76px;
  border-style: solid;
  background: var(--color-panel);
  padding: 12px 16px;
}

.empty-state.compact h3 { margin: 0; font-size: 15px; }
.empty-state.compact p { font-size: 13px; }
</style>
