import { useQuery } from '@tanstack/react-query'
import { fetchBlackspots, fetchBlackspotById } from '../services/blackspotService'

export const BLACKSPOT_KEYS = {
  all:    ['blackspots'],
  list:   (params) => ['blackspots', 'list', params],
  detail: (id)     => ['blackspots', 'detail', id],
}

/**
 * Fetch all black spots with optional severity filter.
 * Cached for 10 minutes — this data changes rarely.
 */
export const useBlackspots = (params = {}) =>
  useQuery({
    queryKey:  BLACKSPOT_KEYS.list(params),
    queryFn:   () => fetchBlackspots(params),
    staleTime: 10 * 60 * 1000,
    retry:     2,
  })

export const useBlackspotDetail = (id) =>
  useQuery({
    queryKey:  BLACKSPOT_KEYS.detail(id),
    queryFn:   () => fetchBlackspotById(id),
    enabled:   !!id,
    staleTime: 10 * 60 * 1000,
  })
