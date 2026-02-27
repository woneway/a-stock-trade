/**
 * 测试数据配置
 * 游资常用接口测试所需的测试数据
 */

/**
 * 获取昨天的日期 (YYYYMMDD格式)
 */
export function getYesterday(): string {
  const date = new Date();
  date.setDate(date.getDate() - 1);
  return formatDate(date);
}

/**
 * 获取N天前的日期
 */
export function getDaysAgo(days: number): string {
  const date = new Date();
  date.setDate(date.getDate() - days);
  return formatDate(date);
}

/**
 * 格式化日期为 YYYYMMDD 格式
 */
function formatDate(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}${month}${day}`;
}

/**
 * 测试接口列表
 * 按功能阶段分组
 */
export const TEST_INTERFACES = {
  // 情绪判断阶段
  sentiment: {
    '涨停家数': 'stock_zh_a_limit_up_em',
    '跌停家数': 'stock_zh_a_limit_up_em',
    '炸板率': 'stock_zt_pool_zbgc_em',
    '最高板': 'stock_zt_pool_em',
    '昨日涨停溢价': 'stock_zt_pool_previous_em',
    '昨日连板表现': 'stock_zt_pool_em',
  },

  // 涨停板复盘
  limitUp: {
    '当日涨停列表': 'stock_zh_a_limit_up_em',
    '涨停时间排序': 'stock_zh_a_limit_up_em',
    '连板股/龙头': 'stock_zt_pool_em',
    '强势涨停池': 'stock_zt_pool_strong_em',
    '昨日涨停池': 'stock_zt_pool_previous_em',
    '涨停原因': 'stock_zh_a_limit_up_em',
  },

  // 炸板复盘
  zbgc: {
    '炸板股列表': 'stock_zt_pool_zbgc_em',
    '炸板原因分析': 'stock_zt_pool_zbgc_em',
  },

  // 龙虎榜复盘 - 核心
  lhb: {
    '龙虎榜详情': 'stock_lhb_detail_em',
    '机构买入': 'stock_lhb_detail_em',
    '游资席位动向': 'stock_lhb_yytj_sina',
    '营业部上榜次数': 'stock_lh_yyb_most',
    '营业部资金实力': 'stock_lh_yyb_capital',
    '龙虎榜营业部详情': 'stock_lhb_yyb_detail_em',
    '机构席位统计': 'stock_lhb_jgmmtj_em',
  },

  // 资金流向复盘 - 核心
  fundFlow: {
    '个股资金流向': 'stock_individual_fund_flow',
    '个股资金流向(多日)': 'stock_individual_fund_flow_stick',
    '板块资金流向排名': 'stock_sector_fund_flow_rank',
    '概念板块资金流向': 'stock_fund_flow_concept',
    '行业板块资金流向': 'stock_fund_flow_industry',
    '板块资金流向历史': 'stock_sector_fund_flow_hist',
    '主力资金流向': 'stock_main_fund_flow',
    '大盘资金流向': 'stock_fund_flow',
  },

  // 板块分析
  board: {
    '行业板块列表': 'stock_board_industry_name_em',
    '概念板块列表': 'stock_board_concept_name_em',
    '沪深港通持股': 'stock_hsgt_em',
    '融资融券': 'stock_rzrq_em',
    '大宗交易': 'stock_dzjy_em',
  },
};

/**
 * 接口默认参数
 * 部分接口需要传入特定参数才能查询
 */
export const DEFAULT_PARAMS: Record<string, Record<string, string>> = {
  'stock_individual_fund_flow': { stock: '600519' },
  'stock_individual_fund_flow_stick': { stock: '600519', num: '3' },
  'stock_lhb_detail_em': { trade_date: getYesterday() },
  'stock_sector_fund_flow_rank': { indicator: '今日', sector_type: '行业资金流' },
  'stock_sector_fund_flow_hist': { sector_type: '行业资金流', start_date: getDaysAgo(30), end_date: getYesterday() },
  'stock_fund_flow_concept': { indicator: '今日' },
  'stock_fund_flow_industry': { indicator: '今日' },
};

/**
 * 热门股票代码列表
 */
export const POPULAR_STOCKS = [
  '600519',  // 贵州茅台
  '000858',  // 五粮液
  '601318',  // 中国平安
  '600036',  // 招商银行
  '000333',  // 美的集团
];

/**
 * 接口功能描述
 */
export const INTERFACE_DESCRIPTIONS: Record<string, string> = {
  'stock_zh_a_limit_up_em': '涨停板',
  'stock_zt_pool_em': '涨停板池',
  'stock_zt_pool_strong_em': '强势涨停池',
  'stock_zt_pool_zbgc_em': '炸板股池',
  'stock_zt_pool_previous_em': '昨日涨停池',
  'stock_lhb_detail_em': '龙虎榜详情',
  'stock_lhb_yytj_sina': '游资席位动向',
  'stock_lh_yyb_most': '龙虎榜营业部',
  'stock_lh_yyb_capital': '营业部资金实力',
  'stock_lhb_yyb_detail_em': '营业部详情',
  'stock_lhb_jgmmtj_em': '机构席位统计',
  'stock_individual_fund_flow': '个股资金流向',
  'stock_individual_fund_flow_stick': '资金流向多日',
  'stock_sector_fund_flow_rank': '板块资金排名',
  'stock_fund_flow_concept': '概念资金流向',
  'stock_fund_flow_industry': '行业资金流向',
  'stock_sector_fund_flow_hist': '板块资金历史',
  'stock_main_fund_flow': '主力资金流向',
  'stock_fund_flow': '大盘资金流向',
  'stock_board_industry_name_em': '行业板块',
  'stock_board_concept_name_em': '概念板块',
  'stock_hsgt_em': '沪深港通持股',
  'stock_rzrq_em': '融资融券',
  'stock_dzjy_em': '大宗交易',
};
