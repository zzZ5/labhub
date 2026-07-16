import { computed, ref, watch, type Ref } from 'vue'

type Options = {
  pageSize?: number
  page?: Ref<number>
  initialPage?: number
}

export function useListPagination(total: Ref<number>, options: Options = {}) {
  const pageSize = options.pageSize || 12
  const page = options.page || ref(Math.max(1, options.initialPage || 1))
  const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

  function setPage(next: number) {
    page.value = Math.min(totalPages.value, Math.max(1, Math.trunc(next) || 1))
  }

  function resetPage() {
    page.value = 1
  }

  function paginate<T>(items: T[]) {
    const start = (page.value - 1) * pageSize
    return items.slice(start, start + pageSize)
  }

  watch(totalPages, () => setPage(page.value), { immediate: true })

  return { page, pageSize, totalPages, setPage, resetPage, paginate }
}
