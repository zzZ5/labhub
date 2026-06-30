import { http } from './http'

export interface Instrument {
  id: number
  name: string
  model: string
  serial_number?: string
  category?: { id: number; name: string; slug: string } | null
  room: string
  location_detail: string
  image: string | null
  status: string
  status_label: string
  need_training?: boolean
  notes: string
  sort_order?: number
  training_passed?: boolean
}

export async function fetchInstruments() {
  const response = await http.get<Instrument[]>('/instruments/instruments/')
  return response.data
}
