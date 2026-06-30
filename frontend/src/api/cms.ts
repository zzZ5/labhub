import { http } from './http'
import type { Instrument } from './instruments'
import type { Member, NewsArticle, NewsCategory, Publication, ResearchDirection } from './publicPortal'

export interface InstrumentCategory {
  id: number
  name: string
  slug: string
  description: string
  sort_order: number
}

export type CmsResource =
  | 'research-directions'
  | 'members'
  | 'news-categories'
  | 'news-articles'
  | 'publications'
  | 'instrument-categories'
  | 'instruments'

async function list<T>(resource: CmsResource) {
  const response = await http.get<T[]>(`/cms/${resource}/`)
  return response.data
}

function toRequestBody(payload: Record<string, unknown>) {
  const hasFile = Object.values(payload).some((value) => value instanceof File)
  if (!hasFile) return payload

  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    if (value instanceof File) formData.append(key, value)
    else formData.append(key, String(value))
  })
  return formData
}

async function create<T>(resource: CmsResource, payload: Record<string, unknown>) {
  const response = await http.post<T>(`/cms/${resource}/`, toRequestBody(payload))
  return response.data
}

async function update<T>(resource: CmsResource, idOrSlug: number | string, payload: Record<string, unknown>) {
  const response = await http.patch<T>(`/cms/${resource}/${idOrSlug}/`, toRequestBody(payload))
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

export const cmsApi = {
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
  createNews: (payload: Record<string, unknown>) => create<CmsNewsArticle>('news-articles', payload),
  updateNews: (slug: string, payload: Record<string, unknown>) => update<CmsNewsArticle>('news-articles', slug, payload),
  deleteNews: (slug: string) => remove('news-articles', slug),

  listPublications: () => list<Publication>('publications'),
  createPublication: (payload: Record<string, unknown>) => create<Publication>('publications', payload),
  updatePublication: (id: number, payload: Record<string, unknown>) => update<Publication>('publications', id, payload),
  deletePublication: (id: number) => remove('publications', id),

  listInstrumentCategories: () => list<InstrumentCategory>('instrument-categories'),
  createInstrumentCategory: (payload: Record<string, unknown>) => create<InstrumentCategory>('instrument-categories', payload),
  updateInstrumentCategory: (slug: string, payload: Record<string, unknown>) => update<InstrumentCategory>('instrument-categories', slug, payload),
  deleteInstrumentCategory: (slug: string) => remove('instrument-categories', slug),

  listInstruments: () => list<Instrument>('instruments'),
  createInstrument: (payload: Record<string, unknown>) => create<Instrument>('instruments', payload),
  updateInstrument: (id: number, payload: Record<string, unknown>) => update<Instrument>('instruments', id, payload),
  deleteInstrument: (id: number) => remove('instruments', id),
}
