import { http } from './http'

export interface ResearchDirection {
  id: number
  title: string
  slug: string
  summary: string
  content?: string
  cover_image?: string
  sort_order?: number
}

export interface Member {
  id: number
  name: string
  name_en: string
  role_type: string
  role_label: string
  grade: string
  research_direction: string
  avatar: string
  email: string
  profile: string
}

export interface NewsArticle {
  id: number
  title: string
  slug: string
  summary: string
  content?: string
  cover_image: string
  word_file?: string
  word_html?: string
  event_date: string | null
  location?: string
  category: { name: string } | null
  tags?: { id: number; name: string; slug: string }[]
  images?: { id: number; image: string; caption: string; sort_order: number }[]
  created_at?: string
  updated_at?: string
}

export interface NewsCategory {
  id: number
  name: string
  slug: string
  description: string
  sort_order: number
}

export interface Publication {
  id: number
  title: string
  authors: string
  journal: string
  year: number
  volume?: string
  issue?: string
  pages?: string
  doi: string
  impact_factor?: string | number | null
  jcr_partition?: string
  cas_partition?: string
  abstract: string
  pdf_file: string
  visibility: string
  is_representative: boolean
  sort_order?: number
  created_at?: string
  updated_at?: string
}

export interface PublicationStats {
  publications: number
  projects: number
  patents: number
  awards: number
}

export interface Project {
  id: number
  title: string
  project_number: string
  funding_source: string
  principal_investigator: string
  start_date: string | null
  end_date: string | null
  status: string
  visibility?: string
  description: string
}

export interface Patent {
  id: number
  title: string
  patent_number: string
  inventors: string
  application_date: string | null
  authorization_date: string | null
  status: string
  visibility?: string
}

export async function fetchResearchDirections() {
  const response = await http.get<ResearchDirection[]>('/portal/research-directions/')
  return response.data
}

export async function fetchMembers() {
  const response = await http.get<Member[]>('/members/')
  return response.data
}

export async function fetchNews(params: { category__slug?: string } = {}) {
  const response = await http.get<NewsArticle[]>('/news/articles/', { params })
  return response.data
}

export async function fetchNewsArticle(slug: string) {
  const response = await http.get<NewsArticle>(`/news/articles/${slug}/`)
  return response.data
}

export async function fetchNewsCategories() {
  const response = await http.get<NewsCategory[]>('/news/categories/')
  return response.data
}

export async function fetchRepresentativePublications() {
  const response = await http.get<Publication[]>('/publications/publications/', {
    params: { is_representative: true },
  })
  return response.data
}

export async function fetchPublications(params: { year?: number; is_representative?: boolean } = {}) {
  const response = await http.get<Publication[]>('/publications/publications/', { params })
  return response.data
}

export async function fetchPublication(id: number | string) {
  const response = await http.get<Publication>(`/publications/publications/${id}/`)
  return response.data
}

export async function fetchProjects() {
  const response = await http.get<Project[]>('/publications/projects/')
  return response.data
}

export async function fetchPatents() {
  const response = await http.get<Patent[]>('/publications/patents/')
  return response.data
}

export async function fetchPublicationStats() {
  const response = await http.get<PublicationStats>('/publications/stats/')
  return response.data
}
