import { Layers, RefreshCw, Map } from 'lucide-react'
import { useMapStore } from '../../store/useMapStore'

export default function MapControls({ onRefresh }) {
  const { activeLayers, toggleLayer } = useMapStore()

  return (
    <div style={{
      position: 'absolute',
      top: 16, left: 16,
      zIndex: 1000,
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
    }}>
      {/* Layer toggles */}
      <div style={{
        background: '#111418',
        border: '1px solid #1E2329',
        borderRadius: 10,
        padding: 12,
        display: 'flex',
        flexDirection: 'column',
        gap: 8,
        minWidth: 160,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
          <Layers size={13} color="#94A3B8" />
          <span style={{ fontSize: 11, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: 1 }}>
            Layers
          </span>
        </div>

        {[
          { key: 'heatmap',   label: 'Risk Heatmap',   color: '#EF4444' },
          { key: 'blackspots', label: 'Black Spots',   color: '#F59E0B' },
        ].map(({ key, label, color }) => (
          <label key={key} style={{
            display: 'flex', alignItems: 'center', gap: 8,
            cursor: 'pointer', fontSize: 12, color: '#94A3B8',
          }}>
            <div
              onClick={() => toggleLayer(key)}
              style={{
                width: 32, height: 18, borderRadius: 9,
                background: activeLayers[key] ? color : '#1E2329',
                position: 'relative', cursor: 'pointer',
                transition: 'background 0.2s',
                flexShrink: 0,
              }}
            >
              <div style={{
                position: 'absolute',
                top: 2, left: activeLayers[key] ? 16 : 2,
                width: 14, height: 14, borderRadius: '50%',
                background: '#fff',
                transition: 'left 0.2s',
              }} />
            </div>
            {label}
          </label>
        ))}
      </div>

      {/* Refresh button */}
      {onRefresh && (
        <button
          onClick={onRefresh}
          style={{
            background: '#111418',
            border: '1px solid #1E2329',
            borderRadius: 8,
            padding: '8px 12px',
            display: 'flex', alignItems: 'center', gap: 6,
            cursor: 'pointer', color: '#94A3B8', fontSize: 12,
          }}
          onMouseEnter={(e) => e.currentTarget.style.borderColor = '#F59E0B'}
          onMouseLeave={(e) => e.currentTarget.style.borderColor = '#1E2329'}
        >
          <RefreshCw size={13} />
          Refresh
        </button>
      )}
    </div>
  )
}
