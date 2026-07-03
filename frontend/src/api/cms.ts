import type { AxiosProgressEvent } from 'axios'
import { http } from './http'
import type { Instrument } from './instruments'
import type { Award, ContactInfo, Member, NewsArticle, NewsCategory, PaginatedResult, Patent, Project, Publication, ResearchDirection, SiteSetting } from './publicPortal'

export interface InstrumentCategory {
  id: number
  name: string
  slug: string
  description: string
  sort_order: number
}

export type CmsResource =
  | 'site-settings'
  | 'contact-info'
  | 'research-directions'
  | 'members'
  | 'news-categories'
  | 'news-articles'
  | 'news-images'
  | 'publications'
  | 'projects'
  | 'patents'
  | 'awards'
  | 'instrument-categories'
  | 'instruments'

async function list<T>(resource: CmsResource) {
  const response = await http.get<T[] | PaginatedResult<T>>(`/cms/${resource}/`)
  return Array.isArray(response.data) ? response.data : response.data.results
}

function toRequestBody(payload: Record<string, unknown>) {
  const hasFile = Object.values(payload).some((value) => value instanceof File)
  if (!hasFile) return payload

  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    if (value instanceof File) formData.append(key, value)
    else if (typeof value === 'object') formData.append(key, JSON.stringify(value))
    else formData.append(key, String(value))
  })
  return formData
}

async function create<T>(resource: CmsResource, payload: Record<string, unknown>, onUploadProgress?: (event: AxiosProgressEvent) => void) {
  const body = toRequestBody(payload)
  const response = await http.post<T>(`/cms/${resource}/`, body, {
    timeout: body instanceof FormData ? 5400000 : undefined,
    onUploadProgress,
  })
  return response.data
}

async function update<T>(resource: CmsResource, idOrSlug: number | string, payload: Record<string, unknown>, onUploadProgress?: (event: AxiosProgressEvent) => void) {
  const body = toRequestBody(payload)
  const response = await http.patch<T>(`/cms/${resource}/${idOrSlug}/`, body, {
    timeout: body instanceof FormData ? 5400000 : undefined,
    onUploadProgress,
  })
  return response.data
}

async function remove(resource: CmsResource, idOrSlug: number | string) {
  await http.delete(`/cms/${resource}/${idOrSlug}/`)
}

export interface CmsNewsArticle extends Omit<NewsArticle, 'category'> {
  category: NewsCategory | null
  content: string
  status: string
  visibility: string
  location: string
  is_pinned: boolean
}

export interface CmsNewsImage {
  id: number
  article: number
  image: string
  caption: string
  sort_order: number
}

export const cmsApi = {
  listSiteSettings: () => list<SiteSetting>('site-settings'),
  createSiteSetting: (payload: Record<string, unknown>) => create<SiteSetting>('site-settings', payload),
  updateSiteSetting: (id: number, payload: Record<string, unknown>) => update<SiteSetting>('site-settings', id, payload),

  listContactInfo: () => list<ContactInfo>('contact-info'),
  createContactInfo: (payload: Record<string, unknown>) => create<ContactInfo>('contact-info', payload),
  updateContactInfo: (id: number, payload: Record<string, unknown>) => update<ContactInfo>('contact-info', id, payload),

  listResearch: () => list<ResearchDirection>('research-directions'),
  createResearch: (payload: Record<string, unknown>) => create<ResearchDirection>('research-directions', payload),
  updateResearch: (slug: string, payload: Record<string, unknown>) => update<ResearchDirection>('research-directions', slug, payload),
  deleteResearch: (slug: string) => remove('research-directions', slug),

  listMembers: () => list<Member>('members'),
  createMember: (payload: Record<string, unknown>) => create<Member>('members', payload),
  updateMember: (id: number, payload: Record<string, unknown>) => update<Member>('members', id, payload),
  deleteMember: (id: number) => remove('members', id),

  listNewsCategories: () => list<NewsCategory>('news-categories'),
  createNewsCategory: (payload: Record<string, unknown>) => create<NewsCategory>('news-categories', payload),
  updateNewsCategory: (slug: string, payload: Record<string, unknown>) => update<NewsCategory>('news-categories', slug, payload),
  deleteNewsCategory: (slug: string) => remove('news-categories', slug),

  listNews: () => list<CmsNewsArticle>('news-articles'),
  createNews: (payload: Record<string, unknown>, onUploadProgress?: (event: AxiosProgressEvent) => void) => create<CmsNewsArticle>('news-articles', payload, onUploadProgress),
  updateNews: (slug: string, payload: Record<string, unknown>, onUploadProgress?: (event: AxiosProgressEvent) => void) => update<CmsNewsArticle>('news-articles', slug, payload, onUploadProgress),
  deleteNews: (slug: string) => remove('news-articles', slug),
  createNewsImage: (payload: Record<string, unknown>, onUploadProgress?: (event: AxiosProgressEvent) => void) => create<CmsNewsImage>('news-images', payload, onUploadProgress),
  deleteNewsImage: (id: number) => remove('news-images', id),

  listPublications: () => list<Publication>('publications'),
  createPublication: (payload: Record<string, unknown>) => create<Publication>('publications', payload),
  updatePublication: (id: number, payload: Record<string, unknown>) => update<Publication>('publications', id, payload),
  deletePublication: (id: number) => remove('publications', id),

  listProjects: () => list<Project>('projects'),
  createProject: (payload: Record<string, unknown>) => create<Project>('projects', payload),
  updateProject: (id: number, payload: Record<string, unknown>) => update<Project>('projects', id, payload),
  deleteProject: (id: number) => remove('projects', id),

  listPatents: () => list<Patent>('patents'),
  createPatent: (payload: Record<string, unknown>) => create<Patent>('patents', payload),
  updatePatent: (id: number, payload: Record<string, unknown>) => update<Patent>('patents', id, payload),
  deletePatent: (id: number) => remove('patents', id),

  listAwards: () => list<Award>('awards'),
  createAward: (payload: Record<string, unknown>) => create<Award>('awards', payload),
  updateAward: (id: number, payload: Record<string, unknown>) => update<Award>('awards', id, payload),
  deleteAward: (id: number) => remove('awards', id),

  listInstrumentCategories: () => list<InstrumentCategory>('instrument-categories'),
  createInstrumentCategory: (payload: Record<string, unknown>) => create<InstrumentCategory>('instrument-categories', payload),
  updateInstrumentCategory: (slug: string, payload: Record<string, unknown>) => update<InstrumentCategory>('instrument-categories', slug, payload),
  deleteInstrumentCategory: (slug: string) => remove('instrument-categories', slug),

  listInstruments: () => list<Instrument>('instruments'),
  createInstrument: (payload: Record<string, unknown>) => create<Instrument>('instruments', payload),
  updateInstrument: (id: number, payload: Record<string, unknown>) => update<Instrument>('instruments', id, payload),
  deleteInstrument: (id: number) => remove('instruments', id),
}
