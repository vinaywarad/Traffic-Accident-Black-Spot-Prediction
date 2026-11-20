import { useState } from 'react';

const REQUIRED_FIELDS = [
  { key: 'lat', label: 'Latitude', required: true },
  { key: 'lng', label: 'Longitude', required: true },
  { key: 'date', label: 'Date', required: true },
  { key: 'severity', label: 'Severity', required: true },
  { key: 'roadName', label: 'Road Name', required: false },
  { key: 'weather', label: 'Weather', required: false },
  { key: 'casualties', label: 'Casualties', required: false },
  { key: 'fatalities', label: 'Fatalities', required: false },
];

const SAMPLE_COLUMNS = ['latitude', 'longitude', 'accident_date', 'severity_level', 'road', 'weather_cond', 'num_casualties', 'num_fatalities', 'time', 'type'];

export default function ColumnMapper({ columns, onMapping }) {
  const cols = columns || SAMPLE_COLUMNS;
  const [mapping, setMapping] = useState({});

  const handleChange = (field, col) => {
    const next = { ...mapping, [field]: col };
    setMapping(next);
    onMapping?.(next);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
      <p style={{ fontSize: 13, color: '#94A3B8', marginBottom: 4 }}>
        Map your CSV columns to the expected fields:
      </p>
      {REQUIRED_FIELDS.map(({ key, label, required }) => (
        <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 140, flexShrink: 0 }}>
            <span style={{ fontSize: 13, color: '#F1F5F9', fontWeight: 500 }}>{label}</span>
            {required && <span style={{ color: '#EF4444', marginLeft: 4, fontSize: 12 }}>*</span>}
          </div>
          <select
            value={mapping[key] || ''}
            onChange={(e) => handleChange(key, e.target.value)}
            style={{
              flex: 1, background: '#0A0C10', color: '#F1F5F9',
              border: `1px solid ${mapping[key] ? '#22C55E' : '#1E2329'}`,
              borderRadius: 8, padding: '8px 12px', fontSize: 13,
              outline: 'none', cursor: 'pointer',
            }}
          >
            <option value="">— Select column —</option>
            {cols.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          {mapping[key] && (
            <span style={{ fontSize: 11, color: '#22C55E' }}>✓</span>
          )}
        </div>
      ))}
    </div>
  );
}
