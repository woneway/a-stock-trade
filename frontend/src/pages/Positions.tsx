import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import type { Position } from '../types';

export default function Positions() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPositions();
  }, []);

  const loadPositions = async () => {
    setLoading(true);
    try {
      const res = await axios.get('/api/positions', { params: { status: 'holding' } });
      setPositions(res.data || []);
    } catch (err) {
      console.error('Failed to load positions:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = async (id: number) => {
    if (!confirm('确定要平仓吗？')) return;
    try {
      await axios.post(`/api/positions/${id}/close`);
      alert('平仓成功');
      loadPositions();
    } catch (err) {
      alert('平仓失败');
    }
  };

  // 统计
  const totalMarketValue = positions.reduce((sum, p) => sum + (p.current_price || p.cost_price) * p.quantity, 0);
  const totalCost = positions.reduce((sum, p) => sum + p.cost_price * p.quantity, 0);
  const totalProfit = totalMarketValue - totalCost;
  const totalProfitRatio = totalCost > 0 ? (totalProfit / totalCost) * 100 : 0;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>持仓列表</h1>
          <span className="date">当前持仓: {positions.length} 只</span>
        </div>
      </div>

      {/* 汇总卡片 */}
      <div className="summary-cards">
        <div className="summary-card">
          <span className="card-label">持仓市值</span>
          <span className="card-value">¥{totalMarketValue.toLocaleString()}</span>
        </div>
        <div className="summary-card">
          <span className="card-label">持仓成本</span>
          <span className="card-value">¥{totalCost.toLocaleString()}</span>
        </div>
        <div className="summary-card">
          <span className="card-label">总盈亏</span>
          <span className={`card-value ${totalProfit >= 0 ? 'positive' : 'negative'}`}>
            {totalProfit >= 0 ? '+' : ''}¥{totalProfit.toLocaleString()}
          </span>
        </div>
        <div className="summary-card">
          <span className="card-label">盈亏比例</span>
          <span className={`card-value ${totalProfitRatio >= 0 ? 'positive' : 'negative'}`}>
            {totalProfitRatio >= 0 ? '+' : ''}{totalProfitRatio.toFixed(2)}%
          </span>
        </div>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : positions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">💼</div>
          <div className="empty-text">当前无持仓</div>
        </div>
      ) : (
        <div className="positions-table">
          <table>
            <thead>
              <tr>
                <th>股票</th>
                <th>数量</th>
                <th>成本价</th>
                <th>现价</th>
                <th>盈亏金额</th>
                <th>盈亏比例</th>
                <th>止损价</th>
                <th>止盈价</th>
                <th>持仓日期</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((pos) => {
                const currentPrice = pos.current_price || pos.cost_price;
                const profit = (currentPrice - pos.cost_price) * pos.quantity;
                const profitRatio = pos.cost_price > 0 ? ((currentPrice - pos.cost_price) / pos.cost_price) * 100 : 0;

                return (
                  <tr key={pos.id}>
                    <td>
                      <div className="stock-info">
                        <span className="stock-name">{pos.stock_name}</span>
                        <span className="stock-code">{pos.stock_code}</span>
                      </div>
                    </td>
                    <td>{pos.quantity}</td>
                    <td>¥{pos.cost_price.toFixed(2)}</td>
                    <td>¥{currentPrice.toFixed(2)}</td>
                    <td className={profit >= 0 ? 'positive' : 'negative'}>
                      {profit >= 0 ? '+' : ''}¥{profit.toFixed(2)}
                    </td>
                    <td className={profitRatio >= 0 ? 'positive' : 'negative'}>
                      {profitRatio >= 0 ? '+' : ''}{profitRatio.toFixed(2)}%
                    </td>
                    <td>{pos.stop_loss_price ? `¥${pos.stop_loss_price.toFixed(2)}` : '-'}</td>
                    <td>{pos.take_profit_price ? `¥${pos.take_profit_price.toFixed(2)}` : '-'}</td>
                    <td>{pos.opened_at}</td>
                    <td>
                      <div className="action-btns">
                        <Link to={`/positions/${pos.id}`} className="btn-link">详情</Link>
                        <button className="btn-link danger" onClick={() => handleClose(pos.id)}>
                          平仓
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
