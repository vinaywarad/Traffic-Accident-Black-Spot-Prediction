import apiClient from '../client'
import { ENDPOINTS } from '../endpoints'

export const fetchBlackspots = async (params = {}) => {
  const { data } = await apiClient.get(ENDPOINTS.BLACKSPOTS, { params })
  return data
}

export const fetchBlackspotById = async (id) => {
  const { data } = await apiClient.get(ENDPOINTS.BLACKSPOT_BY_ID(id))
  return data
}
