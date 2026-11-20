const VARIANTS = {
  primary: {
    background: '#F59E0B',
    color: '#0A0C10',
    border: 'none',
  },
  secondary: {
    background: '#111418',
    color: '#F1F5F9',
    border: '1px solid #1E2329',
  },
  danger: {
    background: 'rgba(239,68,68,0.15)',
    color: '#EF4444',
    border: '1px solid rgba(239,68,68,0.3)',
  },
  ghost: {
    background: 'transparent',
    color: '#94A3B8',
    border: '1px solid transparent',
  },
};

export default function Button({
  children,
  variant = 'secondary',
  size = 'md',
  disabled = false,
  onClick,
  className = '',
  style,
  type = 'button',
  ...props
}) {
  const v = VARIANTS[variant] || VARIANTS.secondary;
  const padding = size === 'sm' ? '6px 12px' : size === 'lg' ? '12px 24px' : '8px 16px';
  const fontSize = size === 'sm' ? '12px' : size === 'lg' ? '16px' : '14px';

  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={className}
      style={{
        ...v,
        padding,
        fontSize,
        fontFamily: 'Inter, sans-serif',
        fontWeight: 500,
        borderRadius: '8px',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        transition: 'opacity 0.15s, filter 0.15s',
        ...style,
      }}
      onMouseEnter={(e) => { if (!disabled) e.currentTarget.style.filter = 'brightness(1.1)'; }}
      onMouseLeave={(e) => { e.currentTarget.style.filter = 'none'; }}
      {...props}
    >
      {children}
    </button>
  );
}
