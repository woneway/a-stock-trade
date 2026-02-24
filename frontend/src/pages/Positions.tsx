import { useState, useEffect } from 'react';
import axios from 'axios';
import dayjs from 'dayjs';

interface Position {
  id: number;
  stock_code: string;
  stock_name: string;
  quantity: number;
  cost_price: number;
  current_price: number;
  market_value: number;
  profit_amount: number;
  profit_ratio: number;
  status: string;
  opened_at: string;
  sell_target?: number;
  stop_loss?: number;
  trade_plan?: string;
  holding_reason?: string;
}

export default function Positions() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editForm, setEditForm] = useState({
    sell_target: '',
    stop_loss: '',
    trade_plan: '',
    holding_reason: '',
  });

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

  const startEdit = (pos: Position) => {
    setEditingId(pos.id);
    setEditForm({
      sell_target: pos.sell_target?.toString() || '',
      stop_loss: pos.stop_loss?.toString() || '',
      trade_plan: pos.trade_plan || '',
      holding_reason: pos.holding_reason || '',
    });
  };

  const savePlan = async (id: number) => {
    try {
      await axios.put(`/api/positions/${id}`, {
        sell_target: editForm.sell_target ? parseFloat(editForm.sell_target) : null,
        stop_loss: editForm.stop_loss ? parseFloat(editForm.stop_loss) : null,
        trade_plan: editForm.trade_plan || null,
        holding_reason: editForm.holding_reason || null,
      });
      setEditingId(null);
      loadPositions();
    } catch (err) {
      console.error('Failed to save plan:', err);
      alert('保存失败');
    }
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditForm({ sell_target: '', stop_loss: '', trade_plan: '', holding_reason: '' });
  };

  const totalValue = positions.reduce((sum, p) => sum + p.market_value, 0);
  const totalProfit = positions.reduce((sum, p) => sum + p.profit_amount, 0);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>持仓管理</h1>
          <span className="date">{dayjs().format('YYYY-MM-DD')}</span>
        </div>
      </div>

      <div className="summary-cards" style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <div className="stat-card" style={{ flex: 1 }}>
          <span className="stat-value">{positions.length}</span>
          <span className="stat-label">持仓数量</span>
        </div>
        <div className="stat-card" style={{ flex: 1 }}>
          <span className="stat-value">¥{totalValue.toLocaleString()}</span>
          <span className="stat-label">持仓市值</span>
        </div>
        <div className="stat-card" style={{ flex: 1 }}>
          <span className={`stat-value ${totalProfit >= 0 ? 'positive' : 'negative'}`}>
            {totalProfit >= 0 ? '+' : ''}¥{totalProfit.toLocaleString()}
          </span>
          <span className="stat-label">总盈亏</span>
        </div>
      </div>

      {loading ? (
        <div className="loading">加载中...</div>
      ) : positions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📦</div>
          <div className="empty-text">暂无持仓</div>
        </div>
      ) : (
        <div className="positions-grid">
          {positions.map((pos) => (
            <div key={pos.id} className="position-card">
              <div className="position-header">
                <div className="stock-info">
                  <span className="stock-name">{pos.stock_name}</span>
                  <span className="stock-code">{pos.stock_code}</span>
                </div>
                <span className={`profit-tag ${pos.profit_ratio >= 0 ? 'profit' : 'loss'}`}>
                  {pos.profit_ratio >= 0 ? '+' : ''}{pos.profit_ratio.toFixed(2)}%
                </span>
              </div>

              <div className="position-details">
                <div className="detail-row">
                  <span className="detail-label">持仓数量</span>
                  <span className="detail-value">{pos.quantity}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">成本价</span>
                  <span className="detail-value">¥{pos.cost_price}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">现价</span>
                  <span className="detail-value">¥{pos.current_price}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">市值</span>
                  <span className="detail-value">¥{pos.market_value.toLocaleString()}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-label">盈亏</span>
                  <span className={`detail-value ${pos.profit_amount >= 0 ? 'profit' : 'loss'}`}>
                    {pos.profit_amount >= 0 ? '+' : ''}¥{pos.profit_amount.toLocaleString()}
                  </span>
                </div>
              </div>

              <div className="position-plan">
                <div className="plan-header">
                  <h4>交易计划</h4>
                  <button className="btn-link" onClick={() => startEdit(pos)}>
                    {editingId === pos.id ? '保存' : '编辑'}
                  </button>
                </div>

                {editingId === pos.id ? (
                  <div className="plan-form">
                    <div className="form-row">
                      <label>卖出目标价</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editForm.sell_target}
                        onChange={(e) => setEditForm({ ...editForm, sell_target: e.target.value })}
                        placeholder="达到此价卖出"
                      />
                    </div>
                    <div className="form-row">
                      <label>止损价</label>
                      <input
                        type="number"
                        step="0.01"
                        value={editForm.stop_loss}
                        onChange={(e) => setEditForm({ ...editForm, stop_loss: e.target.value })}
                        placeholder="跌破此价止损"
                      />
                    </div>
                    <div className="form-row">
                      <label>持仓理由</label>
                      <textarea
                        value={editForm.holding_reason}
                        onChange={(e) => setEditForm({ ...editForm, holding_reason: e.target.value })}
                        placeholder="为什么持有..."
                        rows={2}
                      />
                    </div>
                    <div className="form-row">
                      <label>交易计划</label>
                      <textarea
                        value={editForm.trade_plan}
                        onChange={(e) => setEditForm({ ...editForm, trade_plan: e.target.value })}
                        placeholder="卖出策略..."
                        rows={2}
                      />
                    </div>
                    <div className="form-actions">
                      <button className="btn" onClick={cancelEdit}>取消</button>
                      <button className="btn btn-primary" onClick={() => savePlan(pos.id)}>保存</button>
                    </div>
                  </div>
                ) : (
                  <div className="plan-display">
                    {pos.sell_target && (
                      <div className="plan-item">
                        <span className="plan-label">卖出目标:</span>
                        <span className="plan-value">¥{pos.sell_target}</span>
                      </div>
                    )}
                    {pos.stop_loss && (
                      <div className="plan-item">
                        <span className="plan-label">止损:</span>
                        <span className="plan-value loss">¥{pos.stop_loss}</span>
                      </div>
                    )}
                    {pos.holding_reason && (
                      <div className="plan-item">
                        <span className="plan-label">持仓理由:</span>
                        <span className="plan-value">{pos.holding_reason}</span>
                      </div>
                    )}
                    {pos.trade_plan && (
                      <div className="plan-item">
                        <span className="plan-label">交易计划:</span>
                        <span className="plan-value">{pos.trade_plan}</span>
                      </div>
                    )}
                    {!pos.sell_target && !pos.stop_loss && !pos.holding_reason && !pos.trade_plan && (
                      <div className="plan-empty">点击编辑添加交易计划</div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
