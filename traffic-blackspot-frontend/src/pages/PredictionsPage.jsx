import { useState } from 'react'
import { usePredictionTable } from '../api/hooks/usePrediction'
import { useModels } from '../api/hooks/useModels'
import PredictionTable from '../components/predictions/PredictionTable'
import ModelSelector   from '../components/predictions/ModelSelector'
import { TableSkeleton } from '../components/ui/Skeletons'
import { Download, RefreshCw } from 'lucide-react'

export default function PredictionsPage() {
  const [selectedModel, setSelectedModel] = useState('best')
  const { data, isLoading, error, refetch, isFetching } = usePredictionTable()
  const { data: modelsData } = useModels()

  const predictions = data?.predictions || []

  const handleExport = () => {
    if (!predictions.length) return
    const rows = [
      ['Location', 'Road Type', 'Risk Score', 'Risk Level', 'Confidence', 'Black Spot'],
      ...predictions.map((p) => [
        `${p.location.latitude},${p.location.longitude}`,
        p.model_used,
        p.risk_score,
        p.risk_level,
        p.confidence,
        p.is_blackspot ? 'Yes' : 'No',
      ]),
    ]
    const csv = rows.map((r) => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href = url; a.download = 'blackspot_predictions.csv'; a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 600, color: '#F1F5F9', margin: 0 }}>
            Prediction Results
          </h1>
          <p style={{ fontSize: 13, color: '#475569', margin: '4px 0 0' }}>
            Live risk scores for{' '}
            <span style={{ color: '#F59E0B', fontFamily: 'DM Mono, monospace' }}>
              {data?.total ?? '—'}
            </span>{' '}
            Bengaluru road segments
            {data?.blackspot_count > 0 && (
              <span style={{ color: '#EF4444' }}>
                {' '}· {data.blackspot_count} black spots detected
              </span>
            )}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <ModelSelector value={selectedModel} onChange={setSelectedModel} />

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '7px 14px', borderRadius: 8,
              border: '1px solid #1E2329', background: '#111418',
              color: '#94A3B8', fontSize: 12, cursor: 'pointer',
            }}
          >
            <RefreshCw size={13} style={{ animation: isFetching ? 'spin 0.8s linear infinite' : 'none' }} />
            Refresh
          </button>

          <button
            onClick={handleExport}
            disabled={!predictions.length}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '7px 14px', borderRadius: 8,
              border: '1px solid #1E2329', background: '#111418',
              color: '#94A3B8', fontSize: 12, cursor: 'pointer',
            }}
          >
            <Download size={13} />
            Export CSV
          </button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div style={{
          padding: 14, borderRadius: 8,
          background: '#EF444410', border: '1px solid #EF444430',
          color: '#EF4444', fontSize: 13,
        }}>
          Failed to load predictions — is the backend running at{' '}
          <code style={{ fontFamily: 'DM Mono, monospace' }}>localhost:8000</code>?
        </div>
      )}

      {/* Table */}
      {isLoading
        ? <TableSkeleton rows={12} />
        : <PredictionTable data={predictions} isLoading={isFetching} />
      }

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  )
}
