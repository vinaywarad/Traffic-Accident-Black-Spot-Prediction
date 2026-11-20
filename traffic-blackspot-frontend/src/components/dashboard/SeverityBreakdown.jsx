import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { useDataStore } from '../../store/useDataStore';

const COLORS = { CRITICAL: '#EF4444', HIGH: '#F97316', MEDIUM: '#F59E0B', LOW: '#22C55E' };

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0];
  return (
    <div style={{ background: '#111418', border: '1px solid #1E2329', borderRadius: 8, padding: '8px 12px' }}>
      <p style={{ color: d.payload.fill, fontWeight: 600, fontSize: 13 }}>{d.name}</p>
      <p style={{ color: '#94A3B8', fontSize: 12 }}>{d.value} accidents</p>
    </div>
  );
};

export default function SeverityBreakdown() {
  const accidentData = useDataStore((s) => s.accidentData);

  const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
  accidentData.forEach((a) => { if (counts[a.severity] !== undefined) counts[a.severity]++; });

  const data = Object.entries(counts).map(([name, value]) => ({ name, value, fill: COLORS[name] }));
  const total = data.reduce((s, d) => s + d.value, 0);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ height: 180 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data} cx="50%" cy="50%"
              innerRadius={50} outerRadius={80}
              paddingAngle={3} dataKey="value"
            >
              {data.map((entry) => (
                <Cell key={entry.name} fill={entry.fill} />
              ))}
            </Pie>
            <Tooltip content={<CustomTooltip />} />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
        {data.map((d) => (
          <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 10, height: 10, borderRadius: 2, background: d.fill, flexShrink: 0 }} />
            <span style={{ fontSize: 12, color: '#94A3B8' }}>{d.name}</span>
            <span style={{ fontSize: 12, color: '#F1F5F9', fontWeight: 600, marginLeft: 'auto' }}>
              {total > 0 ? Math.round((d.value / total) * 100) : 0}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
