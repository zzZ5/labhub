<template>
  <header class="portal-page-header">
    <div class="container">
      <span v-if="eyebrow">{{ eyebrow }}</span>
      <h1>{{ title }}</h1>
      <p v-if="description">{{ description }}</p>
    </div>
  </header>
</template>

<script setup lang="ts">
withDefaults(defineProps<{ title: string; description?: string; eyebrow?: string }>(), {
  description: '',
  eyebrow: '',
})
</script>

<style scoped>
.portal-page-header {
  position: relative;
  border-bottom: 1px solid var(--color-border-quiet);
  padding: 33px 0 31px;
  background: #f4f7f4;
}

.portal-page-header .container {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
}

.portal-page-header span {
  display: inline-flex;
  width: fit-content;
  margin-bottom: 6px;
  color: var(--color-cau-gold-deep);
  font-size: 12px;
  font-weight: 650;
}

.portal-page-header h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: var(--font-page-title);
  font-weight: 680;
  line-height: 1.2;
}

.portal-page-header p {
  max-width: 820px;
  margin: 7px 0 0;
  color: var(--color-muted);
  font-size: 15px;
  line-height: 1.65;
}

@media (max-width: 720px) {
  .portal-page-header {
    padding: 20px 0 18px;
  }

  .portal-page-header .container {
    display: block;
  }

  .portal-page-header h1 {
    font-size: 27px;
  }

  .portal-page-header p {
    margin-top: 6px;
    font-size: 14px;
  }
}
</style>
