import { Link, useLocation } from 'react-router-dom';
import './Layout.css';

interface MenuItem {
  path?: string;
  label: string;
  icon?: string;
}

const menuItems: MenuItem[] = [
  // 核心功能
  { path: '/daily', label: '计划与复盘', icon: '📋' },

  // 持仓与交易
  { path: '/positions', label: '持仓', icon: '💼' },
  { path: '/trades', label: '交易记录', icon: '📜' },

  // 策略分析
  { path: '/strategy-analysis', label: '策略分析', icon: '📈' },

  // 数据查询
  { path: '/data-query', label: '数据查询', icon: '🔍' },

  // 设置
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
              to={item.path || '#'}
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
