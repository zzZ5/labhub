import { http } from './http'

export interface ResearchDirection {
  id: number
  title: string
  slug: string
  summary: string
  keywords?: string
  content?: string
  cover_image?: string
  sort_order?: number
}

export interface SiteSetting {
  id: number
  site_name: string
  site_subtitle: string
  logo?: string
  favicon?: string
  hero_image?: string
  description: string
  keywords: string
  footer_text: string
  contact_email: string
  contact_phone: string
  address: string
  map_embed: string
}

export interface ContactInfo {
  id: number
  title: string
  content: string
  email: string
  phone: string
  address: string
  map_url: string
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
  join_date?: string | null
  graduation_date?: string | null
  destination?: string
  sort_order?: number
  educations?: { school: string; degree: string; major: string; start_date: string | null; end_date: string | null; description: string }[]
  experiences?: { organization: string; position: string; start_date: string | null; end_date: string | null; description: string }[]
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

export interface PaginatedResult<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
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
  sort_order?: number
}

export interface Patent {
  id: number
  title: string
  patent_number: string
  inventors: string
  application_date: string | null
  authorization_date: string | null
  status: string
  pdf_file?: string
  visibility?: string
  sort_order?: number
}

export interface Award {
  id: number
  title: string
  award_level: string
  award_date: string | null
  participants: string
  description: string
  image?: string
  attachment?: string
  visibility?: string
  sort_order?: number
}

function unwrapList<T>(data: T[] | PaginatedResult<T>) {
  return Array.isArray(data) ? data : data.results
}

export async function fetchResearchDirections() {
  const response = await http.get<ResearchDirection[]>('/portal/research-directions/')
  return response.data
}

export async function fetchResearchDirection(slug: string) {
  const response = await http.get<ResearchDirection>(`/portal/research-directions/${slug}/`)
  return response.data
}

export async function fetchSiteSetting() {
  const response = await http.get<Partial<SiteSetting>>('/portal/site-setting/')
  return response.data
}

export async function fetchContactInfo() {
  const response = await http.get<Partial<ContactInfo>>('/portal/contact/')
  return response.data
}

export async function fetchMembers() {
  const response = await http.get<Member[]>('/members/')
  return response.data
}

export async function fetchMember(id: number | string) {
  const response = await http.get<Member>(`/members/${id}/`)
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
  const response = await http.get<Publication[] | PaginatedResult<Publication>>('/publications/publications/', {
    params: { is_representative: true, page_size: 8 },
  })
  return unwrapList(response.data)
}

export async function fetchPublications(params: { year?: number; is_representative?: boolean; search?: string; page?: number; page_size?: number; ordering?: string } = {}) {
  const response = await http.get<Publication[] | PaginatedResult<Publication>>('/publications/publications/', { params })
  return unwrapList(response.data)
}

export async function fetchPublicationPage(params: { year?: number; is_representative?: boolean; search?: string; page?: number; page_size?: number; ordering?: string } = {}) {
  const response = await http.get<Publication[] | PaginatedResult<Publication>>('/publications/publications/', { params })
  return Array.isArray(response.data)
    ? { count: response.data.length, next: null, previous: null, results: response.data }
    : response.data
}

export async function fetchPublication(id: number | string) {
  const response = await http.get<Publication>(`/publications/publications/${id}/`)
  return response.data
}

export async function fetchProjects(params: { search?: string; page?: number; page_size?: number; ordering?: string } = {}) {
  const response = await http.get<Project[] | PaginatedResult<Project>>('/publications/projects/', { params })
  return unwrapList(response.data)
}

export async function fetchProjectPage(params: { search?: string; page?: number; page_size?: number; ordering?: string } = {}) {
  const response = await http.get<Project[] | PaginatedResult<Project>>('/publications/projects/', { params })
  return Array.isArray(response.data)
    ? { count: response.data.length, next: null, previous: null, results: response.data }
    : response.data
}

export async function fetchProject(id: number | string) {
  const response = await http.get<Project>(`/publications/projects/${id}/`)
  return response.data
}

export async function fetchPatents(params: { search?: string; page?: number; page_size?: number; ordering?: string } = {}) {
  const response = await http.get<Patent[] | PaginatedResult<Patent>>('/publications/patents/', { params })
  return unwrapList(response.data)
}

export async function fetchPatentPage(params: { search?: string; page?: number; page_size?: number; ordering?: string } = {}) {
  const response = await http.get<Patent[] | PaginatedResult<Patent>>('/publications/patents/', { params })
  return Array.isArray(response.data)
    ? { count: response.data.length, next: null, previous: null, results: response.data }
    : response.data
}

export async function fetchPatent(id: number | string) {
  const response = await http.get<Patent>(`/publications/patents/${id}/`)
  return response.data
}

export async function fetchAwardPage(params: { search?: string; page?: number; page_size?: number; ordering?: string } = {}) {
  const response = await http.get<Award[] | PaginatedResult<Award>>('/publications/awards/', { params })
  return Array.isArray(response.data)
    ? { count: response.data.length, next: null, previous: null, results: response.data }
    : response.data
}

export async function fetchAwards(params: { search?: string; page?: number; page_size?: number; ordering?: string } = {}) {
  const response = await http.get<Award[] | PaginatedResult<Award>>('/publications/awards/', { params })
  return unwrapList(response.data)
}

export async function fetchAward(id: number | string) {
  const response = await http.get<Award>(`/publications/awards/${id}/`)
  return response.data
}

export async function fetchPublicationStats() {
  const response = await http.get<PublicationStats>('/publications/stats/')
  return response.data
}
