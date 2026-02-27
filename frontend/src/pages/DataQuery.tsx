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
  source?: 'cache' | 'akshare';  // 数据来源
}

export default function DataQuery() {
  const [selectedFunction, setSelectedFunction] = useState<string>('stock_zh_a_spot_em');
  const [functionDetail, setFunctionDetail] = useState<AkshareFunction | null>(null);
  const [params, setParams] = useState<Record<string, string>>({});
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<QueryResult | null>(null);
  const [queryError, setQueryError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [apiCategories, setApiCategories] = useState<Record<string, Array<{name: string, description: string}>> | null>(null);
  const [activeTab, setActiveTab] = useState<string>('游资常用');

  // 从API加载分类
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const res = await axios.get('/api/data/akshare/categories');
        setApiCategories(res.data);
      } catch (err) {
        console.error('Failed to load categories:', err);
      }
    };
    loadCategories();
  }, []);
  // 接口状态（测试结果）
  const [funcStatus, setFuncStatus] = useState<Record<string, 'testing' | 'success' | 'error' | null>>({
    "stock_zh_a_minute": "success",
    "forex_zh_spot": "error",
    "forex_spot_em": "error",
    "futures_comm_info": "error",
    "stock_zh_a_new_em": "error",
    "stock_zt_pool_em": "success",
    "stock_us_spot_em": "error",
    "stock_zh_a_hist": "error",
    "stock_rzrq_em": "error",
    "stock_zh_a_trade": "error",
    "macro_china_gdp": "success",
    "stock_zh_a_treda": "error",
    "stock_lhb_stock_detail_em": "success",
    "stock_rzrq_detail_em": "error",
    "macro_china_m2": "error",
    "stock_zh_index_daily_em": "error",
    "stock_zh_a_tredb": "error",
    "stock_zt_pool_previous_em": "success",
    "macro_china_cpi": "success",
    "stock_hsgt_individual_em": "success",
    "futures_zh_spot": "error",
    "stock_zt_pool_zbgc_em": "error",
    "fund_manager_em": "error",
    "stock_individual_fund_flow": "success",
    "stock_zt_pool_sub_new_em": "success",
    "stock_hk_spot_em": "error",
    "stock_lh_yyb_most": "success",
    "stock_lh_yyb_capital": "success",
    "stock_hsgt_fund_flow_summary_em": "success",
    "stock_fund_flow_big_deal": "error",
    "stock_zt_pool_dtgc_em": "error",
    "stock_hk_daily": "success",
    "stock_lhb_stock_statistic_em": "error",
    "stock_rzrq_fund_flow": "error",
    "stock_yjyg_em": "success",
    "stock_yjkb_em": "success",
    "macro_china_ppi": "success",
    "futures_hist_em": "error",
    "stock_fh_em": "error",
    "stock_lhb_jgzz_sina": "success",
    "stock_fhps_em": "success",
    "stock_zh_a_hist_min_em": "error",
    "stock_financial_analysis_indicator": "success",
    "stock_board_concept_spot_em": "error",
    "stock_board_concept_cons_em": "error",
    "bond_zh_hs_spot": "error",
    "stock_fund_flow": "error",
    "stock_board_change_em": "success",
    "stock_sector_fund_flow_rank": "error",
    "stock_rzrq_latest": "error",
    "stock_zt_pool_strong_em": "success",
    "stock_yjbb_em": "success",
    "stock_lhb_hyyyb_em": "success",
    "stock_individual_fund_flow_stick": "error",
    "stock_financial_abstract": "success",
    "stock_lhb_detail_em": "success",
    "bond_zh_cov": "success",
    "stock_lhb_yybph_em": "success",
    "stock_market_fund_flow": "success",
    "stock_info_sh_name_code": "success",
    "stock_board_industry_spot_em": "success",
    "stock_hsgt_hold_stock_em": "success",
    "fund_open_fund_daily_em": "error",
    "stock_info_sz_name_code": "success",
    "stock_zh_index_spot_em": "error",
    "stock_hsgt_hist_em": "success",
    "option_current_day_sse": "success",
    "fund_etf_spot_em": "error",
    "fund_etf_hist_em": "error",
    "stock_individual_fund_flow_rank": "error",
    "stock_board_concept_name_em": "error",
    "stock_board_industry_cons_em": "error",
    "stock_info_a_code_name": "success",
    // 新增可用接口
    "stock_dzjy_mrtj": "success",
    "stock_fund_flow_industry": "success",
    "stock_lhb_yytj_sina": "success",
  });

  // 游资常用分类
  const categories = useMemo(() => [
    {
      name: '游资必看',
      icon: '🔥',
      items: [
        { name: 'stock_zh_a_spot_em', desc: '实时行情' },
        { name: 'stock_zh_a_new_em', desc: '新股实时行情' },
        { name: 'stock_zh_a_limit_up_em', desc: '涨停板' },
        { name: 'stock_zh_a_limit_down_em', desc: '跌停板' },
        { name: 'stock_zt_pool_em', desc: '涨停板池' },
        { name: 'stock_zt_pool_strong_em', desc: '涨停板池-强势' },
        { name: 'stock_zt_pool_dtgc_em', desc: '涨停池-龙头股' },
        { name: 'stock_zt_pool_previous_em', desc: '昨日涨停池' },
        { name: 'stock_sector_fund_flow_rank', desc: '板块资金流向' },
        { name: 'stock_individual_fund_flow', desc: '个股资金流向' },
        { name: 'stock_lhb_detail_em', desc: '龙虎榜详情' },
        { name: 'stock_lh_yyb_most', desc: '龙虎榜营业部' },
        { name: 'stock_board_industry_name_em', desc: '行业板块' },
        { name: 'stock_board_concept_name_em', desc: '概念板块' },
      ]
    },
    {
      name: '行情数据',
      icon: '📊',
      items: [
        { name: 'stock_zh_a_hist', desc: '历史K线' },
        { name: 'stock_zh_a_minute', desc: '分时数据' },
        { name: 'stock_zh_a_hist_min_em', desc: '分时历史数据' },
        { name: 'stock_zh_index_daily_em', desc: '指数日K' },
        { name: 'stock_zh_index_spot_em', desc: '指数实时' },
        { name: 'stock_zh_a_treda', desc: '市场总貌(上海)' },
        { name: 'stock_zh_a_tredb', desc: '市场总貌(深圳)' },
        { name: 'stock_zh_a_trade', desc: '市场交易数据' },
      ]
    },
    {
      name: '资金流向',
      icon: '💰',
      items: [
        { name: 'stock_fund_flow', desc: '大盘资金流向' },
        { name: 'stock_market_fund_flow', desc: '市场资金流向' },
        { name: 'stock_sector_fund_flow_rank', desc: '板块资金排名' },
        { name: 'stock_individual_fund_flow', desc: '个股资金流向' },
        { name: 'stock_individual_fund_flow_rank', desc: '个股资金流向排名' },
        { name: 'stock_individual_fund_flow_stick', desc: '个股资金流向(多日)' },
        { name: 'stock_fund_flow_big_deal', desc: '大单交易' },
        { name: 'stock_hsgt_hist_em', desc: '沪深港通历史' },
        { name: 'stock_hsgt_fund_flow_summary_em', desc: '沪深港通资金汇总' },
      ]
    },
    {
      name: '龙虎榜',
      icon: '🐯',
      items: [
        { name: 'stock_lhb_detail_em', desc: '龙虎榜详情' },
        { name: 'stock_lh_yyb_most', desc: '营业部排行' },
        { name: 'stock_lh_yyb_capital', desc: '资金实力' },
        { name: 'stock_lhb_hyyyb_em', desc: '活跃营业部' },
        { name: 'stock_lhb_yybph_em', desc: '营业部排行(新版)' },
        { name: 'stock_lhb_jgzz_sina', desc: '机构席位' },
        { name: 'stock_lhb_stock_detail_em', desc: '龙虎榜个股明细' },
        { name: 'stock_lhb_stock_statistic_em', desc: '龙虎榜股票统计' },
      ]
    },
    {
      name: '涨跌停',
      icon: '🚀',
      items: [
        { name: 'stock_zh_a_limit_up_em', desc: '涨停板' },
        { name: 'stock_zh_a_limit_down_em', desc: '跌停板' },
        { name: 'stock_zt_pool_em', desc: '涨停板池' },
        { name: 'stock_zt_pool_strong_em', desc: '涨停板池-强势' },
        { name: 'stock_zt_pool_dtgc_em', desc: '涨停池-龙头股' },
        { name: 'stock_zt_pool_zbgc_em', desc: '涨停池-炸板股' },
        { name: 'stock_zt_pool_previous_em', desc: '昨日涨停池' },
        { name: 'stock_zt_pool_sub_new_em', desc: '涨停池-次新股' },
        { name: 'stock_zh_a_limit_up_sina', desc: '涨停板(新浪)' },
      ]
    },
    {
      name: '板块轮动',
      icon: '🔄',
      items: [
        { name: 'stock_board_industry_name_em', desc: '行业板块' },
        { name: 'stock_board_concept_name_em', desc: '概念板块' },
        { name: 'stock_board_industry_spot_em', desc: '行业板块行情' },
        { name: 'stock_board_concept_spot_em', desc: '概念板块行情' },
        { name: 'stock_board_change_em', desc: '板块涨跌排行' },
        { name: 'stock_board_industry_cons_em', desc: '行业成分股' },
        { name: 'stock_board_concept_cons_em', desc: '概念成分股' },
        { name: 'stock_board_industry_hist_em', desc: '行业板块历史' },
        { name: 'stock_board_concept_hist_em', desc: '概念板块历史' },
      ]
    },
    {
      name: '财务数据',
      icon: '📈',
      items: [
        { name: 'stock_financial_abstract', desc: '财务摘要' },
        { name: 'stock_financial_analysis_indicator', desc: '财务分析指标' },
        { name: 'stock_yjbb_em', desc: '业绩报表' },
        { name: 'stock_yjkb_em', desc: '业绩快报' },
        { name: 'stock_yjyg_em', desc: '业绩预告' },
        { name: 'stock_fh_em', desc: '分红送转' },
        { name: 'stock_fhps_em', desc: '分红送配' },
        { name: 'stock_gpwy_em', desc: '股本演变' },
        { name: 'stock_yysj_em', desc: '营业数据' },
      ]
    },
    {
      name: '融资融券',
      icon: '💳',
      items: [
        { name: 'stock_rzrq_em', desc: '融资融券' },
        { name: 'stock_rzrq_detail_em', desc: '融资融券明细' },
        { name: 'stock_rzrq_fund_flow', desc: '融资融券资金流向' },
        { name: 'stock_rzrq_latest', desc: '融资融券最新' },
      ]
    },
    {
      name: '沪深港通',
      icon: '🌏',
      items: [
        { name: 'stock_hsgt_hist_em', desc: '沪深港通历史' },
        { name: 'stock_hsgt_em', desc: '沪深港通持股' },
        { name: 'stock_hsgt_sse_sgt_em', desc: '沪深港通持股标的' },
        { name: 'stock_hsgt_individual_em', desc: '沪深港通个人持股' },
        { name: 'stock_hsgt_hold_stock_em', desc: '沪深港通持股股票' },
        { name: 'stock_hsgt_board_rank_em', desc: '沪深港通板块排名' },
        { name: 'stock_hsgt_fund_flow_summary_em', desc: '沪深港通资金流向' },
        { name: 'stock_hsgt_stock_statistics_em', desc: '沪深港通股票统计' },
      ]
    },
    {
      name: '基础信息',
      icon: '📋',
      items: [
        { name: 'stock_info_a_code_name', desc: '股票列表' },
        { name: 'stock_info_sh_name_code', desc: '上交所股票' },
        { name: 'stock_info_sz_name_code', desc: '深交所股票' },
        { name: 'stock_info_change_name', desc: '股票更名' },
        { name: 'stock_info_cjzc_em', desc: '筹码分布' },
        { name: 'stock_ipo_info', desc: '新股上市信息' },
        { name: 'stock_ipo_declare_em', desc: '新股申报信息' },
        { name: 'stock_zh_index_cons', desc: '指数成分' },
        { name: 'stock_info_sh_delist', desc: '退市股票(上海)' },
        { name: 'stock_info_sz_delist', desc: '退市股票(深圳)' },
      ]
    },
    {
      name: '资讯公告',
      icon: '📰',
      items: [
        { name: 'stock_news_em', desc: '股票新闻' },
        { name: 'stock_notice_em', desc: '股票公告' },
        { name: 'stock_jgzy_em', desc: '机构调研' },
      ]
    },
    {
      name: '多市场行情',
      icon: '🌐',
      items: [
        { name: 'stock_sz_a_spot_em', desc: '深市A股' },
        { name: 'stock_sh_a_spot_em', desc: '沪市A股' },
        { name: 'stock_cy_a_spot_em', desc: '创业板' },
        { name: 'stock_kc_a_spot_em', desc: '科创板' },
        { name: 'stock_bj_a_spot_em', desc: '北交所' },
        { name: 'stock_new_a_spot_em', desc: '新股' },
        { name: 'stock_zh_a_st_em', desc: 'ST股' },
        { name: 'stock_zh_a_stop_em', desc: '退市股' },
      ]
    },
    {
      name: '宏观数据',
      icon: '🏛️',
      items: [
        { name: 'macro_china_gdp', desc: '中国GDP' },
        { name: 'macro_china_cpi', desc: '中国CPI' },
        { name: 'macro_china_ppi', desc: '中国PPI' },
        { name: 'macro_china_m2', desc: '中国M2' },
        { name: 'macro_china_stock_market_cap', desc: '股市市值' },
        { name: 'macro_china_trade', desc: '贸易数据' },
        { name: 'macro_china_fdi', desc: 'FDI数据' },
        { name: 'macro_china_bank_financing', desc: '社会融资' },
      ]
    },
    {
      name: '基金',
      icon: '📊',
      items: [
        { name: 'fund_etf_spot_em', desc: 'ETF实时行情' },
        { name: 'fund_etf_hist_em', desc: 'ETF历史数据' },
        { name: 'fund_open_fund_daily_em', desc: '开放式基金净值' },
        { name: 'fund_open_fund_info_em', desc: '开放式基金列表' },
        { name: 'fund_money_fund_daily_em', desc: '货币基金净值' },
        { name: 'fund_fh_em', desc: '基金分红' },
        { name: 'fund_manager_em', desc: '基金经理' },
        { name: 'fund_portfolio_hold_em', desc: '基金持仓' },
      ]
    },
    {
      name: '期货',
      icon: '📉',
      items: [
        { name: 'futures_zh_spot', desc: '期货实时行情' },
        { name: 'futures_zh_realtime', desc: '期货实时数据' },
        { name: 'futures_hist_em', desc: '期货历史数据' },
        { name: 'futures_comm_info', desc: '期货品种信息' },
        { name: 'futures_contract_info_cffex', desc: '中金所合约' },
        { name: 'futures_contract_info_shfe', desc: '上期所合约' },
        { name: 'futures_contract_info_dce', desc: '大商所合约' },
        { name: 'futures_contract_info_czce', desc: '郑商所合约' },
      ]
    },
    {
      name: '期权',
      icon: '🎯',
      items: [
        { name: 'option_current_day_sse', desc: '上证期权行情' },
        { name: 'option_current_day_szse', desc: '深证期权行情' },
        { name: 'option_sse_list_sina', desc: '期权标的列表' },
        { name: 'option_comm_symbol', desc: '期权合约代码' },
      ]
    },
    {
      name: '债券',
      icon: '📑',
      items: [
        { name: 'bond_zh_hs_spot', desc: '沪深债券行情' },
        { name: 'bond_zh_hs_daily', desc: '沪深债券日K' },
        { name: 'bond_zh_cov', desc: '可转债列表' },
        { name: 'bond_cb_jsl', desc: '可转债(集思录)' },
      ]
    },
    {
      name: '外汇',
      icon: '💱',
      items: [
        { name: 'forex_spot_em', desc: '外汇实时行情' },
        { name: 'forex_hist_em', desc: '外汇历史数据' },
        { name: 'forex_zh_spot', desc: '外汇实时(人民币)' },
      ]
    },
    {
      name: '港股',
      icon: '🏢',
      items: [
        { name: 'stock_hk_spot_em', desc: '港股实时行情' },
        { name: 'stock_hk_daily', desc: '港股日K线' },
        { name: 'stock_hk_index_spot_em', desc: '港股指数行情' },
      ]
    },
    {
      name: '美股',
      icon: '🇺🇸',
      items: [
        { name: 'stock_us_spot_em', desc: '美股实时行情' },
        { name: 'stock_us_daily', desc: '美股日K线' },
      ]
    },
  ], []);

  // 将API分类转换为前端格式
  const apiCategoriesFormatted = useMemo(() => {
    if (!apiCategories) return null;
    const iconMap: Record<string, string> = {
      '【一】A股行情': '📈',
      '【二】港股行情': '🏢',
      '【三】美股行情': '🇺🇸',
      '【四】指数数据': '📊',
      '【五】板块行情': '🔄',
      '【六】资金流向': '💰',
      '【七】龙虎榜': '🐯',
      '【八】股东数据': '👥',
      '【九】财务报表': '📋',
      '【十】融资融券': '💳',
      '【十一】大宗交易/限售股': '📦',
      '【十二】沪深港通': '🌏',
      '【十三】基金数据': '💵',
      '【十四】期货行情': '📉',
      '【十五】期权行情': '🎯',
      '【十六】债券数据': '📑',
      '【十七】宏观数据': '🏛️',
      '【十八】外汇数据': '💱',
      '【十九】新股/IPO': '🆕',
      '【二十】基础信息': '📋',
      '【二十一】资讯数据': '📰',
      '【二十二】补充函数': '➕',
    };

    return Object.entries(apiCategories).map(([name, items]) => ({
      name: name.replace(/^【\d+】/, ''), // 去掉序号
      icon: iconMap[name] || '📌',
      items: items.map((item: any) => ({
        name: item.name,
        desc: item.description || item.name
      }))
    }));
  }, [apiCategories]);

  // 游资常用分类 - 置顶
  const yzFavoriteCategory = {
    name: '游资常用',
    icon: '🔥',
    items: [
      { name: 'stock_zt_pool_em', desc: '涨停板池' },
      { name: 'stock_zt_pool_strong_em', desc: '涨停板池-强势' },
      { name: 'stock_zt_pool_previous_em', desc: '昨日涨停池' },
      { name: 'stock_individual_fund_flow', desc: '个股资金流向' },
      { name: 'stock_lhb_detail_em', desc: '龙虎榜详情' },
      { name: 'stock_lh_yyb_most', desc: '龙虎榜营业部' },
      { name: 'stock_lh_yyb_capital', desc: '营业部资金实力' },
      { name: 'stock_lhb_yytj_sina', desc: '游资席位动向' },
      { name: 'stock_board_industry_spot_em', desc: '行业板块' },
      { name: 'stock_board_concept_name_em', desc: '概念板块' },
      { name: 'stock_hsgt_hold_stock_em', desc: '沪深港通持股' },
      { name: 'stock_dzjy_mrtj', desc: '大宗交易' },
      { name: 'stock_fund_flow_industry', desc: '行业资金流向' },
      { name: 'stock_market_fund_flow', desc: '市场资金流向' },
    ]
  };

  // 获取所有tab名称及数量
  const allTabs = useMemo(() => {
    const cats = apiCategoriesFormatted || categories;
    return [
      { name: '游资常用', count: yzFavoriteCategory.items.length },
      ...cats.map((c: any) => ({ name: c.name, count: c.items.length }))
    ];
  }, [apiCategories, yzFavoriteCategory]);

  // 总接口数和可用接口数
  const totalCount = useMemo(() => {
    const cats = apiCategoriesFormatted || categories;
    return cats.reduce((sum: number, c: any) => sum + c.items.length, 0) + yzFavoriteCategory.items.length;
  }, [apiCategories, yzFavoriteCategory]);

  const availableCount = useMemo(() => {
    return Object.keys(funcStatus).filter(k => funcStatus[k] === 'success').length;
  }, [funcStatus]);

  // 根据activeTab获取当前分类
  const currentCategories = useMemo(() => {
    if (activeTab === '游资常用') {
      return [yzFavoriteCategory];
    }
    const cats = apiCategoriesFormatted || categories;
    return cats.filter((c: any) => c.name === activeTab);
  }, [activeTab, yzFavoriteCategory, apiCategoriesFormatted, categories]);

  // 过滤函数
  const filteredCategories = useMemo(() => {
    if (!searchQuery.trim()) return currentCategories;
    const q = searchQuery.toLowerCase();
    return currentCategories.map(cat => ({
      ...cat,
      items: cat.items.filter(item =>
        item.name.toLowerCase().includes(q) ||
        item.desc.toLowerCase().includes(q)
      )
    })).filter(cat => cat.items.length > 0);
  }, [currentCategories, searchQuery]);

  useEffect(() => {
    fetchFunctionDetail(selectedFunction);
  }, []);

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

  // 测试接口连接状态
  const testConnection = async (funcName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setFuncStatus(prev => ({ ...prev, [funcName]: 'testing' }));
    try {
      const res = await axios.post(`/api/data/akshare/execute`, {
        func_name: funcName,
        params: {}
      });
      setFuncStatus(prev => ({ ...prev, [funcName]: 'success' }));
    } catch (err) {
      setFuncStatus(prev => ({ ...prev, [funcName]: 'error' }));
    }
  };

  const handleQuery = async (useCache: boolean = true) => {
    setQueryLoading(true);
    setQueryError(null);
    setQueryResult(null);

    try {
      // 先获取函数详情，然后执行
      const res = await axios.post(`/api/data/akshare/execute`, {
        func_name: selectedFunction,
        params: params,
        use_cache: useCache
      });
      setQueryResult(res.data);
    } catch (err: any) {
      setQueryError(err.response?.data?.detail || err.message || '查询失败');
    } finally {
      setQueryLoading(false);
    }
  };

  // 强制刷新
  const handleForceRefresh = () => {
    handleQuery(false); // use_cache = false
  };

  // 手动同步
  const handleSync = async () => {
    setQueryLoading(true);
    try {
      await axios.post(`/api/data/akshare/sync/${selectedFunction}`);
      // 同步后重新查询
      await handleQuery(true);
    } catch (err: any) {
      setQueryError(err.response?.data?.detail || err.message || '同步失败');
    } finally {
      setQueryLoading(false);
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
    <div className="dq-container">
      {/* 头部搜索 */}
      <div className="dq-header">
        <h1>数据查询</h1>
        <div className="dq-search">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="搜索接口..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {/* Tab导航 */}
      <div className="dq-tabs">
        <div className="dq-tabs-info">
          <span className="dq-tabs-total">总接口: {totalCount}</span>
          <span className="dq-tabs-available">可用: {availableCount}</span>
        </div>
        {allTabs.map((tab: any) => (
          <button
            key={tab.name}
            className={`dq-tab ${activeTab === tab.name ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.name)}
          >
            {tab.name} ({tab.count})
          </button>
        ))}
      </div>

      {/* 主内容区 */}
      <div className="dq-main">
        {/* 左侧分类 */}
        <div className="dq-sidebar">
          {filteredCategories.map(cat => (
            <div key={cat.name} className="dq-category">
              <div className="dq-category-title">
                <span className="cat-icon">{cat.icon}</span>
                {cat.name}
              </div>
              <div className="dq-category-items">
                {cat.items.map(item => (
                  <button
                    key={item.name}
                    className={`dq-item ${selectedFunction === item.name ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedFunction(item.name);
                      fetchFunctionDetail(item.name);
                    }}
                  >
                    <span className="item-name">
                      {funcStatus[item.name] === 'success' && <span style={{color: '#52c41a'}}>✅ </span>}
                      {funcStatus[item.name] === 'error' && <span style={{color: '#ff4d4f'}}>❌ </span>}
                      {funcStatus[item.name] === 'testing' && <span style={{color: '#1890ff'}}>🔄 </span>}
                      {item.name}
                    </span>
                    <span className="item-desc">{item.desc}</span>
                    <span
                      className="dq-status-btn"
                      onClick={(e) => testConnection(item.name, e)}
                      title="测试连接"
                      style={{
                        opacity: funcStatus[item.name] === 'testing' ? 1 : 0.5,
                        fontSize: '10px',
                        marginLeft: '4px'
                      }}
                    >
                      {funcStatus[item.name] === 'testing' ? '🔄' : '⬤'}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* 右侧详情 */}
        <div className="dq-content">
          {functionDetail && (
            <div className="dq-detail">
              <div className="dq-detail-header">
                <div className="dq-detail-title">
                  <h2>{functionDetail.name}</h2>
                  {functionDetail.doc_url && (
                    <a
                      href={functionDetail.doc_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="dq-doc-link"
                    >
                      📖 文档
                    </a>
                  )}
                </div>
                <p className="dq-detail-desc">{functionDetail.description}</p>
                {functionDetail.remark && (
                  <p className="dq-detail-remark">{functionDetail.remark}</p>
                )}
              </div>

              {functionDetail.params && functionDetail.params.length > 0 && (
                <div className="dq-params">
                  <h3>参数</h3>
                  <div className="dq-params-grid">
                    {functionDetail.params.map(param => (
                      <div key={param.name} className="dq-param">
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

              <div style={{ display: 'flex', gap: '8px', marginTop: '16px' }}>
                <button
                  className="dq-query-btn"
                  onClick={() => handleQuery(true)}
                  disabled={queryLoading}
                  style={{ flex: 1 }}
                >
                  {queryLoading ? '查询中...' : '▶ 执行查询'}
                </button>
                <button
                  className="dq-query-btn"
                  onClick={handleForceRefresh}
                  disabled={queryLoading}
                  style={{ flex: 1, background: 'linear-gradient(135deg, #fa8c16 0%, #ffc069 100%)' }}
                >
                  强制刷新
                </button>
                <button
                  className="dq-query-btn"
                  onClick={handleSync}
                  disabled={queryLoading}
                  style={{ flex: 1, background: 'linear-gradient(135deg, #52c41a 0%, #95de64 100%)' }}
                >
                  同步数据
                </button>
              </div>
            </div>
          )}

          {queryError && (
            <div className="dq-error">
              <span>{queryError}</span>
              <button onClick={() => setQueryError(null)}>×</button>
            </div>
          )}

          {queryResult && (
            <div className="dq-result">
              <div className="dq-result-header">
                <h3>查询结果</h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  {queryResult.source && (
                    <span style={{
                      padding: '2px 8px',
                      borderRadius: '10px',
                      fontSize: '12px',
                      background: queryResult.source === 'cache' ? '#f6ffed' : '#e6f4ff',
                      color: queryResult.source === 'cache' ? '#52c41a' : '#1890ff',
                      border: `1px solid ${queryResult.source === 'cache' ? '#b7eb8f' : '#91d5ff'}`
                    }}>
                      {queryResult.source === 'cache' ? '📦 缓存' : '🌐 实时'}
                    </span>
                  )}
                  <span className="result-count">
                    {queryResult.data?.length || 0} 条
                  </span>
                </div>
              </div>

              {queryResult.data && queryResult.data.length > 0 ? (
                <div className="dq-result-table">
                  <table>
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
                <div className="dq-empty">暂无数据</div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
