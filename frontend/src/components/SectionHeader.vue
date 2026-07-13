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
  max-width: 820px;
  margin-bottom: 34px;
  padding-top: 16px;
}

.section-header::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 56px;
  height: 3px;
  content: "";
  background: var(--color-cau-green);
}

.section-header h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(34px, 4.4vw, 46px);
  font-weight: 650;
  line-height: 1.18;
}

.section-header p:last-child {
  margin: 14px 0 0;
  color: var(--color-muted);
  font-size: 17px;
  line-height: 1.8;
}

@media (max-width: 640px) {
  .section-header {
    margin-bottom: 26px;
  }

  .section-header h2 {
    font-size: 30px;
  }

  .section-header p:last-child {
    font-size: 15px;
  }
}
</style>
