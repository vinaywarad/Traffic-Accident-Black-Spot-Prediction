import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { clusterData } from '../../data/mockData';
import { CLUSTER_COLORS } from '../../utils/colorUtils';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  return (
    <div style={{ background: '#111418', border: '1px solid #1E2329', borderRadius: 8, padding: '8px 12px' }}>
      <p style={{ color: CLUSTER_COLORS[d?.cluster] || '#94A3B8', fontSize: 13, fontWeight: 500 }}>
        Cluster {(d?.cluster ?? 0) + 1}
      </p>
      <p style={{ color: '#94A3B8', fontSize: 12 }}>X: {d?.x?.toFixed(3)}, Y: {d?.y?.toFixed(3)}</p>
      <p style={{ color: '#94A3B8', fontSize: 12 }}>Size: {d?.size}</p>
    </div>
  );
};

const CLUSTERS = [0, 1, 2, 3];

export default function AccidentClusters() {
  return (
    <div style={{ width: '100%', height: 280 }}>
      <ResponsiveContainer>
        <ScatterChart margin={{ top: 8, right: 16, left: -10, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#1E2329" />
          <XAxis type="number" dataKey="x" domain={[0, 1]} tick={{ fill: '#94A3B8', fontSize: 11 }} stroke="#1E2329" name="Longitude" />
          <YAxis type="number" dataKey="y" domain={[0, 1]} tick={{ fill: '#94A3B8', fontSize: 11 }} stroke="#1E2329" name="Latitude" />
          <Tooltip content={<CustomTooltip />} />
          {CLUSTERS.map((c) => (
            <Scatter
              key={c}
              name={`Cluster ${c + 1}`}
              data={clusterData.filter((d) => d.cluster === c)}
              fill={CLUSTER_COLORS[c]}
              opacity={0.8}
            />
          ))}
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
