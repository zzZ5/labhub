import { http } from './http'

export interface DashboardSummaryItem {
  label: string
  value: number
  note: string
}

export interface DashboardInstrumentStatus {
  id: number
  name: string
  location_detail: string
  status: string
  status_label: string
}

export interface DashboardDocument {
  id: number
  title: string
  category_name: string
  original_filename: string
  file_size: number
  updated_at: string
}

export interface DashboardTodo {
  title: string
  detail: string
  level: 'normal' | 'warning' | 'info'
  target: string
}

export interface DashboardStudentArchive {
  id: number
  name: string
  degree_type: string
  grade: string
  research_direction: string
  file_count: number
  latest_file_title: string
  latest_uploaded_at: string | null
}

export interface DashboardDownload {
  id: number
  document_title: string
  downloaded_at: string
}

export interface DashboardData {
  summary: DashboardSummaryItem[]
  instrument_status: DashboardInstrumentStatus[]
  latest_documents: DashboardDocument[]
  todos: DashboardTodo[]
  student_archives: DashboardStudentArchive[]
  recent_downloads: DashboardDownload[]
}

export async function fetchDashboard() {
  const response = await http.get<DashboardData>('/dashboard/')
  return response.data
}
