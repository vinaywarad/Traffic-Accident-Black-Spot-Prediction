import { getScoreColor } from '../../utils/riskUtils';

export default function ConfidenceBar({ value = 0, showLabel = true }) {
  const color = getScoreColor(value);
  const pct = Math.round(value * 100);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <div style={{ flex: 1, height: 6, background: '#1E2329', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${pct}%`,
          background: color, borderRadius: 3,
          transition: 'width 0.3s ease',
        }} />
      </div>
      {showLabel && (
        <span style={{ fontSize: 11, color, fontFamily: 'DM Mono, monospace', minWidth: 36, textAlign: 'right' }}>
          {pct}%
        </span>
      )}
    </div>
  );
}
