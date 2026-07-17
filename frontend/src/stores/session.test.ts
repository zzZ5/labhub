import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { fetchCurrentUser, login, logout } from '../api/accounts'
import { useSessionStore } from './session'

vi.mock('../api/accounts', () => ({
  fetchCurrentUser: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
}))

const user = {
  id: 1,
  username: 'student',
  email: 'student@cau.edu.cn',
  is_active: true,
  is_staff: false,
  is_superuser: false,
  roles: [],
  profile: { real_name: '学生甲', is_approved: true },
} as any

describe('session store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('logs in with a trimmed account and stores the current user', async () => {
    vi.mocked(login).mockResolvedValue(user)
    const session = useSessionStore()

    await session.login('  student  ', 'password')

    expect(login).toHaveBeenCalledWith('student', 'password')
    expect(session.isAuthenticated).toBe(true)
    expect(session.displayName).toBe('学生甲')
    expect(session.loading).toBe(false)
  })

  it('clears stale authentication when loading the session fails', async () => {
    vi.mocked(fetchCurrentUser).mockRejectedValue(new Error('expired'))
    const session = useSessionStore()
    session.setUser(user)

    await session.loadCurrentUser()

    expect(session.isAuthenticated).toBe(false)
    expect(session.user).toBeNull()
    expect(session.initialized).toBe(true)
    expect(session.loading).toBe(false)
  })

  it('clears local state even when the logout request fails', async () => {
    vi.mocked(logout).mockRejectedValue(new Error('csrf expired'))
    const session = useSessionStore()
    session.setUser(user)

    await session.logout()

    expect(session.isAuthenticated).toBe(false)
    expect(session.user).toBeNull()
    expect(session.initialized).toBe(true)
    expect(session.loading).toBe(false)
  })
})
