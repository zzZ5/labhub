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
  cover_image: string
  event_date: string | null
  category: { name: string } | null
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
  doi: string
  abstract: string
  pdf_file: string
  visibility: string
  is_representative: boolean
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
