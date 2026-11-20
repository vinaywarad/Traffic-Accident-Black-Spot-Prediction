import { useEffect } from 'react'
import { useBatchPredict } from '../api/hooks/usePrediction'
import { useBlackspots }   from '../api/hooks/useBlackspots'
import { useMapStore }     from '../store/useMapStore'
import AccidentMap         from '../components/map/AccidentMap'
import MapControls         from '../components/map/MapControls'
import MapLegend           from '../components/map/MapLegend'
import MapDrawer           from '../components/map/MapDrawer'

export default function MapPage() {
  const { activeLayers, setLivePredictions } = useMapStore()

  // Live batch predictions for heatmap
  const {
    data:      batchData,
    isLoading: loadingPreds,
    refetch:   refetchPreds,
  } = useBatchPredict('medium', activeLayers.heatmap)

  // Known black spots from API
  const { data: blackspotData, isLoading: loadingSpots } = useBlackspots({ limit: 50 })

  // Push predictions into map store when data arrives
  useEffect(() => {
    if (batchData?.predictions) {
      setLivePredictions(batchData.predictions)
    }
  }, [batchData, setLivePredictions])

  const isLoading = loadingPreds || loadingSpots

  return (
    <div style={{ position: 'relative', width: '100%', height: 'calc(100vh - 60px)' }}>

      {/* Loading indicator */}
      {isLoading && (
        <div style={{
          position: 'absolute', top: 16, left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 1000,
          background: '#111418',
          border: '1px solid #F59E0B44',
          borderRadius: 20,
          padding: '6px 16px',
          display: 'flex', alignItems: 'center', gap: 8,
          fontSize: 12, color: '#F59E0B',
        }}>
          <div style={{
            width: 12, height: 12,
            border: '2px solid #F59E0B',
            borderTopColor: 'transparent',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite',
          }} />
          Loading live predictions...
        </div>
      )}

      {/* Map */}
      <AccidentMap
        height="100%"
        predictions={batchData?.predictions || []}
        blackspots={blackspotData?.spots || []}
        isLoading={isLoading}
      />

      {/* Layer controls */}
      <MapControls onRefresh={refetchPreds} />

      {/* Legend */}
      <MapLegend />

      {/* Detail drawer */}
      <MapDrawer />

      {/* Floating stats bar */}
      {batchData && (
        <div style={{
          position: 'absolute',
          bottom: 24, left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 1000,
          background: 'rgba(17,20,24,0.92)',
          backdropFilter: 'blur(12px)',
          border: '1px solid #1E2329',
          borderRadius: 12,
          padding: '10px 24px',
          display: 'flex', alignItems: 'center', gap: 24,
          fontSize: 12, color: '#94A3B8',
          whiteSpace: 'nowrap',
        }}>
          <Stat label="Locations scored" value={batchData.total} color="#F1F5F9" />
          <Stat label="Black spots"      value={batchData.blackspot_count} color="#EF4444" />
          <Stat label="Avg risk"         value={`${(batchData.avg_risk_score * 100).toFixed(0)}%`} color="#F59E0B" />
          <Stat label="Response"         value={`${batchData.processing_ms}ms`} color="#06B6D4" />
        </div>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}

function Stat({ label, value, color }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <span style={{ color: '#475569' }}>{label}:</span>
      <span style={{ color, fontWeight: 700, fontFamily: 'DM Mono, monospace' }}>{value}</span>
    </div>
  )
}
