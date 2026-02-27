import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './TraderDashboard.css';

// ============ 类型定义 ============

interface TradeStatus {
  is_trade_time: boolean;
  is_trade_day: boolean;
  current_time: string;
  current_date: string;
  weekday: string;
}

interface MarketStats {
  limitUpCount: number;
  limitDownCount: number;
  zgCount: number;
  highestBoard: number;
  yesterdayLimitUpCount: number;
}

interface StockData {
  代码?: string;
  名称?: string;
  涨跌幅?: number;
  涨停原因?: string;
  现价?: number;
}

interface IndividualFlowData {
  日期?: string;
  代码?: string;
  名称?: string;
  收盘价?: number;
  涨跌幅?: number;
  '主力净流入-净额'?: number;
}

interface SectorFlowData {
  名称?: string;
  主力净流入?: number;
  涨跌幅?: number;
}

interface LhbYybData {
  营业部名称?: string;
  上榜次数?: number;
  合计动用资金?: string;
}

interface LhbDetailData {
  代码?: string;
  名称?: string;
  上榜日?: string;
}

interface HsgtData {
  类型?: string;
  今日?: number;
  今日变化?: number;
}

interface ApiError {
  message: string;
}

// ============ 工具函数 ============

const getFieldValue = (obj: any, cnField: string, enField: string): any => {
  return obj[cnField] ?? obj[enField] ?? null;
};

const formatNumber = (num: number | string | undefined | null): string => {
  if (num === undefined || num === null) return '-';
  const n = typeof num === 'string' ? parseFloat(num) : num;
  if (isNaN(n)) return '-';
  return n.toFixed(2);
};

const formatMoney = (num: number | string | undefined | null): string => {
  if (num === undefined || num === null) return '-';
  const n = typeof num === 'string' ? parseFloat(num) : num;
  if (isNaN(n)) return '-';
  if (Math.abs(n) >= 100000000) return (n / 100000000).toFixed(2) + '亿';
  if (Math.abs(n) >= 10000) return (n / 10000).toFixed(1) + '万';
  return n.toFixed(0);
};

// ============ 主组件 ============

export default function TraderDashboard() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [tradeStatus, setTradeStatus] = useState<TradeStatus | null>(null);
  const [stats, setStats] = useState<MarketStats | null>(null);

  // 涨跌停数据
  const [limitUpStocks, setLimitUpStocks] = useState<StockData[]>([]);
  const [limitDownStocks, setLimitDownStocks] = useState<StockData[]>([]);
  const [zgStocks, setZgStocks] = useState<StockData[]>([]);
  const [yesterdayLimitUp, setYesterdayLimitUp] = useState<StockData[]>([]);
  const [strongStocks, setStrongStocks] = useState<StockData[]>([]);

  // 资金流向
  const [individualFlows, setIndividualFlows] = useState<IndividualFlowData[]>([]);
  const [conceptFlows, setConceptFlows] = useState<SectorFlowData[]>([]);
  const [industryFlows, setIndustryFlows] = useState<SectorFlowData[]>([]);
  const [hsgtFlows, setHsgtFlows] = useState<HsgtData[]>([]);

  // 龙虎榜
  const [lhbYybs, setLhbYybs] = useState<LhbYybData[]>([]);
  const [lhbDetails, setLhbDetails] = useState<LhbDetailData[]>([]);

  const [errors, setErrors] = useState<ApiError[]>([]);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  // ============ 数据获取 ============

  const fetchData = useCallback(async (forceRefresh = false) => {
    if (forceRefresh) setRefreshing(true);
    else setLoading(true);

    setErrors([]);
    const headers = forceRefresh ? { 'Cache-Control': 'no-cache' } : {};

    try {
      // 1. 获取交易状态
      const statusRes = await axios.get('/api/data/trade-status', { headers });
      setTradeStatus(statusRes.data);

      // 2. 并行请求核心游资数据 (10个接口)
      const results = await Promise.allSettled([
        // 涨跌停 (5个)
        axios.post('/api/data/akshare/execute', { func_name: 'stock_zt_pool_em', params: {} }, { headers }),
        axios.post('/api/data/akshare/execute', { func_name: 'stock_zh_a_limit_down_em', params: {} }, { headers }),
        axios.post('/api/data/akshare/execute', { func_name: 'stock_zt_pool_zbgc_em', params: {} }, { headers }),
        axios.post('/api/data/akshare/execute', { func_name: 'stock_zt_pool_previous_em', params: {} }, { headers }),
        axios.post('/api/data/akshare/execute', { func_name: 'stock_zt_pool_strong_em', params: {} }, { headers }),

        // 资金流向 (4个)
        axios.post('/api/data/akshare/execute', { func_name: 'stock_individual_fund_flow', params: {} }, { headers }),
        axios.post('/api/data/akshare/execute', { func_name: 'stock_fund_flow_concept', params: {} }, { headers }),
        axios.post('/api/data/akshare/execute', { func_name: 'stock_fund_flow_industry', params: {} }, { headers }),
        axios.post('/api/data/akshare/execute', { func_name: 'stock_hsgt_fund_flow_summary_em', params: {} }, { headers }),

        // 龙虎榜 (2个)
        axios.post('/api/data/akshare/execute', { func_name: 'stock_lh_yyb_most', params: {} }, { headers }),
        axios.post('/api/data/akshare/execute', { func_name: 'stock_lhb_detail_em', params: {} }, { headers }),
      ]);

      // 处理涨跌停
      let limitUpCount = 0, limitDownCount = 0, zgCount = 0, yesterdayCount = 0, highestBoard = 0;

      if (results[0].status === 'fulfilled' && results[0].value.data?.data) {
        const data = results[0].value.data.data;
        limitUpCount = data.length;
        data.forEach((s: any) => {
          const 连板数 = parseInt(s['连板数'] || '0');
          if (连板数 > highestBoard) highestBoard = 连板数;
        });
        setLimitUpStocks(data.slice(0, 15));
      }

      if (results[1].status === 'fulfilled' && results[1].value.data?.data) {
        limitDownCount = results[1].value.data.data.length;
        setLimitDownStocks(results[1].value.data.data.slice(0, 10));
      }

      if (results[2].status === 'fulfilled' && results[2].value.data?.data) {
        zgCount = results[2].value.data.data.length;
        setZgStocks(results[2].value.data.data.slice(0, 10));
      }

      if (results[3].status === 'fulfilled' && results[3].value.data?.data) {
        yesterdayCount = results[3].value.data.data.length;
        setYesterdayLimitUp(results[3].value.data.data.slice(0, 15));
      }

      if (results[4].status === 'fulfilled' && results[4].value.data?.data) {
        setStrongStocks(results[4].value.data.data.slice(0, 15));
      }

      // 处理资金流向
      if (results[5].status === 'fulfilled' && results[5].value.data?.data) {
        const data = results[5].value.data.data;
        const sorted = [...data].sort((a: any, b: any) => {
          return (b['主力净流入-净额'] || 0) - (a['主力净流入-净额'] || 0);
        }).slice(0, 15);
        setIndividualFlows(sorted);
      }

      if (results[6].status === 'fulfilled' && results[6].value.data?.data) {
        const data = results[6].value.data.data;
        const sorted = [...data].sort((a: any, b: any) => {
          return (b['主力净流入'] || b['主力净流入-净额'] || 0) - (a['主力净流入'] || a['主力净流入-净额'] || 0);
        }).slice(0, 15);
        setConceptFlows(sorted);
      }

      if (results[7].status === 'fulfilled' && results[7].value.data?.data) {
        const data = results[7].value.data.data;
        const sorted = [...data].sort((a: any, b: any) => {
          return (b['涨跌幅'] || 0) - (a['涨跌幅'] || 0);
        }).slice(0, 15);
        setIndustryFlows(sorted);
      }

      if (results[8].status === 'fulfilled' && results[8].value.data?.data) {
        setHsgtFlows(results[8].value.data.data.slice(0, 5));
      }

      // 处理龙虎榜
      if (results[9].status === 'fulfilled' && results[9].value.data?.data) {
        setLhbYybs(results[9].value.data.data.slice(0, 10));
      }

      if (results[10].status === 'fulfilled' && results[10].value.data?.data) {
        setLhbDetails(results[10].value.data.data.slice(0, 10));
      }

      // 设置统计
      setStats({
        limitUpCount, limitDownCount, zgCount, highestBoard,
        yesterdayLimitUpCount: yesterdayCount,
      });

      setLastUpdate(new Date().toLocaleTimeString());

    } catch (err) {
      console.error('Failed to fetch data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(true), 60000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const handleRefresh = () => fetchData(true);

  // ============ 渲染 ============

  if (loading) {
    return (
      <div className="trader-dashboard">
        <div className="dashboard-loading">
          <div className="loading-spinner"></div>
          <span>加载游资数据中...</span>
        </div>
      </div>
    );
  }

  const showHint = !tradeStatus?.is_trade_time || !tradeStatus?.is_trade_day;

  return (
    <div className="trader-dashboard">
      {/* 头部 */}
      <div className="dashboard-header">
        <div>
          <h1>🔥 游资看板</h1>
          {lastUpdate && <span className="last-update">最后更新: {lastUpdate}</span>}
          {tradeStatus && (
            <span className={`trade-status ${tradeStatus.is_trade_time ? 'status-open' : 'status-closed'}`}>
              {tradeStatus.is_trade_time ? '🟢 交易中' : '🔴 休市'} | {tradeStatus.current_date} {tradeStatus.weekday}
            </span>
          )}
        </div>
        <button className={`refresh-btn ${refreshing ? 'refreshing' : ''}`} onClick={handleRefresh} disabled={refreshing}>
          {refreshing ? '刷新中...' : '🔄 刷新数据'}
        </button>
      </div>

      {showHint && (
        <div className="trade-hint-banner">
          {tradeStatus?.is_trade_day === false
            ? `📅 今日为${tradeStatus?.weekday}，非交易日`
            : `⏰ 当前非交易时间（${tradeStatus?.current_time}）`}
        </div>
      )}

      {/* 情绪指标 */}
      <section className="dashboard-section">
        <h2>📊 情绪指标</h2>
        <div className="stats-grid">
          <div className="stat-card stat-limit-up">
            <div className="stat-label">涨停家数</div>
            <div className="stat-value">{stats?.limitUpCount || 0}</div>
          </div>
          <div className="stat-card stat-limit-down">
            <div className="stat-label">跌停家数</div>
            <div className="stat-value">{stats?.limitDownCount || 0}</div>
          </div>
          <div className="stat-card stat-zg">
            <div className="stat-label">炸板家数</div>
            <div className="stat-value">{stats?.zgCount || 0}</div>
          </div>
          <div className="stat-card stat-highest">
            <div className="stat-label">最高板</div>
            <div className="stat-value">{stats?.highestBoard || 0}板</div>
          </div>
          <div className="stat-card stat-yesterday">
            <div className="stat-label">昨日涨停</div>
            <div className="stat-value">{stats?.yesterdayLimitUpCount || 0}</div>
          </div>
        </div>
      </section>

      {/* 涨跌停 + 炸板 */}
      <section className="dashboard-section">
        <h2>🔥 涨跌停与炸板</h2>
        <div className="four-columns">
          <div className="data-card">
            <h3>涨停板 ({limitUpStocks.length})</h3>
            {limitUpStocks.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>代码</th><th>名称</th><th>涨跌幅</th></tr></thead>
                  <tbody>
                    {limitUpStocks.map((s, i) => (
                      <tr key={i}>
                        <td>{getFieldValue(s, '代码', 'code')}</td>
                        <td className="stock-name">{getFieldValue(s, '名称', 'name')}</td>
                        <td className="price-up">+{formatNumber(getFieldValue(s, '涨跌幅', 'change_pct'))}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">暂无</div>}
          </div>

          <div className="data-card">
            <h3>跌停板 ({limitDownStocks.length})</h3>
            {limitDownStocks.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>代码</th><th>名称</th><th>涨跌幅</th></tr></thead>
                  <tbody>
                    {limitDownStocks.map((s, i) => (
                      <tr key={i}>
                        <td>{getFieldValue(s, '代码', 'code')}</td>
                        <td className="stock-name">{getFieldValue(s, '名称', 'name')}</td>
                        <td className="price-down">{formatNumber(getFieldValue(s, '涨跌幅', 'change_pct'))}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">无跌停</div>}
          </div>

          <div className="data-card">
            <h3>炸板股 ({zgStocks.length})</h3>
            {zgStocks.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>代码</th><th>名称</th><th>涨跌幅</th></tr></thead>
                  <tbody>
                    {zgStocks.map((s, i) => (
                      <tr key={i}>
                        <td>{getFieldValue(s, '代码', 'code')}</td>
                        <td className="stock-name">{getFieldValue(s, '名称', 'name')}</td>
                        <td className="price-down">{formatNumber(getFieldValue(s, '涨跌幅', 'change_pct'))}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">无炸板</div>}
          </div>

          <div className="data-card">
            <h3>强势涨停 ({strongStocks.length})</h3>
            {strongStocks.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>代码</th><th>名称</th><th>涨跌幅</th></tr></thead>
                  <tbody>
                    {strongStocks.map((s, i) => (
                      <tr key={i}>
                        <td>{getFieldValue(s, '代码', 'code')}</td>
                        <td className="stock-name">{getFieldValue(s, '名称', 'name')}</td>
                        <td className="price-up">+{formatNumber(getFieldValue(s, '涨跌幅', 'change_pct'))}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">暂无</div>}
          </div>
        </div>
      </section>

      {/* 资金流向 */}
      <section className="dashboard-section">
        <h2>💰 资金流向</h2>
        <div className="three-columns">
          <div className="data-card">
            <h3>概念板块 ({conceptFlows.length})</h3>
            {conceptFlows.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>板块</th><th>主力净流入</th><th>涨跌幅</th></tr></thead>
                  <tbody>
                    {conceptFlows.map((s: any, i) => (
                      <tr key={i}>
                        <td className="stock-name">{s['名称'] || '-'}</td>
                        <td className={parseFloat(s['主力净流入']||s['主力净流入-净额']||0) > 0 ? 'money-in' : 'money-out'}>
                          {formatMoney(s['主力净流入'] || s['主力净流入-净额'])}
                        </td>
                        <td className={parseFloat(s['涨跌幅']||0) >= 0 ? 'price-up' : 'price-down'}>
                          {formatNumber(s['涨跌幅'])}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">暂无</div>}
          </div>

          <div className="data-card">
            <h3>行业板块 ({industryFlows.length})</h3>
            {industryFlows.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>板块</th><th>涨跌幅</th></tr></thead>
                  <tbody>
                    {industryFlows.map((s: any, i) => (
                      <tr key={i}>
                        <td className="stock-name">{s['板块名称'] || s['名称'] || '-'}</td>
                        <td className={parseFloat(s['涨跌幅']||0) >= 0 ? 'price-up' : 'price-down'}>
                          {formatNumber(s['涨跌幅'])}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">暂无</div>}
          </div>

          <div className="data-card">
            <h3>沪深港通 ({hsgtFlows.length})</h3>
            {hsgtFlows.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>类型</th><th>今日</th><th>变化</th></tr></thead>
                  <tbody>
                    {hsgtFlows.map((s: any, i) => (
                      <tr key={i}>
                        <td className="stock-name">{s['类型'] || '-'}</td>
                        <td className={parseFloat(s['今日']||0) >= 0 ? 'money-in' : 'money-out'}>
                          {formatMoney(s['今日'])}
                        </td>
                        <td className={parseFloat(s['今日变化']||0) >= 0 ? 'price-up' : 'price-down'}>
                          {formatNumber(s['今日变化'])}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">暂无</div>}
          </div>
        </div>

        {/* 个股资金 */}
        <div className="data-card" style={{ marginTop: 16 }}>
          <h3>个股资金流向 TOP15</h3>
          {individualFlows.length > 0 ? (
            <div className="table-container">
              <table className="data-table">
                <thead><tr><th>日期</th><th>代码</th><th>名称</th><th>涨跌幅</th><th>主力净流入</th></tr></thead>
                <tbody>
                  {individualFlows.map((s: any, i) => (
                    <tr key={i}>
                      <td>{s['日期'] || '-'}</td>
                      <td>{s['代码'] || '-'}</td>
                      <td className="stock-name">{s['名称'] || '-'}</td>
                      <td className={parseFloat(s['涨跌幅']||0) >= 0 ? 'price-up' : 'price-down'}>
                        {formatNumber(s['涨跌幅'])}%
                      </td>
                      <td className={parseFloat(s['主力净流入-净额']||0) >= 0 ? 'money-in' : 'money-out'}>
                        {formatMoney(s['主力净流入-净额'])}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <div className="empty-data">暂无</div>}
        </div>
      </section>

      {/* 龙虎榜 */}
      <section className="dashboard-section">
        <h2>🐉 龙虎榜</h2>
        <div className="two-columns">
          <div className="data-card">
            <h3>游资营业部 ({lhbYybs.length})</h3>
            {lhbYybs.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>营业部</th><th>上榜</th><th>动用资金</th></tr></thead>
                  <tbody>
                    {lhbYybs.map((item, i) => (
                      <tr key={i}>
                        <td className="broker-name">{getFieldValue(item, '营业部名称', 'broker_name')}</td>
                        <td>{getFieldValue(item, '上榜次数', 'up_count')}</td>
                        <td className="money-in">{getFieldValue(item, '合计动用资金', 'total_capital') || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">暂无</div>}
          </div>

          <div className="data-card">
            <h3>龙虎榜详情</h3>
            {lhbDetails.length > 0 ? (
              <div className="table-container">
                <table className="data-table">
                  <thead><tr><th>代码</th><th>名称</th><th>上榜日</th></tr></thead>
                  <tbody>
                    {lhbDetails.map((item, i) => (
                      <tr key={i}>
                        <td>{getFieldValue(item, '代码', 'code')}</td>
                        <td className="stock-name">{getFieldValue(item, '名称', 'name')}</td>
                        <td>{getFieldValue(item, '上榜日', 'date')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <div className="empty-data">暂无</div>}
          </div>
        </div>
      </section>

      {/* 昨日涨停 */}
      <section className="dashboard-section">
        <h2>📋 昨日涨停</h2>
        <div className="data-card">
          <h3>昨日涨停 ({yesterdayLimitUp.length})</h3>
          {yesterdayLimitUp.length > 0 ? (
            <div className="table-container">
              <table className="data-table">
                <thead><tr><th>代码</th><th>名称</th><th>涨跌幅</th><th>涨停原因</th></tr></thead>
                <tbody>
                  {yesterdayLimitUp.slice(0, 15).map((s, i) => (
                    <tr key={i}>
                      <td>{getFieldValue(s, '代码', 'code')}</td>
                      <td className="stock-name">{getFieldValue(s, '名称', 'name')}</td>
                      <td className="price-up">+{formatNumber(getFieldValue(s, '涨跌幅', 'change_pct'))}%</td>
                      <td className="reason">{getFieldValue(s, '涨停原因', 'reason') || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : <div className="empty-data">暂无</div>}
        </div>
      </section>
    </div>
  );
}
