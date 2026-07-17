<template>
  <header class="internal-page-header">
    <div class="internal-page-header__copy">
      <div class="internal-page-header__description"><slot /></div>
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
  gap: var(--space-4);
  min-width: 0;
  border-bottom: 1px solid var(--color-line);
  padding: 2px 0 var(--space-3);
}

.internal-page-header__copy {
  display: grid;
  min-width: 0;
  gap: var(--space-2);
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

.internal-page-header__actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 0 0 auto;
  gap: var(--space-2);
}

@media (max-width: 720px) {
  .internal-page-header {
    display: grid;
    gap: var(--space-3);
    padding-bottom: var(--space-3);
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
