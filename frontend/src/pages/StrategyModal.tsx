import { useState } from 'react';
import axios from 'axios';

interface StrategyParam {
  name: string;
  label: string;
  default: number;
  min?: number;
  max?: number;
  step?: number;
  type?: string;
}

interface BacktestStrategy {
  id?: number;
  name: string;
  description?: string;
  code: string;
  params_definition?: StrategyParam[];
}

interface StrategyModalProps {
  strategy: BacktestStrategy | null;
  onClose: () => void;
  onSave: () => void;
}

const DEFAULT_CODE = `from backtesting import Strategy
import pandas as pd


class MyStrategy(Strategy):
    """自定义策略 - 请修改以下参数"""

    # 在此定义策略参数
    n1 = 10
    n2 = 20

    def init(self):
        # 在此定义指标计算
        self.sma1 = self.I(
            lambda x: pd.Series(x).rolling(self.n1).mean(),
            self.data.Close
        )
        self.sma2 = self.I(
            lambda x: pd.Series(x).rolling(self.n2).mean(),
            self.data.Close
        )

    def next(self):
        # 在此定义交易逻辑
        # self.buy() 买入
        # self.sell() 卖出
        # self.position.close() 平仓
        pass
`;

export default function StrategyModal({ strategy, onClose, onSave }: StrategyModalProps) {
  const [name, setName] = useState(strategy?.name || '');
  const [description, setDescription] = useState(strategy?.description || '');
  const [code, setCode] = useState(strategy?.code || DEFAULT_CODE);
  const [params, setParams] = useState<StrategyParam[]>(strategy?.params_definition || []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 解析代码参数
  const parseParams = async () => {
    try {
      setLoading(true);
      const res = await axios.post('/api/backtest/strategies/parse-params', { code });
      if (res.data.valid) {
        setParams(res.data.params || []);
        setError(null);
      } else {
        setError(res.data.error || '代码解析失败');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '解析失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存策略
  const handleSave = async () => {
    if (!name.trim()) {
      setError('请输入策略名称');
      return;
    }
    if (!code.trim()) {
      setError('请输入策略代码');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const data = {
        name,
        description,
        code,
        strategy_type: 'custom',
        params_definition: params,
        is_active: true,
      };

      if (strategy?.id) {
        await axios.put(`/api/backtest/strategies/${strategy.id}`, data);
      } else {
        await axios.post('/api/backtest/strategies', data);
      }

      onSave();
    } catch (err: any) {
      setError(err.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{strategy?.id ? '编辑策略' : '新建策略'}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label>策略名称 *</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="请输入策略名称"
            />
          </div>

          <div className="form-group">
            <label>策略描述</label>
            <input
              type="text"
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="请输入策略描述"
            />
          </div>

          <div className="form-group">
            <label>
              策略代码 *
              <button
                className="btn btn-sm btn-secondary"
                style={{ marginLeft: '10px' }}
                onClick={parseParams}
                disabled={loading}
              >
                解析参数
              </button>
            </label>
            <textarea
              className="code-editor"
              value={code}
              onChange={e => setCode(e.target.value)}
              placeholder="请输入策略代码 (Python)"
              rows={20}
              spellCheck={false}
            />
            <p className="hint">
              提示: 代码需要继承 backtesting.Strategy，并在类中定义策略参数
            </p>
          </div>

          {/* 参数预览 */}
          {params.length > 0 && (
            <div className="form-group">
              <label>解析到的参数</label>
              <div className="params-preview">
                {params.map((param, idx) => (
                  <div key={idx} className="param-tag">
                    {param.name}: {param.default}
                    <span className="param-type">({param.type})</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-secondary" onClick={onClose}>取消</button>
          <button className="btn btn-primary" onClick={handleSave} disabled={loading}>
            {loading ? '保存中...' : '保存'}
          </button>
        </div>
      </div>
    </div>
  );
}
