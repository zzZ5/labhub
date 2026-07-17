import { nextTick, ref } from 'vue'
import { describe, expect, it } from 'vitest'

import { useListPagination } from './useListPagination'

describe('useListPagination', () => {
  it('clamps direct page changes and slices the current page', () => {
    const total = ref(25)
    const pagination = useListPagination(total, { pageSize: 10 })
    const items = Array.from({ length: 25 }, (_, index) => index + 1)

    pagination.setPage(99)

    expect(pagination.page.value).toBe(3)
    expect(pagination.paginate(items)).toEqual([21, 22, 23, 24, 25])

    pagination.setPage(-2)
    expect(pagination.page.value).toBe(1)
  })

  it('returns to the last valid page after deleting the final item', async () => {
    const total = ref(13)
    const page = ref(2)
    const pagination = useListPagination(total, { pageSize: 12, page })

    total.value = 12
    await nextTick()

    expect(pagination.totalPages.value).toBe(1)
    expect(page.value).toBe(1)
  })

  it('keeps an empty list on page one', async () => {
    const total = ref(1)
    const page = ref(1)
    const pagination = useListPagination(total, { pageSize: 12, page })

    total.value = 0
    await nextTick()

    expect(pagination.totalPages.value).toBe(1)
    expect(page.value).toBe(1)
    expect(pagination.paginate([])).toEqual([])
  })
})
