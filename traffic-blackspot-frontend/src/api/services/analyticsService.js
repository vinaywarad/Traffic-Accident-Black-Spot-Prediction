import apiClient from '../client'
import { ENDPOINTS } from '../endpoints'

export const fetchAnalyticsSummary = async () => {
  const { data } = await apiClient.get(ENDPOINTS.ANALYTICS_SUMMARY)
  return data
}

export const fetchHeatmapData = async (params = {}) => {
  const { data } = await apiClient.get(ENDPOINTS.ANALYTICS_HEATMAP, { params })
  return data
}

export const fetchTrendData = async (months = 24) => {
  const { data } = await apiClient.get(ENDPOINTS.ANALYTICS_TRENDS, { params: { months } })
  return data
}
