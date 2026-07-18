<template>
  <div class="compact-data-row">
    <div v-if="$slots.leading" class="compact-data-row__leading"><slot name="leading" /></div>
    <div class="compact-data-row__copy">
      <strong class="compact-data-row__title" :title="title">{{ title }}</strong>
      <p v-if="description" class="compact-data-row__description" :title="description">{{ description }}</p>
      <div v-if="$slots.meta" class="compact-data-row__meta"><slot name="meta" /></div>
    </div>
    <div v-if="$slots.trailing" class="compact-data-row__trailing"><slot name="trailing" /></div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
}>()
</script>

<style scoped>
.compact-data-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 12px 16px;
  min-width: 0;
  min-height: 58px;
  padding: 11px 8px;
  transition: background 160ms ease, padding 160ms ease;
}

.compact-data-row:hover {
  padding-right: 5px;
  padding-left: 11px;
  background: linear-gradient(90deg, rgba(234, 245, 238, 0.62), rgba(245, 239, 227, 0.2));
}

.compact-data-row__leading,
.compact-data-row__copy,
.compact-data-row__meta,
.compact-data-row__trailing {
  min-width: 0;
}

.compact-data-row__copy {
  display: grid;
  gap: 3px;
}

.compact-data-row__title,
.compact-data-row__description {
  overflow: hidden;
  overflow-wrap: anywhere;
  text-overflow: ellipsis;
}

.compact-data-row__title {
  color: var(--color-deep-green);
  font-size: 15px;
  font-weight: 650;
  line-height: 1.4;
  white-space: nowrap;
}

.compact-data-row__description {
  display: -webkit-box;
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.5;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.compact-data-row__trailing {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.compact-data-row:hover .compact-data-row__title {
  color: var(--color-cau-green);
}

@media (max-width: 640px) {
  .compact-data-row {
    grid-template-columns: auto minmax(0, 1fr);
    gap: 8px 10px;
    min-height: 64px;
    padding: 10px 0;
  }

  .compact-data-row__trailing {
    grid-column: 1 / -1;
    justify-content: flex-start;
  }

  .compact-data-row__title {
    display: -webkit-box;
    line-height: 1.45;
    white-space: normal;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 2;
  }
}
</style>
