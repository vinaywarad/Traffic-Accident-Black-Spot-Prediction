import { X, MapPin, AlertTriangle, Car, CloudRain } from 'lucide-react'
import { useMapStore } from '../../store/useMapStore'

const SEVERITY_COLORS = {
  CRITICAL: '#EF4444',
  HIGH:     '#F97316',
  MEDIUM:   '#F59E0B',
  LOW:      '#22C55E',
}

export default function MapDrawer() {
  const { selectedBlackspot, drawerOpen, clearSelection } = useMapStore()

  const spot = selectedBlackspot
  const open = drawerOpen && !!spot

  return (
    <div style={{
      position: 'absolute',
      top: 0, right: 0,
      width: 320,
      height: '100%',
      background: '#111418',
      borderLeft: '1px solid #1E2329',
      zIndex: 1000,
      transform: open ? 'translateX(0)' : 'translateX(100%)',
      transition: 'transform 0.25s ease',
      overflowY: 'auto',
      padding: 20,
      display: 'flex',
      flexDirection: 'column',
      gap: 16,
    }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <div>
          <p style={{ fontSize: 15, fontWeight: 600, color: '#F1F5F9', margin: 0 }}>
            {spot?.name}
          </p>
          <p style={{ fontSize: 12, color: '#94A3B8', margin: '4px 0 0' }}>
            {spot?.road_type}
          </p>
        </div>
        <button
          onClick={clearSelection}
          style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 4 }}
        >
          <X size={16} color="#94A3B8" />
        </button>
      </div>

      {spot && (
        <>
          {/* Risk Score */}
          <div style={{
            background: '#0A0C10', borderRadius: 10,
            padding: 16, textAlign: 'center',
            border: `1px solid ${SEVERITY_COLORS[spot.severity]}33`,
          }}>
            <p style={{
              fontSize: 36, fontWeight: 700,
              fontFamily: 'DM Mono, monospace',
              color: SEVERITY_COLORS[spot.severity],
              margin: 0,
            }}>
              {(spot.risk_score * 100).toFixed(0)}%
            </p>
            <p style={{ fontSize: 12, color: '#94A3B8', margin: '4px 0 0' }}>Risk Score</p>
            <span style={{
              display: 'inline-block', marginTop: 8,
              padding: '3px 10px', borderRadius: 20,
              background: `${SEVERITY_COLORS[spot.severity]}22`,
              color: SEVERITY_COLORS[spot.severity],
              fontSize: 11, fontWeight: 600,
            }}>
              {spot.severity}
            </span>
          </div>

          {/* Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
            {[
              { icon: AlertTriangle, label: 'Accidents/yr', value: spot.annual_accidents, color: '#EF4444' },
              { icon: Car,           label: 'Fatalities',   value: spot.fatalities_ytd,   color: '#F97316' },
            ].map(({ icon: Icon, label, value, color }) => (
              <div key={label} style={{
                background: '#0A0C10', borderRadius: 8,
                padding: 12, border: '1px solid #1E2329',
              }}>
                <Icon size={14} color={color} />
                <p style={{ fontSize: 20, fontWeight: 700, color: '#F1F5F9', margin: '6px 0 2px', fontFamily: 'DM Mono, monospace' }}>
                  {value}
                </p>
                <p style={{ fontSize: 11, color: '#475569', margin: 0 }}>{label}</p>
              </div>
            ))}
          </div>

          {/* Primary Cause */}
          <div style={{
            background: '#0A0C10', borderRadius: 8,
            padding: 12, border: '1px solid #1E2329',
          }}>
            <p style={{ fontSize: 11, color: '#475569', margin: '0 0 6px', textTransform: 'uppercase', letterSpacing: 1 }}>
              Primary Cause
            </p>
            <p style={{ fontSize: 13, color: '#F1F5F9', margin: 0 }}>
              {spot.primary_cause}
            </p>
          </div>

          {/* Coordinates */}
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <MapPin size={12} color="#475569" />
            <span style={{ fontSize: 11, color: '#475569', fontFamily: 'DM Mono, monospace' }}>
              {spot.lat.toFixed(4)}, {spot.lng.toFixed(4)}
            </span>
          </div>
        </>
      )}
    </div>
  )
}
