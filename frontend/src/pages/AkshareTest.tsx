import { useState, useEffect } from 'react';
import axios from 'axios';
import './AkshareTest.css';

interface FunctionInfo {
  name: string;
  description: string;
}

interface Category {
  name: string;
  functions: FunctionInfo[];
}

interface Param {
  name: string;
  type: string;
  required: boolean;
  default?: string;
  description?: string;
}

interface Schema {
  name: string;
  description: string;
  fields: Record<string, {
    type: string;
    description: string;
    required: boolean;
    default?: string;
  }>;
}

interface FunctionSchema {
  name: string;
  description: string;
  params: Param[];
  input_schema: Schema | null;
  output_schema: Schema | null;
}

function AkshareTest() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [activeTab, setActiveTab] = useState<string>('');
  const [searchText, setSearchText] = useState('');
  const [selectedFunc, setSelectedFunc] = useState<string>('');
  const [funcSchema, setFuncSchema] = useState<FunctionSchema | null>(null);
  const [params, setParams] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 获取分类
  useEffect(() => {
    fetchCategories();
  }, []);

  // 加载函数 schema
  useEffect(() => {
    if (selectedFunc) {
      fetchSchema(selectedFunc);
    }
  }, [selectedFunc]);

  // 重置参数
  useEffect(() => {
    if (funcSchema) {
      const defaultParams: Record<string, string> = {};
      funcSchema.params.forEach(p => {
        if (p.default && p.default !== 'PydanticUndefined') {
          defaultParams[p.name] = p.default;
        }
      });
      setParams(defaultParams);
    }
  }, [funcSchema]);

  const fetchCategories = async () => {
    try {
      const res = await axios.get('/akshare/categories');
      const cats = res.data;
      const catList: Category[] = Object.entries(cats).map(([name, funcs]) => ({
        name,
        functions: funcs as FunctionInfo[],
      }));
      setCategories(catList);
      if (catList.length > 0) {
        setActiveTab(catList[0].name);
      }
    } catch (e) {
      console.error('Failed to fetch categories', e);
    }
  };

  const fetchSchema = async (funcName: string) => {
    try {
      const res = await axios.get(`/akshare/schema/${funcName}`);
      setFuncSchema(res.data);
    } catch (e) {
      console.error('Failed to fetch schema', e);
    }
  };

  const handleCall = async () => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // 处理日期参数
      const processedParams: Record<string, string> = {};
      for (const [key, value] of Object.entries(params)) {
        if (value) {
          if (key.includes('date') || key.includes('start_date') || key.includes('end_date')) {
            processedParams[key] = value.replace(/-/g, '');
          } else {
            processedParams[key] = value;
          }
        }
      }

      // 使用 URLSearchParams 确保参数正确编码
      const queryString = new URLSearchParams(processedParams).toString();
      const url = queryString
        ? `/akshare/functions/${selectedFunc}?${queryString}`
        : `/akshare/functions/${selectedFunc}`;

      const response = await axios.get(url, { timeout: 60000 });
      setResult(response.data);
    } catch (err: any) {
      if (err.code === 'ECONNABORTED') {
        setError('请求超时，请稍后重试');
      } else if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError(err.message || '调用失败');
      }
    } finally {
      setLoading(false);
    }
  };

  // 过滤函数
  const filteredFunctions = categories
    .find(c => c.name === activeTab)
    ?.functions.filter(f =>
      f.name.toLowerCase().includes(searchText.toLowerCase()) ||
      f.description.toLowerCase().includes(searchText.toLowerCase())
    ) || [];

  return (
    <div className="akshare-test">
      <div className="test-header">
        <h1>🔧 AKShare 接口测试</h1>
        <p>多 Tab 分类展示，支持模糊搜索，自动提取 Schema</p>
      </div>

      <div className="test-content">
        {/* 左侧：分类 Tab + 函数列表 */}
        <div className="func-panel">
          {/* 搜索框 */}
          <div className="search-box">
            <input
              type="text"
              placeholder="搜索函数名或描述..."
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
            />
          </div>

          {/* Tab 分类 */}
          <div className="tab-list">
            {categories.map(cat => (
              <button
                key={cat.name}
                className={`tab-btn ${activeTab === cat.name ? 'active' : ''}`}
                onClick={() => setActiveTab(cat.name)}
              >
                {cat.name}
              </button>
            ))}
          </div>

          {/* 函数列表 */}
          <div className="func-list">
            {filteredFunctions.map(func => (
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

        {/* 中间：参数面板 */}
        <div className="param-panel">
          {selectedFunc && funcSchema ? (
            <>
              <div className="func-header">
                <h3>{funcSchema.name}</h3>
                <p>{funcSchema.description}</p>
              </div>

              {/* 参数输入 */}
              <div className="params-form">
                <h4>参数设置</h4>
                {funcSchema.params.length === 0 ? (
                  <div className="no-params">无需参数</div>
                ) : (
                  funcSchema.params.map(param => {
                    // 优先使用 schema 中的描述
                    const fieldDesc = funcSchema.input_schema?.fields?.[param.name]?.description;
                    return (
                      <div key={param.name} className="param-item">
                        <label>
                          {param.name}
                          {param.required && <span className="required">*</span>}
                          {fieldDesc && <span className="param-desc"> - {fieldDesc}</span>}
                        </label>
                        {renderParamInput(param)}
                      </div>
                    );
                  })
                )}

                <button
                  className="call-btn"
                  onClick={handleCall}
                  disabled={loading}
                >
                  {loading ? '调用中...' : '调用接口'}
                </button>
              </div>

              {/* 输出 Schema */}
              {funcSchema.output_schema && (
                <div className="output-schema">
                  <h4>返回字段说明</h4>
                  <div className="schema-table">
                    <table>
                      <thead>
                        <tr>
                          <th>字段</th>
                          <th>类型</th>
                          <th>说明</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(funcSchema.output_schema.fields).map(([name, field]) => (
                          <tr key={name}>
                            <td>{name}</td>
                            <td>{field.type}</td>
                            <td>{field.description}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="no-selection">
              <p>请从左侧选择一个函数</p>
            </div>
          )}
        </div>

        {/* 右侧：结果展示 */}
        <div className="result-panel">
          <h3>返回结果</h3>
          {loading && <div className="loading">加载中...</div>}
          {error && <div className="error">{error}</div>}
          {result && (
            <pre className="result-content">
              {typeof result === 'string' ? result : JSON.stringify(result, null, 2)}
            </pre>
          )}
          {!loading && !error && !result && (
            <div className="empty-result">点击"调用接口"查看结果</div>
          )}
        </div>
      </div>
    </div>
  );

  function renderParamInput(param: Param) {
    const name = param.name;
    const value = params[name] || '';

    if (name.includes('date')) {
      return (
        <input
          type="date"
          value={value}
          onChange={e => setParams({ ...params, [name]: e.target.value })}
        />
      );
    }

    if (name === 'symbol') {
      return (
        <input
          type="text"
          placeholder="如: 000001"
          value={value}
          onChange={e => setParams({ ...params, [name]: e.target.value })}
        />
      );
    }

    if (name === 'indicator') {
      return (
        <select
          value={value || '今日'}
          onChange={e => setParams({ ...params, [name]: e.target.value })}
        >
          <option value="今日">今日</option>
          <option value="5日">5日</option>
          <option value="10日">10日</option>
          <option value="20日">20日</option>
        </select>
      );
    }

    if (name === 'sector_type') {
      return (
        <select
          value={value || '行业资金流'}
          onChange={e => setParams({ ...params, [name]: e.target.value })}
        >
          <option value="行业资金流">行业资金流</option>
          <option value="概念资金流">概念资金流</option>
        </select>
      );
    }

    if (name === 'period') {
      return (
        <select
          value={value || 'daily'}
          onChange={e => setParams({ ...params, [name]: e.target.value })}
        >
          <option value="daily">日K</option>
          <option value="weekly">周K</option>
          <option value="monthly">月K</option>
          <option value="5">5分钟</option>
          <option value="15">15分钟</option>
          <option value="30">30分钟</option>
          <option value="60">60分钟</option>
        </select>
      );
    }

    if (name === 'adjust') {
      return (
        <select
          value={value || ''}
          onChange={e => setParams({ ...params, [name]: e.target.value })}
        >
          <option value="">不复权</option>
          <option value="qfq">前复权</option>
          <option value="hfq">后复权</option>
        </select>
      );
    }

    // 时间范围参数（如"近一月"）
    if (name === 'symbol' && (param.description?.includes('近一月') || param.default === '近一月')) {
      return (
        <select
          value={value || '近一月'}
          onChange={e => setParams({ ...params, [name]: e.target.value })}
        >
          <option value="近一月">近一月</option>
          <option value="近三月">近三月</option>
          <option value="近六月">近六月</option>
          <option value="近一年">近一年</option>
        </select>
      );
    }

    return (
      <input
        type="text"
        value={value}
        onChange={e => setParams({ ...params, [name]: e.target.value })}
        placeholder={param.default || ''}
      />
    );
  }
}

export default AkshareTest;
