import { http } from './http'

export interface HealthPayload {
  status: string
  service: string
  database: string
}

export async function fetchHealth() {
  const response = await http.get<HealthPayload>('/health/')
  return response.data
}
