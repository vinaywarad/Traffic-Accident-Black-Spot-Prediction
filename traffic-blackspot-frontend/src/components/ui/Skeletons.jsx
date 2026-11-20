/**
 * Skeleton loaders — shown while API data is loading.
 * Never show spinners — skeletons give better perceived performance.
 */

const pulse = {
  animation: 'skeleton-pulse 1.5s ease-in-out infinite',
  background: 'linear-gradient(90deg, #1E2329 25%, #252B33 50%, #1E2329 75%)',
  backgroundSize: '200% 100%',
  borderRadius: 6,
}

// Inject keyframes once
if (typeof document !== 'undefined' && !document.getElementById('skeleton-style')) {
  const style = document.createElement('style')
  style.id = 'skeleton-style'
  style.textContent = `
    @keyframes skeleton-pulse {
      0%   { background-position: 200% 0; }
      100% { background-position: -200% 0; }
    }
  `
  document.head.appendChild(style)
}

export function StatCardsSkeleton() {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
      {[...Array(4)].map((_, i) => (
        <div key={i} style={{
          padding: 16, borderRadius: 12,
          border: '1px solid #1E2329', background: '#111418',
          display: 'flex', flexDirection: 'column', gap: 10,
        }}>
          <div style={{ ...pulse, height: 14, width: 100 }} />
          <div style={{ ...pulse, height: 32, width: 70 }} />
          <div style={{ ...pulse, height: 10, width: 80 }} />
        </div>
      ))}
    </div>
  )
}

export function ChartSkeleton({ height = 300 }) {
  return <div style={{ ...pulse, width: '100%', height, borderRadius: 8 }} />
}

export function ListSkeleton({ rows = 5 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {[...Array(rows)].map((_, i) => (
        <div key={i} style={{ ...pulse, height: 52, width: '100%', borderRadius: 8 }} />
      ))}
    </div>
  )
}

export function TableSkeleton({ rows = 10 }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ ...pulse, height: 40, width: '100%', borderRadius: 6 }} />
      {[...Array(rows)].map((_, i) => (
        <div key={i} style={{ ...pulse, height: 48, width: '100%', borderRadius: 6 }} />
      ))}
    </div>
  )
}
