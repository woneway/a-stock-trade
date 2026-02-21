import { useState } from 'react';
import dayjs from 'dayjs';

interface PlanRecord {
  id: number;
  date: string;
  tradeCount: number;
  profit: number;
  strategy?: string;
  stocks?: {
    code: string;
    name: string;
    signal?: 'buy' | 'sell' | 'watch' | 'none';
    reason?: string;
  }[];
  trades?: { time: string; stock: string; type: string; price: number; quantity: number; result?: number }[];
  review?: {
    sentiment?: string;
    mistakes?: string;
    lessons?: string;
  };
}

export default function PlanList() {
  const [currentMonth, setCurrentMonth] = useState(dayjs());
  const [selectedPlan, setSelectedPlan] = useState<PlanRecord | null>(null);

  const [plans] = useState<PlanRecord[]>([
    {
      id: 1,
      date: dayjs().format('YYYY-MM-DD'),
      tradeCount: 3,
      profit: 2500,
      strategy: '追涨策略',
      stocks: [
        { code: '600519', name: '贵州茅台', signal: 'buy', reason: '突破前高' },
        { code: '300750', name: '宁德时代', signal: 'sell', reason: '跌破5日线' },
        { code: '002594', name: '比亚迪', signal: 'buy', reason: '龙回头' },
      ],
      trades: [
        { time: '09:35', stock: '600519', type: '买入', price: 1850, quantity: 100, result: 2.8 },
        { time: '10:20', stock: '300750', type: '卖出', price: 280, quantity: 200, result: -1.2 },
        { time: '14:30', stock: '002594', type: '买入', price: 270, quantity: 50, result: 1.5 },
      ],
      review: { sentiment: '回暖', mistakes: '卖点稍早', lessons: '龙头分歧时先保利润' },
    },
    {
      id: 2,
      date: dayjs().subtract(1, 'day').format('YYYY-MM-DD'),
      tradeCount: 2,
      profit: -800,
      stocks: [
        { code: '600519', name: '贵州茅台', signal: 'buy', reason: '低吸' },
      ],
      trades: [
        { time: '09:45', stock: '600519', type: '买入', price: 1800, quantity: 100, result: -1.1 },
        { time: '14:00', stock: '600519', type: '卖出', price: 1780, quantity: 100, result: -1.1 },
      ],
      review: { sentiment: '分歧', mistakes: '未设置止损', lessons: '严格止损纪律' },
    },
    {
      id: 3,
      date: dayjs().subtract(2, 'day').format('YYYY-MM-DD'),
      tradeCount: 4,
      profit: 1200,
    },
    {
      id: 4,
      date: dayjs().subtract(3, 'day').format('YYYY-MM-DD'),
      tradeCount: 1,
      profit: 500,
    },
  ]);

  const daysInMonth = currentMonth.daysInMonth();
  const monthStart = currentMonth.startOf('month');
  const startDay = monthStart.day();

  const getPlansForDay = (day: number) => {
    const date = currentMonth.date(day).format('YYYY-MM-DD');
    return plans.filter(p => p.date === date);
  };

  const prevMonth = () => setCurrentMonth(currentMonth.subtract(1, 'month'));
  const nextMonth = () => setCurrentMonth(currentMonth.add(1, 'month'));

  return (
    <div className="page">
      <div className="page-header">
        <h1>计划列表</h1>
      </div>

      <div className="calendar-header">
        <button className="calendar-nav" onClick={prevMonth}>‹</button>
        <span className="calendar-title">{currentMonth.format('YYYY年MM月')}</span>
        <button className="calendar-nav" onClick={nextMonth}>›</button>
      </div>

      <div className="plan-list">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className="plan-item"
            onClick={() => setSelectedPlan(plan)}
          >
            <div className="plan-date">
              <span className="plan-day">{dayjs(plan.date).format('MM/DD')}</span>
              <span className="plan-weekday">{dayjs(plan.date).format('ddd')}</span>
            </div>
            <div className="plan-info">
              <span className="plan-count">{plan.tradeCount}笔交易</span>
              {plan.strategy && <span className="plan-strategy">{plan.strategy}</span>}
            </div>
            <div className={`plan-profit ${plan.profit >= 0 ? 'positive' : 'negative'}`}>
              {plan.profit >= 0 ? '+' : ''}¥{plan.profit.toLocaleString()}
            </div>
            <span className="plan-arrow">›</span>
          </div>
        ))}
      </div>

      {selectedPlan && (
        <div className="modal-overlay" onClick={() => setSelectedPlan(null)}>
          <div className="modal plan-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedPlan.date} 计划详情</h2>
              <button onClick={() => setSelectedPlan(null)}>×</button>
            </div>

            <div className="execution-flow">
              <div className="flow-step completed">
                <span className="step-icon">📋</span>
                <span className="step-label">计划</span>
              </div>
              <div className="flow-arrow">→</div>
              <div className={`flow-step ${selectedPlan.strategy ? 'completed' : ''}`}>
                <span className="step-icon">🎯</span>
                <span className="step-label">策略</span>
              </div>
              <div className="flow-arrow">→</div>
              <div className={`flow-step ${selectedPlan.stocks ? 'completed' : ''}`}>
                <span className="step-icon">📈</span>
                <span className="step-label">选股</span>
              </div>
              <div className="flow-arrow">→</div>
              <div className={`flow-step ${selectedPlan.stocks?.some(s => s.signal) ? 'completed' : ''}`}>
                <span className="step-icon">💡</span>
                <span className="step-label">信号</span>
              </div>
              <div className="flow-arrow">→</div>
              <div className={`flow-step ${selectedPlan.trades?.length ? 'completed' : ''}`}>
                <span className="step-icon">✅</span>
                <span className="step-label">执行</span>
              </div>
            </div>

            {selectedPlan.strategy && (
              <div className="detail-section">
                <h4>引用策略</h4>
                <p>{selectedPlan.strategy}</p>
              </div>
            )}

            {selectedPlan.stocks && selectedPlan.stocks.length > 0 && (
              <div className="detail-section">
                <h4>策略选股 → 信号</h4>
                <div className="stock-signal-list">
                  {selectedPlan.stocks.map((stock, i) => (
                    <div key={i} className={`stock-signal-item signal-${stock.signal}`}>
                      <div className="stock-info">
                        <span className="stock-name">{stock.name}</span>
                        <span className="stock-code">{stock.code}</span>
                      </div>
                      <div className="signal-info">
                        <span className={`signal-tag ${stock.signal}`}>
                          {stock.signal === 'buy' ? '买入' : stock.signal === 'sell' ? '卖出' : stock.signal === 'watch' ? '观察' : '无'}
                        </span>
                        {stock.reason && <span className="signal-reason">{stock.reason}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedPlan.trades && selectedPlan.trades.length > 0 && (
              <div className="detail-section">
                <h4>执行记录</h4>
                <div className="trade-list">
                  {selectedPlan.trades.map((trade, i) => (
                    <div key={i} className="trade-item">
                      <span className="trade-time">{trade.time}</span>
                      <span className={`trade-type ${trade.type === '买入' ? 'buy' : 'sell'}`}>{trade.type}</span>
                      <span className="trade-stock">{trade.stock}</span>
                      <span className="trade-quantity">{trade.quantity}股</span>
                      <span className="trade-price">@{trade.price}</span>
                      {trade.result !== undefined && (
                        <span className={`trade-result ${trade.result >= 0 ? 'positive' : 'negative'}`}>
                          {trade.result >= 0 ? '+' : ''}{trade.result}%
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {selectedPlan.review && (
              <div className="detail-section">
                <h4>复盘总结</h4>
                {selectedPlan.review.sentiment && (
                  <p>情绪周期: {selectedPlan.review.sentiment}</p>
                )}
                {selectedPlan.review.mistakes && (
                  <p className="review-mistakes">失误: {selectedPlan.review.mistakes}</p>
                )}
                {selectedPlan.review.lessons && (
                  <p className="review-lessons">心得: {selectedPlan.review.lessons}</p>
                )}
              </div>
            )}

            <div className="modal-footer">
              <button className="btn btn-primary">新建今日计划</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
