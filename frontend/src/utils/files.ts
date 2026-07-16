export const MAX_UPLOAD_SIZE = 200 * 1024 * 1024

export function formatFileSize(size: number) {
  if (!Number.isFinite(size) || size <= 0) return '0 B'
  if (size >= 1024 * 1024 * 1024) return `${(size / 1024 / 1024 / 1024).toFixed(2)} GB`
  if (size >= 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`
  if (size >= 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${size} B`
}

export function formatOptionalFileSize(size?: number | null, fallback = '大小未知') {
  return size ? formatFileSize(size) : fallback
}

export function validateUploadFile(file: File, maxSize = MAX_UPLOAD_SIZE) {
  if (file.size > maxSize) return `文件不能超过 ${formatFileSize(maxSize)}。`
  return ''
}
