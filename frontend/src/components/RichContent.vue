<template>
  <article class="rich-content" v-html="html"></article>
</template>

<script setup lang="ts">
defineProps<{ html: string }>()
</script>

<style scoped>
.rich-content {
  min-width: 0;
  color: var(--color-text);
  overflow-wrap: anywhere;
  word-break: normal;
}

.rich-content :deep(p) {
  margin: 0 0 18px;
  font-size: 16px;
  line-height: 1.95;
  white-space: pre-wrap;
}

.rich-content :deep(h2),
.rich-content :deep(h3),
.rich-content :deep(h4) {
  color: var(--color-deep-green);
  font-weight: 650;
  line-height: 1.45;
}

.rich-content :deep(h2) { margin: 32px 0 14px; font-size: 26px; }
.rich-content :deep(h3) { margin: 26px 0 12px; font-size: 21px; }
.rich-content :deep(h4) { margin: 22px 0 10px; font-size: 18px; }

.rich-content :deep(ul),
.rich-content :deep(ol) {
  margin: 0 0 20px;
  padding-left: 1.7em;
  line-height: 1.9;
}

.rich-content :deep(li + li) { margin-top: 5px; }

.rich-content :deep(blockquote) {
  margin: 24px 0;
  border-left: 3px solid var(--color-cau-green);
  padding: 5px 0 5px 20px;
  color: var(--color-muted);
}

.rich-content :deep(a) {
  color: var(--color-cau-green);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.rich-content :deep(figure) { margin: 26px 0; }

.rich-content :deep(img) {
  display: block;
  max-width: min(100%, 920px);
  height: auto;
  margin: 24px auto;
  border-radius: var(--radius-md);
}

.rich-content :deep(figcaption) {
  margin: -14px auto 0;
  color: var(--color-muted);
  font-size: 13px;
  line-height: 1.6;
  text-align: center;
}

.rich-content :deep(table) {
  display: block;
  width: max-content;
  max-width: 100%;
  overflow-x: auto;
  border-collapse: collapse;
  margin: 22px 0;
  font-size: 14px;
}

.rich-content :deep(th),
.rich-content :deep(td) {
  min-width: 110px;
  border: 1px solid var(--color-border);
  padding: 9px 11px;
  text-align: left;
  vertical-align: top;
}

.rich-content :deep(th) {
  background: var(--color-panel);
  color: var(--color-deep-green);
  font-weight: 650;
}

.rich-content :deep(pre) {
  max-width: 100%;
  overflow-x: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 14px;
  background: var(--color-panel);
  font-size: 13px;
  line-height: 1.65;
  white-space: pre;
}

.rich-content :deep(code) { overflow-wrap: normal; }

@media (max-width: 640px) {
  .rich-content :deep(p) { font-size: 15px; line-height: 1.85; }
  .rich-content :deep(h2) { font-size: 22px; }
  .rich-content :deep(h3) { font-size: 19px; }
}
</style>
