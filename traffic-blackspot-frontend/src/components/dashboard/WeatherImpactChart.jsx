import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { weatherImpactData } from '../../data/mockData';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#111418', border: '1px solid #1E2329', borderRadius: 8, padding: '10px 14px' }}>
      <p style={{ color: '#94A3B8', fontSize: 12, marginBottom: 4 }}>{label}</p>
      <p style={{ color: '#06B6D4', fontSize: 13, fontWeight: 500 }}>{payload[0].value} accidents</p>
      <p style={{ color: '#475569', fontSize: 12 }}>{payload[0].payload.percentage}% of total</p>
    </div>
  );
};

export default function WeatherImpactChart() {
  return (
    <div style={{ width: '100%', height: 220 }}>
      <ResponsiveContainer>
        <BarChart data={weatherImpactData} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1E2329" vertical={false} />
          <XAxis dataKey="weather" tick={{ fill: '#94A3B8', fontSize: 11 }} stroke="#1E2329" />
          <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} stroke="#1E2329" />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="accidents" fill="#06B6D4" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
