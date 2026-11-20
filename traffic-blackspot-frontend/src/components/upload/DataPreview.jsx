const MOCK_PREVIEW = [
  { id: 'ACC-001', lat: 12.9176, lng: 77.6237, date: '2024-03-15', severity: 'HIGH', road: 'Outer Ring Road', weather: 'Rainy' },
  { id: 'ACC-002', lat: 13.0358, lng: 77.5970, date: '2024-03-14', severity: 'CRITICAL', road: 'Bellary Road', weather: 'Foggy' },
  { id: 'ACC-003', lat: 12.8399, lng: 77.6770, date: '2024-03-13', severity: 'MEDIUM', road: 'Hosur Road', weather: 'Clear' },
  { id: 'ACC-004', lat: 12.9591, lng: 77.6974, date: '2024-03-12', severity: 'LOW', road: 'Outer Ring Road', weather: 'Clear' },
  { id: 'ACC-005', lat: 13.0050, lng: 77.6960, date: '2024-03-11', severity: 'HIGH', road: 'Old Madras Road', weather: 'Cloudy' },
];

const SEV_COLORS = { CRITICAL: '#EF4444', HIGH: '#F97316', MEDIUM: '#F59E0B', LOW: '#22C55E' };

export default function DataPreview({ data }) {
  const rows = data || MOCK_PREVIEW;
  const cols = Object.keys(rows[0] || {});

  return (
    <div style={{ overflowX: 'auto' }}>
      <p style={{ fontSize: 12, color: '#475569', marginBottom: 8 }}>
        Showing first {rows.length} rows
      </p>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
        <thead>
          <tr>
            {cols.map((col) => (
              <th key={col} style={{
                padding: '8px 12px', textAlign: 'left',
                color: '#94A3B8', fontWeight: 600, textTransform: 'uppercase',
                fontSize: 10, letterSpacing: '0.06em',
                borderBottom: '1px solid #1E2329', whiteSpace: 'nowrap',
              }}>
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} style={{ borderBottom: '1px solid #1E2329' }}>
              {cols.map((col) => (
                <td key={col} style={{
                  padding: '8px 12px', whiteSpace: 'nowrap',
                  color: col === 'severity' ? SEV_COLORS[row[col]] || '#94A3B8' : '#F1F5F9',
                  fontFamily: typeof row[col] === 'number' ? 'DM Mono, monospace' : 'inherit',
                }}>
                  {String(row[col])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
