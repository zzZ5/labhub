import type { AxiosProgressEvent } from 'axios'
import { http } from './http'

export interface DocumentCategory {
  id: number
  name: string
  parent: number | null
  slug: string
  description: string
  sort_order: number
}

export interface LabDocument {
  id: number
  title: string
  category: DocumentCategory | null
  description: string
  allow_download: boolean
  status: string
  status_label: string
  updated_at: string
  original_filename: string
  uploaded_by_name: string
  uploaded_at: string | null
  file_size: number
  file_type: string
  preview_status: string
  preview_error: string
  can_view: boolean
  can_preview: boolean
  can_download: boolean
  can_edit: boolean
  can_delete: boolean
}

export interface DocumentImportResult {
  created: number
  updated: number
  skipped: number
  errors: string[]
}

export interface DocumentFormPayload {
  title: string
  category_id?: number
  description?: string
  file?: File
}

export interface DocumentImportPayload {
  file: File
  archive?: File
}

export async function fetchDocumentCategories() {
  const response = await http.get<DocumentCategory[]>('/documents/categories/')
  return response.data
}

export async function fetchDocuments(params: { search?: string; category__slug?: string } = {}) {
  const response = await http.get<LabDocument[]>('/documents/documents/', { params })
  return response.data
}

export async function fetchDocument(documentId: number) {
  const response = await http.get<LabDocument>(`/documents/documents/${documentId}/`)
  return response.data
}

export async function createDocument(
  payload: DocumentFormPayload & { allow_download: boolean; status: string },
  onUploadProgress?: (event: AxiosProgressEvent) => void,
) {
  const formData = new FormData()
  formData.append('title', payload.title)
  formData.append('status', payload.status)
  formData.append('allow_download', String(payload.allow_download))
  if (payload.category_id) formData.append('category_id', String(payload.category_id))
  if (payload.description) formData.append('description', payload.description)
  if (payload.file) formData.append('file', payload.file)

  const response = await http.post<LabDocument>('/documents/documents/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 5400000,
    onUploadProgress,
  })
  return response.data
}

export async function updateDocument(
  documentId: number,
  payload: DocumentFormPayload & { allow_download: boolean; status: string },
  onUploadProgress?: (event: AxiosProgressEvent) => void,
) {
  const formData = new FormData()
  formData.append('title', payload.title)
  formData.append('status', payload.status)
  formData.append('allow_download', String(payload.allow_download))
  if (payload.category_id) formData.append('category_id', String(payload.category_id))
  if (payload.description) formData.append('description', payload.description)
  if (payload.file) formData.append('file', payload.file)

  const response = await http.patch<LabDocument>(`/documents/documents/${documentId}/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 5400000,
    onUploadProgress,
  })
  return response.data
}

export async function importDocumentsExcel(
  file: File,
  archive?: File,
  onUploadProgress?: (event: AxiosProgressEvent) => void,
) {
  const formData = new FormData()
  formData.append('file', file)
  if (archive) formData.append('archive', archive)

  const response = await http.post<DocumentImportResult>('/documents/documents/import-excel/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 5400000,
    onUploadProgress,
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
