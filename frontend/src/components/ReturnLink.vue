<template>
  <a class="return-link" :href="href" @click.prevent="navigate">
    <el-icon><ArrowLeft /></el-icon><span><slot /></span>
  </a>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useRouter, type RouteLocationRaw } from 'vue-router'

const props = defineProps<{ to: RouteLocationRaw }>()
const router = useRouter()
const href = computed(() => router.resolve(props.to).href)

function navigate() {
  const target = router.resolve(props.to).fullPath
  const previous = window.history.state?.back
  if (typeof previous === 'string' && previous === target) {
    router.back()
    return
  }
  void router.push(props.to)
}
</script>

<style scoped>
.return-link {
  display: inline-flex;
  width: fit-content;
  min-height: 36px;
  align-items: center;
  gap: 7px;
  border: 1px solid var(--color-border-accent);
  border-radius: var(--radius-sm);
  padding: 0 12px;
  background: var(--surface-white-soft);
  color: var(--color-cau-green);
  font-size: 14px;
  font-weight: 650;
  text-decoration: none;
  transition: border-color 160ms ease, background 160ms ease, gap 160ms ease;
}

.return-link:hover {
  gap: 10px;
  border-color: var(--color-cau-green);
  background: var(--color-eco-green);
}

.return-link :deep(svg) {
  width: 15px;
  height: 15px;
}

@media (max-width: 720px) {
  .return-link {
    min-height: var(--control-touch);
  }
}
</style>
