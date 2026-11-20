import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ReferenceLine, ResponsiveContainer } from 'recharts';
import { rocCurveData } from '../../data/mockData';
import { modelMetrics } from '../../data/mockData';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{ background: '#111418', border: '1px solid #1E2329', borderRadius: 8, padding: '10px 14px' }}>
      <p style={{ color: '#94A3B8', fontSize: 12, marginBottom: 4 }}>FPR: {label}</p>
      {payload.map((p) => (
        <p key={p.dataKey} style={{ color: p.color, fontSize: 12 }}>
          {p.name}: {p.value?.toFixed(3)}
        </p>
      ))}
    </div>
  );
};

export default function ROCCurve() {
  return (
    <div>
      <div style={{ width: '100%', height: 260 }}>
        <ResponsiveContainer>
          <LineChart data={rocCurveData} margin={{ top: 8, right: 16, left: -10, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E2329" />
            <XAxis dataKey="fpr" tick={{ fill: '#94A3B8', fontSize: 11 }} stroke="#1E2329" label={{ value: 'FPR', position: 'insideBottom', offset: -4, fill: '#475569', fontSize: 11 }} />
            <YAxis tick={{ fill: '#94A3B8', fontSize: 11 }} stroke="#1E2329" label={{ value: 'TPR', angle: -90, position: 'insideLeft', fill: '#475569', fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12, color: '#94A3B8' }} />
            <ReferenceLine x={0} y={0} stroke="#1E2329" />
            <Line type="monotone" dataKey="tpr_rf" name={`RF (AUC=${modelMetrics.randomForest.auc})`} stroke="#F59E0B" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="tpr_xgb" name={`XGB (AUC=${modelMetrics.xgboost.auc})`} stroke="#06B6D4" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="tpr_lr" name={`LR (AUC=${modelMetrics.logisticRegression.auc})`} stroke="#94A3B8" strokeWidth={2} dot={false} strokeDasharray="4 2" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
