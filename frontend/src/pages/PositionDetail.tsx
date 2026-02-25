import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import dayjs from 'dayjs';
import type { Position, Trade } from '../types';

interface PositionDetail extends Position {
  trades: Trade[];
}

export default function PositionDetail() {
  const { id } = useParams<{ id: string }>();
  const [position, setPosition] = useState<PositionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [updatingPrice, setUpdatingPrice] = useState(false);
  const [newPrice, setNewPrice] = useState('');

  useEffect(() => {
    if (id) {
      loadPosition(parseInt(id));
    }
  }, [id]);

  const loadPosition = async (positionId: number) => {
    setLoading(true);
    try {
      const res = await axios.get(`/api/positions/${positionId}`);
      setPosition(res.data);

      // 加载关联的交易记录
      const tradesRes = await axios.get('/api/trades', {
        params: { stock_code: res.data.stock_code },
      });
      setPosition({
        ...res.data,
        trades: tradesRes.data || [],
      });
    } catch (err) {
      console.error('Failed to load position:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePrice = async () => {
    if (!position?.id || !newPrice) return;
    const price = parseFloat(newPrice);
    if (isNaN(price) || price <= 0) {
      alert('请输入有效的价格');
      return;
    }

    setUpdatingPrice(true);
    try {
      await axios.put(`/api/positions/${position.id}/update-price`, null, {
        params: { current_price: price },
      });
      alert('价格已更新');
      loadPosition(position.id);
      setNewPrice('');
    } catch (err) {
      alert('更新失败');
    } finally {
      setUpdatingPrice(false);
    }
  };

  const handleClose = async () => {
    if (!position?.id || !confirm('确定要平仓吗？')) return;
    try {
      await axios.post(`/api/positions/${position.id}/close`);
      alert('平仓成功');
      window.location.href = '/positions';
    } catch (err) {
      alert('平仓失败');
    }
  };

  if (loading) {
    return <div className="page"><div className="loading">加载中...</div></div>;
  }

  if (!position) {
    return <div className="page"><div className="empty-state">持仓不存在</div></div>;
  }

  const currentPrice = position.current_price || position.cost_price;
  const profit = (currentPrice - position.cost_price) * position.quantity;
  const profitRatio = position.cost_price > 0 ? ((currentPrice - position.cost_price) / position.cost_price) * 100 : 0;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/positions" className="back-link">← 返回列表</Link>
          <h1>{position.stock_name}</h1>
          <span className="date">{position.stock_code}</span>
        </div>
        <button className="btn btn-danger" onClick={handleClose}>平仓</button>
      </div>

      {/* 持仓信息 */}
      <div className="detail-cards">
        <div className="detail-card">
          <span className="card-label">持仓数量</span>
          <span className="card-value">{position.quantity}股</span>
        </div>
        <div className="detail-card">
          <span className="card-label">成本价</span>
          <span className="card-value">¥{position.cost_price.toFixed(2)}</span>
        </div>
        <div className="detail-card">
          <span className="card-label">现价</span>
          <span className="card-value highlight">¥{currentPrice.toFixed(2)}</span>
        </div>
        <div className="detail-card">
          <span className="card-label">市值</span>
          <span className="card-value">¥{(currentPrice * position.quantity).toLocaleString()}</span>
        </div>
        <div className="detail-card">
          <span className="card-label">盈亏金额</span>
          <span className={`card-value ${profit >= 0 ? 'positive' : 'negative'}`}>
            {profit >= 0 ? '+' : ''}¥{profit.toFixed(2)}
          </span>
        </div>
        <div className="detail-card">
          <span className="card-label">盈亏比例</span>
          <span className={`card-value ${profitRatio >= 0 ? 'positive' : 'negative'}`}>
            {profitRatio >= 0 ? '+' : ''}{profitRatio.toFixed(2)}%
          </span>
        </div>
      </div>

      {/* 更新价格 */}
      <div className="detail-section">
        <h3>更新价格</h3>
        <div className="price-update-form">
          <input
            type="number"
            step="0.01"
            placeholder="输入最新价格"
            value={newPrice}
            onChange={(e) => setNewPrice(e.target.value)}
          />
          <button
            className="btn btn-primary"
            onClick={handleUpdatePrice}
            disabled={updatingPrice}
          >
            {updatingPrice ? '更新中...' : '更新'}
          </button>
        </div>
      </div>

      {/* 止损止盈 */}
      <div className="detail-section">
        <h3>止损止盈</h3>
        <div className="form-grid">
          <div className="form-group">
            <label>止损价</label>
            <span className="value-display">
              {position.stop_loss_price ? `¥${position.stop_loss_price.toFixed(2)}` : '未设置'}
            </span>
          </div>
          <div className="form-group">
            <label>止盈价</label>
            <span className="value-display">
              {position.take_profit_price ? `¥${position.take_profit_price.toFixed(2)}` : '未设置'}
            </span>
          </div>
          <div className="form-group">
            <label>持仓日期</label>
            <span className="value-display">{position.opened_at}</span>
          </div>
          <div className="form-group">
            <label>状态</label>
            <span className="value-display status-badge">{position.status}</span>
          </div>
        </div>
      </div>

      {/* 交易历史 */}
      <div className="detail-section">
        <h3>交易历史</h3>
        {position.trades && position.trades.length > 0 ? (
          <div className="trades-table">
            <table>
              <thead>
                <tr>
                  <th>日期</th>
                  <th>时间</th>
                  <th>操作</th>
                  <th>价格</th>
                  <th>数量</th>
                  <th>金额</th>
                  <th>理由</th>
                </tr>
              </thead>
              <tbody>
                {position.trades.map((trade) => (
                  <tr key={trade.id}>
                    <td>{trade.trade_date}</td>
                    <td>{trade.trade_time || '-'}</td>
                    <td>
                      <span className={`action-tag ${trade.trade_type === '买入' ? 'buy' : 'sell'}`}>
                        {trade.trade_type}
                      </span>
                    </td>
                    <td>¥{trade.price.toFixed(2)}</td>
                    <td>{trade.quantity}</td>
                    <td>¥{trade.amount.toLocaleString()}</td>
                    <td>{trade.reason || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-tip">暂无交易记录</div>
        )}
      </div>
    </div>
  );
}
