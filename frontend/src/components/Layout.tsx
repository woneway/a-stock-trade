import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

const menuItems = [
  { path: '/', label: '首页', icon: '🏠' },
  { path: '/today', label: '今日计划', icon: '📋' },
  { path: '/strategies', label: '策略列表', icon: '🎯' },
  { path: '/plans', label: '计划列表', icon: '📊' },
  { path: '/reviews', label: '复盘列表', icon: '📝' },
  { path: '/positions', label: '持仓列表', icon: '💼' },
  { path: '/trades', label: '交易记录', icon: '📜' },
  { path: '/settings', label: '设置', icon: '⚙️' },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="logo">A股交易系统</div>
        <nav className="nav">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span className="nav-label">{item.label}</span>
            </Link>
          ))}
        </nav>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
