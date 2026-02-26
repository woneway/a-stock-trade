import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

interface MenuItem {
  path?: string;
  label: string;
  icon?: string;
  children?: MenuItem[];
}

const menuItems: MenuItem[] = [
  { path: '/review', label: '复盘', icon: '📝' },
  { path: '/plan', label: '计划', icon: '🎯' },
  { path: '/positions', label: '持仓', icon: '💼' },
  { path: '/trades', label: '交易记录', icon: '📜' },

  // 交易记录下方
  { path: '/history', label: '历史计划', icon: '📋' },
  { path: '/reviews', label: '复盘列表', icon: '📝' },

  { path: '/settings', label: '设置', icon: '⚙️' },

  // 更多子菜单
  {
    label: '更多',
    icon: '···',
    children: [
      { path: '/strategies', label: '策略列表' },
      { path: '/backtest', label: '回测' },
      { path: '/plaza', label: '游资广场' },
    ]
  },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();
  const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});

  const toggleGroup = (label: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [label]: !prev[label]
    }));
  };

  const isGroupActive = (item: MenuItem) => {
    if (!item.children) return false;
    return item.children.some(child => location.pathname === child.path);
  };

  const renderMenuItem = (item: MenuItem, index: number) => {
    if (item.children) {
      const isExpanded = expandedGroups[item.label] || isGroupActive(item);
      const isActive = isGroupActive(item);

      return (
        <div key={item.label} className="nav-group">
          <div
            className={`nav-group-title ${isExpanded ? 'expanded' : ''} ${isActive ? 'active' : ''}`}
            onClick={() => toggleGroup(item.label)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
            <span className="nav-arrow">▶</span>
          </div>
          <div className="nav-group-items">
            {item.children.map((child, childIndex) => (
              <Link
                key={child.path}
                to={child.path || '#'}
                className={`nav-item sub ${location.pathname === child.path ? 'active' : ''}`}
              >
                <span className="nav-label">{child.label}</span>
              </Link>
            ))}
          </div>
        </div>
      );
    }

    return (
      <Link
        key={item.path}
        to={item.path || '#'}
        className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
      >
        <span className="nav-icon">{item.icon}</span>
        <span className="nav-label">{item.label}</span>
      </Link>
    );
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">A股交易系统</div>
        <nav className="nav">
          {menuItems.map((item, index) => renderMenuItem(item, index))}
        </nav>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
