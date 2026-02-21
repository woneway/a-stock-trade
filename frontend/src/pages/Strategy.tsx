import { useState } from 'react';

interface Strategy {
  id: number;
  name: string;
  stockConditions: string[];
  buySignals: string[];
  sellSignals: string[];
  scene: string;
  winRate: number;
  useCount: number;
}

export default function Strategy() {
  const [strategies, setStrategies] = useState<Strategy[]>([
    {
      id: 1,
      name: '追涨策略',
      stockConditions: ['涨停板突破', '量能放大 >1.5倍', '板块涨幅 >3%', '流通市值 <50亿'],
      buySignals: ['首次涨停时买入', '涨停后首次打开', '回调到均线支撑'],
      sellSignals: ['-5% 止损', '破板即卖', '+8% 止盈', '板块走弱时卖出'],
      scene: '龙头股/题材股',
      winRate: 65,
      useCount: 12,
    },
    {
      id: 2,
      name: '低吸策略',
      stockConditions: ['回调到支撑位', '缩量'],
      buySignals: ['均线附近低吸'],
      sellSignals: ['-3% 止损', '+8% 止盈'],
      scene: '趋势股',
      winRate: 58,
      useCount: 8,
    },
  ]);
  const [showModal, setShowModal] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>策略</h1>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + 新建策略
        </button>
      </div>

      <div className="strategy-list">
        {strategies.map((strategy) => (
          <div
            key={strategy.id}
            className={`strategy-card ${expandedId === strategy.id ? 'expanded' : ''}`}
          >
            <div className="strategy-header" onClick={() => toggleExpand(strategy.id)}>
              <div className="strategy-info">
                <span className="strategy-name">{strategy.name}</span>
                <span className="strategy-meta">
                  适用: {strategy.scene} | 胜率: {strategy.winRate}% | 已使用: {strategy.useCount}次
                </span>
              </div>
              <span className="expand-icon">{expandedId === strategy.id ? '−' : '+'}</span>
            </div>

            {expandedId === strategy.id && (
              <div className="strategy-content">
                <div className="strategy-section">
                  <h4>选股条件</h4>
                  <ul>
                    {strategy.stockConditions.map((condition, i) => (
                      <li key={i}>{condition}</li>
                    ))}
                  </ul>
                </div>
                <div className="strategy-section">
                  <h4>买入信号</h4>
                  <ul>
                    {strategy.buySignals.map((signal, i) => (
                      <li key={i}>{signal}</li>
                    ))}
                  </ul>
                </div>
                <div className="strategy-section">
                  <h4>卖出信号</h4>
                  <ul>
                    {strategy.sellSignals.map((signal, i) => (
                      <li key={i}>{signal}</li>
                    ))}
                  </ul>
                </div>
                <div className="strategy-actions">
                  <button className="action-btn primary">编辑</button>
                  <button className="action-btn danger">删除</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>新建策略</h2>
              <button onClick={() => setShowModal(false)}>×</button>
            </div>
            <div className="form-group">
              <label>策略名称</label>
              <input placeholder="例如: 追涨策略" />
            </div>
            <div className="form-group">
              <label>选股条件 (每行一条)</label>
              <textarea rows={3} placeholder="涨停板突破&#10;量能放大 >1.5倍&#10;板块涨幅 >3%" />
            </div>
            <div className="form-group">
              <label>买入信号 (每行一条)</label>
              <textarea rows={3} placeholder="首次涨停时买入&#10;涨停后首次打开" />
            </div>
            <div className="form-group">
              <label>卖出信号 (每行一条)</label>
              <textarea rows={3} placeholder="-5% 止损&#10;+8% 止盈" />
            </div>
            <div className="form-group">
              <label>适用场景</label>
              <input placeholder="例如: 龙头股/题材股" />
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowModal(false)}>取消</button>
              <button className="btn btn-primary">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
