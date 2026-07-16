<template>
  <div class="global-loading" :class="{ visible }" aria-live="polite" aria-atomic="true">
    <div class="global-loading-track" aria-hidden="true">
      <span :style="{ transform: `scaleX(${progress / 100})` }"></span>
    </div>
    <Transition name="loading-label">
      <div v-if="visible && showLabel" class="global-loading-label" role="status">
        <i aria-hidden="true"></i>
        <span>正在加载</span>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { useNetworkActivity } from '../stores/networkActivity'

const { progress, showLabel, visible } = useNetworkActivity()
</script>

<style scoped>
.global-loading {
  position: fixed;
  inset: 0;
  z-index: 9999;
  pointer-events: none;
  visibility: hidden;
}

.global-loading.visible {
  visibility: visible;
}

.global-loading-track {
  position: absolute;
  top: 0;
  right: 0;
  left: 0;
  height: 3px;
  overflow: hidden;
  background: rgba(0, 135, 60, 0.08);
}

.global-loading-track span {
  display: block;
  width: 100%;
  height: 100%;
  transform: scaleX(0);
  transform-origin: left center;
  background: var(--color-cau-green);
  box-shadow: 0 0 10px rgba(0, 135, 60, 0.28);
  transition: transform 220ms ease-out;
}

.global-loading-label {
  position: absolute;
  right: 18px;
  bottom: 18px;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  min-height: 36px;
  border: 1px solid rgba(0, 135, 60, 0.16);
  border-radius: 7px;
  padding: 0 13px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 8px 22px rgba(31, 61, 43, 0.1);
  color: var(--color-deep-green);
  font-size: 13px;
  font-weight: 600;
}

.global-loading-label i {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(0, 135, 60, 0.18);
  border-top-color: var(--color-cau-green);
  border-radius: 50%;
  animation: loading-spin 720ms linear infinite;
}

.loading-label-enter-active,
.loading-label-leave-active {
  transition: opacity 160ms ease, transform 160ms ease;
}

.loading-label-enter-from,
.loading-label-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

@keyframes loading-spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 720px) {
  .global-loading-track {
    height: 2px;
  }

  .global-loading-label {
    right: 50%;
    bottom: 14px;
    transform: translateX(50%);
  }

  .loading-label-enter-from,
  .loading-label-leave-to {
    opacity: 0;
    transform: translate(50%, 6px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .global-loading-track span,
  .loading-label-enter-active,
  .loading-label-leave-active {
    transition: none;
  }

  .global-loading-label i {
    animation-duration: 1.6s;
  }
}
</style>
