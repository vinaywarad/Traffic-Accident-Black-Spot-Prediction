import { format, parseISO } from 'date-fns';

/** Format a number with commas */
export function fmtNumber(n) {
  if (n === null || n === undefined) return '—';
  return Number(n).toLocaleString();
}

/** Format a decimal as percentage string */
export function fmtPercent(n, decimals = 1) {
  if (n === null || n === undefined) return '—';
  return `${(Number(n) * 100).toFixed(decimals)}%`;
}

/** Format a 0-1 score as percentage */
export function fmtScore(n, decimals = 1) {
  if (n === null || n === undefined) return '—';
  return `${(Number(n) * 100).toFixed(decimals)}%`;
}

/** Format a date string (ISO) to readable format */
export function fmtDate(dateStr) {
  if (!dateStr) return '—';
  try {
    return format(parseISO(dateStr), 'dd MMM yyyy');
  } catch {
    return dateStr;
  }
}

/** Format a date string with time */
export function fmtDateTime(dateStr, timeStr) {
  if (!dateStr) return '—';
  try {
    const base = format(parseISO(dateStr), 'dd MMM yyyy');
    return timeStr ? `${base} ${timeStr}` : base;
  } catch {
    return dateStr;
  }
}

/** Format a timestamp to relative label */
export function fmtRelative(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = parseISO(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - d) / 86400000);
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    return format(d, 'dd MMM yyyy');
  } catch {
    return dateStr;
  }
}

/** Format a decimal to fixed places */
export function fmtFixed(n, places = 3) {
  if (n === null || n === undefined) return '—';
  return Number(n).toFixed(places);
}

/** Format last updated timestamp */
export function fmtLastUpdated(date = new Date()) {
  return format(date, 'dd MMM yyyy, HH:mm');
}
