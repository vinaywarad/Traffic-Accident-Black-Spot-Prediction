import { useQuery } from '@tanstack/react-query'
import { fetchHealth, fetchHealthDetailed } from '../services/healthService'

/**
 * Polls health endpoint every 30 seconds.
 * Used by ApiStatusBar to show live API connection status.
 */
export const useApiHealth = () =>
  useQuery({
    queryKey:        ['health'],
    queryFn:         fetchHealth,
    refetchInterval: 30 * 1000,
    retry:           1,
    throwOnError:    false,
  })

export const useApiHealthDetailed = () =>
  useQuery({
    queryKey:  ['health', 'detailed'],
    queryFn:   fetchHealthDetailed,
    staleTime: 30 * 1000,
    retry:     1,
    throwOnError: false,
  })
