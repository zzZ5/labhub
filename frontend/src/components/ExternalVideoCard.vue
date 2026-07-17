<template>
  <a class="external-video-card" :href="url" target="_blank" rel="noopener noreferrer" :aria-label="`在${sourceLabel}观看：${title}`">
    <div class="external-video-card__cover">
      <img v-if="cover" :src="cover" :alt="`${title}视频封面`" loading="lazy" />
      <ImagePlaceholder v-else label="视频资料" />
      <span class="external-video-card__play" aria-hidden="true"><el-icon><VideoPlay /></el-icon></span>
    </div>
    <div class="external-video-card__body">
      <strong>{{ title }}</strong>
      <span>{{ sourceLabel }} · 点击打开视频</span>
    </div>
    <el-icon class="external-video-card__arrow" aria-hidden="true"><TopRight /></el-icon>
  </a>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TopRight, VideoPlay } from '@element-plus/icons-vue'
import ImagePlaceholder from './ImagePlaceholder.vue'

const props = withDefaults(defineProps<{ url: string; title: string; cover?: string; source?: string }>(), {
  cover: '', source: '',
})
const sourceLabel = computed(() => props.source || (/bilibili\.com|b23\.tv/i.test(props.url) ? '哔哩哔哩' : '外部视频'))
</script>

<style scoped>
.external-video-card { display: grid; grid-template-columns: 132px minmax(0, 1fr) auto; align-items: center; gap: var(--space-4); overflow: hidden; border: var(--border-default); border-radius: var(--radius-md); padding: var(--space-3); background: var(--color-white); color: inherit; text-decoration: none; transition: border-color 160ms ease, background 160ms ease; }
.external-video-card:hover { border-color: var(--color-border-accent); background: var(--surface-hover); }
.external-video-card__cover { position: relative; overflow: hidden; aspect-ratio: 16 / 9; border-radius: var(--radius-sm); background: var(--color-panel-strong); }
.external-video-card__cover img { width: 100%; height: 100%; object-fit: cover; }
.external-video-card__play { position: absolute; inset: 0; display: grid; place-items: center; color: #fff; font-size: 28px; filter: drop-shadow(0 1px 3px rgba(0,0,0,.42)); }
.external-video-card__body { display: grid; min-width: 0; gap: 5px; }
.external-video-card__body strong { overflow: hidden; color: var(--color-deep-green); font-size: 15px; text-overflow: ellipsis; white-space: nowrap; }
.external-video-card__body span { color: var(--color-muted); font-size: 13px; }
.external-video-card__arrow { color: var(--color-cau-green); }
@media (max-width: 520px) {
  .external-video-card { grid-template-columns: 104px minmax(0, 1fr); gap: var(--space-3); }
  .external-video-card__arrow { display: none; }
}
</style>
