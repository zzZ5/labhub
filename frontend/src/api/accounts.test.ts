import { describe, expect, it, vi } from 'vitest'

const { post } = vi.hoisted(() => ({ post: vi.fn() }))
vi.mock('./http', () => ({ http: { post } }))

import { importAccountsExcel } from './accounts'

describe('importAccountsExcel', () => {
  it('uses the long-running upload timeout for password hashing and account creation', async () => {
    post.mockResolvedValue({ data: { total: 1, created: 1, skipped: 0, failed: 0, student_profiles: 0, issues: [] } })
    const progress = vi.fn()

    await importAccountsExcel(new File(['xlsx'], 'accounts.xlsx'), progress)

    expect(post).toHaveBeenCalledWith(
      '/accounts/users/import-excel/',
      expect.any(FormData),
      expect.objectContaining({ timeout: 5400000, onUploadProgress: progress }),
    )
  })
})
