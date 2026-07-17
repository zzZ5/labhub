export const BYTES_PER_MB = 1024 * 1024

export const UPLOAD_LIMIT_MB = {
  document: 200,
  spreadsheet: 50,
  image: 20,
  avatar: 10,
  logo: 5,
  favicon: 2,
} as const

export const UPLOAD_LIMIT = Object.fromEntries(
  Object.entries(UPLOAD_LIMIT_MB).map(([key, value]) => [key, value * BYTES_PER_MB]),
) as Record<keyof typeof UPLOAD_LIMIT_MB, number>

export const MAX_UPLOAD_SIZE = UPLOAD_LIMIT.document

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

export function middleEllipsisFilename(filename: string, maxLength = 46) {
  if (!filename || filename.length <= maxLength) return filename
  const dotIndex = filename.lastIndexOf('.')
  const extension = dotIndex > 0 && filename.length - dotIndex <= 12 ? filename.slice(dotIndex) : ''
  const basename = extension ? filename.slice(0, dotIndex) : filename
  const available = Math.max(12, maxLength - extension.length - 1)
  const headLength = Math.ceil(available * 0.62)
  const tailLength = Math.max(4, available - headLength)
  return `${basename.slice(0, headLength)}…${basename.slice(-tailLength)}${extension}`
}

export function validateUploadFile(file: File, maxSize = MAX_UPLOAD_SIZE) {
  if (file.size > maxSize) return `文件不能超过 ${formatFileSize(maxSize)}。`
  return ''
}
