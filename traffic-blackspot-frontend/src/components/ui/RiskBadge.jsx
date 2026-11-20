import Badge from './Badge';

const SEVERITY_COLORS = {
  CRITICAL: '#EF4444',
  HIGH: '#F97316',
  MEDIUM: '#F59E0B',
  LOW: '#22C55E',
};

export default function RiskBadge({ severity, className }) {
  const color = SEVERITY_COLORS[severity] || '#94A3B8';
  return (
    <Badge color={color} className={className}>
      {severity || 'UNKNOWN'}
    </Badge>
  );
}
