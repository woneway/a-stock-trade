import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
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
  createdAt: string;
  updatedAt: string;
}

interface PrePlan {
  id: number;
  selectedStrategy: string;
  sentiment: string;
  candidateStocks: string;
  stopLoss: number;
  positionSize: number;
  entryCondition: string;
  exitCondition: string;
}

interface Trade {
  id: number;
  code: string;
  name: string;
  action: string;
  price: number;
  quantity: number;
  amount: number;
  pnl: number;
  reason: string;
  tradeDate: string;
  tradeTime: string;
}

interface PostReview {
  id: number;
  emotionRecord: string;
  mistakes: string;
  lessons: string;
  tradeAnalysis: string;
  tomorrowPlan: string;
  executionRate: number;
  tradeDate: string;
}

export default function HistoryDetail() {
  const { id } = useParams<{ id: string }>();
  const [plan, setPlan] = useState<HistoricalPlan | null>(null);
  const [prePlan, setPrePlan] = useState<PrePlan | null>(null);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [postReview, setPostReview] = useState<PostReview | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'plan' | 'execute' | 'review'>('plan');

  useEffect(() => {
    if (id) {
      loadData(parseInt(id));
    }
  }, [id]);

  const loadData = async (planId: number) => {
    setLoading(true);
    try {
      // 获取历史计划详情
      const planRes = await axios.get(`/api/plan/history/${planId}`);
      const planData = planRes.data;
      setPlan(planData);

      if (!planData.tradeDate) {
        setLoading(false);
        return;
      }

      // 根据日期获取PrePlan
      try {
        const prePlanRes = await axios.get('/api/plan/pre', {
          params: { trade_date: planData.tradeDate }
        });
        if (prePlanRes.data && prePlanRes.data.id) {
          setPrePlan(prePlanRes.data);
        }
      } catch (e) {
        // PrePlan可能不存在，这是正常的
      }

      // 获取交易记录
      try {
        const tradesRes = await axios.get('/api/trades', {
          params: { trade_date: planData.tradeDate }
        });
        setTrades(tradesRes.data || []);
      } catch (e) {
        // 交易记录可能不存在
      }

      // 获取后复盘
      try {
        const postRes = await axios.get('/api/plan/post', {
          params: { trade_date: planData.tradeDate }
        });
        if (postRes.data && postRes.data.id) {
          setPostReview(postRes.data);
        }
      } catch (e) {
        // 后复盘可能不存在
      }
    } catch (err) {
      console.error('加载失败', err);
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

  const parseStocks = (stocksJson: string) => {
    try {
      return JSON.parse(stocksJson);
    } catch {
      return [];
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="loading">加载中...</div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="page">
        <div className="empty-state">
          <div className="empty-text">未找到该计划</div>
          <Link to="/history" className="btn btn-primary">返回历史计划</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>历史计划详情</h1>
          <span className="date">{plan.tradeDate} {dayjs(plan.tradeDate).format('dddd')}</span>
        </div>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {getStatusBadge(plan.status)}
          <Link to="/history" className="btn btn-outline">返回列表</Link>
        </div>
      </div>

      {/* 汇总信息 */}
      <div className="summary-cards">
        <div className="summary-card">
          <span className="summary-label">情绪周期</span>
          <span className="summary-value">{plan.marketCycle || '-'}</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">仓位计划</span>
          <span className="summary-value">{plan.positionPlan || '-'}</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">目标股票</span>
          <span className="summary-value">{plan.plannedStockCount}只</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">执行股票</span>
          <span className="summary-value">{plan.executedStockCount}只</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">执行率</span>
          <span className="summary-value">{plan.executionRate || 0}%</span>
        </div>
        <div className="summary-card">
          <span className="summary-label">总盈亏</span>
          <span className={`summary-value ${(plan.totalPnl || 0) >= 0 ? 'positive' : 'negative'}`}>
            {plan.totalPnl ? (plan.totalPnl > 0 ? '+' : '') + plan.totalPnl.toFixed(2) : '-'}
          </span>
        </div>
      </div>

      {/* Tab切换 */}
      <div className="detail-tabs">
        <button
          className={`detail-tab ${activeTab === 'plan' ? 'active' : ''}`}
          onClick={() => setActiveTab('plan')}
        >
          计划内容
        </button>
        <button
          className={`detail-tab ${activeTab === 'execute' ? 'active' : ''}`}
          onClick={() => setActiveTab('execute')}
        >
          执行记录
        </button>
        <button
          className={`detail-tab ${activeTab === 'review' ? 'active' : ''}`}
          onClick={() => setActiveTab('review')}
        >
          复盘总结
        </button>
      </div>

      {/* Tab内容 */}
      <div className="detail-content">
        {activeTab === 'plan' && (
          <div className="plan-section">
            {prePlan ? (
              <>
                <div className="info-card">
                  <h3>策略选择</h3>
                  <p>{prePlan.selectedStrategy || '-'}</p>
                </div>
                <div className="info-card">
                  <h3>情绪判断</h3>
                  <p>{prePlan.sentiment || '-'}</p>
                </div>
                <div className="info-card">
                  <h3>候选股票</h3>
                  {prePlan.candidateStocks ? (
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>代码</th>
                          <th>名称</th>
                          <th>优先级</th>
                          <th>买入理由</th>
                        </tr>
                      </thead>
                      <tbody>
                        {parseStocks(prePlan.candidateStocks).map((stock: any, idx: number) => (
                          <tr key={idx}>
                            <td>{stock.code || '-'}</td>
                            <td>{stock.name || '-'}</td>
                            <td>{stock.priority || '-'}</td>
                            <td>{stock.buy_reason || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <p className="empty-text">暂无候选股票</p>
                  )}
                </div>
                <div className="info-row">
                  <div className="info-card">
                    <h3>止损线</h3>
                    <p>{prePlan.stopLoss ? `-${prePlan.stopLoss}%` : '-'}</p>
                  </div>
                  <div className="info-card">
                    <h3>仓位</h3>
                    <p>{prePlan.positionSize ? `${prePlan.positionSize}成` : '-'}</p>
                  </div>
                </div>
                <div className="info-card">
                  <h3>买入条件</h3>
                  <p>{prePlan.entryCondition || '-'}</p>
                </div>
                <div className="info-card">
                  <h3>卖出条件</h3>
                  <p>{prePlan.exitCondition || '-'}</p>
                </div>
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-text">暂无计划内容</div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'execute' && (
          <div className="execute-section">
            {trades.length > 0 ? (
              <table className="data-table">
                <thead>
                  <tr>
                    <th>时间</th>
                    <th>股票</th>
                    <th>操作</th>
                    <th>价格</th>
                    <th>数量</th>
                    <th>金额</th>
                    <th>盈亏</th>
                    <th>理由</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.map((trade) => (
                    <tr key={trade.id}>
                      <td>{trade.tradeTime || '-'}</td>
                      <td>{trade.name} {trade.code}</td>
                      <td>
                        <span className={`action-tag ${trade.action === 'buy' ? 'buy' : 'sell'}`}>
                          {trade.action === 'buy' ? '买入' : '卖出'}
                        </span>
                      </td>
                      <td>¥{trade.price}</td>
                      <td>{trade.quantity}</td>
                      <td>¥{trade.amount.toLocaleString()}</td>
                      <td className={(trade.pnl || 0) >= 0 ? 'positive' : 'negative'}>
                        {trade.pnl ? (trade.pnl > 0 ? '+' : '') + trade.pnl.toFixed(2) : '-'}
                      </td>
                      <td>{trade.reason || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="empty-state">
                <div className="empty-text">暂无交易记录</div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'review' && (
          <div className="review-section">
            {postReview ? (
              <>
                <div className="info-card">
                  <h3>情绪记录</h3>
                  <p>{postReview.emotionRecord || '-'}</p>
                </div>
                <div className="info-card">
                  <h3>失误记录</h3>
                  <p>{postReview.mistakes || '-'}</p>
                </div>
                <div className="info-card">
                  <h3>心得体会</h3>
                  <p>{postReview.lessons || '-'}</p>
                </div>
                <div className="info-card">
                  <h3>交易分析</h3>
                  <p>{postReview.tradeAnalysis || '-'}</p>
                </div>
                <div className="info-card">
                  <h3>明日计划</h3>
                  <p>{postReview.tomorrowPlan || '-'}</p>
                </div>
                <div className="info-card">
                  <h3>执行率</h3>
                  <p>{postReview.executionRate || 0}%</p>
                </div>
              </>
            ) : (
              <div className="empty-state">
                <div className="empty-text">暂无复盘内容</div>
                <Link to={`/today?planId=${id}`} className="btn btn-primary">
                  去执行复盘
                </Link>
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        .summary-cards {
          display: grid;
          grid-template-columns: repeat(6, 1fr);
          gap: 16px;
          margin-bottom: 24px;
        }

        @media (max-width: 1200px) {
          .summary-cards {
            grid-template-columns: repeat(3, 1fr);
          }
        }

        .summary-card {
          background: var(--bg-card);
          border-radius: var(--radius-md);
          padding: 16px;
          text-align: center;
          border: 1px solid var(--gray-200);
        }

        .summary-label {
          display: block;
          font-size: 12px;
          color: var(--text-secondary);
          margin-bottom: 4px;
        }

        .summary-value {
          font-size: 18px;
          font-weight: 600;
        }

        .summary-value.positive {
          color: var(--success);
        }

        .summary-value.negative {
          color: var(--danger);
        }

        .detail-tabs {
          display: flex;
          gap: 4px;
          margin-bottom: 24px;
          background: var(--gray-100);
          padding: 4px;
          border-radius: 8px;
          width: fit-content;
        }

        .detail-tab {
          padding: 10px 20px;
          border: none;
          background: transparent;
          cursor: pointer;
          border-radius: 6px;
          font-size: 14px;
          transition: all 0.2s;
        }

        .detail-tab:hover {
          background: var(--gray-200);
        }

        .detail-tab.active {
          background: white;
          box-shadow: var(--shadow-sm);
        }

        .detail-content {
          background: var(--bg-card);
          border-radius: var(--radius-md);
          padding: 24px;
          border: 1px solid var(--gray-200);
        }

        .info-card {
          margin-bottom: 20px;
        }

        .info-card h3 {
          font-size: 14px;
          color: var(--text-secondary);
          margin-bottom: 8px;
        }

        .info-card p {
          font-size: 15px;
          line-height: 1.6;
          white-space: pre-wrap;
        }

        .info-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
        }

        .data-table {
          width: 100%;
          border-collapse: collapse;
        }

        .data-table th,
        .data-table td {
          padding: 12px;
          text-align: left;
          border-bottom: 1px solid var(--gray-100);
        }

        .data-table th {
          font-size: 12px;
          color: var(--text-secondary);
          font-weight: 500;
        }

        .data-table td {
          font-size: 14px;
        }

        .action-tag {
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 500;
        }

        .action-tag.buy {
          background: #d1fae5;
          color: #047857;
        }

        .action-tag.sell {
          background: #fee2e2;
          color: #b91c1c;
        }

        .positive {
          color: var(--success);
        }

        .negative {
          color: var(--danger);
        }
      `}</style>
    </div>
  );
}
