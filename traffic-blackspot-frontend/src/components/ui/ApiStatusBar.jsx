/**
 * Live API connection status indicator shown in the TopBar.
 * Shows: connected (green) | connecting (amber) | offline (red)
 * Polls /health every 30 seconds automatically via useApiHealth.
 */
import { useApiHealth } from '../../api/hooks/useHealth'

export default function ApiStatusBar() {
  const { data, isLoading, isError } = useApiHealth()

  const status = isLoading ? 'connecting' : isError ? 'offline' : 'connected'

  const config = {
    connected:  { color: '#22C55E', label: 'API connected',  pulse: false },
    connecting: { color: '#F59E0B', label: 'Connecting...',  pulse: true  },
    offline:    { color: '#EF4444', label: 'API offline',    pulse: false },
  }[status]

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      {/* Dot with optional pulse */}
      <div style={{ position: 'relative', width: 8, height: 8 }}>
        <span style={{
          display: 'block', width: 8, height: 8,
          borderRadius: '50%', background: config.color,
          boxShadow: `0 0 6px ${config.color}`,
        }} />
        {config.pulse && (
          <span style={{
            position: 'absolute', inset: 0,
            borderRadius: '50%', background: config.color,
            opacity: 0.6,
            animation: 'pulse-ring 1.5s ease-out infinite',
          }} />
        )}
      </div>

      <span style={{ fontSize: 12, color: '#94A3B8' }}>{config.label}</span>

      {data?.model_name && (
        <span style={{ fontSize: 11, color: '#475569' }}>
          · {data.model_name}
        </span>
      )}
    </div>
  )
}
