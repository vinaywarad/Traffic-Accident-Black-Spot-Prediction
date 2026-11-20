import { useBlackspots } from '../../api/hooks/useBlackspots'
import { ListSkeleton } from '../ui/Skeletons'
import RiskBadge from '../ui/RiskBadge'

export default function TopBlackSpots({ limit = 5 }) {
  const { data, isLoading, error } = useBlackspots({ limit })

  if (isLoading) return <ListSkeleton rows={limit} />

  if (error) return (
    <div style={{ color: '#475569', fontSize: 13, padding: '12px 0' }}>
      Failed to load black spots
    </div>
  )

  const spots = data?.spots || []

  if (!spots.length) return (
    <div style={{ color: '#475569', fontSize: 13, padding: '12px 0' }}>
      No black spots found
    </div>
  )

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {spots.map((spot, i) => (
        <div
          key={spot.id}
          style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            padding: '10px 12px', borderRadius: 8,
            background: '#0A0C10', border: '1px solid #1E2329',
            cursor: 'pointer', transition: 'border-color 0.2s',
          }}
          onMouseEnter={(e) => e.currentTarget.style.borderColor = '#F59E0B'}
          onMouseLeave={(e) => e.currentTarget.style.borderColor = '#1E2329'}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 11, color: '#475569', width: 16, textAlign: 'right' }}>
              {i + 1}
            </span>
            <div>
              <p style={{ fontSize: 13, fontWeight: 500, color: '#F1F5F9', margin: 0 }}>
                {spot.name}
              </p>
              <p style={{ fontSize: 11, color: '#475569', margin: 0 }}>
                {spot.road_type} · {spot.annual_accidents} acc/yr
              </p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{
              fontSize: 11, fontFamily: 'DM Mono, monospace',
              color: spot.risk_score >= 0.75 ? '#EF4444' : spot.risk_score >= 0.55 ? '#F97316' : '#F59E0B',
            }}>
              {(spot.risk_score * 100).toFixed(0)}%
            </span>
            <RiskBadge severity={spot.severity} />
          </div>
        </div>
      ))}
    </div>
  )
}
