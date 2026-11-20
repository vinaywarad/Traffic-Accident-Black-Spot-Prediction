import { useQuery } from '@tanstack/react-query'
import { fetchAnalyticsSummary, fetchHeatmapData, fetchTrendData } from '../services/analyticsService'

export const ANALYTICS_KEYS = {
  summary: ['analytics', 'summary'],
  heatmap: (params) => ['analytics', 'heatmap', params],
  trends:  (months) => ['analytics', 'trends', months],
}

/**
 * Dashboard KPI summary — refetches every 5 minutes.
 */
export const useAnalyticsSummary = () =>
  useQuery({
    queryKey:        ANALYTICS_KEYS.summary,
    queryFn:         fetchAnalyticsSummary,
    staleTime:       5 * 60 * 1000,
    refetchInterval: 5 * 60 * 1000,
    retry:           2,
  })

export const useHeatmapData = (params = {}) =>
  useQuery({
    queryKey:  ANALYTICS_KEYS.heatmap(params),
    queryFn:   () => fetchHeatmapData(params),
    staleTime: 5 * 60 * 1000,
  })

export const useTrendData = (months = 24) =>
  useQuery({
    queryKey:  ANALYTICS_KEYS.trends(months),
    queryFn:   () => fetchTrendData(months),
    staleTime: 10 * 60 * 1000,
    retry:     2,
  })
