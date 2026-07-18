import { describe, expect, it } from 'vitest'

import { resolveVideoPlayback } from './videoPlayback'

describe('resolveVideoPlayback', () => {
  it('converts a bilibili page into an embedded player', () => {
    const result = resolveVideoPlayback('https://www.bilibili.com/video/BV1xx411c7mD?p=2')
    expect(result.kind).toBe('embed')
    expect(result.source).toBe('哔哩哔哩')
    expect(result.src).toContain('bvid=BV1xx411c7mD')
    expect(result.src).toContain('page=2')
  })

  it('recognizes common video providers and direct files', () => {
    expect(resolveVideoPlayback('https://youtu.be/dQw4w9WgXcQ').src).toContain('youtube-nocookie.com/embed/')
    expect(resolveVideoPlayback('https://v.qq.com/x/page/a123456.html').src).toContain('vid=a123456')
    expect(resolveVideoPlayback('https://example.com/demo.mp4?token=1').kind).toBe('direct')
  })

  it('keeps unknown and bilibili short links as external fallbacks', () => {
    expect(resolveVideoPlayback('https://b23.tv/abc123').kind).toBe('external')
    expect(resolveVideoPlayback('https://example.com/watch/123').kind).toBe('external')
  })
})
