<template>
  <form :class="['page-jump', { compact }]" @submit.prevent="submit">
    <input v-model.number="targetPage" type="number" inputmode="numeric" min="1" :max="totalPages" aria-label="当前页码，修改后跳转" @blur="inline && submit()" />
    <span v-if="!compact || inline">/ {{ totalPages }}</span>
    <button v-if="!inline" type="submit" aria-label="跳转到指定页">跳转</button>
  </form>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = withDefaults(defineProps<{ page: number; totalPages: number; compact?: boolean; inline?: boolean }>(), {
  compact: false,
  inline: false,
})
const emit = defineEmits<{ change: [page: number] }>()
const targetPage = ref(props.page)

watch(() => props.page, (page) => { targetPage.value = page })

function submit() {
  const value = Number(targetPage.value)
  const page = Number.isFinite(value) ? Math.min(props.totalPages, Math.max(1, Math.trunc(value))) : props.page
  targetPage.value = page
  emit('change', page)
}
</script>

<style scoped>
.page-jump { display: inline-flex; flex: 0 0 auto; align-items: center; justify-content: center; gap: 6px; color: #6b7280; font-size: 13px; white-space: nowrap; }
.page-jump input { width: 44px; height: 32px; box-sizing: border-box; appearance: textfield; padding: 0 4px; border: 1px solid #d7ded9; border-radius: 5px; background: #fff; color: #2f3437; font-variant-numeric: tabular-nums; line-height: 30px; text-align: center; outline: none; }
.page-jump input:focus { border-color: #00873c; box-shadow: 0 0 0 2px rgb(0 135 60 / 10%); }
.page-jump input::-webkit-inner-spin-button, .page-jump input::-webkit-outer-spin-button { margin: 0; appearance: none; }
.page-jump button { width: 48px; height: 32px; box-sizing: border-box; padding: 0; border: 1px solid #c9d8cf; border-radius: 5px; background: #fff; color: #1f5938; font-weight: 600; cursor: pointer; }
.page-jump button:hover { border-color: #00873c; background: #f2f8f4; }
.page-jump.compact input { width: 40px; height: 30px; }
.page-jump.compact button { width: 44px; height: 30px; }
.page-jump.compact.inline { gap: 4px; font-variant-numeric: tabular-nums; }
.page-jump.compact.inline input { width: 34px; border-color: transparent; background: transparent; font-weight: 700; }
.page-jump.compact.inline input:hover,
.page-jump.compact.inline input:focus { border-color: #c9d8cf; background: #fff; }
</style>
