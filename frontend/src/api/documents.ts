import { http } from './http'

export interface DocumentCategory {
  id: number
  name: string
  parent: number | null
  slug: string
  description: string
  sort_order: number
  visibility: string
}

export interface DocumentVersion {
  id: number
  version: string
  original_filename: string
  change_log: string
  uploaded_at: string
  file_size: number
  file_type: string
  is_current: boolean
  preview_status: string
  preview_error: string
}

export interface LabDocument {
  id: number
  title: string
  category: DocumentCategory | null
  description: string
  current_version: string
  visibility: string
  visibility_label: string
  allow_download: boolean
  status: string
  status_label: string
  updated_at: string
  versions: DocumentVersion[]
  can_view: boolean
  can_preview: boolean
  can_download: boolean
  can_edit: boolean
  can_delete: boolean
}

export async function fetchDocumentCategories() {
  const response = await http.get<DocumentCategory[]>('/documents/categories/')
  return response.data
}

export async function fetchDocuments(params: { search?: string; category__slug?: string } = {}) {
  const response = await http.get<LabDocument[]>('/documents/documents/', { params })
  return response.data
}

export async function createDocument(payload: {
  title: string
  category_id?: number
  description?: string
  visibility: string
  allow_download: boolean
  status: string
  version: string
  change_log?: string
  file?: File
}) {
  const formData = new FormData()
  formData.append('title', payload.title)
  formData.append('visibility', payload.visibility)
  formData.append('status', payload.status)
  formData.append('allow_download', String(payload.allow_download))
  formData.append('version', payload.version)
  if (payload.category_id) formData.append('category_id', String(payload.category_id))
  if (payload.description) formData.append('description', payload.description)
  if (payload.change_log) formData.append('change_log', payload.change_log)
  if (payload.file) formData.append('file', payload.file)

  const response = await http.post<LabDocument>('/documents/documents/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function downloadDocument(document: LabDocument) {
  const response = await http.get(`/documents/documents/${document.id}/download/`, {
    responseType: 'blob',
  })
  const disposition = response.headers['content-disposition'] || ''
  const match = disposition.match(/filename\*=UTF-8''([^;]+)/)
  const filename = match ? decodeURIComponent(match[1]) : `${document.title}.download`
  const url = window.URL.createObjectURL(response.data)
  const link = window.document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  window.URL.revokeObjectURL(url)
}

export async function deleteDocument(document: LabDocument) {
  await http.delete(`/documents/documents/${document.id}/`)
}

export function previewDocumentUrl(document: LabDocument) {
  return `/api/documents/documents/${document.id}/preview/`
}
