const LEGEND_ITEMS = [
  { label: 'Critical', color: '#EF4444' },
  { label: 'High', color: '#F97316' },
  { label: 'Medium', color: '#F59E0B' },
  { label: 'Low', color: '#22C55E' },
];

export default function MapLegend() {
  return (
    <div style={{
      position: 'absolute', bottom: 24, right: 16, zIndex: 1000,
      background: 'rgba(17,20,24,0.9)',
      border: '1px solid #1E2329',
      borderRadius: 10, padding: '12px 16px',
      backdropFilter: 'blur(12px)',
    }}>
      <p style={{ fontSize: 11, color: '#94A3B8', fontWeight: 600, marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
        Risk Level
      </p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {LEGEND_ITEMS.map(({ label, color }) => (
          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: color, flexShrink: 0 }} />
            <span style={{ fontSize: 12, color: '#F1F5F9' }}>{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
