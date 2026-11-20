import { CircleMarker, Popup } from 'react-leaflet'

const SEVERITY_COLORS = {
  CRITICAL: '#EF4444',
  HIGH:     '#F97316',
  MEDIUM:   '#F59E0B',
  LOW:      '#22C55E',
}

const SEVERITY_RADIUS = {
  CRITICAL: 10,
  HIGH:     8,
  MEDIUM:   6,
  LOW:      5,
}

export default function BlackSpotMarker({ spot, onClick }) {
  const color  = SEVERITY_COLORS[spot.severity] || '#94A3B8'
  const radius = SEVERITY_RADIUS[spot.severity] || 6

  return (
    <CircleMarker
      center={[spot.lat, spot.lng]}
      radius={radius}
      pathOptions={{
        color:       '#fff',
        weight:      2,
        fillColor:   color,
        fillOpacity: 0.85,
      }}
      eventHandlers={{ click: onClick }}
    >
      <Popup>
        <div style={{
          fontFamily: 'Inter, sans-serif',
          minWidth: 200,
          color: '#F1F5F9',
        }}>
          <p style={{ fontWeight: 600, fontSize: 13, margin: '0 0 6px' }}>{spot.name}</p>
          <p style={{ fontSize: 11, color: '#94A3B8', margin: '0 0 8px' }}>{spot.road_type}</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <Row label="Risk Score"  value={`${(spot.risk_score * 100).toFixed(0)}%`} color={color} />
            <Row label="Severity"    value={spot.severity} color={color} />
            <Row label="Accidents/yr" value={spot.annual_accidents} />
            <Row label="Fatalities"  value={spot.fatalities_ytd} />
          </div>
          <p style={{ fontSize: 11, color: '#94A3B8', marginTop: 8, borderTop: '1px solid #1E2329', paddingTop: 6 }}>
            {spot.primary_cause}
          </p>
        </div>
      </Popup>
    </CircleMarker>
  )
}

function Row({ label, value, color }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
      <span style={{ color: '#94A3B8' }}>{label}</span>
      <span style={{ color: color || '#F1F5F9', fontWeight: 500 }}>{value}</span>
    </div>
  )
}
