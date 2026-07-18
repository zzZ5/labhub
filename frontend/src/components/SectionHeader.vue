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
  margin-bottom: 26px;
  padding-top: 13px;
}

.section-header::before {
  position: absolute;
  top: 0;
  left: 0;
  width: 36px;
  height: 3px;
  content: "";
  background: var(--color-cau-green);
}

.section-header::after {
  position: absolute;
  top: 0;
  left: 40px;
  width: 12px;
  height: 3px;
  background: var(--color-cau-gold);
  content: "";
}

.section-header h2 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: clamp(28px, 3.2vw, 34px);
  font-weight: 680;
  line-height: 1.18;
}

.section-header p:last-child {
  margin: 10px 0 0;
  color: var(--color-muted);
  font-size: 15px;
  line-height: 1.7;
}

@media (max-width: 640px) {
  .section-header {
    margin-bottom: 22px;
  }

  .section-header h2 {
    font-size: 27px;
  }

  .section-header p:last-child {
    font-size: 15px;
  }
}
</style>
