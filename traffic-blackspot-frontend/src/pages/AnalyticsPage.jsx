import { useState } from 'react'
import { useModels } from '../api/hooks/useModels'
import Card from '../components/ui/Card'
import TimeHeatmap from '../components/analytics/TimeHeatmap'
import FeatureImportance from '../components/analytics/FeatureImportance'
import AccidentClusters from '../components/analytics/AccidentClusters'
import ROCCurve from '../components/analytics/ROCCurve'
import TopBlackSpots from '../components/dashboard/TopBlackSpots'
import AccidentTrendChart from '../components/dashboard/AccidentTrendChart'
import WeatherImpactChart from '../components/dashboard/WeatherImpactChart'

const TABS = ['Overview', 'Temporal', 'Spatial', 'Model Performance']

function MetricCard({ label, value, color = '#F59E0B' }) {
  const display = typeof value === 'number'
    ? `${(value * 100).toFixed(1)}%`
    : value ?? '--'
  return (
    <div style={{
      background: '#0A0C10', borderRadius: 8,
      padding: '12px 16px', textAlign: 'center',
    }}>
      <p style={{ fontSize: 11, color: '#475569', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 6 }}>
        {label}
      </p>
      <p style={{ fontSize: 22, fontWeight: 700, color, fontFamily: 'DM Mono, monospace', margin: 0 }}>
        {display}
      </p>
    </div>
  )
}

const MODEL_DISPLAY = {
  logistic_regression: 'Logistic Regression',
  random_forest:       'Random Forest',
  xgboost:             'XGBoost',
  lightgbm:            'LightGBM',
}

export default function AnalyticsPage() {
  const [activeTab, setActiveTab] = useState('Overview')
  const { data: modelsData } = useModels()

  const allMetrics = modelsData?.metrics || {}

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Tab nav */}
      <div style={{ display: 'flex', gap: 4, borderBottom: '1px solid #1E2329' }}>
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '10px 20px', background: 'none', border: 'none',
              borderBottom: `2px solid ${activeTab === tab ? '#F59E0B' : 'transparent'}`,
              color: activeTab === tab ? '#F59E0B' : '#94A3B8',
              fontSize: 14, fontWeight: activeTab === tab ? 600 : 400,
              cursor: 'pointer', transition: 'all 0.15s',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Overview */}
      {activeTab === 'Overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: 16 }}>
            <Card>
              <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>Accident Trends</p>
              <AccidentTrendChart />
            </Card>
            <Card>
              <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>Weather Impact</p>
              <WeatherImpactChart />
            </Card>
          </div>
          <Card>
            <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 12 }}>All Black Spots</p>
            <TopBlackSpots limit={15} />
          </Card>
        </div>
      )}

      {/* Temporal */}
      {activeTab === 'Temporal' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card>
            <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>Accident Heatmap (Day × Hour)</p>
            <TimeHeatmap />
          </Card>
          <Card>
            <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>Monthly Trend (24 months)</p>
            <AccidentTrendChart />
          </Card>
        </div>
      )}

      {/* Spatial */}
      {activeTab === 'Spatial' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <Card>
            <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>Accident Clusters</p>
            <AccidentClusters />
          </Card>
          <Card>
            <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 12 }}>Black Spot Risk Table</p>
            <TopBlackSpots limit={15} />
          </Card>
        </div>
      )}

      {/* Model Performance */}
      {activeTab === 'Model Performance' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <Card>
              <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>ROC Curves</p>
              <ROCCurve />
            </Card>
            <Card>
              <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 16 }}>Feature Importance (SHAP)</p>
              <FeatureImportance />
            </Card>
          </div>

          {/* Live model metrics from API */}
          {Object.entries(allMetrics).map(([model, metrics]) => (
            <Card key={model}>
              <p style={{ fontSize: 14, fontWeight: 600, color: '#F1F5F9', marginBottom: 12 }}>
                {MODEL_DISPLAY[model] || model}
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
                <MetricCard label="AUC-ROC"   value={metrics.auc_roc}   color="#F59E0B" />
                <MetricCard label="AUC-PR"    value={metrics.auc_pr}    color="#06B6D4" />
                <MetricCard label="F1 Score"  value={metrics.f1}        color="#22C55E" />
                <MetricCard label="Precision" value={metrics.precision} color="#F97316" />
                <MetricCard label="Recall"    value={metrics.recall}    color="#94A3B8" />
              </div>
            </Card>
          ))}

          {/* Fallback if API not available */}
          {!Object.keys(allMetrics).length && (
            <div style={{ color: '#475569', fontSize: 13, padding: 16 }}>
              Model metrics will appear here once the backend is connected.
            </div>
          )}
        </div>
      )}
    </div>
  )
}
