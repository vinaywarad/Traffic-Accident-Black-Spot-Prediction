import { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Map, BarChart3, Brain, Upload, Settings, ChevronLeft, ChevronRight } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/map', icon: Map, label: 'Map' },
  { path: '/analytics', icon: BarChart3, label: 'Analytics' },
  { path: '/predictions', icon: Brain, label: 'Predictions' },
  { path: '/upload', icon: Upload, label: 'Upload' },
  { path: '/settings', icon: Settings, label: 'Settings' },
];

export default function Sidebar({ collapsed, onToggle }) {
  const w = collapsed ? 64 : 240;

  return (
    <aside style={{
      width: w, minWidth: w, height: '100vh',
      background: '#111418',
      borderRight: '1px solid #1E2329',
      display: 'flex', flexDirection: 'column',
      transition: 'width 0.25s ease, min-width 0.25s ease',
      overflow: 'hidden',
      position: 'fixed', left: 0, top: 0, zIndex: 50,
    }}>
      {/* Logo */}
      <div style={{
        height: 60, display: 'flex', alignItems: 'center',
        padding: collapsed ? '0 20px' : '0 20px',
        borderBottom: '1px solid #1E2329',
        gap: 10, overflow: 'hidden',
      }}>
        <span style={{ fontSize: 22 }}>🚦</span>
        {!collapsed && (
          <span style={{ color: '#F59E0B', fontWeight: 700, fontSize: 16, whiteSpace: 'nowrap' }}>
            BlackSpot
          </span>
        )}
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '12px 8px', display: 'flex', flexDirection: 'column', gap: 4 }}>
        {NAV_ITEMS.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            end={path === '/'}
            style={({ isActive }) => ({
              display: 'flex', alignItems: 'center', gap: 12,
              padding: collapsed ? '10px 18px' : '10px 14px',
              borderRadius: 8,
              textDecoration: 'none',
              color: isActive ? '#F59E0B' : '#94A3B8',
              background: isActive ? 'rgba(245,158,11,0.1)' : 'transparent',
              transition: 'all 0.15s',
              overflow: 'hidden',
              whiteSpace: 'nowrap',
            })}
            onMouseEnter={(e) => {
              if (!e.currentTarget.style.background.includes('245,158,11')) {
                e.currentTarget.style.background = 'rgba(255,255,255,0.04)';
              }
            }}
            onMouseLeave={(e) => {
              if (!e.currentTarget.style.background.includes('245,158,11')) {
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            <Icon size={18} strokeWidth={1.8} style={{ flexShrink: 0 }} />
            {!collapsed && <span style={{ fontSize: 14, fontWeight: 500 }}>{label}</span>}
          </NavLink>
        ))}
      </nav>

      {/* Toggle */}
      <div style={{ padding: '12px 8px', borderTop: '1px solid #1E2329' }}>
        <button
          onClick={onToggle}
          style={{
            width: '100%', display: 'flex', alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'flex-end',
            padding: '8px 12px', background: 'none', border: 'none',
            cursor: 'pointer', color: '#475569', borderRadius: 8,
          }}
        >
          {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>
    </aside>
  );
}
