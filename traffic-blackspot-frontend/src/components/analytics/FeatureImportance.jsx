import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { featureImportance } from '../../data/mockData';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#111418', border: '1px solid #1E2329', borderRadius: 8, padding: '8px 12px' }}>
      <p style={{ color: '#F1F5F9', fontSize: 13, fontWeight: 500 }}>{payload[0].payload.feature}</p>
      <p style={{ color: '#F59E0B', fontSize: 12 }}>SHAP: {(payload[0].value * 100).toFixed(1)}%</p>
    </div>
  );
};

export default function FeatureImportance() {
  return (
    <div style={{ width: '100%', height: 280 }}>
      <ResponsiveContainer>
        <BarChart
          data={featureImportance}
          layout="vertical"
          margin={{ top: 4, right: 16, left: 80, bottom: 4 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#1E2329" horizontal={false} />
          <XAxis type="number" tick={{ fill: '#94A3B8', fontSize: 11 }} stroke="#1E2329" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
          <YAxis type="category" dataKey="feature" tick={{ fill: '#94A3B8', fontSize: 11 }} stroke="#1E2329" width={80} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {featureImportance.map((_, i) => (
              <Cell key={i} fill={i === 0 ? '#F59E0B' : i === 1 ? '#F97316' : '#06B6D4'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
