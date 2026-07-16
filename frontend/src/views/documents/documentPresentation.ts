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
  return document.file_size ? formatFileSize(document.file_size) : '-'
}

export function currentFileLabel(document: LabDocument) {
  return document.file_size
    ? `${currentFilename(document)}（${formatFileSize(document.file_size)}）`
    : currentFilename(document)
}

export function fileTypeLabel(document: LabDocument) {
  const filename = currentFilename(document).toLowerCase()
  if (filename.endsWith('.pdf')) return 'PDF'
  if (filename.endsWith('.docx') || filename.endsWith('.doc')) return 'Word'
  if (filename.endsWith('.pptx') || filename.endsWith('.ppt')) return 'PPT'
  if (filename.endsWith('.xlsx') || filename.endsWith('.xls')) return 'Excel'
  if (filename.endsWith('.txt') || filename.endsWith('.md')) return '文本'
  return '资料'
}

export function formatDate(value: string) {
  return value ? value.slice(0, 10) : '-'
}
