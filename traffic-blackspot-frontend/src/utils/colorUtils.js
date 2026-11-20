/** Returns hex color for severity */
export function severityHex(severity) {
  const map = {
    CRITICAL: '#EF4444',
    HIGH: '#F97316',
    MEDIUM: '#F59E0B',
    LOW: '#22C55E',
  };
  return map[severity] || '#94A3B8';
}

/** Returns background color style for severity */
export function severityBg(severity) {
  const map = {
    CRITICAL: 'rgba(239,68,68,0.15)',
    HIGH: 'rgba(249,115,22,0.15)',
    MEDIUM: 'rgba(245,158,11,0.15)',
    LOW: 'rgba(34,197,94,0.15)',
  };
  return map[severity] || 'rgba(148,163,184,0.15)';
}

/** Returns text color style for severity */
export function severityText(severity) {
  const map = {
    CRITICAL: '#EF4444',
    HIGH: '#F97316',
    MEDIUM: '#F59E0B',
    LOW: '#22C55E',
  };
  return map[severity] || '#94A3B8';
}

/** Returns border color style for severity */
export function severityBorder(severity) {
  const map = {
    CRITICAL: 'rgba(239,68,68,0.4)',
    HIGH: 'rgba(249,115,22,0.4)',
    MEDIUM: 'rgba(245,158,11,0.4)',
    LOW: 'rgba(34,197,94,0.4)',
  };
  return map[severity] || 'rgba(148,163,184,0.4)';
}

/** Cluster colors for scatter chart */
export const CLUSTER_COLORS = ['#F59E0B', '#06B6D4', '#EF4444', '#22C55E'];
