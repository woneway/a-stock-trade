import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';

interface HistoricalPlan {
  id: number;
  tradeDate: string;
  status: string;
  marketCycle: string;
  positionPlan: string;
  plannedStockCount: number;
  executedStockCount: number;
  executionRate: number;
  totalPnl: number;
  prePlanId?: number;
  postReviewId?: number;
}

export default function HistoryList() {
  const [plans, setPlans] = useState<HistoricalPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadPlans();
  }, [filter]);

  const loadPlans = async () => {
    setLoading(true);
    try {
      let params = {};
      const today = dayjs();

      if (filter === 'week') {
        params = {
          start_date: today.subtract(7, 'day').format('YYYY-MM-DD'),
          end_date: today.format('YYYY-MM-DD')
        };
      } else if (filter === 'month') {
        params = {
          start_date: today.subtract(30, 'day').format('YYYY-MM-DD'),
          end_date: today.format('YYYY-MM-DD')
        };
      }

      const res = await axios.get('/api/plan/history', { params });
      setPlans(res.data || []);
    } catch (err) {
      console.error('Failed to load plans:', err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { text: string; class: string }> = {
      'draft': { text: '草稿', class: 'draft' },
      'confirmed': { text: '已确认', class: 'confirmed' },
      'executed': { text: '执行中', class: 'executed' },
      'completed': { text: '已完成', class: 'completed' },
      'reviewed': { text: '已复盘', class: 'reviewed' },
    };
    const s = statusMap[status] || { text: status, class: '' };
    return <span className={`status-badge ${s.class}`}>{s.text}</span>;
  };

  const getCycleTagClass = (cycle: string) => {
    const cycleMap: Record<string, string> = {
      '冰点': 'ice',
      '启动': 'start',
      '发酵': 'start',
      '分歧': 'divergence',
      '高潮': 'peak',
      '退潮': 'ebb'
    };
    return cycleMap[cycle] || '';
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>历史计划</h1>
        </div>
        <button className="btn btn-primary">
          <Link to="/today" style={{ color: 'white', textDecoration: 'none' }}>
            + 新建计划
          </Link>
        </button>
      </div>

      <div className="filter-bar">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          全部
        </button>
        <button
          className={`filter-btn ${filter === 'week' ? 'active' : ''}`}
          onClick={() => setFilter('week')}
        >
          本周
        </button>
        <button
          className={`filter-btn ${filter === 'month' ? 'active' : ''}`}
          onClick={() => setFilter('month')}
        >
          本月
        </button>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : plans.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <div className="empty-text">暂无历史计划</div>
          <Link to="/today" className="btn btn-primary">去创建计划</Link>
        </div>
      ) : (
        <div className="history-list">
          {plans.map((plan) => (
            <div key={plan.id} className="history-card">
              <div className="history-header">
                <div className="history-date">
                  <span className="date-label">📅 {plan.tradeDate}</span>
                  {dayjs(plan.tradeDate).isSame(dayjs(), 'day') && (
                    <span className="today-tag">今日</span>
                  )}
                </div>
                {getStatusBadge(plan.status)}
              </div>

              <div className="history-stats">
                <div className="stat-item">
                  <span className="stat-label">周期</span>
                  {plan.marketCycle && (
                    <span className={`cycle-tag ${getCycleTagClass(plan.marketCycle)}`}>
                      {plan.marketCycle}
                    </span>
                  )}
                </div>
                <div className="stat-item">
                  <span className="stat-label">仓位</span>
                  <span className="stat-value">{plan.positionPlan || '-'}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">目标股</span>
                  <span className="stat-value">{plan.plannedStockCount}只</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">执行率</span>
                  <span className="stat-value">{plan.executionRate || 0}%</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">盈亏</span>
                  <span className={`stat-value ${(plan.totalPnl || 0) >= 0 ? 'positive' : 'negative'}`}>
                    {plan.totalPnl ? (plan.totalPnl > 0 ? '+' : '') + plan.totalPnl.toFixed(2) : '-'}
                  </span>
                </div>
              </div>

              <div className="history-actions">
                <Link to={`/history/${plan.id}`} className="btn-link">
                  查看详情 →
                </Link>
                {plan.status !== 'reviewed' && (
                  <Link to={`/today?planId=${plan.id}`} className="btn btn-sm">
                    继续执行
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .filter-bar {
          display: flex;
          gap: 8px;
          margin-bottom: 24px;
        }

        .filter-btn {
          padding: 8px 16px;
          border: 1px solid var(--gray-300);
          background: white;
          border-radius: 20px;
          cursor: pointer;
          font-size: 13px;
          transition: all 0.2s;
        }

        .filter-btn:hover {
          border-color: var(--primary);
        }

        .filter-btn.active {
          background: var(--primary);
          color: white;
          border-color: var(--primary);
        }

        .history-list {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }

        .history-card {
          background: var(--bg-card);
          border-radius: var(--radius-md);
          padding: 20px;
          box-shadow: var(--shadow-sm);
          border: 1px solid var(--gray-200);
        }

        .history-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .history-date {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .date-label {
          font-size: 16px;
          font-weight: 600;
        }

        .today-tag {
          background: var(--primary);
          color: white;
          padding: 2px 8px;
          border-radius: 10px;
          font-size: 11px;
        }

        .status-badge {
          padding: 4px 12px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 500;
        }

        .status-badge.draft {
          background: var(--gray-100);
          color: var(--text-secondary);
        }

        .status-badge.confirmed {
          background: #dbeafe;
          color: #1d4ed8;
        }

        .status-badge.executed {
          background: #fef3c7;
          color: #b45309;
        }

        .status-badge.completed {
          background: #d1fae5;
          color: #047857;
        }

        .status-badge.reviewed {
          background: #e0e7ff;
          color: #4338ca;
        }

        .history-stats {
          display: flex;
          gap: 24px;
          margin-bottom: 16px;
          flex-wrap: wrap;
        }

        .stat-item {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .stat-label {
          font-size: 12px;
          color: var(--text-secondary);
        }

        .stat-value {
          font-size: 14px;
          font-weight: 500;
        }

        .stat-value.positive {
          color: var(--success);
        }

        .stat-value.negative {
          color: var(--danger);
        }

        .cycle-tag {
          padding: 2px 8px;
          border-radius: 8px;
          font-size: 12px;
          font-weight: 500;
        }

        .cycle-tag.ice { background: #e0f2fe; color: #0369a1; }
        .cycle-tag.start { background: #dcfce7; color: #15803d; }
        .cycle-tag.divergence { background: #fef3c7; color: #b45309; }
        .cycle-tag.peak { background: #fce7f3; color: #be185d; }
        .cycle-tag.ebb { background: #fee2e2; color: #b91c1c; }

        .history-actions {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding-top: 12px;
          border-top: 1px solid var(--gray-100);
        }

        .btn-link {
          color: var(--primary);
          text-decoration: none;
          font-size: 14px;
        }

        .btn-link:hover {
          text-decoration: underline;
        }

        .btn-sm {
          padding: 6px 12px;
          font-size: 12px;
        }
      `}</style>
    </div>
  );
}
