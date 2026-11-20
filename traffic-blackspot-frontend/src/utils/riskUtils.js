/** Returns risk color hex for a severity level */
export function getRiskColor(severity) {
  switch (severity) {
    case 'CRITICAL': return '#EF4444';
    case 'HIGH': return '#F97316';
    case 'MEDIUM': return '#F59E0B';
    case 'LOW': return '#22C55E';
    default: return '#94A3B8';
  }
}

/** Returns risk color hex for a 0-1 score */
export function getScoreColor(score) {
  if (score >= 0.8) return '#EF4444';
  if (score >= 0.6) return '#F97316';
  if (score >= 0.4) return '#F59E0B';
  return '#22C55E';
}

/** Calculates aggregate risk score from accident array */
export function calcAggregateRisk(accidents) {
  if (!accidents || accidents.length === 0) return 0;
  const sum = accidents.reduce((acc, a) => acc + (a.riskScore || 0), 0);
  return parseFloat((sum / accidents.length).toFixed(3));
}

/** Returns severity label for a 0-1 score */
export function scoreToSeverity(score) {
  if (score >= 0.8) return 'CRITICAL';
  if (score >= 0.6) return 'HIGH';
  if (score >= 0.4) return 'MEDIUM';
  return 'LOW';
}

/** Returns a 0-100 integer risk level */
export function scoreToPercent(score) {
  return Math.round(Math.min(1, Math.max(0, score)) * 100);
}
