import { AlertTriangle, MapPin, TrendingUp, Activity } from 'lucide-react'
import { useAnalyticsSummary, useTrendData } from '../api/hooks/useAnalytics'
import StatCard from '../components/dashboard/StatCard'
import AccidentTrendChart from '../components/dashboard/AccidentTrendChart'
import SeverityBreakdown from '../components/dashboard/SeverityBreakdown'
import TopBlackSpots from '../components/dashboard/TopBlackSpots'
import WeatherImpactChart from '../components/dashboard/WeatherImpactChart'
import TimeHeatmap from '../components/analytics/TimeHeatmap'
import Card from '../components/ui/Card'
import AccidentMap from '../components/map/AccidentMap'
import { StatCardsSkeleton } from '../components/ui/Skeletons'

export default function DashboardPage() {
  const { data: summary, isLoading: loadingSummary } = useAnalyticsSummary()
  const { data: trends } = useTrendData(8)

  // Build sparkline from trend data
  const sparkData = (trends || []).map((t) => t.accidents)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Row 1: Stat Cards */}
      {loadingSummary ? <StatCardsSkeleton /> : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          <StatCard
            title="Accidents (MTD)"
            value={summary?.total_accidents_mtd ?? '--'}
            trend={summary?.blackspot_change_pct}
            trendLabel="vs last month"
            icon={AlertTriangle}
            color="#EF4444"
            sparkData={sparkData}
          />
          <StatCard
            title="Active Black Spots"
            value={summary?.active_blackspots ?? '--'}
            icon={MapPin}
            color="#F59E0B"
            sparkData={sparkData.map((v) => v * 0.4)}
          />
          <StatCard
            title="High Risk Roads"
            value={summary?.high_risk_roads ?? '--'}
            icon={TrendingUp}
            color="#F97316"
            sparkData={sparkData.map((v) => v * 0.2)}
          />
          <StatCard
            title="Model Accuracy"
            value={summary?.model_accuracy
              ? `${(summary.model_accuracy * 100).toFixed(0)}%`
              : '--'}
            icon={Activity}
            color="#06B6D4"
            subtitle="AUC-ROC score"
          />
        </div>
      )}

      {/* Row 2: Trend + Severity */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 16 }}>
        <Card>
          <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>
            Accident Trends (24 Months)
          </p>
          <AccidentTrendChart />
        </Card>
        <Card>
          <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>
            Severity Breakdown
          </p>
          <SeverityBreakdown />
        </Card>
      </div>

      {/* Row 3: Mini Map + Top Black Spots */}
      <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 16 }}>
        <Card style={{ padding: 0, overflow: 'hidden', minHeight: 300 }}>
          <AccidentMap height="300px" />
        </Card>
        <Card>
          <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 12 }}>
            Top Black Spots
          </p>
          <TopBlackSpots limit={5} />
        </Card>
      </div>

      {/* Row 4: Weather + Time Heatmap */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <Card>
          <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>
            Weather Impact
          </p>
          <WeatherImpactChart />
        </Card>
        <Card>
          <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>
            Accident Heatmap (Day × Hour)
          </p>
          <TimeHeatmap />
        </Card>
      </div>
    </div>
  )
}
