import { onBeforeUnmount, ref, watch, type Ref } from 'vue'

export function useDebouncedValue<T>(source: Ref<T>, delay = 250) {
  const value = ref(source.value) as Ref<T>
  let timer: number | undefined

  watch(source, (next) => {
    if (timer) window.clearTimeout(timer)
    timer = window.setTimeout(() => { value.value = next }, delay)
  })

  onBeforeUnmount(() => {
    if (timer) window.clearTimeout(timer)
  })

  return value
}
