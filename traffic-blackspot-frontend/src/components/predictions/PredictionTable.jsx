import { useState } from 'react'
import RiskBadge from '../ui/RiskBadge'
import ConfidenceBar from './ConfidenceBar'
import { TableSkeleton } from '../ui/Skeletons'
import { ChevronUp, ChevronDown, Search } from 'lucide-react'

const PAGE_SIZE = 20

export default function PredictionTable({ data = [], isLoading = false }) {
  const [search,  setSearch]  = useState('')
  const [sortKey, setSortKey] = useState('risk_score')
  const [sortDir, setSortDir] = useState('desc')
  const [page,    setPage]    = useState(1)

  if (isLoading) return <TableSkeleton rows={12} />

  // Filter
  const filtered = data.filter((p) => {
    if (!search) return true
    const loc = `${p.location?.latitude?.toFixed(4)},${p.location?.longitude?.toFixed(4)}`
    return (
      loc.includes(search) ||
      p.risk_level?.toLowerCase().includes(search.toLowerCase()) ||
      p.model_used?.toLowerCase().includes(search.toLowerCase())
    )
  })

  // Sort
  const sorted = [...filtered].sort((a, b) => {
    const av = a[sortKey] ?? 0
    const bv = b[sortKey] ?? 0
    return sortDir === 'asc' ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1)
  })

  // Paginate
  const totalPages = Math.ceil(sorted.length / PAGE_SIZE)
  const paged = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const handleSort = (key) => {
    if (sortKey === key) setSortDir((d) => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('desc') }
    setPage(1)
  }

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <ChevronUp size={12} color="#475569" />
    return sortDir === 'asc'
      ? <ChevronUp size={12} color="#F59E0B" />
      : <ChevronDown size={12} color="#F59E0B" />
  }

  const thStyle = (col) => ({
    padding: '10px 12px', textAlign: 'left',
    fontSize: 11, color: '#94A3B8',
    textTransform: 'uppercase', letterSpacing: '0.06em',
    cursor: 'pointer', userSelect: 'none',
    borderBottom: '1px solid #1E2329',
    whiteSpace: 'nowrap',
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      {/* Search */}
      <div style={{ position: 'relative', maxWidth: 320 }}>
        <Search size={14} color="#475569" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
        <input
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          placeholder="Search by location or risk level..."
          style={{
            width: '100%', padding: '8px 12px 8px 32px',
            background: '#111418', border: '1px solid #1E2329',
            borderRadius: 8, color: '#F1F5F9', fontSize: 13,
            outline: 'none',
          }}
        />
      </div>

      {/* Table */}
      <div style={{ overflowX: 'auto', borderRadius: 10, border: '1px solid #1E2329' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <thead style={{ background: '#111418' }}>
            <tr>
              <th style={thStyle('location')} onClick={() => handleSort('location')}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>Location <SortIcon col="location" /></div>
              </th>
              <th style={thStyle('risk_score')} onClick={() => handleSort('risk_score')}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>Risk Score <SortIcon col="risk_score" /></div>
              </th>
              <th style={thStyle('risk_level')} onClick={() => handleSort('risk_level')}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>Level <SortIcon col="risk_level" /></div>
              </th>
              <th style={thStyle('confidence')} onClick={() => handleSort('confidence')}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>Confidence <SortIcon col="confidence" /></div>
              </th>
              <th style={thStyle('is_blackspot')} onClick={() => handleSort('is_blackspot')}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>Black Spot <SortIcon col="is_blackspot" /></div>
              </th>
              <th style={{ ...thStyle('explanation'), cursor: 'default' }}>Explanation</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((p, i) => (
              <tr
                key={i}
                style={{
                  borderBottom: '1px solid #1E2329',
                  background: i % 2 === 0 ? '#0A0C10' : '#111418',
                  transition: 'background 0.15s',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#1E2329'}
                onMouseLeave={(e) => e.currentTarget.style.background = i % 2 === 0 ? '#0A0C10' : '#111418'}
              >
                <td style={{ padding: '10px 12px', color: '#94A3B8', fontFamily: 'DM Mono, monospace', fontSize: 11 }}>
                  {p.location?.latitude?.toFixed(4)}, {p.location?.longitude?.toFixed(4)}
                </td>
                <td style={{ padding: '10px 12px' }}>
                  <ConfidenceBar value={p.risk_score} />
                </td>
                <td style={{ padding: '10px 12px' }}>
                  <RiskBadge level={p.risk_level} />
                </td>
                <td style={{ padding: '10px 12px' }}>
                  <ConfidenceBar value={p.confidence} color="#06B6D4" />
                </td>
                <td style={{ padding: '10px 12px' }}>
                  <span style={{
                    fontSize: 11, fontWeight: 600,
                    color: p.is_blackspot ? '#EF4444' : '#22C55E',
                  }}>
                    {p.is_blackspot ? '● Yes' : '○ No'}
                  </span>
                </td>
                <td style={{ padding: '10px 12px', color: '#475569', fontSize: 11, maxWidth: 240 }}>
                  <span style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                    {p.explanation || '—'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 12, color: '#475569' }}>
          <span>
            Showing {(page - 1) * PAGE_SIZE + 1}–{Math.min(page * PAGE_SIZE, sorted.length)} of {sorted.length}
          </span>
          <div style={{ display: 'flex', gap: 6 }}>
            {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => setPage(p)}
                style={{
                  width: 28, height: 28, borderRadius: 6,
                  border: `1px solid ${page === p ? '#F59E0B' : '#1E2329'}`,
                  background: page === p ? '#F59E0B22' : 'transparent',
                  color: page === p ? '#F59E0B' : '#94A3B8',
                  fontSize: 12, cursor: 'pointer',
                }}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
