<template>
  <div class="section-header">
    <p v-if="kicker" class="section-kicker">{{ kicker }}</p>
    <div>
      <h2>{{ title }}</h2>
      <p v-if="description">{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  kicker?: string
  title: string
  description?: string
}>()
</script>

<style scoped>
.section-header {
  position: relative;
  max-width: 760px;
  margin-bottom: 38px;
  padding-top: 12px;
}

.section-header::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 42px;
  height: 3px;
  content: "";
  background: var(--color-cau-green);
}

.section-header h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(28px, 4vw, 38px);
  font-weight: 650;
  line-height: 1.25;
}

.section-header p:last-child {
  margin: 12px 0 0;
  color: var(--color-muted);
  font-size: 16px;
  line-height: 1.8;
}
</style>
