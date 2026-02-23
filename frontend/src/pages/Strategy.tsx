import { useState, useEffect } from 'react';
import axios from 'axios';

interface Strategy {
  id: number;
  name: string;
  description?: string;
  stock_selection_logic?: string;
  watch_signals?: string;
  entry_condition?: string;
  exit_condition?: string;
  position_condition?: string;
  min_turnover_rate?: number;
  max_turnover_rate?: number;
  min_volume_ratio?: number;
  max_volume_ratio?: number;
  min_market_cap?: number;
  max_market_cap?: number;
  min_price?: number;
  max_price?: number;
  limit_up_days?: number;
  min_amplitude?: number;
  max_amplitude?: number;
  ma_days?: string;
  volume_ma_days?: number;
  take_profit_1?: number;
  take_profit_2?: number;
  trailing_stop?: number;
  max_daily_loss?: number;
  max_positions?: number;
  min_single_position?: number;
  max_single_position?: number;
  win_rate_target?: number;
  profit_factor_target?: number;
  max_drawdown_target?: number;
  stop_loss: number;
  position_size: number;
  is_active: boolean;
  iteration_history?: string;
  created_at: string;
  updated_at: string;
}

interface StrategyForm {
  name: string;
  description: string;
  stock_selection_logic: string;
  watch_signals: string;
  entry_condition: string;
  exit_condition: string;
  position_condition: string;
  min_turnover_rate?: number;
  max_turnover_rate?: number;
  min_volume_ratio?: number;
  max_volume_ratio?: number;
  min_market_cap?: number;
  max_market_cap?: number;
  min_price?: number;
  max_price?: number;
  limit_up_days?: number;
  min_amplitude?: number;
  max_amplitude?: number;
  ma_days?: string;
  volume_ma_days?: number;
  take_profit_1?: number;
  take_profit_2?: number;
  trailing_stop?: number;
  max_daily_loss?: number;
  max_positions?: number;
  min_single_position?: number;
  max_single_position?: number;
  win_rate_target?: number;
  profit_factor_target?: number;
  max_drawdown_target?: number;
  stop_loss: number;
  position_size: number;
  is_active?: boolean;
  iteration_history?: string;
}

export default function Strategy() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterActive, setFilterActive] = useState<boolean | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null);
  const [formData, setFormData] = useState<StrategyForm>({
    name: '',
    description: '',
    stock_selection_logic: '',
    watch_signals: '',
    entry_condition: '',
    exit_condition: '',
    position_condition: '',
    min_turnover_rate: undefined,
    max_turnover_rate: undefined,
    min_volume_ratio: undefined,
    max_volume_ratio: undefined,
    min_market_cap: undefined,
    max_market_cap: undefined,
    min_price: undefined,
    max_price: undefined,
    limit_up_days: undefined,
    min_amplitude: undefined,
    max_amplitude: undefined,
    ma_days: '',
    volume_ma_days: undefined,
    max_positions: 4,
    min_single_position: 10,
    max_single_position: 30,
    win_rate_target: undefined,
    profit_factor_target: undefined,
    max_drawdown_target: undefined,
    stop_loss: 7,
    position_size: 20,
    is_active: true,
    iteration_history: '',
  });

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const res = await axios.get('/api/strategies');
      setStrategies(res.data);
    } catch (err) {
      console.error('Failed to fetch strategies:', err);
    }
  };

  const filteredStrategies = strategies.filter(s => {
    const matchesSearch = !searchTerm || 
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      s.stock_selection_logic?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesActive = filterActive === null || s.is_active === filterActive;
    return matchesSearch && matchesActive;
  });

  const handleToggleActive = async (strategy: Strategy) => {
    try {
      await axios.put(`/api/strategies/${strategy.id}`, { is_active: !strategy.is_active });
      fetchStrategies();
    } catch (err) {
      console.error('Failed to toggle strategy status:', err);
    }
  };

  const handleClone = (strategy: Strategy) => {
    setFormData({
      name: `${strategy.name} (副本)`,
      description: strategy.description || '',
      stock_selection_logic: strategy.stock_selection_logic || '',
      watch_signals: strategy.watch_signals || '',
      entry_condition: strategy.entry_condition || '',
      exit_condition: strategy.exit_condition || '',
      position_condition: strategy.position_condition || '',
      min_turnover_rate: strategy.min_turnover_rate,
      max_turnover_rate: strategy.max_turnover_rate,
      min_volume_ratio: strategy.min_volume_ratio,
      max_volume_ratio: strategy.max_volume_ratio,
      min_market_cap: strategy.min_market_cap,
      max_market_cap: strategy.max_market_cap,
      min_price: strategy.min_price,
      max_price: strategy.max_price,
      limit_up_days: strategy.limit_up_days,
      min_amplitude: strategy.min_amplitude,
      max_amplitude: strategy.max_amplitude,
      ma_days: strategy.ma_days || '',
      volume_ma_days: strategy.volume_ma_days,
      take_profit_1: strategy.take_profit_1,
      take_profit_2: strategy.take_profit_2,
      trailing_stop: strategy.trailing_stop,
      max_daily_loss: strategy.max_daily_loss,
      max_positions: strategy.max_positions,
      min_single_position: strategy.min_single_position,
      max_single_position: strategy.max_single_position,
      win_rate_target: strategy.win_rate_target,
      profit_factor_target: strategy.profit_factor_target,
      max_drawdown_target: strategy.max_drawdown_target,
      stop_loss: strategy.stop_loss,
      position_size: strategy.position_size,
    });
    setEditingStrategy(null);
    setShowModal(true);
  };

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  const openCreateModal = () => {
    setEditingStrategy(null);
    setFormData({
      name: '',
      description: '',
      stock_selection_logic: '',
      watch_signals: '',
      entry_condition: '',
      exit_condition: '',
      position_condition: '',
      min_turnover_rate: undefined,
      max_turnover_rate: undefined,
      min_volume_ratio: undefined,
      max_volume_ratio: undefined,
      min_market_cap: undefined,
      max_market_cap: undefined,
      min_price: undefined,
      max_price: undefined,
      limit_up_days: undefined,
      min_amplitude: undefined,
      max_amplitude: undefined,
      ma_days: '',
      volume_ma_days: undefined,
      take_profit_1: 7,
      take_profit_2: 15,
      trailing_stop: 5,
      max_daily_loss: -5,
      max_positions: 3,
      min_single_position: 10,
      max_single_position: 25,
      win_rate_target: undefined,
      profit_factor_target: undefined,
      max_drawdown_target: undefined,
      stop_loss: 6,
      position_size: 20,
      is_active: true,
      iteration_history: '',
    });
    setShowModal(true);
  };

  const openEditModal = (strategy: Strategy) => {
    setEditingStrategy(strategy);
    setFormData({
      name: strategy.name,
      description: strategy.description || '',
      stock_selection_logic: strategy.stock_selection_logic || '',
      watch_signals: strategy.watch_signals || '',
      entry_condition: strategy.entry_condition || '',
      exit_condition: strategy.exit_condition || '',
      position_condition: strategy.position_condition || '',
      min_turnover_rate: strategy.min_turnover_rate,
      max_turnover_rate: strategy.max_turnover_rate,
      min_volume_ratio: strategy.min_volume_ratio,
      max_volume_ratio: strategy.max_volume_ratio,
      min_market_cap: strategy.min_market_cap,
      max_market_cap: strategy.max_market_cap,
      min_price: strategy.min_price,
      max_price: strategy.max_price,
      limit_up_days: strategy.limit_up_days,
      min_amplitude: strategy.min_amplitude,
      max_amplitude: strategy.max_amplitude,
      ma_days: strategy.ma_days || '',
      volume_ma_days: strategy.volume_ma_days,
      take_profit_1: strategy.take_profit_1,
      take_profit_2: strategy.take_profit_2,
      trailing_stop: strategy.trailing_stop,
      max_daily_loss: strategy.max_daily_loss,
      max_positions: strategy.max_positions,
      min_single_position: strategy.min_single_position,
      max_single_position: strategy.max_single_position,
      win_rate_target: strategy.win_rate_target,
      profit_factor_target: strategy.profit_factor_target,
      max_drawdown_target: strategy.max_drawdown_target,
      stop_loss: strategy.stop_loss,
      position_size: strategy.position_size,
      is_active: strategy.is_active,
      iteration_history: strategy.iteration_history || '',
    });
    setShowModal(true);
  };

  const handleSubmit = async () => {
    try {
      if (editingStrategy) {
        await axios.put(`/api/strategies/${editingStrategy.id}`, formData);
      } else {
        await axios.post('/api/strategies', formData);
      }
      fetchStrategies();
      setShowModal(false);
    } catch (err) {
      console.error('Failed to save strategy:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('确定删除该策略?')) return;
    try {
      await axios.delete(`/api/strategies/${id}`);
      fetchStrategies();
    } catch (err) {
      console.error('Failed to delete strategy:', err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>策略管理</h1>
        <div className="header-actions">
          <button className="btn btn-primary" onClick={openCreateModal}>
            + 创建策略
          </button>
        </div>
      </div>

      <div className="filter-bar">
        <input
          type="text"
          placeholder="搜索策略名称、描述、选股思路..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <div className="filter-buttons">
          <button
            className={`filter-btn ${filterActive === null ? 'active' : ''}`}
            onClick={() => setFilterActive(null)}
          >
            全部
          </button>
          <button
            className={`filter-btn ${filterActive === true ? 'active' : ''}`}
            onClick={() => setFilterActive(true)}
          >
            启用中
          </button>
          <button
            className={`filter-btn ${filterActive === false ? 'active' : ''}`}
            onClick={() => setFilterActive(false)}
          >
            已停用
          </button>
        </div>
      </div>

      <div className="strategy-list">
        {filteredStrategies.length === 0 ? (
          <div className="empty-state">
            <p>{searchTerm || filterActive !== null ? '没有匹配的策略' : '暂无策略，请创建或从模板添加'}</p>
          </div>
        ) : (
          filteredStrategies.map((strategy) => (
            <div
              key={strategy.id}
              className={`strategy-card ${expandedId === strategy.id ? 'expanded' : ''} ${!strategy.is_active ? 'inactive' : ''}`}
            >
              <div className="strategy-header" onClick={() => toggleExpand(strategy.id)}>
                <div className="strategy-info">
                  <span className="strategy-name">{strategy.name}</span>
                  <span className={`status-badge ${strategy.is_active ? 'active' : 'inactive'}`}>
                    {strategy.is_active ? '启用' : '停用'}
                  </span>
                  <span className="strategy-meta">
                    {strategy.description || '暂无描述'} | 仓位: {strategy.position_size}% | 止损: {strategy.stop_loss}%
                  </span>
                  {strategy.watch_signals && (
                    <div className="strategy-signals">
                      {strategy.watch_signals.split(',').map((signal, i) => (
                        <span key={i} className="signal-tag">{signal.trim()}</span>
                      ))}
                    </div>
                  )}
                </div>
                <span className="expand-icon">{expandedId === strategy.id ? '−' : '+'}</span>
              </div>

              {expandedId === strategy.id && (
                <div className="strategy-content">
                  {strategy.stock_selection_logic && (
                    <div className="strategy-section">
                      <h4>选股思路</h4>
                      <p className="strategy-text">{strategy.stock_selection_logic}</p>
                    </div>
                  )}
                  {strategy.entry_condition && (
                    <div className="strategy-section">
                      <h4>买入条件</h4>
                      <p className="strategy-text">{strategy.entry_condition}</p>
                    </div>
                  )}
                  {strategy.exit_condition && (
                    <div className="strategy-section">
                      <h4>卖出条件</h4>
                      <p className="strategy-text">{strategy.exit_condition}</p>
                    </div>
                  )}
                  {strategy.position_condition && (
                    <div className="strategy-section">
                      <h4>持仓条件</h4>
                      <p className="strategy-text">{strategy.position_condition}</p>
                    </div>
                  )}
                  <div className="strategy-section">
                    <h4>风控参数</h4>
                    <p className="strategy-text">
                      止损: {strategy.stop_loss}% | 
                      仓位: {strategy.position_size}% | 
                      止盈1: {strategy.take_profit_1 || '-'}% | 
                      止盈2: {strategy.take_profit_2 || '-'}% | 
                      移动止损: {strategy.trailing_stop || '-'}% | 
                      单日最大亏损: {strategy.max_daily_loss || '-'}%
                    </p>
                  </div>
                  {strategy.iteration_history && (
                    <div className="strategy-section">
                      <h4>迭代历史</h4>
                      <p className="strategy-text">{strategy.iteration_history}</p>
                    </div>
                  )}
                  <div className="strategy-actions">
                    <button className="action-btn primary" onClick={() => openEditModal(strategy)}>编辑</button>
                    <button className="action-btn" onClick={() => handleClone(strategy)}>复制</button>
                    <button className={`action-btn ${strategy.is_active ? 'warning' : 'success'}`} onClick={() => handleToggleActive(strategy)}>
                      {strategy.is_active ? '停用' : '启用'}
                    </button>
                    <button className="action-btn danger" onClick={() => handleDelete(strategy.id)}>删除</button>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingStrategy ? '编辑策略' : '新建策略'}</h2>
              <button onClick={() => setShowModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-row">
                <div className="form-group">
                  <label>策略名称 *</label>
                  <input
                    value={formData.name}
                    onChange={e => setFormData({...formData, name: e.target.value})}
                    placeholder="如: 龙头战法"
                  />
                </div>
                <div className="form-group">
                  <label>描述</label>
                  <input
                    value={formData.description}
                    onChange={e => setFormData({...formData, description: e.target.value})}
                    placeholder="如: 市场龙头/空间板"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>选股思路</label>
                <textarea
                  value={formData.stock_selection_logic}
                  onChange={e => setFormData({...formData, stock_selection_logic: e.target.value})}
                  placeholder="板块首板涨停后第二天的二板确认..."
                  rows={2}
                />
              </div>
              <div className="form-group">
                <label>关注信号</label>
                <input
                  value={formData.watch_signals}
                  onChange={e => setFormData({...formData, watch_signals: e.target.value})}
                  placeholder="🔥二板,🐉龙回头,📈板块强度"
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>买入条件</label>
                  <textarea
                    value={formData.entry_condition}
                    onChange={e => setFormData({...formData, entry_condition: e.target.value})}
                    placeholder="二板开盘高开大于5%且放量"
                    rows={2}
                  />
                </div>
                <div className="form-group">
                  <label>卖出条件</label>
                  <textarea
                    value={formData.exit_condition}
                    onChange={e => setFormData({...formData, exit_condition: e.target.value})}
                    placeholder="跌破5日均线或跌幅超过7%"
                    rows={2}
                  />
                </div>
              </div>
              <div className="form-group">
                <label>持仓条件</label>
                <textarea
                  value={formData.position_condition}
                  onChange={e => setFormData({...formData, position_condition: e.target.value})}
                  placeholder="连续涨停后炸板卖出"
                  rows={2}
                />
              </div>
              <div className="form-section-title">量化选股条件</div>
              <div className="form-row">
                <div className="form-group">
                  <label>换手率 (%)</label>
                  <div className="range-input">
                    <input
                      type="number"
                      placeholder="最小"
                      value={formData.min_turnover_rate || ''}
                      onChange={e => setFormData({...formData, min_turnover_rate: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                    <span>-</span>
                    <input
                      type="number"
                      placeholder="最大"
                      value={formData.max_turnover_rate || ''}
                      onChange={e => setFormData({...formData, max_turnover_rate: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>量比</label>
                  <div className="range-input">
                    <input
                      type="number"
                      placeholder="最小"
                      value={formData.min_volume_ratio || ''}
                      onChange={e => setFormData({...formData, min_volume_ratio: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                    <span>-</span>
                    <input
                      type="number"
                      placeholder="最大"
                      value={formData.max_volume_ratio || ''}
                      onChange={e => setFormData({...formData, max_volume_ratio: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                  </div>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>股价 (元)</label>
                  <div className="range-input">
                    <input
                      type="number"
                      placeholder="最低"
                      value={formData.min_price || ''}
                      onChange={e => setFormData({...formData, min_price: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                    <span>-</span>
                    <input
                      type="number"
                      placeholder="最高"
                      value={formData.max_price || ''}
                      onChange={e => setFormData({...formData, max_price: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>涨停天数</label>
                  <input
                    type="number"
                    value={formData.limit_up_days || ''}
                    onChange={e => setFormData({...formData, limit_up_days: e.target.value ? parseInt(e.target.value) : undefined})}
                    placeholder="如: 1-2"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>振幅 (%)</label>
                  <div className="range-input">
                    <input
                      type="number"
                      placeholder="最小"
                      value={formData.min_amplitude || ''}
                      onChange={e => setFormData({...formData, min_amplitude: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                    <span>-</span>
                    <input
                      type="number"
                      placeholder="最大"
                      value={formData.max_amplitude || ''}
                      onChange={e => setFormData({...formData, max_amplitude: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>均线天数</label>
                  <input
                    value={formData.ma_days || ''}
                    onChange={e => setFormData({...formData, ma_days: e.target.value})}
                    placeholder="如: 5,10,20"
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>量能均线天数</label>
                  <input
                    type="number"
                    value={formData.volume_ma_days || ''}
                    onChange={e => setFormData({...formData, volume_ma_days: e.target.value ? parseInt(e.target.value) : undefined})}
                    placeholder="如: 5"
                  />
                </div>
              </div>
              <div className="form-section-title">仓位管理</div>
              <div className="form-row">
                <div className="form-group">
                  <label>最大持仓数</label>
                  <input
                    type="number"
                    value={formData.max_positions || ''}
                    onChange={e => setFormData({...formData, max_positions: e.target.value ? parseInt(e.target.value) : undefined})}
                    min={1}
                    max={10}
                  />
                </div>
                <div className="form-group">
                  <label>单笔仓位 (%)</label>
                  <div className="range-input">
                    <input
                      type="number"
                      placeholder="最小"
                      value={formData.min_single_position || ''}
                      onChange={e => setFormData({...formData, min_single_position: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                    <span>-</span>
                    <input
                      type="number"
                      placeholder="最大"
                      value={formData.max_single_position || ''}
                      onChange={e => setFormData({...formData, max_single_position: e.target.value ? parseFloat(e.target.value) : undefined})}
                    />
                  </div>
                </div>
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>止盈1 (%)</label>
                  <input
                    type="number"
                    value={formData.take_profit_1 || ''}
                    onChange={e => setFormData({...formData, take_profit_1: e.target.value ? parseFloat(e.target.value) : undefined})}
                    placeholder="如: 7"
                  />
                </div>
                <div className="form-group">
                  <label>止盈2 (%)</label>
                  <input
                    type="number"
                    value={formData.take_profit_2 || ''}
                    onChange={e => setFormData({...formData, take_profit_2: e.target.value ? parseFloat(e.target.value) : undefined})}
                    placeholder="如: 15"
                  />
                </div>
                <div className="form-group">
                  <label>移动止损 (%)</label>
                  <input
                    type="number"
                    value={formData.trailing_stop || ''}
                    onChange={e => setFormData({...formData, trailing_stop: e.target.value ? parseFloat(e.target.value) : undefined})}
                    placeholder="如: 5"
                  />
                </div>
                <div className="form-group">
                  <label>单日最大亏损 (%)</label>
                  <input
                    type="number"
                    value={formData.max_daily_loss || ''}
                    onChange={e => setFormData({...formData, max_daily_loss: e.target.value ? parseFloat(e.target.value) : undefined})}
                    placeholder="如: -5"
                  />
                </div>
              </div>
              <div className="form-section-title">效果目标</div>
              <div className="form-row">
                <div className="form-group">
                  <label>目标胜率 (%)</label>
                  <input
                    type="number"
                    value={formData.win_rate_target || ''}
                    onChange={e => setFormData({...formData, win_rate_target: e.target.value ? parseFloat(e.target.value) : undefined})}
                    placeholder="如: 60"
                  />
                </div>
                <div className="form-group">
                  <label>目标盈亏比</label>
                  <input
                    type="number"
                    value={formData.profit_factor_target || ''}
                    onChange={e => setFormData({...formData, profit_factor_target: e.target.value ? parseFloat(e.target.value) : undefined})}
                    placeholder="如: 1.5"
                  />
                </div>
                <div className="form-group">
                  <label>最大回撤 (%)</label>
                  <input
                    type="number"
                    value={formData.max_drawdown_target || ''}
                    onChange={e => setFormData({...formData, max_drawdown_target: e.target.value ? parseFloat(e.target.value) : undefined})}
                    placeholder="如: 15"
                  />
                </div>
              </div>
              <div className="form-group">
                <label>迭代历史</label>
                <textarea
                  value={formData.iteration_history}
                  onChange={e => setFormData({...formData, iteration_history: e.target.value})}
                  placeholder="策略执行后的总结和反思，如: 2024-01: 首板成功率偏低，增加资金面过滤条件..."
                  rows={3}
                />
              </div>
              <div className="form-row">
                <div className="form-group">
                  <label>止损比例 (%)</label>
                  <input
                    type="number"
                    value={formData.stop_loss}
                    onChange={e => setFormData({...formData, stop_loss: parseFloat(e.target.value)})}
                    min={1}
                    max={20}
                  />
                </div>
                <div className="form-group">
                  <label>仓位比例 (%)</label>
                  <input
                    type="number"
                    value={formData.position_size}
                    onChange={e => setFormData({...formData, position_size: parseFloat(e.target.value)})}
                    min={5}
                    max={100}
                  />
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>取消</button>
              <button className="btn btn-primary" onClick={handleSubmit}>保存</button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
