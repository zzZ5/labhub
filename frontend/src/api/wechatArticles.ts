import { http } from './http'
import type { PaginatedResult } from './publicPortal'

export type WechatSourceType = 'rss' | 'json_api' | 'manual'

export interface WechatAccount {
  id: number
  name: string
  description: string
}

export interface ManagedWechatAccount extends WechatAccount {
  source_type: WechatSourceType
  source_type_label: string
  source_url: string
  api_token_env: string
  is_active: boolean
  sort_order: number
  article_count: number
  last_sync_attempt_at: string | null
  last_sync_success_at: string | null
  last_sync_error: string
  created_at: string
  updated_at: string
}

export interface WechatArticle {
  id: number
  account: WechatAccount
  title: string
  summary: string
  cover_url: string
  source_url: string
  published_at: string
  created_at: string
  updated_at: string
}

export interface ManagedWechatArticle {
  id: number
  account: number
  account_name: string
  title: string
  summary: string
  cover_url: string
  source_url: string
  source_guid: string
  published_at: string
  is_visible: boolean
  is_manual: boolean
  synced_at: string | null
  created_at: string
  updated_at: string
}

export interface WechatAccountPayload {
  name: string
  description: string
  source_type: WechatSourceType
  source_url: string
  api_token_env: string
  is_active: boolean
  sort_order: number
}

export interface WechatArticlePayload {
  account: number
  title: string
  summary: string
  cover_url: string
  source_url: string
  published_at: string
  is_visible: boolean
}

export async function fetchWechatAccounts() {
  const response = await http.get<WechatAccount[]>('/wechat/accounts/')
  return response.data
}

export async function fetchWechatArticles(params: { account?: number; search?: string; page?: number; page_size?: number } = {}) {
  const response = await http.get<PaginatedResult<WechatArticle>>('/wechat/articles/', { params })
  return response.data
}

export async function fetchManagedWechatAccounts(params: { search?: string; ordering?: string } = {}) {
  const response = await http.get<ManagedWechatAccount[]>('/wechat/manage/accounts/', { params })
  return response.data
}

export async function createWechatAccount(payload: WechatAccountPayload) {
  const response = await http.post<ManagedWechatAccount>('/wechat/manage/accounts/', payload)
  return response.data
}

export async function updateWechatAccount(id: number, payload: Partial<WechatAccountPayload>) {
  const response = await http.patch<ManagedWechatAccount>(`/wechat/manage/accounts/${id}/`, payload)
  return response.data
}

export async function deleteWechatAccount(id: number) {
  await http.delete(`/wechat/manage/accounts/${id}/`)
}

export async function syncWechatAccount(id: number) {
  const response = await http.post<{ detail: string }>(`/wechat/manage/accounts/${id}/sync/`)
  return response.data
}

export async function syncAllWechatAccounts() {
  const response = await http.post<{ detail: string }>('/wechat/manage/accounts/sync-all/')
  return response.data
}

export async function fetchManagedWechatArticles(params: {
  account?: number
  search?: string
  page?: number
  page_size?: number
  ordering?: string
} = {}) {
  const response = await http.get<PaginatedResult<ManagedWechatArticle>>('/wechat/manage/articles/', { params })
  return response.data
}

export async function createWechatArticle(payload: WechatArticlePayload) {
  const response = await http.post<ManagedWechatArticle>('/wechat/manage/articles/', payload)
  return response.data
}

export async function updateWechatArticle(id: number, payload: Partial<WechatArticlePayload>) {
  const response = await http.patch<ManagedWechatArticle>(`/wechat/manage/articles/${id}/`, payload)
  return response.data
}

export async function deleteWechatArticle(id: number) {
  await http.delete(`/wechat/manage/articles/${id}/`)
}

export async function bulkUpdateWechatArticles(ids: number[], operation: 'show' | 'hide' | 'delete') {
  const response = await http.post<{ affected: number }>('/wechat/manage/articles/bulk/', { ids, operation })
  return response.data
}
