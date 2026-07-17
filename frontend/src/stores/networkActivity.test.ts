import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { beginNetworkRequest, finishNetworkRequest, useNetworkActivity } from './networkActivity'

describe('network activity', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    while (useNetworkActivity().activeRequests.value > 0) finishNetworkRequest()
    vi.runAllTimers()
  })

  afterEach(() => {
    while (useNetworkActivity().activeRequests.value > 0) finishNetworkRequest()
    vi.runAllTimers()
    vi.useRealTimers()
  })

  it('does not flash for a fast request', () => {
    const state = useNetworkActivity()

    beginNetworkRequest()
    finishNetworkRequest()
    vi.advanceTimersByTime(200)

    expect(state.visible.value).toBe(false)
    expect(state.progress.value).toBe(0)
  })

  it('shows progress for a slow request and hides after completion', () => {
    const state = useNetworkActivity()

    beginNetworkRequest()
    vi.advanceTimersByTime(121)
    expect(state.visible.value).toBe(true)
    expect(state.progress.value).toBeGreaterThanOrEqual(18)

    vi.advanceTimersByTime(530)
    expect(state.showLabel.value).toBe(true)

    finishNetworkRequest()
    expect(state.progress.value).toBe(100)
    vi.advanceTimersByTime(241)
    expect(state.visible.value).toBe(false)
    expect(state.progress.value).toBe(0)
  })

  it('waits for every concurrent request before hiding', () => {
    const state = useNetworkActivity()

    beginNetworkRequest()
    beginNetworkRequest()
    vi.advanceTimersByTime(121)
    finishNetworkRequest()

    expect(state.activeRequests.value).toBe(1)
    expect(state.visible.value).toBe(true)

    finishNetworkRequest()
    vi.advanceTimersByTime(241)
    expect(state.activeRequests.value).toBe(0)
    expect(state.visible.value).toBe(false)
  })
})
