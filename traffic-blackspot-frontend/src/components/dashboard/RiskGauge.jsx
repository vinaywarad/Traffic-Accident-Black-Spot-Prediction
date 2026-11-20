import { useEffect, useRef, useState } from 'react';

export default function RiskGauge({ score = 0, size = 160 }) {
  const [animated, setAnimated] = useState(0);
  const rafRef = useRef(null);

  useEffect(() => {
    const target = Math.min(100, Math.max(0, score));
    const start = Date.now();
    const duration = 1000;
    function tick() {
      const p = Math.min((Date.now() - start) / duration, 1);
      const eased = 1 - Math.pow(1 - p, 3);
      setAnimated(Math.round(target * eased));
      if (p < 1) rafRef.current = requestAnimationFrame(tick);
    }
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [score]);

  const color = animated >= 70 ? '#EF4444' : animated >= 40 ? '#F59E0B' : '#22C55E';
  const r = (size / 2) - 16;
  const cx = size / 2, cy = size / 2;
  const circumference = Math.PI * r; // half circle
  const startAngle = Math.PI;
  const endAngle = 0;
  const totalArc = circumference;
  const filled = (animated / 100) * totalArc;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
      <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
        {/* Track */}
        <path
          d={`M ${16} ${cy} A ${r} ${r} 0 0 1 ${size - 16} ${cy}`}
          fill="none" stroke="#1E2329" strokeWidth="10" strokeLinecap="round"
        />
        {/* Fill */}
        <path
          d={`M ${16} ${cy} A ${r} ${r} 0 0 1 ${size - 16} ${cy}`}
          fill="none" stroke={color} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={`${filled} ${totalArc}`}
          style={{ transition: 'stroke 0.3s' }}
        />
        {/* Center text */}
        <text x={cx} y={cy + 4} textAnchor="middle" fill="#F1F5F9" fontSize="22" fontWeight="700" fontFamily="DM Mono, monospace">
          {animated}
        </text>
        <text x={cx} y={cy + 20} textAnchor="middle" fill="#94A3B8" fontSize="11" fontFamily="Inter, sans-serif">
          Risk Score
        </text>
      </svg>
      <div style={{ display: 'flex', gap: 16, fontSize: 11, color: '#475569' }}>
        <span style={{ color: '#22C55E' }}>● Low</span>
        <span style={{ color: '#F59E0B' }}>● Medium</span>
        <span style={{ color: '#EF4444' }}>● High</span>
      </div>
    </div>
  );
}
