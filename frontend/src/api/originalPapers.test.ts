import { describe, expect, it, vi } from 'vitest'
vi.mock('./http', () => ({ http: { defaults: { baseURL: '/api' } } }))
import { paperFileUrl, paperSourceUrl, type OriginalPaper } from './originalPapers'

describe('original paper links', () => {
  it('uses the protected API route without duplicating api prefix', () => {
    expect(paperFileUrl('/api/wechat/papers/1/download/')).toBe('/api/wechat/papers/1/download/')
    expect(paperFileUrl('')).toBe('')
  })
  it('prefers publisher links and otherwise resolves a DOI', () => {
    expect(paperSourceUrl({ publisher_url: 'https://example.com/paper', doi: '10.1234/test' } as OriginalPaper)).toBe('https://example.com/paper')
    expect(paperSourceUrl({ publisher_url: '', doi: '10.1234/a#b?c' } as OriginalPaper)).toBe('https://doi.org/10.1234/a%23b%3Fc')
    expect(paperSourceUrl({ publisher_url: '', doi: null } as OriginalPaper)).toBe('')
  })
})
