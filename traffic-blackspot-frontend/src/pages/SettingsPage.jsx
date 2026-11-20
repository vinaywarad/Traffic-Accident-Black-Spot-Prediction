import { useState } from 'react';
import { Save, Check } from 'lucide-react';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

function SettingRow({ label, description, children }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between',
      padding: '16px 0', borderBottom: '1px solid #1E2329', gap: 24,
    }}>
      <div style={{ flex: 1 }}>
        <p style={{ fontSize: 14, fontWeight: 500, color: '#F1F5F9', marginBottom: 4 }}>{label}</p>
        {description && <p style={{ fontSize: 12, color: '#475569' }}>{description}</p>}
      </div>
      <div style={{ flexShrink: 0 }}>{children}</div>
    </div>
  );
}

const inputStyle = {
  background: '#0A0C10', color: '#F1F5F9',
  border: '1px solid #1E2329', borderRadius: 8,
  padding: '8px 12px', fontSize: 13,
  outline: 'none', fontFamily: 'Inter, sans-serif',
  width: 240,
};

const selectStyle = {
  ...inputStyle,
  cursor: 'pointer',
  appearance: 'none',
};

export default function SettingsPage() {
  const [saved, setSaved] = useState(false);
  const [settings, setSettings] = useState({
    apiEndpoint: 'http://localhost:8000/api',
    defaultModel: 'xgboost',
    riskThreshold: '0.65',
    notifyEmail: true,
    notifySlack: false,
    autoRefresh: true,
    refreshInterval: '30',
  });

  const update = (key, val) => setSettings((s) => ({ ...s, [key]: val }));

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div style={{ maxWidth: 720, display: 'flex', flexDirection: 'column', gap: 20 }}>
      <Card>
        <p style={{ fontSize: 16, fontWeight: 600, color: '#F1F5F9', marginBottom: 4 }}>API Configuration</p>
        <p style={{ fontSize: 13, color: '#475569', marginBottom: 16 }}>Configure backend connection settings.</p>

        <SettingRow label="API Endpoint" description="Base URL for the prediction API">
          <input style={inputStyle} value={settings.apiEndpoint} onChange={(e) => update('apiEndpoint', e.target.value)} />
        </SettingRow>
        <SettingRow label="Default Model" description="Model used for predictions by default">
          <select style={selectStyle} value={settings.defaultModel} onChange={(e) => update('defaultModel', e.target.value)}>
            <option value="xgboost">XGBoost</option>
            <option value="randomForest">Random Forest</option>
            <option value="logisticRegression">Logistic Regression</option>
          </select>
        </SettingRow>
        <SettingRow label="Risk Threshold" description="Minimum score to flag as black spot (0–1)">
          <input style={{ ...inputStyle, width: 120 }} type="number" min="0" max="1" step="0.05" value={settings.riskThreshold} onChange={(e) => update('riskThreshold', e.target.value)} />
        </SettingRow>
      </Card>

      <Card>
        <p style={{ fontSize: 16, fontWeight: 600, color: '#F1F5F9', marginBottom: 4 }}>Notifications</p>
        <p style={{ fontSize: 13, color: '#475569', marginBottom: 16 }}>Configure alert preferences.</p>

        {[
          { key: 'notifyEmail', label: 'Email Alerts', desc: 'Receive alerts via email for new black spots' },
          { key: 'notifySlack', label: 'Slack Notifications', desc: 'Send alerts to a Slack channel' },
          { key: 'autoRefresh', label: 'Auto Refresh', desc: 'Automatically refresh data on the dashboard' },
        ].map(({ key, label, desc }) => (
          <SettingRow key={key} label={label} description={desc}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={settings[key]}
                onChange={(e) => update(key, e.target.checked)}
                style={{ accentColor: '#F59E0B', width: 16, height: 16 }}
              />
              <span style={{ fontSize: 13, color: settings[key] ? '#22C55E' : '#475569' }}>
                {settings[key] ? 'Enabled' : 'Disabled'}
              </span>
            </label>
          </SettingRow>
        ))}

        <SettingRow label="Refresh Interval" description="How often to refresh data (seconds)">
          <input style={{ ...inputStyle, width: 120 }} type="number" min="10" max="300" value={settings.refreshInterval} onChange={(e) => update('refreshInterval', e.target.value)} />
        </SettingRow>
      </Card>

      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button variant="primary" onClick={handleSave}>
          {saved ? <><Check size={14} /> Saved!</> : <><Save size={14} /> Save Settings</>}
        </Button>
      </div>
    </div>
  );
}
