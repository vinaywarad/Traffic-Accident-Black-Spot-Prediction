import { useState } from 'react';
import { Check, ChevronRight } from 'lucide-react';
import FileDropzone from '../components/upload/FileDropzone';
import ColumnMapper from '../components/upload/ColumnMapper';
import DataPreview from '../components/upload/DataPreview';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Spinner from '../components/ui/Spinner';

const STEPS = ['Upload', 'Map Columns', 'Preview', 'Run'];

export default function UploadPage() {
  const [step, setStep] = useState(0);
  const [file, setFile] = useState(null);
  const [mapping, setMapping] = useState({});
  const [running, setRunning] = useState(false);
  const [done, setDone] = useState(false);

  const handleRun = () => {
    setRunning(true);
    setTimeout(() => { setRunning(false); setDone(true); }, 2500);
  };

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Step indicator */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
        {STEPS.map((s, i) => (
          <div key={s} style={{ display: 'flex', alignItems: 'center', flex: i < STEPS.length - 1 ? 1 : 0 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{
                width: 28, height: 28, borderRadius: '50%',
                background: i < step ? '#22C55E' : i === step ? '#F59E0B' : '#1E2329',
                color: i <= step ? '#0A0C10' : '#475569',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 12, fontWeight: 700, flexShrink: 0,
              }}>
                {i < step ? <Check size={14} /> : i + 1}
              </div>
              <span style={{ fontSize: 13, color: i === step ? '#F1F5F9' : i < step ? '#22C55E' : '#475569', fontWeight: i === step ? 600 : 400 }}>
                {s}
              </span>
            </div>
            {i < STEPS.length - 1 && (
              <div style={{ flex: 1, height: 1, background: i < step ? '#22C55E' : '#1E2329', margin: '0 12px' }} />
            )}
          </div>
        ))}
      </div>

      {/* Step content */}
      <Card>
        {step === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <p style={{ fontSize: 15, fontWeight: 600, color: '#F1F5F9' }}>Upload Data File</p>
            <p style={{ fontSize: 13, color: '#94A3B8' }}>Upload a CSV, JSON, or Excel file containing accident records.</p>
            <FileDropzone onFile={setFile} />
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button variant="primary" disabled={!file} onClick={() => setStep(1)}>
                Next <ChevronRight size={14} />
              </Button>
            </div>
          </div>
        )}

        {step === 1 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <p style={{ fontSize: 15, fontWeight: 600, color: '#F1F5F9' }}>Map Columns</p>
            <p style={{ fontSize: 13, color: '#94A3B8' }}>Match your file's columns to the required fields.</p>
            <ColumnMapper onMapping={setMapping} />
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button variant="ghost" onClick={() => setStep(0)}>Back</Button>
              <Button variant="primary" onClick={() => setStep(2)}>
                Next <ChevronRight size={14} />
              </Button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <p style={{ fontSize: 15, fontWeight: 600, color: '#F1F5F9' }}>Preview Data</p>
            <p style={{ fontSize: 13, color: '#94A3B8' }}>Review the first 10 rows before running predictions.</p>
            <DataPreview />
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Button variant="ghost" onClick={() => setStep(1)}>Back</Button>
              <Button variant="primary" onClick={() => setStep(3)}>
                Next <ChevronRight size={14} />
              </Button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20, alignItems: 'center', padding: '24px 0' }}>
            {done ? (
              <>
                <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'rgba(34,197,94,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Check size={32} color="#22C55E" />
                </div>
                <p style={{ fontSize: 18, fontWeight: 600, color: '#22C55E' }}>Predictions Complete!</p>
                <p style={{ fontSize: 14, color: '#94A3B8', textAlign: 'center' }}>
                  150 records processed. Results are available in the Predictions tab.
                </p>
                <Button variant="primary" onClick={() => { setStep(0); setFile(null); setDone(false); }}>
                  Upload Another File
                </Button>
              </>
            ) : (
              <>
                <p style={{ fontSize: 15, fontWeight: 600, color: '#F1F5F9' }}>Ready to Run</p>
                <p style={{ fontSize: 13, color: '#94A3B8', textAlign: 'center', maxWidth: 400 }}>
                  All columns mapped. Click "Run Prediction" to process your data using the selected ML models.
                </p>
                <div style={{ display: 'flex', gap: 12 }}>
                  <Button variant="ghost" onClick={() => setStep(2)}>Back</Button>
                  <Button variant="primary" disabled={running} onClick={handleRun}>
                    {running ? <><Spinner size={14} color="#0A0C10" /> Running...</> : 'Run Prediction'}
                  </Button>
                </div>
              </>
            )}
          </div>
        )}
      </Card>
    </div>
  );
}
