<template>
  <section :class="['feedback-panel', `is-${type}`]" :role="type === 'error' ? 'alert' : 'status'" aria-live="polite">
    <el-icon class="feedback-panel__icon">
      <CircleCheckFilled v-if="type === 'success'" />
      <WarningFilled v-else-if="type === 'warning' || type === 'error'" />
      <Loading v-else-if="type === 'processing'" class="is-loading" />
      <InfoFilled v-else />
    </el-icon>
    <div class="feedback-panel__body">
      <strong>{{ title }}</strong>
      <p v-if="description">{{ description }}</p>
      <slot />
    </div>
    <div v-if="$slots.action" class="feedback-panel__action"><slot name="action" /></div>
  </section>
</template>

<script setup lang="ts">
import { CircleCheckFilled, InfoFilled, Loading, WarningFilled } from '@element-plus/icons-vue'

withDefaults(defineProps<{
  type?: 'info' | 'success' | 'warning' | 'error' | 'processing'
  title: string
  description?: string
}>(), { type: 'info', description: '' })
</script>

<style scoped>
.feedback-panel {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: start;
  gap: var(--space-3);
  border: var(--border-default);
  border-radius: var(--radius-sm);
  padding: var(--space-3) var(--space-4);
  background: var(--color-panel);
  color: var(--color-text);
}
.feedback-panel__icon { margin-top: 2px; color: var(--color-info); font-size: 18px; }
.feedback-panel__body { min-width: 0; }
.feedback-panel strong { display: block; color: var(--color-deep-green); font-size: 14px; line-height: 1.5; }
.feedback-panel p { margin: 2px 0 0; color: var(--color-muted); font-size: 13px; line-height: 1.6; }
.feedback-panel__action { align-self: center; }
.feedback-panel.is-success { border-color: var(--color-success-border); background: var(--color-success-soft); }
.feedback-panel.is-success .feedback-panel__icon { color: var(--color-cau-green); }
.feedback-panel.is-warning { border-color: var(--color-warning-border); background: var(--surface-warning); }
.feedback-panel.is-warning .feedback-panel__icon { color: var(--color-warning); }
.feedback-panel.is-error { border-color: rgba(159, 47, 47, .22); background: var(--color-danger-soft); }
.feedback-panel.is-error .feedback-panel__icon { color: var(--color-danger); }
.feedback-panel.is-processing { border-color: var(--color-border-accent); background: var(--surface-hover); }
.feedback-panel.is-processing .feedback-panel__icon { color: var(--color-cau-green); }
@media (max-width: 480px) {
  .feedback-panel { grid-template-columns: auto minmax(0, 1fr); padding: var(--space-3); }
  .feedback-panel__action { grid-column: 2; justify-self: start; }
}
</style>
