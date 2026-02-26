import { useState, useEffect } from 'react';
import axios from 'axios';
import './DataQuery.css';

interface AkshareFunction {
  name: string;
  description: string;
  category: string;
  params: Array<{
    name: string;
    default?: string;
    description?: string;
    required?: boolean;
    type?: string;
  }>;
}

interface QueryResult {
  data: any[];
  columns?: string[];
  total?: number;
  function?: string;
}

interface SyncStatus {
  stock_basic_count: number;
  stock_quote_count: number;
  stock_kline_count: number;
}

export default function DataQuery() {
  const [activeTab, setActiveTab] = useState<'query' | 'sync'>('query');

  // 查询相关状态
  const [categories, setCategories] = useState<Record<string, { name: string; description: string }[]>>({});
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedFunction, setSelectedFunction] = useState<string>('');
  const [functionDetail, setFunctionDetail] = useState<AkshareFunction | null>(null);
  const [params, setParams] = useState<Record<string, string>>({});
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);

  // 同步相关状态
  const [syncLoading, setSyncLoading] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string>('');
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [syncForm, setSyncForm] = useState({
    startDate: '',
    endDate: '',
    stockCodes: '',
  });

  useEffect(() => {
    fetchCategories();
    fetchSyncStatus();
  }, []);

  const fetchCategories = async () => {
    try {
      const res = await axios.get('/api/data/akshare/categories');
      setCategories(res.data);
      // 默认选择第一个分类
      const firstCat = Object.keys(res.data)[0];
      if (firstCat) {
        setSelectedCategory(firstCat);
        if (res.data[firstCat].length > 0) {
          setSelectedFunction(res.data[firstCat][0].name);
        }
      }
    } catch (err) {
      console.error('Failed to fetch categories:', err);
    }
  };

  const fetchFunctionDetail = async (funcName: string) => {
    try {
      const res = await axios.get(`/api/data/akshare/function/${funcName}`);
      setFunctionDetail(res.data);
      setParams({});
      setQueryResult(null);
      setQueryError(null);
    } catch (err) {
      console.error('Failed to fetch function detail:', err);
    }
  };

  useEffect(() => {
    if (selectedCategory && categories[selectedCategory]?.length > 0) {
      const firstFunc = categories[selectedCategory][0].name;
      setSelectedFunction(firstFunc);
      fetchFunctionDetail(firstFunc);
    }
  }, [selectedCategory]);

  useEffect(() => {
    if (selectedFunction) {
      fetchFunctionDetail(selectedFunction);
    }
  }, [selectedFunction]);

  const handleQuery = async () => {
    setQueryLoading(true);
    setQueryError(null);
    setQueryResult(null);

    try {
      const res = await axios.post('/api/akshare/query', {
        function: selectedFunction,
        params: Object.entries(params).reduce((acc, [key, value]) => {
          if (value) acc[key] = value;
          return acc;
        }, {} as Record<string, string>),
      });
      setQueryResult(res.data);
    } catch (err: any) {
      setQueryError(err.response?.data?.detail || err.message || '查询失败');
    } finally {
      setQueryLoading(false);
    }
  };

  const fetchSyncStatus = async () => {
    try {
      const res = await axios.get('/api/sync/v2/status');
      setSyncStatus(res.data);
    } catch (err) {
      console.error('Failed to fetch sync status:', err);
    }
  };

  const handleSyncBasics = async () => {
    setSyncLoading(true);
    setSyncMessage('');
    try {
      const res = await axios.post('/api/sync/v2/basics');
      setSyncMessage(`股票基本信息同步完成: 共 ${res.data.total} 只股票，新增 ${res.data.added} 只`);
      fetchSyncStatus();
    } catch (err: any) {
      setSyncMessage(`同步失败: ${err.response?.data?.detail || err.message}`);
    } finally {
      setSyncLoading(false);
    }
  };

  const handleSyncQuotes = async () => {
    setSyncLoading(true);
    setSyncMessage('');
    try {
      const res = await axios.post('/api/sync/v2/quotes');
      setSyncMessage(`实时行情同步完成: 共更新 ${res.data.quotes_updated} 只股票`);
      fetchSyncStatus();
    } catch (err: any) {
      setSyncMessage(`同步失败: ${err.response?.data?.detail || err.message}`);
    } finally {
      setSyncLoading(false);
    }
  };

  const handleSyncKlines = async () => {
    if (!syncForm.startDate || !syncForm.endDate) {
      setSyncMessage('请选择开始和结束日期');
      return;
    }

    setSyncLoading(true);
    setSyncMessage('');
    try {
      const res = await axios.post('/api/sync/v2/klines', {
        start_date: syncForm.startDate,
        end_date: syncForm.endDate,
        codes: syncForm.stockCodes || undefined,
      });
      setSyncMessage(`K线数据同步完成: 共获取 ${res.data.klines_updated} 条数据`);
      fetchSyncStatus();
    } catch (err: any) {
      setSyncMessage(`同步失败: ${err.response?.data?.detail || err.message}`);
    } finally {
      setSyncLoading(false);
    }
  };

  const formatValue = (value: any): string => {
    if (value === null || value === undefined) return '-';
    if (typeof value === 'number') {
      return value.toLocaleString();
    }
    return String(value);
  };

  return (
    <div className="data-query-page">
      <div className="page-header">
        <h1>数据查询与同步</h1>
      </div>

      <div className="tabs">
        <button
          className={`tab ${activeTab === 'query' ? 'active' : ''}`}
          onClick={() => setActiveTab('query')}
        >
          <span className="tab-icon">🔍</span>
          AkShare 查询
        </button>
        <button
          className={`tab ${activeTab === 'sync' ? 'active' : ''}`}
          onClick={() => setActiveTab('sync')}
        >
          <span className="tab-icon">📡</span>
          数据同步
        </button>
      </div>

      {activeTab === 'query' && (
        <div className="query-panel">
          <div className="query-sidebar">
            <h3>数据分类</h3>
            <div className="category-list">
              {Object.keys(categories).map(cat => (
                <button
                  key={cat}
                  className={`category-item ${selectedCategory === cat ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat}
                </button>
              ))}
            </div>

            <h3>数据接口</h3>
            <div className="function-list">
              {categories[selectedCategory]?.map(func => (
                <button
                  key={func.name}
                  className={`function-item ${selectedFunction === func.name ? 'active' : ''}`}
                  onClick={() => setSelectedFunction(func.name)}
                >
                  {func.description}
                </button>
              ))}
            </div>
          </div>

          <div className="query-main">
            {functionDetail && (
              <div className="function-detail">
                <div className="detail-header">
                  <h3>{functionDetail.name}</h3>
                  <span className="category-tag">{functionDetail.category}</span>
                </div>

                {functionDetail.description && (
                  <p className="function-desc">{functionDetail.description}</p>
                )}

                {functionDetail.params && functionDetail.params.length > 0 && (
                  <div className="params-section">
                    <h4>参数配置</h4>
                    <div className="params-grid">
                      {functionDetail.params.map((param: any) => (
                        <div key={param.name} className="param-item">
                          <label>
                            {param.name}
                            {param.required && <span className="required">*</span>}
                          </label>
                          <input
                            type="text"
                            placeholder={param.description || param.default || ''}
                            value={params[param.name] || ''}
                            onChange={e => setParams({ ...params, [param.name]: e.target.value })}
                          />
                          {param.description && (
                            <span className="param-hint">{param.description}</span>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <button
                  className="btn btn-primary btn-large"
                  onClick={handleQuery}
                  disabled={queryLoading}
                >
                  {queryLoading ? '查询中...' : '查询数据'}
                </button>
              </div>
            )}

            {queryError && (
              <div className="error-message">
                <span>{queryError}</span>
                <button onClick={() => setQueryError(null)}>×</button>
              </div>
            )}

            {queryResult && (
              <div className="result-section">
                <div className="result-header">
                  <h4>
                    查询结果
                    {queryResult.total !== undefined && (
                      <span className="result-count">共 {queryResult.total} 条</span>
                    )}
                  </h4>
                </div>

                {queryResult.data && queryResult.data.length > 0 ? (
                  <div className="result-table-wrapper">
                    <table className="result-table">
                      <thead>
                        <tr>
                          {queryResult.columns?.map(col => (
                            <th key={col}>{col}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {queryResult.data.slice(0, 100).map((row: any, idx: number) => (
                          <tr key={idx}>
                            {queryResult.columns?.map(col => (
                              <td key={col}>{formatValue(row[col])}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="empty-result">
                    <p>暂无数据</p>
                  </div>
                )}

                {queryResult.total && queryResult.total > 100 && (
                  <p className="result-hint">仅显示前 100 条数据</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'sync' && (
        <div className="sync-panel">
          <div className="sync-status-card">
            <h3>数据状态</h3>
            <div className="status-grid">
              <div className="status-item">
                <span className="status-label">股票基本信息</span>
                <span className="status-value">{syncStatus?.stock_basic_count || 0}</span>
              </div>
              <div className="status-item">
                <span className="status-label">实时行情</span>
                <span className="status-value">{syncStatus?.stock_quote_count || 0}</span>
              </div>
              <div className="status-item">
                <span className="status-label">K线数据</span>
                <span className="status-value">{syncStatus?.stock_kline_count || 0}</span>
              </div>
            </div>
          </div>

          <div className="sync-sections">
            <div className="sync-section">
              <h3>同步股票基本信息</h3>
              <p>从 baostock 获取股票代码、名称、市场等基本信息</p>
              <button
                className="btn btn-primary"
                onClick={handleSyncBasics}
                disabled={syncLoading}
              >
                {syncLoading ? '同步中...' : '开始同步'}
              </button>
            </div>

            <div className="sync-section">
              <h3>同步实时行情</h3>
              <p>获取股票的最新价格、涨跌幅、成交量等数据</p>
              <button
                className="btn btn-primary"
                onClick={handleSyncQuotes}
                disabled={syncLoading}
              >
                {syncLoading ? '同步中...' : '开始同步'}
              </button>
            </div>

            <div className="sync-section highlight">
              <h3>同步K线数据（用于回测）</h3>
              <p>获取历史K线数据，用于回测策略</p>
              <div className="sync-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>开始日期</label>
                    <input
                      type="date"
                      value={syncForm.startDate}
                      onChange={e => setSyncForm({ ...syncForm, startDate: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label>结束日期</label>
                    <input
                      type="date"
                      value={syncForm.endDate}
                      onChange={e => setSyncForm({ ...syncForm, endDate: e.target.value })}
                    />
                  </div>
                </div>
                <div className="form-group">
                  <label>股票代码（可选，逗号分隔留空则同步所有）</label>
                  <input
                    type="text"
                    placeholder="如: 600519,000001,300750"
                    value={syncForm.stockCodes}
                    onChange={e => setSyncForm({ ...syncForm, stockCodes: e.target.value })}
                  />
                </div>
                <button
                  className="btn btn-success"
                  onClick={handleSyncKlines}
                  disabled={syncLoading}
                >
                  {syncLoading ? '同步中...' : '开始同步K线数据'}
                </button>
              </div>
            </div>
          </div>

          {syncMessage && (
            <div className="sync-message">
              {syncMessage}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
