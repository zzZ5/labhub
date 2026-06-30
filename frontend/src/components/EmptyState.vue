<template>
  <div class="empty-state">
    <component :is="icon" v-if="icon" />
    <h3>{{ title }}</h3>
    <p>{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  icon?: Component
  title: string
  description: string
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
</style>
