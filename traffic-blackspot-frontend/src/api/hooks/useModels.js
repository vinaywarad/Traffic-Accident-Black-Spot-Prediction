import { useQuery } from '@tanstack/react-query'
import { fetchModels, fetchModelMetrics } from '../services/modelService'

export const useModels = () =>
  useQuery({
    queryKey:  ['models'],
    queryFn:   fetchModels,
    staleTime: 10 * 60 * 1000,
    retry:     2,
  })

export const useModelMetrics = (modelName) =>
  useQuery({
    queryKey:  ['models', modelName, 'metrics'],
    queryFn:   () => fetchModelMetrics(modelName),
    enabled:   !!modelName,
    staleTime: 10 * 60 * 1000,
  })
