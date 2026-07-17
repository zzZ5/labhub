<template>
  <header class="internal-page-header">
    <div v-if="$slots.default || $slots.summary" class="internal-page-header__copy">
      <div v-if="$slots.default" class="internal-page-header__description"><slot /></div>
      <div v-if="$slots.summary" class="internal-page-header__summary"><slot name="summary" /></div>
    </div>
    <div v-if="$slots.actions" class="internal-page-header__actions"><slot name="actions" /></div>
  </header>
</template>

<style scoped>
.internal-page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  min-width: 0;
  min-height: 36px;
}

.internal-page-header__copy {
  display: flex;
  align-items: center;
  min-width: 0;
  gap: var(--space-3);
}

.internal-page-header__description :deep(p) {
  max-width: 820px;
  margin: 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.65;
}

.internal-page-header__summary,
.internal-page-header__actions {
  min-width: 0;
}

.internal-page-header__summary :deep(.compact-summary) {
  gap: 8px 18px;
}

.internal-page-header__summary :deep(.compact-summary strong) {
  font-size: 15px;
}

.internal-page-header__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 0 0 auto;
  gap: var(--space-2);
}

@media (max-width: 720px) {
  .internal-page-header {
    gap: var(--space-2);
    min-height: 36px;
  }

  .internal-page-header__actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    width: 100%;
  }

  .internal-page-header__actions :deep(.el-button),
  .internal-page-header__actions :deep(a) {
    width: 100%;
    min-height: var(--control-touch);
    margin: 0;
  }
}
</style>
