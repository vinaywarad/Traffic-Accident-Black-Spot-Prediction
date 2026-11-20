export default function EmptyState({ icon: Icon, title = 'No data', message = '', action }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      justifyContent: 'center', padding: '48px 24px', gap: '12px',
      color: '#475569',
    }}>
      {Icon && <Icon size={40} strokeWidth={1.5} />}
      <p style={{ fontSize: '16px', fontWeight: 600, color: '#94A3B8' }}>{title}</p>
      {message && <p style={{ fontSize: '14px', textAlign: 'center', maxWidth: 320 }}>{message}</p>}
      {action}
    </div>
  );
}
