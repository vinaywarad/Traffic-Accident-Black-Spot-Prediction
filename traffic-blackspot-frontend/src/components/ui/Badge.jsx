export default function Badge({ children, color = '#94A3B8', bg, style, className = '' }) {
  return (
    <span
      className={className}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        borderRadius: '9999px',
        fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.04em',
        color,
        background: bg || `${color}22`,
        border: `1px solid ${color}44`,
        ...style,
      }}
    >
      {children}
    </span>
  );
}
