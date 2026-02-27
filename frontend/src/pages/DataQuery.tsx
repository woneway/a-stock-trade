import { useState, useEffect } from 'react';
import axios from 'axios';
import './DataQuery.css';

// 接口定义
interface FunctionInfo {
  name: string;
  description: string;
  params: string[];
}

const FUNCTIONS: FunctionInfo[] = [
  // 股票信息
  { name: 'get_stock_info_a_code_name', description: '股票代码名称映射', params: [] },
  { name: 'get_stock_individual_info_em', description: '个股基本信息', params: ['symbol'] },

  // 涨跌停
  { name: 'get_zt_pool_em', description: '涨停股池', params: ['date'] },
  { name: 'get_zt_pool_previous_em', description: '昨日涨停', params: ['date'] },
  { name: 'get_zt_pool_dtgc_em', description: '跌停股池', params: ['date'] },
  { name: 'get_zt_pool_zbgc_em', description: '炸板股池', params: ['date'] },

  // 龙虎榜
  { name: 'get_lhb_detail_em', description: '龙虎榜详情', params: ['start_date', 'end_date'] },
  { name: 'get_lhb_yybph_em', description: '营业部排行', params: ['symbol'] },
  { name: 'get_lhb_stock_statistic_em', description: '个股上榜统计', params: ['symbol'] },
  { name: 'get_lhb_stock_detail_em', description: '个股龙虎榜详情', params: ['symbol', 'date', 'flag'] },

  // K线
  { name: 'get_stock_zh_a_hist', description: '日K线数据', params: ['symbol', 'start_date', 'end_date', 'period', 'adjust'] },
  { name: 'get_stock_zh_a_hist_min_em', description: '分时K线', params: ['symbol', 'period', 'start_date', 'end_date'] },

  // 资金流向
  { name: 'get_market_fund_flow', description: '大盘资金流向', params: [] },
  { name: 'get_sector_fund_flow_rank', description: '板块资金流', params: ['indicator', 'sector_type'] },
  { name: 'get_individual_fund_flow_rank', description: '个股资金流排名', params: ['indicator'] },
  { name: 'get_individual_fund_flow', description: '个股资金流向', params: ['stock', 'market'] },

  // 两融
  { name: 'get_margin_sse', description: '上交所融资融券', params: ['start_date', 'end_date'] },
  { name: 'get_margin_szse', description: '深交所融资融券', params: ['date'] },
  { name: 'get_margin_account_info', description: '两融账户统计', params: [] },

  // 大宗交易
  { name: 'get_dzjy_mrmx', description: '大宗交易明细', params: ['symbol', 'start_date', 'end_date'] },
  { name: 'get_dzjy_mrtj', description: '大宗交易统计', params: ['start_date', 'end_date'] },

  // 市场情绪
  { name: 'get_market_activity_legu', description: '赚钱效应分析', params: [] },
  { name: 'get_a_high_low_statistics', description: '创新高/新低', params: ['symbol'] },
  { name: 'get_hot_rank_em', description: '股票热度排名', params: [] },
];

function DataQuery() {
  const [selectedFunc, setSelectedFunc] = useState<string>('get_zt_pool_em');
  const [params, setParams] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const currentFunc = FUNCTIONS.find(f => f.name === selectedFunc);

  // 重置参数
  useEffect(() => {
    setParams({});
    setResult(null);
    setError(null);
  }, [selectedFunc]);

  // 处理参数变化
  const handleParamChange = (key: string, value: string) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  // 调用接口
  const handleCall = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // 处理日期参数
      const processedParams: Record<string, string> = {};
      for (const [key, value] of Object.entries(params)) {
        if (value) {
          // 如果是日期字段且格式为 YYYY-MM-DD，转换为 YYYYMMDD
          if (key.includes('date') || key.includes('start_date') || key.includes('end_date')) {
            processedParams[key] = value.replace(/-/g, '');
          } else {
            processedParams[key] = value;
          }
        }
      }

      const queryString = new URLSearchParams(processedParams).toString();
      const url = queryString ? `/akshare/functions/${selectedFunc}?${queryString}` : `/akshare/functions/${selectedFunc}`;

      const response = await axios.get(url);
      setResult(response.data);
    } catch (err: any) {
      setError(err.response?.data?.error || err.message || '调用失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="data-query">
      <div className="query-header">
        <h1>🔧 AKShare 接口调试</h1>
        <p>选择接口并填写参数进行测试</p>
      </div>

      <div className="query-content">
        {/* 左侧：接口列表 */}
        <div className="func-list">
          <h3>接口列表</h3>
          <div className="func-items">
            {FUNCTIONS.map(func => (
              <div
                key={func.name}
                className={`func-item ${selectedFunc === func.name ? 'active' : ''}`}
                onClick={() => setSelectedFunc(func.name)}
              >
                <span className="func-name">{func.name}</span>
                <span className="func-desc">{func.description}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 中间：参数输入 */}
        <div className="param-panel">
          <h3>参数设置</h3>
          {currentFunc && (
            <>
              <div className="current-func">
                <code>{currentFunc.name}</code>
                <span>{currentFunc.description}</span>
              </div>

              <div className="params-form">
                {currentFunc.params.length === 0 ? (
                  <div className="no-params">该接口无需参数</div>
                ) : (
                  currentFunc.params.map(param => (
                    <div key={param} className="param-item">
                      <label>{param}</label>
                      {param.includes('date') ? (
                        <input
                          type="date"
                          value={params[param] || ''}
                          onChange={e => handleParamChange(param, e.target.value)}
                        />
                      ) : param === 'symbol' ? (
                        <input
                          type="text"
                          placeholder="如: 000001"
                          value={params[param] || ''}
                          onChange={e => handleParamChange(param, e.target.value)}
                        />
                      ) : param === 'indicator' ? (
                        <select
                          value={params[param] || '今日'}
                          onChange={e => handleParamChange(param, e.target.value)}
                        >
                          <option value="今日">今日</option>
                          <option value="5日">5日</option>
                          <option value="10日">10日</option>
                          <option value="20日">20日</option>
                        </select>
                      ) : param === 'sector_type' ? (
                        <select
                          value={params[param] || '行业资金流'}
                          onChange={e => handleParamChange(param, e.target.value)}
                        >
                          <option value="行业资金流">行业资金流</option>
                          <option value="概念资金流">概念资金流</option>
                        </select>
                      ) : param === 'symbol' && currentFunc.name.includes('lhb') ? (
                        <select
                          value={params[param] || '近一月'}
                          onChange={e => handleParamChange(param, e.target.value)}
                        >
                          <option value="近一周">近一周</option>
                          <option value="近一月">近一月</option>
                          <option value="近三月">近三月</option>
                          <option value="近六月">近六月</option>
                        </select>
                      ) : param === 'period' ? (
                        <select
                          value={params[param] || '5'}
                          onChange={e => handleParamChange(param, e.target.value)}
                        >
                          <option value="5">5分钟</option>
                          <option value="15">15分钟</option>
                          <option value="30">30分钟</option>
                          <option value="60">60分钟</option>
                        </select>
                      ) : param === 'adjust' ? (
                        <select
                          value={params[param] || ''}
                          onChange={e => handleParamChange(param, e.target.value)}
                        >
                          <option value="">不复权</option>
                          <option value="qfq">前复权</option>
                          <option value="hfq">后复权</option>
                        </select>
                      ) : (
                        <input
                          type="text"
                          value={params[param] || ''}
                          onChange={e => handleParamChange(param, e.target.value)}
                        />
                      )}
                    </div>
                  ))
                )}

                <button
                  className="call-btn"
                  onClick={handleCall}
                  disabled={loading}
                >
                  {loading ? '调用中...' : '调用接口'}
                </button>
              </div>
            </>
          )}
        </div>

        {/* 右侧：结果展示 */}
        <div className="result-panel">
          <h3>返回结果</h3>
          {loading && <div className="loading">加载中...</div>}
          {error && <div className="error">{error}</div>}
          {result && (
            <pre className="result-content">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
          {!loading && !error && !result && (
            <div className="empty-result">点击"调用接口"查看结果</div>
          )}
        </div>
      </div>
    </div>
  );
}

export default DataQuery;
