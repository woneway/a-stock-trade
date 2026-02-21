import { useState } from 'react';

interface StrategyParam {
  name: string;
  value: number | string;
  unit?: string;
  min?: number;
  max?: number;
  step?: number;
}

interface Strategy {
  id: number;
  name: string;
  scene: string;
  winRate: number;
  useCount: number;
  params: StrategyParam[];
  buySignals: { condition: string; enabled: boolean }[];
  sellSignals: { condition: string; value?: number; enabled: boolean }[];
}

const TEMPLATES: Omit<Strategy, 'id' | 'winRate' | 'useCount'>[] = [
  {
    name: '首板战法',
    scene: '龙头启动/题材爆发',
    params: [
      { name: '流通市值上限', value: 50, unit: '亿', min: 10, max: 200, step: 10 },
      { name: '涨停时间限制', value: 14, unit: '点前', min: 9, max: 15 },
      { name: '量能倍数', value: 1.5, step: 0.1 },
      { name: '板块涨幅', value: 3, unit: '%', min: 1, max: 10 },
    ],
    buySignals: [
      { condition: '首次涨停排队', enabled: true },
      { condition: '涨停后首次开板', enabled: true },
      { condition: '回封时买入', enabled: false },
    ],
    sellSignals: [
      { condition: '止损', value: -5, enabled: true },
      { condition: '破板卖出', enabled: true },
      { condition: '止盈', value: 8, enabled: true },
      { condition: '板块走弱卖出', enabled: true },
    ],
  },
  {
    name: '龙头战法',
    scene: '市场龙头/空间板',
    params: [
      { name: '最高板数', value: 5, unit: '板', min: 3, max: 10 },
      { name: '换手率要求', value: 50, unit: '%', min: 30, max: 80 },
      { name: '量能要求', value: 80, unit: '%', min: 50, max: 100 },
    ],
    buySignals: [
      { condition: '分歧转一致', enabled: true },
      { condition: '分歧低吸', enabled: true },
      { condition: '加速缩量板', enabled: false },
    ],
    sellSignals: [
      { condition: '止损', value: -7, enabled: true },
      { condition: '放巨量收阴', enabled: true },
      { condition: '止盈', value: 15, enabled: true },
      { condition: '龙头首阴', enabled: true },
    ],
  },
  {
    name: '反包战法',
    scene: '涨停次日调整',
    params: [
      { name: '反包时间', value: 2, unit: '日内', min: 1, max: 3 },
      { name: '回调幅度', value: -10, unit: '%以内', min: -20, max: -5 },
      { name: '成交量要求', value: 60, unit: '%', min: 30, max: 80 },
    ],
    buySignals: [
      { condition: '5日线附近低吸', enabled: true },
      { condition: '反包大阳线买入', enabled: true },
      { condition: '水下低吸', enabled: false },
    ],
    sellSignals: [
      { condition: '止损', value: -5, enabled: true },
      { condition: '反包失败卖出', enabled: true },
      { condition: '止盈', value: 10, enabled: true },
    ],
  },
  {
    name: '趋势低吸',
    scene: '趋势股回调',
    params: [
      { name: '均线周期', value: 20, unit: '日线', min: 5, max: 60 },
      { name: '回调幅度', value: -15, unit: '%以内', min: -30, max: -5 },
      { name: '成交量萎缩', value: 50, unit: '%', min: 30, max: 70 },
    ],
    buySignals: [
      { condition: '回踩20日线', enabled: true },
      { condition: '止跌K线出现', enabled: true },
      { condition: '缩量十字星', enabled: true },
    ],
    sellSignals: [
      { condition: '止损', value: -8, enabled: true },
      { condition: '跌破趋势线', enabled: true },
      { condition: '止盈', value: 20, enabled: true },
    ],
  },
  {
    name: '空仓等待',
    scene: '退潮期/风险期',
    params: [
      { name: '跌停板数', value: 20, unit: '家以上空仓', min: 10, max: 50 },
      { name: '空间板高度', value: 3, unit: '板以下', min: 1, max: 5 },
    ],
    buySignals: [
      { condition: '不做', enabled: true },
    ],
    sellSignals: [
      { condition: '强制空仓', enabled: true },
    ],
  },
];

export default function Strategy() {
  const [strategies, setStrategies] = useState<Strategy[]>([
    {
      id: 1,
      name: '首板战法',
      scene: '龙头启动/题材爆发',
      winRate: 65,
      useCount: 12,
      params: [
        { name: '流通市值上限', value: 50, unit: '亿', min: 10, max: 200, step: 10 },
        { name: '涨停时间限制', value: 14, unit: '点前', min: 9, max: 15 },
        { name: '量能倍数', value: 1.5, step: 0.1 },
        { name: '板块涨幅', value: 3, unit: '%', min: 1, max: 10 },
      ],
      buySignals: [
        { condition: '首次涨停排队', enabled: true },
        { condition: '涨停后首次开板', enabled: true },
        { condition: '回封时买入', enabled: false },
      ],
      sellSignals: [
        { condition: '止损', value: -5, enabled: true },
        { condition: '破板卖出', enabled: true },
        { condition: '止盈', value: 8, enabled: true },
        { condition: '板块走弱卖出', enabled: true },
      ],
    },
    {
      id: 2,
      name: '趋势低吸',
      scene: '趋势股回调',
      winRate: 58,
      useCount: 8,
      params: [
        { name: '均线周期', value: 20, unit: '日线', min: 5, max: 60 },
        { name: '回调幅度', value: -15, unit: '%以内', min: -30, max: -5 },
        { name: '成交量萎缩', value: 50, unit: '%', min: 30, max: 70 },
      ],
      buySignals: [
        { condition: '回踩20日线', enabled: true },
        { condition: '止跌K线出现', enabled: true },
        { condition: '缩量十字星', enabled: true },
      ],
      sellSignals: [
        { condition: '止损', value: -8, enabled: true },
        { condition: '跌破趋势线', enabled: true },
        { condition: '止盈', value: 20, enabled: true },
      ],
    },
  ]);
  const [showModal, setShowModal] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const addTemplate = (template: typeof TEMPLATES[0]) => {
    const newStrategy: Strategy = {
      ...template,
      id: Date.now(),
      winRate: Math.floor(Math.random() * 20) + 50,
      useCount: 0,
    };
    setStrategies([...strategies, newStrategy]);
    setShowTemplateModal(false);
  };

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>策略</h1>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => setShowTemplateModal(true)}>
            📋 从模板创建
          </button>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            + 自定义策略
          </button>
        </div>
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
                  <h4>策略参数</h4>
                  <div className="params-grid">
                    {strategy.params.map((param, i) => (
                      <div key={i} className="param-item">
                        <span className="param-name">{param.name}</span>
                        <div className="param-value">
                          <input
                            type="number"
                            value={param.value as number}
                            min={param.min}
                            max={param.max}
                            step={param.step || 1}
                            readOnly
                          />
                          {param.unit && <span className="param-unit">{param.unit}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="strategy-section">
                  <h4>买入信号</h4>
                  <div className="signals-list">
                    {strategy.buySignals.map((signal, i) => (
                      <div key={i} className={`signal-item ${signal.enabled ? 'enabled' : ''}`}>
                        <span className="signal-check">{signal.enabled ? '✓' : '○'}</span>
                        <span>{signal.condition}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="strategy-section">
                  <h4>卖出信号</h4>
                  <div className="signals-list">
                    {strategy.sellSignals.map((signal, i) => (
                      <div key={i} className={`signal-item ${signal.enabled ? 'enabled' : ''}`}>
                        <span className="signal-check">{signal.enabled ? '✓' : '○'}</span>
                        <span>
                          {signal.condition}
                          {signal.value !== undefined && (
                            <span className="signal-value">
                              {signal.value > 0 ? '+' : ''}{signal.value}%
                            </span>
                          )}
                        </span>
                      </div>
                    ))}
                  </div>
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

      {showTemplateModal && (
        <div className="modal-overlay" onClick={() => setShowTemplateModal(false)}>
          <div className="modal modal-lg" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>选择策略模板</h2>
              <button onClick={() => setShowTemplateModal(false)}>×</button>
            </div>
            <div className="template-grid">
              {TEMPLATES.map((template, index) => (
                <div key={index} className="template-card" onClick={() => addTemplate(template)}>
                  <div className="template-name">{template.name}</div>
                  <div className="template-scene">{template.scene}</div>
                  <div className="template-params">
                    {template.params.slice(0, 2).map((p, i) => (
                      <span key={i}>{p.name}: {p.value}{p.unit}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
