import { describe, expect, it } from 'vitest'

import { requestErrorMessage } from './requestErrors'

describe('requestErrorMessage', () => {
  it('uses structured backend error details', () => {
    expect(requestErrorMessage({ response: { data: { detail: '没有操作权限。' } } })).toBe('没有操作权限。')
    expect(requestErrorMessage({ response: { data: { file: ['文件超过大小限制。'] } } })).toBe('文件超过大小限制。')
  })

  it('distinguishes cancellation, timeout and connection failure', () => {
    expect(requestErrorMessage({ code: 'ERR_CANCELED' })).toBe('上传已取消。')
    expect(requestErrorMessage({ code: 'ECONNABORTED' })).toBe('上传超时，请检查网络后重试。')
    expect(requestErrorMessage(new Error('offline'))).toBe('连接失败，请检查网络或服务器上传限制。')
  })

  it('uses the caller fallback for unknown HTTP failures', () => {
    expect(requestErrorMessage({ response: { data: {} } }, '保存失败。')).toBe('保存失败。')
  })
})
