import type { AxiosProgressEvent } from 'axios'
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
  image_size?: number
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

function toInstrumentBody(payload: Record<string, unknown>) {
  const hasFile = Object.values(payload).some((value) => value instanceof File)
  if (!hasFile) return payload
  const formData = new FormData()
  Object.entries(payload).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return
    formData.append(key, value instanceof File ? value : String(value))
  })
  return formData
}

export async function createInstrument(payload: Record<string, unknown>, onUploadProgress?: (event: AxiosProgressEvent) => void) {
  const body = toInstrumentBody(payload)
  const response = await http.post<Instrument>('/instruments/instruments/', body, {
    timeout: body instanceof FormData ? 5400000 : undefined,
    onUploadProgress,
  })
  return response.data
}

export async function updateInstrument(id: number, payload: Record<string, unknown>, onUploadProgress?: (event: AxiosProgressEvent) => void) {
  const body = toInstrumentBody(payload)
  const response = await http.patch<Instrument>(`/instruments/instruments/${id}/`, body, {
    timeout: body instanceof FormData ? 5400000 : undefined,
    onUploadProgress,
  })
  return response.data
}

export async function deleteInstrument(id: number) {
  await http.delete(`/instruments/instruments/${id}/`)
}
