import { useState } from 'react';

export default function Tooltip({ children, content, placement = 'top' }) {
  const [visible, setVisible] = useState(false);

  const posStyle = placement === 'top'
    ? { bottom: '100%', left: '50%', transform: 'translateX(-50%)', marginBottom: '6px' }
    : placement === 'bottom'
    ? { top: '100%', left: '50%', transform: 'translateX(-50%)', marginTop: '6px' }
    : placement === 'left'
    ? { right: '100%', top: '50%', transform: 'translateY(-50%)', marginRight: '6px' }
    : { left: '100%', top: '50%', transform: 'translateY(-50%)', marginLeft: '6px' };

  return (
    <span
      style={{ position: 'relative', display: 'inline-flex' }}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && (
        <span style={{
          position: 'absolute',
          ...posStyle,
          background: '#1E2329',
          color: '#F1F5F9',
          fontSize: '12px',
          padding: '4px 8px',
          borderRadius: '6px',
          whiteSpace: 'nowrap',
          zIndex: 100,
          border: '1px solid #2D3748',
          pointerEvents: 'none',
        }}>
          {content}
        </span>
      )}
    </span>
  );
}
