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
  border-bottom: 1px solid var(--color-border-quiet);
  padding: 30px 0 26px;
  background: var(--surface-white-soft);
}

.portal-page-header .container {
  position: relative;
  padding-left: 20px;
}

.portal-page-header .container::before {
  position: absolute;
  top: 3px;
  bottom: 3px;
  left: 0;
  width: 3px;
  border-radius: 2px;
  background: var(--color-cau-green);
  content: "";
}

.portal-page-header span {
  display: block;
  margin-bottom: 5px;
  color: var(--color-cau-green);
  font-size: 13px;
  font-weight: 700;
}

.portal-page-header h1 {
  margin: 0;
  color: var(--color-deep-green);
  font-size: var(--font-page-title);
  font-weight: 650;
  line-height: 1.2;
}

.portal-page-header p {
  max-width: 820px;
  margin: 8px 0 0;
  color: var(--color-muted);
  font-size: 15px;
  line-height: 1.65;
}

@media (max-width: 720px) {
  .portal-page-header {
    padding: 22px 0 20px;
  }

  .portal-page-header .container {
    padding-left: 14px;
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
