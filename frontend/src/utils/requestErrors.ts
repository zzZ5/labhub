export function requestErrorMessage(error: any, fallback = '操作失败，请稍后重试。') {
  if (error?.code === 'ERR_CANCELED') return '上传已取消。'
  const data = error?.response?.data
  if (typeof data?.detail === 'string') return data.detail
  for (const value of Object.values(data || {})) {
    if (Array.isArray(value) && value.length) return String(value[0])
    if (typeof value === 'string' && value.trim()) return value
  }
  if (error?.code === 'ECONNABORTED') return '上传超时，请检查网络后重试。'
  if (!error?.response) return '连接失败，请检查网络或服务器上传限制。'
  return fallback
}
