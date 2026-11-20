import { timeHeatmapData } from '../../data/mockData';

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const HOURS = Array.from({ length: 24 }, (_, i) => i);

function getColor(count, max) {
  if (count === 0) return '#0A0C10';
  const intensity = count / max;
  if (intensity > 0.75) return '#EF4444';
  if (intensity > 0.5) return '#F97316';
  if (intensity > 0.25) return '#F59E0B';
  return '#22C55E';
}

export default function TimeHeatmap() {
  const grid = {};
  timeHeatmapData.forEach(({ day, hour, count }) => {
    grid[`${day}-${hour}`] = count;
  });
  const max = Math.max(...timeHeatmapData.map((d) => d.count));

  return (
    <div style={{ overflowX: 'auto' }}>
      <div style={{ minWidth: 600 }}>
        {/* Hour labels */}
        <div style={{ display: 'flex', marginLeft: 40, marginBottom: 4 }}>
          {HOURS.map((h) => (
            <div key={h} style={{ flex: 1, textAlign: 'center', fontSize: 9, color: '#475569' }}>
              {h % 4 === 0 ? `${String(h).padStart(2, '0')}` : ''}
            </div>
          ))}
        </div>

        {/* Grid */}
        {DAYS.map((day) => (
          <div key={day} style={{ display: 'flex', alignItems: 'center', marginBottom: 3 }}>
            <span style={{ width: 36, fontSize: 11, color: '#94A3B8', flexShrink: 0 }}>{day}</span>
            {HOURS.map((h) => {
              const count = grid[`${day}-${h}`] || 0;
              return (
                <div
                  key={h}
                  title={`${day} ${String(h).padStart(2, '0')}:00 — ${count} accidents`}
                  style={{
                    flex: 1, height: 20,
                    background: getColor(count, max),
                    borderRadius: 2,
                    margin: '0 1px',
                    cursor: 'default',
                    transition: 'opacity 0.15s',
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.opacity = '0.7'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.opacity = '1'; }}
                />
              );
            })}
          </div>
        ))}

        {/* Legend */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 12, marginLeft: 40 }}>
          <span style={{ fontSize: 11, color: '#475569' }}>Low</span>
          {['#22C55E', '#F59E0B', '#F97316', '#EF4444'].map((c) => (
            <div key={c} style={{ width: 16, height: 16, background: c, borderRadius: 2 }} />
          ))}
          <span style={{ fontSize: 11, color: '#475569' }}>High</span>
        </div>
      </div>
    </div>
  );
}
