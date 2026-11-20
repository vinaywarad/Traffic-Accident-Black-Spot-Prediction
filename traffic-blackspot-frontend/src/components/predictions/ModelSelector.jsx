import { usePredictionStore } from '../../store/usePredictionStore';

const MODELS = [
  { value: 'xgboost', label: 'XGBoost', color: '#06B6D4' },
  { value: 'randomForest', label: 'Random Forest', color: '#F59E0B' },
  { value: 'logisticRegression', label: 'Logistic Regression', color: '#94A3B8' },
];

export default function ModelSelector() {
  const { selectedModel, setSelectedModel } = usePredictionStore();

  return (
    <div style={{ display: 'flex', gap: 8 }}>
      {MODELS.map(({ value, label, color }) => {
        const active = selectedModel === value;
        return (
          <button
            key={value}
            onClick={() => setSelectedModel(value)}
            style={{
              padding: '8px 16px',
              borderRadius: 8,
              border: `1px solid ${active ? color : '#1E2329'}`,
              background: active ? `${color}18` : '#111418',
              color: active ? color : '#94A3B8',
              fontSize: 13,
              fontWeight: active ? 600 : 400,
              cursor: 'pointer',
              transition: 'all 0.15s',
              fontFamily: 'Inter, sans-serif',
            }}
          >
            {label}
          </button>
        );
      })}
    </div>
  );
}
