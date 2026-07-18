import { beforeEach, describe, expect, it, vi } from 'vitest'

const { importPublications, success, warning, error } = vi.hoisted(() => ({
  importPublications: vi.fn(),
  success: vi.fn(),
  warning: vi.fn(),
  error: vi.fn(),
}))

vi.mock('element-plus', () => ({ ElMessage: { success, warning, error } }))
vi.mock('../../../api/cms', () => ({
  cmsApi: {
    importMembers: vi.fn(),
    importPublications,
    importProjects: vi.fn(),
    importPatents: vi.fn(),
    importAwards: vi.fn(),
  },
}))

import { useCmsImport } from './useCmsImport'

describe('useCmsImport', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.clearAllMocks()
  })

  it('keeps a successful import successful when list reload fails', async () => {
    importPublications.mockResolvedValue({ created: 2, updated: 0, skipped: 0 })
    const reload = vi.fn().mockRejectedValue(new Error('refresh failed'))
    const { importFile } = useCmsImport(reload)

    await importFile(new File(['xlsx'], 'papers.xlsx'), 'publications')

    expect(success).toHaveBeenCalledWith('导入完成：新增 2 条，更新 0 条，跳过 0 条。')
    expect(warning).toHaveBeenCalledWith('导入数据已经保存，但列表刷新失败，请手动刷新页面查看。')
    expect(error).not.toHaveBeenCalled()
  })

  it('shows server processing at 100% and blocks the same completed import', async () => {
    importPublications.mockImplementation(async (_file, onProgress) => {
      onProgress({ loaded: 10, total: 10 })
      return { created: 1, updated: 0, skipped: 0 }
    })
    const reload = vi.fn().mockResolvedValue(undefined)
    const { importFile, importProgress, completedKind, resetCompletedImport } = useCmsImport(reload)
    const file = new File(['xlsx'], 'papers.xlsx')

    await importFile(file, 'publications')
    await importFile(file, 'publications')

    expect(importProgress.value).toBe(100)
    expect(completedKind.value).toBe('publications')
    expect(importPublications).toHaveBeenCalledTimes(1)

    vi.advanceTimersByTime(900)
    resetCompletedImport('publications')
    expect(completedKind.value).toBe('')
    expect(importProgress.value).toBe(0)
  })
})
