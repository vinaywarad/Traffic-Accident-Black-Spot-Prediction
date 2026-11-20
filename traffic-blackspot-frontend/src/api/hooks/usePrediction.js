import { useMutation, useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { predictSingle, predictBatch, generateBengaluruGrid } from '../services/predictService'

/**
 * Mutation for single-point prediction (map click / form submit).
 * Shows toast on success for CRITICAL risk.
 */
export const usePredictSingle = () =>
  useMutation({
    mutationFn: predictSingle,
    onSuccess: (data) => {
      if (data.risk_level === 'CRITICAL') {
        toast.error('CRITICAL risk detected at this location!', {
          duration: 5000,
          icon: '⚠️',
        })
      }
    },
    onError: () => {
      toast.error('Prediction failed — check API connection')
    },
  })

/**
 * Batch prediction for the map heatmap.
 * Runs on map page mount and whenever density changes.
 */
export const useBatchPredict = (density = 'medium', enabled = true) => {
  const records = generateBengaluruGrid(density)
  return useQuery({
    queryKey:     ['predictions', 'batch', density],
    queryFn:      () => predictBatch(records),
    enabled,
    staleTime:    5 * 60 * 1000,
    retry:        1,
    throwOnError: false,
  })
}

/**
 * Hook for the predictions table page.
 * Fetches batch results for the full Bengaluru grid.
 */
export const usePredictionTable = () => {
  const records = generateBengaluruGrid('high')
  return useQuery({
    queryKey:  ['predictions', 'table'],
    queryFn:   () => predictBatch(records),
    staleTime: 5 * 60 * 1000,
    retry:     1,
  })
}
