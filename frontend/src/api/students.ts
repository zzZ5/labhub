import type { AxiosProgressEvent } from 'axios'
import { http } from './http'

export interface StudentArchiveFile {
  id: number
  student: number
  file_type: string
  file_type_label: string
  title: string
  file: string
  file_size?: number
  preview_pdf: string
  preview_status: string
  preview_error: string
  original_filename: string
  uploaded_at: string
  description: string
  can_delete: boolean
}

export interface StudentProfile {
  id: number
  user: number
  user_display_name: string
  user_email: string
  user_username: string
  avatar: string
  avatar_size?: number
  name: string
  degree_type: string
  degree_label: string
  grade: string
  supervisor?: number | null
  supervisor_name: string
  supervisor_email?: string
  advisors: number[]
  advisor_names: string[]
  advisor_emails: string[]
  research_topic: string
  research_direction: string
  enrollment_date?: string | null
  graduation_date?: string | null
  destination?: string
  archive_files: StudentArchiveFile[]
  can_edit: boolean
  can_delete: boolean
}

export interface StudentProfilePayload {
  user: number
  name: string
  degree_type: string
  grade?: string
  supervisor?: number | null
  advisors?: number[]
  research_topic?: string
  research_direction?: string
  enrollment_date?: string | null
  graduation_date?: string | null
  destination?: string
  avatar_upload?: File
}

export interface StudentArchiveUploadPayload {
  file_type: string
  title: string
  description: string
  file: File
}

function studentAvatarBody(file: File) {
  const formData = new FormData()
  formData.append('avatar_upload', file)
  return formData
}

export async function fetchStudentProfiles() {
  const response = await http.get<StudentProfile[]>('/students/profiles/')
  return response.data
}

export async function fetchMyStudentProfile() {
  const response = await http.get<StudentProfile>('/students/profiles/me/')
  return response.data
}

export async function createStudentProfile(payload: StudentProfilePayload) {
  const { avatar_upload, ...profileData } = payload
  const response = await http.post<StudentProfile>('/students/profiles/', profileData)
  if (!avatar_upload) return response.data
  const avatarResponse = await http.patch<StudentProfile>(
    `/students/profiles/${response.data.id}/`,
    studentAvatarBody(avatar_upload),
  )
  return avatarResponse.data
}

export async function updateStudentProfile(id: number, payload: StudentProfilePayload) {
  const { avatar_upload, ...profileData } = payload
  const response = await http.put<StudentProfile>(`/students/profiles/${id}/`, profileData)
  if (!avatar_upload) return response.data
  const avatarResponse = await http.patch<StudentProfile>(`/students/profiles/${id}/`, studentAvatarBody(avatar_upload))
  return avatarResponse.data
}

export async function deleteStudentProfile(id: number) {
  await http.delete(`/students/profiles/${id}/`)
}

export async function uploadStudentArchiveFile(
  payload: StudentArchiveUploadPayload & { student: number },
  onUploadProgress?: (event: AxiosProgressEvent) => void,
) {
  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    formData.append(key, value instanceof File ? value : String(value))
  })
  const response = await http.post<StudentArchiveFile>('/students/archive-files/', formData, {
    timeout: 5400000,
    onUploadProgress,
  })
  return response.data
}

export async function deleteStudentArchiveFile(id: number) {
  await http.delete(`/students/archive-files/${id}/`)
}

export function previewStudentArchiveFileUrl(file: StudentArchiveFile) {
  return `/api/students/archive-files/${file.id}/preview/`
}

export function downloadStudentArchiveFileUrl(file: StudentArchiveFile) {
  return `/api/students/archive-files/${file.id}/download/`
}
