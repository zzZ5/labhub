import type { DocumentCategory, LabDocument } from '../../api/documents'
import { formatFileSize as formatSharedFileSize } from '../../utils/files'

export function categoryName(category?: Pick<DocumentCategory, 'name'> | null) {
  return category?.name || '未分类'
}

export function formatFileSize(size: number) {
  return formatSharedFileSize(size)
}

export function currentFilename(document: LabDocument) {
  return document.original_filename || document.title
}

export function currentFileSizeLabel(document: LabDocument) {
  if (document.external_url) return '外部链接'
  return document.file_size ? formatFileSize(document.file_size) : '-'
}

export function currentFileLabel(document: LabDocument) {
  if (document.external_url) return /bilibili\.com|b23\.tv/i.test(document.external_url) ? '哔哩哔哩视频' : '外部视频资料'
  return document.file_size
    ? `${currentFilename(document)}（${formatFileSize(document.file_size)}）`
    : currentFilename(document)
}

export function fileTypeKind(document: LabDocument) {
  if (document.external_url) return 'video'
  const filename = currentFilename(document).toLowerCase()
  if (filename.endsWith('.pdf')) return 'pdf'
  if (filename.endsWith('.docx') || filename.endsWith('.doc')) return 'word'
  if (filename.endsWith('.pptx') || filename.endsWith('.ppt')) return 'ppt'
  if (filename.endsWith('.xlsx') || filename.endsWith('.xls')) return 'excel'
  if (filename.endsWith('.txt') || filename.endsWith('.md')) return 'text'
  return 'file'
}

export function fileTypeLabel(document: LabDocument) {
  return ({ pdf: 'PDF', word: 'Word', ppt: 'PPT', excel: 'Excel', text: '文本', video: '视频', file: '资料' })[fileTypeKind(document)]
}

export function formatDate(value: string) {
  return value ? value.slice(0, 10) : '-'
}
