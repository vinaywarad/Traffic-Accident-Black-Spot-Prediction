/**
 * useAccidentData — Phase 5: delegates to React Query API hooks.
 * Kept for backward compatibility with any remaining references.
 */
import { useBlackspots } from '../api/hooks/useBlackspots'

export function useAccidentData() {
  const { isLoading, error } = useBlackspots()
  return { isLoading, error }
}
