/**
 * useMapFilters — Phase 5: returns live predictions from map store.
 * Kept for backward compatibility.
 */
import { useMapStore } from '../store/useMapStore'

export function useMapFilters() {
  return useMapStore((s) => s.livePredictions)
}
