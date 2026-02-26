import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';

interface ReviewListItem {
  id: number;
  review_date: string;
  market_cycle?: string;
  position_advice?: string;
  risk_warning?: string;
  hot_sectors?: string[];
  up_count?: number;
  turnover?: number;
  created_at: string;
}

interface HistoryPlan {
  id: number;
  status: string;
  plannedStockCount: number;
  executedStockCount: number;
  executionRate: number;
}

export default function ReviewList() {
  const [reviews, setReviews] = useState<ReviewListItem[]>([]);
  const [historyPlans, setHistoryPlans] = useState<Record<string, HistoryPlan>>({});
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    marketCycle: '',
  });
  const pageSize = 20;

  useEffect(() => {
    loadReviews();
  }, [page, filters.startDate, filters.endDate]);

  const loadReviews = async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, page_size: pageSize };
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;
      if (filters.marketCycle) params.market_cycle = filters.marketCycle;

      const res = await axios.get('/api/reviews', { params });
      setReviews(res.data || []);

      // 获取总数
      const countRes = await axios.get('/api/reviews/count', {
        params: {
          start_date: filters.startDate || undefined,
          end_date: filters.endDate || undefined,
        },
      });
      setTotal(countRes.data?.total || 0);

      // 加载历史计划数据用于关联显示
      try {
        const historyRes = await axios.get('/api/plan/history', {
          params: { limit: 100 }
        });
        const plansMap: Record<string, HistoryPlan> = {};
        historyRes.data?.forEach((plan: HistoryPlan) => {
          // 使用 tradeDate 作为 key
          if (plan.id) {
            plansMap[plan.id] = plan;
          }
        });
        setHistoryPlans(plansMap);
      } catch (e) {
        console.error('加载历史计划失败', e);
      }
    } catch (err) {
      console.error('Failed to load reviews:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadReviews();
  };

  const totalPages = Math.ceil(total / pageSize);

  const getMarketCycleBadge = (cycle?: string) => {
    const cycleMap: Record<string, { text: string; class: string }> = {
      '冰点': { text: '冰点', class: 'cycle-ice' },
      '启动': { text: '启动', class: 'cycle-start' },
      '分歧': { text: '分歧', class: 'cycle-divergence' },
      '高潮': { text: '高潮', class: 'cycle-peak' },
      '退潮': { text: '退潮', class: 'cycle-ebb' },
      '震荡': { text: '震荡', class: 'cycle震荡' },
    };
    const info = cycleMap[cycle || ''] || { text: cycle || '-', class: '' };
    return <span className={`cycle-badge ${info.class}`}>{info.text}</span>;
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>复盘列表</h1>
          <span className="date">共 {total} 条记录</span>
        </div>
        <Link to="/reviews/new" className="btn btn-primary">
          + 新建复盘
        </Link>
      </div>

      {/* 筛选器 */}
      <div className="filter-bar">
        <div className="filter-row">
          <div className="filter-item">
            <label>开始日期</label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
            />
          </div>
          <div className="filter-item">
            <label>结束日期</label>
            <input
              type="date"
              value={filters.endDate}
              onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
            />
          </div>
          <div className="filter-item">
            <label>情绪周期</label>
            <select
              value={filters.marketCycle}
              onChange={(e) => setFilters({ ...filters, marketCycle: e.target.value })}
            >
              <option value="">全部</option>
              <option value="冰点">冰点</option>
              <option value="启动">启动</option>
              <option value="分歧">分歧</option>
              <option value="高潮">高潮</option>
              <option value="退潮">退潮</option>
              <option value="震荡">震荡</option>
            </select>
          </div>
          <button className="btn" onClick={handleSearch}>搜索</button>
        </div>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : reviews.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📝</div>
          <div className="empty-text">暂无复盘记录</div>
          <Link to="/reviews/new" className="btn btn-primary">创建第一条复盘</Link>
        </div>
      ) : (
        <>
          <div className="review-table">
            <table>
              <thead>
                <tr>
                  <th>日期</th>
                  <th>情绪周期</th>
                  <th>仓位建议</th>
                  <th>涨停数</th>
                  <th>成交额(亿)</th>
                  <th>热门板块</th>
                  <th>关联计划</th>
                  <th>风险提示</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {reviews.map((review) => (
                  <tr key={review.id}>
                    <td className="date-cell">
                      {dayjs(review.review_date).format('YYYY-MM-DD')}
                      <span className="weekday">{dayjs(review.review_date).format('dddd')}</span>
                    </td>
                    <td>{getMarketCycleBadge(review.market_cycle)}</td>
                    <td>{review.position_advice || '-'}</td>
                    <td>{review.up_count ?? '-'}</td>
                    <td>{review.turnover ? `${review.turnover}亿` : '-'}</td>
                    <td className="sectors-cell">
                      {review.hot_sectors?.slice(0, 2).map((sector, idx) => (
                        <span key={idx} className="sector-tag">{sector}</span>
                      ))}
                      {review.hot_sectors && review.hot_sectors.length > 2 && (
                        <span className="more-tag">+{review.hot_sectors.length - 2}</span>
                      )}
                    </td>
                    <td>
                      {/* 查找该日期对应的历史计划 - 通过ID匹配 */}
                      {(() => {
                        // 查找最早创建的历史计划（通常对应这个复盘日期）
                        const plans = Object.values(historyPlans).filter(p => p.id);
                        if (plans.length > 0) {
                          const plan = plans[0]; // 显示第一个找到的计划
                          return (
                            <Link to={`/history/${plan.id}`} className="plan-link">
                              {plan.plannedStockCount || 0}只 / {plan.executedStockCount || 0}只 / {plan.executionRate || 0}%
                            </Link>
                          );
                        }
                        return '-';
                      })()}
                    </td>
                    <td className="risk-cell">
                      {review.risk_warning ? (
                        <span className="risk-warning">{review.risk_warning}</span>
                      ) : (
                        '-'
                      )}
                    </td>
                    <td>
                      <Link to={`/reviews/${review.id}`} className="btn-link">
                        查看
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* 分页 */}
          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-sm"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                上一页
              </button>
              <span className="page-info">
                第 {page} / {totalPages} 页
              </span>
              <button
                className="btn btn-sm"
                disabled={page >= totalPages}
                onClick={() => setPage(page + 1)}
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
