<template>
  <section class="external-video">
    <div v-if="playback.kind !== 'external'" class="external-video__player">
      <iframe
        v-if="playback.kind === 'embed'"
        :src="playback.src"
        :title="`${title}视频播放器`"
        loading="lazy"
        allow="autoplay; encrypted-media; fullscreen; picture-in-picture"
        allowfullscreen
        referrerpolicy="strict-origin-when-cross-origin"
      ></iframe>
      <video v-else :src="playback.src" :aria-label="title" controls preload="metadata"></video>
    </div>

    <a v-else class="external-video-card" :href="url" target="_blank" rel="noopener noreferrer" :aria-label="`在${sourceLabel}观看：${title}`">
      <div class="external-video-card__cover">
        <img v-if="cover" :src="cover" :alt="`${title}视频封面`" loading="lazy" />
        <ImagePlaceholder v-else label="视频资料" />
        <span class="external-video-card__play" aria-hidden="true"><el-icon><VideoPlay /></el-icon></span>
      </div>
      <div class="external-video-card__body">
        <strong>{{ title }}</strong>
        <span>{{ sourceLabel }} · 暂不能内嵌播放</span>
      </div>
      <el-icon class="external-video-card__arrow" aria-hidden="true"><TopRight /></el-icon>
    </a>

    <footer v-if="playback.kind !== 'external'" class="external-video__footer">
      <span>{{ sourceLabel }}</span>
      <a :href="url" target="_blank" rel="noopener noreferrer">在原网站打开 <el-icon><TopRight /></el-icon></a>
    </footer>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TopRight, VideoPlay } from '@element-plus/icons-vue'
import ImagePlaceholder from './ImagePlaceholder.vue'
import { resolveVideoPlayback } from '../utils/videoPlayback'

const props = withDefaults(defineProps<{ url: string; title: string; cover?: string; source?: string }>(), {
  cover: '', source: '',
})
const playback = computed(() => resolveVideoPlayback(props.url))
const sourceLabel = computed(() => props.source || playback.value.source)
</script>

<style scoped>
.external-video { overflow: hidden; border: var(--border-default); border-radius: var(--radius-md); background: #fff; }
.external-video__player { width: 100%; aspect-ratio: 16 / 9; background: #111; }
.external-video__player iframe, .external-video__player video { display: block; width: 100%; height: 100%; border: 0; object-fit: contain; }
.external-video__footer { display: flex; align-items: center; justify-content: space-between; gap: var(--space-3); border-top: 1px solid var(--color-line); padding: 9px 12px; color: var(--color-muted); font-size: 12px; }
.external-video__footer a { display: inline-flex; align-items: center; gap: 4px; color: var(--color-cau-green); font-weight: 650; }
.external-video-card { display: grid; grid-template-columns: 132px minmax(0, 1fr) auto; align-items: center; gap: var(--space-4); overflow: hidden; border: var(--border-default); border-radius: var(--radius-md); padding: var(--space-3); background: var(--color-white); color: inherit; text-decoration: none; transition: border-color 160ms ease, background 160ms ease; }
.external-video > .external-video-card { border: 0; border-radius: 0; }
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
