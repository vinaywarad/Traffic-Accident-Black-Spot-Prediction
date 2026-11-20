import apiClient from '../client'
import { ENDPOINTS } from '../endpoints'

export const fetchModels = async () => {
  const { data } = await apiClient.get(ENDPOINTS.MODELS)
  return data
}

export const fetchModelMetrics = async (modelName) => {
  const { data } = await apiClient.get(`${ENDPOINTS.MODELS}/${modelName}/metrics`)
  return data
}
