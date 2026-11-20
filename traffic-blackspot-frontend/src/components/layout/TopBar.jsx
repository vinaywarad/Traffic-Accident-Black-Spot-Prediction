import { useLocation } from 'react-router-dom';
import { Bell, ChevronRight } from 'lucide-react';
import { fmtLastUpdated } from '../../utils/formatUtils';
import ApiStatusBar from '../ui/ApiStatusBar';

const PAGE_NAMES = {
  '/': 'Dashboard',
  '/map': 'Map',
  '/analytics': 'Analytics',
  '/predictions': 'Predictions',
  '/upload': 'Upload Data',
  '/settings': 'Settings',
};

export default function TopBar({ sidebarWidth }) {
  const { pathname } = useLocation();
  const pageName = PAGE_NAMES[pathname] || 'Page';
  const alertCount = 3;

  return (
    <header style={{
      height: 60,
      background: '#111418',
      borderBottom: '1px solid #1E2329',
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 24px',
      position: 'fixed', top: 0, right: 0,
      left: sidebarWidth,
      zIndex: 40,
      transition: 'left 0.25s ease',
    }}>
      {/* Breadcrumb */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#94A3B8', fontSize: 14 }}>
        <span>BlackSpot</span>
        <ChevronRight size={14} />
        <span style={{ color: '#F1F5F9', fontWeight: 500 }}>{pageName}</span>
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        {/* Last updated */}
        <span style={{ fontSize: 12, color: '#475569', fontFamily: 'DM Mono, monospace' }}>
          Updated {fmtLastUpdated()}
        </span>

        {/* Live API status */}
        <ApiStatusBar />

        {/* Bell */}
        <div style={{ position: 'relative', cursor: 'pointer' }}>
          <Bell size={18} color="#94A3B8" />
          {alertCount > 0 && (
            <span style={{
              position: 'absolute', top: -6, right: -6,
              background: '#EF4444', color: '#fff',
              fontSize: 10, fontWeight: 700,
              width: 16, height: 16, borderRadius: '50%',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              {alertCount}
            </span>
          )}
        </div>
      </div>
    </header>
  );
}
