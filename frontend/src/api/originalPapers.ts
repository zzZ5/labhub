import { http } from './http'

export const paperTopics = [
  { value: 'compost', label: '堆肥与腐殖化' },
  { value: 'soil', label: '土壤碳氮循环' },
  { value: 'nutrients', label: '养分回收利用' },
  { value: 'biomass', label: '生物质转化' },
  { value: 'environment', label: '环境风险与减排' },
]

export interface OriginalPaper {
  id: number
  title: string
  chinese_title: string
  authors: string
  journal: string
  year: number | null
  doi: string | null
  topic: string
  topic_label: string
  publisher_url: string
  wechat_url: string
  preview_url: string
  download_url: string
}

export interface ManagedOriginalPaper extends OriginalPaper {
  sharing: string
  rights_note: string
  has_pdf: boolean
  is_visible: boolean
}

interface PaperList<T> { count: number; results: T[] }

export interface PaperMetadata {
  doi: string
  title: string
  authors: string
  journal: string
  year: number | null
  publisher_url: string
  topic: string
  metadata_source: string
}

export async function lookupPaperMetadata(doi: string) {
  return (await http.post<PaperMetadata>('/wechat/manage/papers/lookup/', { doi }, { timeout: 15000 })).data
}

export async function fetchOriginalPapers(params: { search?: string; topic?: string; page?: number }, manage = false) {
  return (await http.get<PaperList<ManagedOriginalPaper>>(`/wechat/${manage ? 'manage/' : ''}papers/`, { params })).data
}

export async function saveOriginalPaper(id: number | null, data: FormData, onProgress: (percent: number) => void) {
  const config = {
    timeout: 0,
    onUploadProgress: (event: { loaded: number; total?: number }) => {
      if (event.total) onProgress(Math.round(event.loaded * 100 / event.total))
    },
  }
  if (id) return (await http.patch<ManagedOriginalPaper>(`/wechat/manage/papers/${id}/`, data, config)).data
  return (await http.post<ManagedOriginalPaper>('/wechat/manage/papers/', data, config)).data
}

export async function deleteOriginalPaper(id: number) {
  await http.delete(`/wechat/manage/papers/${id}/`)
}

export function paperSourceUrl(paper: OriginalPaper) {
  return paper.publisher_url || (paper.doi ? `https://doi.org/${encodeURI(paper.doi).replace(/#/g, '%23').replace(/\?/g, '%3F')}` : '')
}

export function paperFileUrl(value: string) {
  // Public API returns relative paths; preserve deployments with a separate API origin.
  if (!value) return ''
  const base = String(http.defaults.baseURL || '/api').replace(/\/$/, '')
  return value.startsWith('/api/') ? `${base}${value.slice(4)}` : value
}
