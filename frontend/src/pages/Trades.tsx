import { useState, useEffect } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';
import type { Trade, TradeStatistics } from '../types';

export default function Trades() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [statistics, setStatistics] = useState<TradeStatistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    startDate: dayjs().subtract(30, 'day').format('YYYY-MM-DD'),
    endDate: dayjs().format('YYYY-MM-DD'),
    tradeType: '',
    stockCode: '',
  });

  useEffect(() => {
    loadTrades();
    loadStatistics();
  }, [filters.startDate, filters.endDate]);

  const loadTrades = async () => {
    setLoading(true);
    try {
      const params: Record<string, string> = {};
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;
      if (filters.tradeType) params.trade_type = filters.tradeType;
      if (filters.stockCode) params.stock_code = filters.stockCode;

      const res = await axios.get('/api/trades', { params });
      setTrades(res.data || []);
    } catch (err) {
      console.error('Failed to load trades:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStatistics = async () => {
    try {
      const params: Record<string, string> = {};
      if (filters.startDate) params.start_date = filters.startDate;
      if (filters.endDate) params.end_date = filters.endDate;

      const res = await axios.get('/api/trades/summary', { params });
      setStatistics(res.data);
    } catch (err) {
      console.error('Failed to load statistics:', err);
    }
  };

  const handleSearch = () => {
    loadTrades();
    loadStatistics();
  };

  const totalBuyAmount = trades
    .filter(t => t.trade_type === '买入' || t.trade_type === 'buy')
    .reduce((sum, t) => sum + t.amount, 0);
  const totalSellAmount = trades
    .filter(t => t.trade_type === '卖出' || t.trade_type === 'sell')
    .reduce((sum, t) => sum + t.amount, 0);
  const netProfit = totalSellAmount - totalBuyAmount - (statistics?.total_fees || 0);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>交易记录</h1>
          <span className="date">时间范围: {filters.startDate} ~ {filters.endDate}</span>
        </div>
      </div>

      {/* 统计卡片 */}
      {statistics && (
        <div className="summary-cards">
          <div className="summary-card">
            <span className="card-label">交易次数</span>
            <span className="card-value">{statistics.total_trades}</span>
          </div>
          <div className="summary-card">
            <span className="card-label">买入次数</span>
            <span className="card-value">{statistics.buy_count}</span>
          </div>
          <div className="summary-card">
            <span className="card-label">卖出次数</span>
            <span className="card-value">{statistics.sell_count}</span>
          </div>
          <div className="summary-card">
            <span className="card-label">买入金额</span>
            <span className="card-value">¥{statistics.total_buy_amount.toLocaleString()}</span>
          </div>
          <div className="summary-card">
            <span className="card-label">卖出金额</span>
            <span className="card-value">¥{statistics.total_sell_amount.toLocaleString()}</span>
          </div>
          <div className="summary-card">
            <span className="card-label">手续费</span>
            <span className="card-value">¥{statistics.total_fees.toFixed(2)}</span>
          </div>
          <div className="summary-card">
            <span className="card-label">净盈亏</span>
            <span className={`card-value ${netProfit >= 0 ? 'positive' : 'negative'}`}>
              {netProfit >= 0 ? '+' : ''}¥{netProfit.toLocaleString()}
            </span>
          </div>
        </div>
      )}

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
            <label>操作类型</label>
            <select
              value={filters.tradeType}
              onChange={(e) => setFilters({ ...filters, tradeType: e.target.value })}
            >
              <option value="">全部</option>
              <option value="买入">买入</option>
              <option value="卖出">卖出</option>
            </select>
          </div>
          <div className="filter-item">
            <label>股票代码</label>
            <input
              type="text"
              value={filters.stockCode}
              onChange={(e) => setFilters({ ...filters, stockCode: e.target.value })}
              placeholder="如: 600519"
            />
          </div>
          <button className="btn" onClick={handleSearch}>搜索</button>
        </div>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : trades.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📜</div>
          <div className="empty-text">暂无交易记录</div>
        </div>
      ) : (
        <div className="trades-table">
          <table>
            <thead>
              <tr>
                <th>日期</th>
                <th>时间</th>
                <th>股票</th>
                <th>操作</th>
                <th>价格</th>
                <th>数量</th>
                <th>金额</th>
                <th>手续费</th>
                <th>理由</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade) => (
                <tr key={trade.id}>
                  <td>{trade.trade_date}</td>
                  <td>{trade.trade_time || '-'}</td>
                  <td>
                    <div className="stock-info">
                      <span className="stock-name">{trade.stock_name}</span>
                      <span className="stock-code">{trade.stock_code}</span>
                    </div>
                  </td>
                  <td>
                    <span className={`action-tag ${trade.trade_type === '买入' || trade.trade_type === 'buy' ? 'buy' : 'sell'}`}>
                      {trade.trade_type}
                    </span>
                  </td>
                  <td>¥{trade.price.toFixed(2)}</td>
                  <td>{trade.quantity}</td>
                  <td>¥{trade.amount.toLocaleString()}</td>
                  <td>¥{(trade.fee + trade.stamp_duty).toFixed(2)}</td>
                  <td className="reason-cell">{trade.reason || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
