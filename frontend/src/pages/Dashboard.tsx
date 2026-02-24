import { useEffect, useState } from 'react';
import { positionsApi, tradesApi } from '../services/api';
import type { Position, Trade } from '../types';
import dayjs from 'dayjs';

export default function Dashboard() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [trades, setTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);
  const [showSellModal, setShowSellModal] = useState(false);
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);
  const [sellForm, setSellForm] = useState({ quantity: 0, price: 0 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [positionsRes, tradesRes] = await Promise.all([
        positionsApi.getAll(),
        tradesApi.getAll(),
      ]);
      setPositions(positionsRes.data);
      const today = dayjs().format('YYYY-MM-DD');
      setTrades(tradesRes.data.filter((t: Trade) => t.trade_date === today));
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const totalAssets = 100000;
  const availableCash = 30000;
  const holdingPositions = positions.filter(p => p.status === 'holding');
  const marketValue = holdingPositions.reduce((sum, p) => sum + (p.current_price || 0) * p.quantity, 0);
  const totalCost = holdingPositions.reduce((sum, p) => sum + p.cost_price * p.quantity, 0);
  const totalProfit = marketValue - totalCost;
  const todayProfit = trades
    .filter(t => t.trade_type === 'sell')
    .reduce((sum, t) => {
      const pos = positions.find(p => p.stock_code === t.stock_code);
      return sum + (t.price - (pos?.cost_price || 0)) * t.quantity;
    }, 0);

  const handleSell = (position: Position) => {
    setSelectedPosition(position);
    setSellForm({ quantity: position.quantity, price: position.current_price || 0 });
    setShowSellModal(true);
  };

  const confirmSell = async () => {
    if (!selectedPosition) return;
    const amount = sellForm.quantity * sellForm.price;
    const fee = amount * 0.0003;
    try {
      await tradesApi.create({
        stock_code: selectedPosition.stock_code,
        stock_name: selectedPosition.stock_name,
        trade_type: 'sell',
        quantity: sellForm.quantity,
        price: sellForm.price,
        amount,
        fee,
        reason: '持仓卖出',
        trade_date: new Date().toISOString().split('T')[0],
        trade_time: new Date().toTimeString().split(' ')[0],
      });
      setShowSellModal(false);
      loadData();
    } catch (error) {
      console.error('Failed to sell:', error);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <h1>首页</h1>
      </div>

      <div className="dashboard-hero">
        <div className="hero-main">
          <div className="hero-label">总资产</div>
          <div className="hero-value">¥{totalAssets.toLocaleString()}</div>
          <div className="hero-change">
            <span className={todayProfit >= 0 ? 'positive' : 'negative'}>
              {todayProfit >= 0 ? '+' : ''}¥{todayProfit.toFixed(2)}
            </span>
            <span className="change-ratio">
              ({todayProfit >= 0 ? '+' : ''}{((todayProfit / totalAssets) * 100).toFixed(2)}%)
            </span>
            <span className="change-label">今日盈亏</span>
          </div>
        </div>
        <div className="hero-stats">
          <div className="hero-stat">
            <span className="hero-stat-label">可用资金</span>
            <span className="hero-stat-value">¥{availableCash.toLocaleString()}</span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat-label">持仓市值</span>
            <span className="hero-stat-value">¥{marketValue.toLocaleString()}</span>
          </div>
          <div className="hero-stat">
            <span className="hero-stat-label">持仓股数</span>
            <span className="hero-stat-value">{holdingPositions.reduce((sum, p) => sum + p.quantity, 0)}</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>持仓</h3>
        </div>
        {positions.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">💼</div>
            <div>暂无持仓</div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>股票代码</th>
                <th>股票名称</th>
                <th>数量</th>
                <th>成本价</th>
                <th>当前价</th>
                <th>盈亏</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {positions.filter(p => p.status === 'holding').map((pos) => {
                const profit = ((pos.current_price || 0) - pos.cost_price) * pos.quantity;
                const profitRatio = ((pos.current_price || 0) - pos.cost_price) / pos.cost_price * 100;
                return (
                  <tr key={pos.id}>
                    <td><strong>{pos.stock_code}</strong></td>
                    <td>{pos.stock_name}</td>
                    <td>{pos.quantity}</td>
                    <td>¥{pos.cost_price}</td>
                    <td>¥{pos.current_price || '-'}</td>
                    <td className={profit >= 0 ? 'positive' : 'negative'}>
                      {profit >= 0 ? '+' : ''}¥{profit.toFixed(2)} ({profitRatio.toFixed(1)}%)
                    </td>
                    <td>
                      <button className="action-btn danger" onClick={() => handleSell(pos)}>
                        卖点
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <h3>今日交易</h3>
        </div>
        {trades.length === 0 ? (
          <div className="empty-state">
            <div className="empty-state-icon">📝</div>
            <div>今日暂无交易</div>
          </div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>时间</th>
                <th>股票代码</th>
                <th>股票名称</th>
                <th>方向</th>
                <th>价格</th>
                <th>数量</th>
                <th>金额</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr key={trade.id}>
                  <td>{trade.trade_time || '-'}</td>
                  <td><strong>{trade.stock_code}</strong></td>
                  <td>{trade.stock_name}</td>
                  <td>
                    <span className={`trade-type-badge ${trade.trade_type}`}>
                      {trade.trade_type === 'buy' ? '买入' : '卖出'}
                    </span>
                  </td>
                  <td>¥{trade.price}</td>
                  <td>{trade.quantity}</td>
                  <td>¥{trade.amount.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {showSellModal && selectedPosition && (
        <div className="modal-overlay" onClick={() => setShowSellModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>卖出 {selectedPosition.stock_name}</h2>
              <button onClick={() => setShowSellModal(false)}>×</button>
            </div>
            <div className="form-group">
              <label>卖出数量</label>
              <input
                type="number"
                value={sellForm.quantity}
                onChange={(e) => setSellForm({ ...sellForm, quantity: parseInt(e.target.value) })}
                max={selectedPosition.quantity}
              />
            </div>
            <div className="form-group">
              <label>卖出价格</label>
              <input
                type="number"
                step="0.01"
                value={sellForm.price}
                onChange={(e) => setSellForm({ ...sellForm, price: parseFloat(e.target.value) })}
              />
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowSellModal(false)}>取消</button>
              <button className="btn btn-primary" onClick={confirmSell}>确认卖出</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
