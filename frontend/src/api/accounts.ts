import type { AxiosProgressEvent } from 'axios'

import { http } from './http'

export interface UserProfile {
  real_name: string
  avatar: string
  avatar_size?: number
  phone: string
  school_identity: string
  school_identity_label: string
  membership_status: string
  membership_status_label: string
  bio: string
  is_approved: boolean
}

export interface CurrentUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_staff: boolean
  is_superuser: boolean
  profile: UserProfile
  roles: string[]
}

export interface Role {
  id: number
  name: string
  code: string
  description: string
  is_system: boolean
  created_at: string
}

export interface AdminUserCreatePayload {
  username?: string
  email: string
  password: string
  real_name?: string
  phone?: string
  avatar?: File
  school_identity: string
  membership_status: string
  is_approved: boolean
  system_roles: string[]
}

export interface AdminUserUpdatePayload {
  username?: string
  email?: string
  real_name?: string
  phone?: string
  avatar?: File
  school_identity?: string
  membership_status?: string
  is_approved?: boolean
  is_active?: boolean
}

export interface AccountImportIssue {
  row: number
  status: 'skipped' | 'failed'
  message: string
}

export interface AccountImportResult {
  total: number
  created: number
  skipped: number
  failed: number
  student_profiles: number
  issues: AccountImportIssue[]
}

export async function login(username: string, password: string) {
  const response = await http.post<CurrentUser>('/accounts/auth/login/', { username, password })
  return response.data
}

export async function logout() {
  await http.post('/accounts/auth/logout/')
}

export async function fetchCurrentUser() {
  const response = await http.get<CurrentUser>('/accounts/auth/me/')
  return response.data
}

export async function updateCurrentUserProfile(payload: {
  username?: string
  real_name?: string
  phone?: string
  bio?: string
  avatar?: File
}) {
  const response = await http.patch<CurrentUser>('/accounts/auth/me/', userPayloadBody(payload))
  return response.data
}

export async function changeCurrentUserPassword(payload: {
  current_password: string
  new_password: string
  confirm_password: string
}) {
  const response = await http.post<{ detail: string }>('/accounts/auth/password/', payload)
  return response.data
}

export async function fetchRoles() {
  const response = await http.get<Role[]>('/accounts/roles/')
  return response.data
}

export async function seedRoles() {
  const response = await http.post<{ created: number }>('/accounts/roles/seed/')
  return response.data
}

export async function fetchUsers() {
  const response = await http.get<CurrentUser[]>('/accounts/users/')
  return response.data
}

export async function fetchPendingUsers() {
  const response = await http.get<CurrentUser[]>('/accounts/users/pending/')
  return response.data
}

export async function createUser(payload: AdminUserCreatePayload) {
  const response = await http.post<CurrentUser>('/accounts/users/create/', userPayloadBody(payload))
  return response.data
}

export async function importAccountsExcel(file: File, onUploadProgress?: (event: AxiosProgressEvent) => void) {
  const body = new FormData()
  body.append('file', file)
  const response = await http.post<AccountImportResult>('/accounts/users/import-excel/', body, { onUploadProgress })
  return response.data
}

export async function updateUser(id: number, payload: AdminUserUpdatePayload) {
  const response = await http.patch<CurrentUser>(`/accounts/users/${id}/update/`, userPayloadBody(payload))
  return response.data
}

function userPayloadBody(payload: AdminUserCreatePayload | AdminUserUpdatePayload | { username?: string; real_name?: string; phone?: string; bio?: string; avatar?: File }) {
  if (!payload.avatar) return payload
  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null) return
    if (key === 'system_roles' && Array.isArray(value)) {
      value.forEach((role) => formData.append('system_roles', role))
      return
    }
    formData.append(key, value instanceof File ? value : String(value))
  })
  return formData
}

export async function deleteUser(id: number) {
  await http.delete(`/accounts/users/${id}/delete/`)
}

export async function resetUserPassword(id: number, password: string) {
  const response = await http.post<CurrentUser>(`/accounts/users/${id}/reset-password/`, { password })
  return response.data
}

export async function approveUser(id: number, payload: { is_approved: boolean; school_identity?: string }) {
  const response = await http.post<CurrentUser>(`/accounts/users/${id}/approve/`, payload)
  return response.data
}

export async function assignUserRole(id: number, role_code: string) {
  const response = await http.post<CurrentUser>(`/accounts/users/${id}/roles/`, { role_code })
  return response.data
}

export async function removeUserRole(id: number, role_code: string) {
  const response = await http.delete<CurrentUser>(`/accounts/users/${id}/roles/${role_code}/`)
  return response.data
}
