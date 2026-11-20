import { useTrendData } from '../../api/hooks/useAnalytics'
import { ChartSkeleton } from '../ui/Skeletons'
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  CartesianGrid, ResponsiveContainer, Legend,
} from 'recharts'

const TICK_STYLE = { fill: '#94A3B8', fontSize: 11 }
const TOOLTIP_STYLE = { background: '#111418', border: '1px solid #1E2329', color: '#F1F5F9', fontSize: 12 }

export default function AccidentTrendChart() {
  const { data, isLoading, error } = useTrendData(24)

  if (isLoading) return <ChartSkeleton height={280} />

  if (error) return (
    <div style={{ height: 280, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', fontSize: 13 }}>
      Failed to load trend data
    </div>
  )

  // Show every 4th label to avoid crowding
  const chartData = (data || []).map((d, i) => ({
    ...d,
    label: i % 4 === 0 ? d.month : '',
  }))

  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 0, left: -10 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1E2329" />
        <XAxis dataKey="label" tick={TICK_STYLE} axisLine={false} tickLine={false} />
        <YAxis tick={TICK_STYLE} axisLine={false} tickLine={false} />
        <Tooltip contentStyle={TOOLTIP_STYLE} />
        <Legend wrapperStyle={{ fontSize: 12, color: '#94A3B8' }} />
        <Line
          type="monotone" dataKey="accidents"
          stroke="#EF4444" strokeWidth={2} dot={false} name="Accidents"
        />
        <Line
          type="monotone" dataKey="blackspots"
          stroke="#F59E0B" strokeWidth={2} dot={false} name="Black Spots"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
