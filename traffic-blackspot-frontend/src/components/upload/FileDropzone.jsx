import { useState, useRef } from 'react';
import { Upload, FileText, X } from 'lucide-react';

export default function FileDropzone({ onFile }) {
  const [dragging, setDragging] = useState(false);
  const [file, setFile] = useState(null);
  const inputRef = useRef(null);

  const handleFile = (f) => {
    if (!f) return;
    setFile(f);
    onFile?.(f);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const onDragOver = (e) => { e.preventDefault(); setDragging(true); };
  const onDragLeave = () => setDragging(false);

  const clearFile = (e) => {
    e.stopPropagation();
    setFile(null);
    onFile?.(null);
    if (inputRef.current) inputRef.current.value = '';
  };

  return (
    <div
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onClick={() => !file && inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? '#F59E0B' : file ? '#22C55E' : '#1E2329'}`,
        borderRadius: 12,
        padding: '48px 24px',
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
        cursor: file ? 'default' : 'pointer',
        background: dragging ? 'rgba(245,158,11,0.05)' : 'rgba(17,20,24,0.5)',
        transition: 'all 0.2s',
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.json,.xlsx,.xls"
        style={{ display: 'none' }}
        onChange={(e) => handleFile(e.target.files[0])}
      />

      {file ? (
        <>
          <FileText size={40} color="#22C55E" strokeWidth={1.5} />
          <div style={{ textAlign: 'center' }}>
            <p style={{ color: '#22C55E', fontWeight: 600, fontSize: 15 }}>{file.name}</p>
            <p style={{ color: '#94A3B8', fontSize: 13, marginTop: 4 }}>
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
          <button
            onClick={clearFile}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
              color: '#EF4444', borderRadius: 8, padding: '6px 14px',
              cursor: 'pointer', fontSize: 13,
            }}
          >
            <X size={14} /> Remove
          </button>
        </>
      ) : (
        <>
          <Upload size={40} color={dragging ? '#F59E0B' : '#475569'} strokeWidth={1.5} />
          <div style={{ textAlign: 'center' }}>
            <p style={{ color: '#F1F5F9', fontWeight: 500, fontSize: 15 }}>
              {dragging ? 'Drop file here' : 'Drag & drop or click to upload'}
            </p>
            <p style={{ color: '#475569', fontSize: 13, marginTop: 4 }}>
              Supports CSV, JSON, Excel (.xlsx, .xls)
            </p>
          </div>
        </>
      )}
    </div>
  );
}
