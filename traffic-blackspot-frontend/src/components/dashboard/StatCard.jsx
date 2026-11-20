import { useEffect, useRef } from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'

/**
 * KPI stat card with count-up animation.
 * Accepts either a raw number (animates) or a string (displays as-is).
 */
export default function StatCard({
  title,
  value,
  trend,
  trendLabel = 'vs last month',
  icon: Icon,
  color = '#F59E0B',
  subtitle,
  sparkData,
}) {
  const displayRef = useRef(null)

  // Count-up animation for numeric values
  useEffect(() => {
    const el = displayRef.current
    if (!el || typeof value !== 'number') return

    let start = 0
    const end = value
    const duration = 1200
    const step = (timestamp) => {
      if (!start) start = timestamp
      const progress = Math.min((timestamp - start) / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      el.textContent = Math.round(eased * end)
      if (progress < 1) requestAnimationFrame(step)
    }
    requestAnimationFrame(step)
  }, [value])

  const isPositiveTrend = trend > 0
  const trendColor = isPositiveTrend ? '#22C55E' : '#EF4444'

  return (
    <div style={{
      background: '#111418',
      border: '1px solid #1E2329',
      borderRadius: 12,
      padding: 16,
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Subtle color accent top border */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0,
        height: 2, background: color, opacity: 0.6,
      }} />

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 12, color: '#94A3B8', fontWeight: 500 }}>{title}</span>
        {Icon && <Icon size={16} color={color} />}
      </div>

      {/* Value */}
      <div style={{
        fontSize: 28, fontWeight: 700,
        fontFamily: 'DM Mono, monospace',
        color: '#F1F5F9',
      }}>
        {typeof value === 'number'
          ? <span ref={displayRef}>0</span>
          : <span>{value ?? '--'}</span>
        }
      </div>

      {/* Subtitle */}
      {subtitle && (
        <span style={{ fontSize: 11, color: '#475569' }}>{subtitle}</span>
      )}

      {/* Trend */}
      {trend !== undefined && trend !== null && (
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          {isPositiveTrend
            ? <TrendingUp size={12} color={trendColor} />
            : <TrendingDown size={12} color={trendColor} />
          }
          <span style={{ fontSize: 11, color: trendColor, fontFamily: 'DM Mono, monospace' }}>
            {isPositiveTrend ? '+' : ''}{trend}%
          </span>
          <span style={{ fontSize: 11, color: '#475569' }}>{trendLabel}</span>
        </div>
      )}

      {/* Sparkline */}
      {sparkData && sparkData.length > 1 && (
        <SparkLine data={sparkData} color={color} />
      )}
    </div>
  )
}

function SparkLine({ data, color }) {
  const max = Math.max(...data)
  const min = Math.min(...data)
  const range = max - min || 1
  const w = 80, h = 24
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w
    const y = h - ((v - min) / range) * h
    return `${x},${y}`
  }).join(' ')

  return (
    <svg width={w} height={h} style={{ opacity: 0.6 }}>
      <polyline
        points={pts}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  )
}
