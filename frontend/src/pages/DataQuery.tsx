import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import './DataQuery.css';

interface AkshareFunction {
  name: string;
  description: string;
  category: string;
  doc_url?: string;
  remark?: string;
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

  // 搜索相关
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<AkshareFunction[]>([]);
  const [showSearchResults, setShowSearchResults] = useState(false);

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

  // 搜索函数
  useEffect(() => {
    const searchFunctions = async () => {
      if (searchQuery.trim().length < 1) {
        setSearchResults([]);
        setShowSearchResults(false);
        return;
      }

      try {
        const res = await axios.get(`/api/data/akshare/search?q=${encodeURIComponent(searchQuery)}`);
        setSearchResults(res.data);
        setShowSearchResults(true);
      } catch (err) {
        console.error('Search failed:', err);
      }
    };

    const debounce = setTimeout(searchFunctions, 300);
    return () => clearTimeout(debounce);
  }, [searchQuery]);

  const handleSearchSelect = (func: AkshareFunction) => {
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);

    // 查找并选中分类
    const category = Object.keys(categories).find(cat =>
      categories[cat]?.some(f => f.name === func.name)
    );
    if (category) {
      setSelectedCategory(category);
      setSelectedFunction(func.name);
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
      // 使用正确的新API路径
      const res = await axios.post(`/api/data/akshare/execute?func_name=${selectedFunction}`, {
        ...Object.entries(params).reduce((acc, [key, value]) => {
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
      const res = await axios.get('/api/data/stats');
      setSyncStatus(res.data);
    } catch (err) {
      console.error('Failed to fetch sync status:', err);
    }
  };

  const handleSyncBasics = async () => {
    setSyncLoading(true);
    setSyncMessage('');
    try {
      const res = await axios.post('/api/data/sync', {
        stock_code: '000001',
        start_date: '20250101',
        end_date: '20250227',
      });
      setSyncMessage(`同步完成: ${JSON.stringify(res.data)}`);
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
      const res = await axios.post('/api/data/sync', {
        stock_code: syncForm.stockCodes || '600519',
        start_date: syncForm.startDate.replace(/-/g, ''),
        end_date: syncForm.endDate.replace(/-/g, ''),
      });
      setSyncMessage(`K线数据同步完成`);
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

  // 按层级分组分类
  const categoryGroups = useMemo(() => {
    const groups: Record<string, string[]> = {
      '微观-个股': [],
      '中观-板块': [],
      '宏观-市场': [],
      '其他': [],
    };

    Object.keys(categories).forEach(cat => {
      if (cat.startsWith('微观')) {
        groups['微观-个股'].push(cat);
      } else if (cat.startsWith('中观')) {
        groups['中观-板块'].push(cat);
      } else if (cat.startsWith('宏观')) {
        groups['宏观-市场'].push(cat);
      } else {
        groups['其他'].push(cat);
      }
    });

    return groups;
  }, [categories]);

  return (
    <div className="data-query-page">
      <div className="page-header">
        <h1>数据查询</h1>
        <p className="subtitle">AkShare 全面接入 - 宏观/中观/微观</p>
      </div>

      {/* 搜索框 */}
      <div className="search-box">
        <input
          type="text"
          placeholder="搜索接口名称或描述... (如: 涨停、资金、龙虎榜)"
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          onFocus={() => searchQuery && setShowSearchResults(true)}
        />
        <span className="search-icon">🔍</span>

        {/* 搜索结果下拉 */}
        {showSearchResults && searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map(func => (
              <div
                key={func.name}
                className="search-result-item"
                onClick={() => handleSearchSelect(func)}
              >
                <span className="result-name">{func.name}</span>
                <span className="result-desc">{func.description}</span>
                <span className="result-cat">{func.category}</span>
              </div>
            ))}
          </div>
        )}
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
          {/* 左侧分类导航 */}
          <div className="query-sidebar">
            {/* 微观-个股 */}
            <div className="category-group">
              <div className="group-title">📊 微观-个股</div>
              {categoryGroups['微观-个股'].map(cat => (
                <div key={cat} className="category-section">
                  <button
                    className={`category-item ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat.replace('微观-', '')}
                    <span className="count">{categories[cat]?.length || 0}</span>
                  </button>
                </div>
              ))}
            </div>

            {/* 中观-板块 */}
            <div className="category-group">
              <div className="group-title">📈 中观-板块</div>
              {categoryGroups['中观-板块'].map(cat => (
                <div key={cat} className="category-section">
                  <button
                    className={`category-item ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat.replace('中观-', '')}
                    <span className="count">{categories[cat]?.length || 0}</span>
                  </button>
                </div>
              ))}
            </div>

            {/* 宏观-市场 */}
            <div className="category-group">
              <div className="group-title">🌐 宏观-市场</div>
              {categoryGroups['宏观-市场'].map(cat => (
                <div key={cat} className="category-section">
                  <button
                    className={`category-item ${selectedCategory === cat ? 'active' : ''}`}
                    onClick={() => setSelectedCategory(cat)}
                  >
                    {cat.replace('宏观-', '')}
                    <span className="count">{categories[cat]?.length || 0}</span>
                  </button>
                </div>
              ))}
            </div>

            {/* 其他 */}
            {categoryGroups['其他'].map(cat => (
              <div key={cat} className="category-section">
                <button
                  className={`category-item ${selectedCategory === cat ? 'active' : ''}`}
                  onClick={() => setSelectedCategory(cat)}
                >
                  {cat}
                  <span className="count">{categories[cat]?.length || 0}</span>
                </button>
              </div>
            ))}
          </div>

          {/* 中间接口列表 */}
          <div className="query-functions">
            <h3>{selectedCategory}</h3>
            <div className="function-list">
              {categories[selectedCategory]?.map(func => (
                <button
                  key={func.name}
                  className={`function-item ${selectedFunction === func.name ? 'active' : ''}`}
                  onClick={() => setSelectedFunction(func.name)}
                >
                  <span className="func-name">{func.name}</span>
                  <span className="func-desc">{func.description}</span>
                </button>
              ))}
            </div>
          </div>

          {/* 右侧详情 */}
          <div className="query-main">
            {functionDetail && (
              <div className="function-detail">
                <div className="detail-header">
                  <div className="detail-title">
                    <h3>{functionDetail.name}</h3>
                    <a
                      href={functionDetail.doc_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="doc-link"
                      title="查看官方文档"
                    >
                      📖 文档
                    </a>
                  </div>
                  <span className="category-tag">{functionDetail.category}</span>
                </div>

                {functionDetail.description && (
                  <p className="function-desc">{functionDetail.description}</p>
                )}

                {functionDetail.remark && (
                  <p className="function-remark">💡 {functionDetail.remark}</p>
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
                            placeholder={param.default || param.description || ''}
                            value={params[param.name] || ''}
                            onChange={e => setParams({ ...params, [param.name]: e.target.value })}
                          />
                          <span className="param-hint">{param.description}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div className="action-buttons">
                  <button
                    className="btn btn-primary btn-large"
                    onClick={handleQuery}
                    disabled={queryLoading}
                  >
                    {queryLoading ? '查询中...' : '▶ 执行查询'}
                  </button>
                </div>
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
                    {queryResult.data && (
                      <span className="result-count">共 {queryResult.data.length} 条</span>
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

                {queryResult.data && queryResult.data.length > 100 && (
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
