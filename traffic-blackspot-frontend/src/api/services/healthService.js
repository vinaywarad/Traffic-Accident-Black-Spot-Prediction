import apiClient from '../client'
import { ENDPOINTS } from '../endpoints'

export const fetchHealth = async () => {
  const { data } = await apiClient.get(ENDPOINTS.HEALTH)
  return data
}

export const fetchHealthDetailed = async () => {
  const { data } = await apiClient.get(ENDPOINTS.HEALTH_DETAILED)
  return data
}
