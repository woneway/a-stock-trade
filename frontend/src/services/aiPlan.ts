import api from '../services/api';

const MOCK_PLANS: GeneratedPlan[] = [
  {
    stock_code: '688555',
    stock_name: '慧辰股份',
    sector: '人工智能',
    trade_mode: '低吸',
    entry_type: '回调低吸',
    entry_conditions: '回调至5日均线附近且缩量',
    target_price: 28.50,
    position_ratio: 15,
    stop_loss_price: 26.50,
    stop_loss_ratio: 7,
    take_profit_price: 33.00,
    take_profit_ratio: 15,
    scenario_responses: {
      break_up: '持有或分批卖出，突破前高考虑加仓',
      break_down: '止损卖出，严格执行纪律',
      consolidate: '高抛低吸降低成本',
      volume_surge: '注意风险，考虑部分止盈',
      news_impact: '根据消息面力度决定持有或卖出',
    },
    logic: 'AI算力需求爆发，公司作为算力基础设施供应商有望受益；近期回调至关键均线位置，具备安全边际。',
    confidence: 85,
    risk_notes: '题材轮动快，注意及时止盈止损',
  },
  {
    stock_code: '002230',
    stock_name: '科士达',
    sector: '新能源',
    trade_mode: '半路',
    entry_type: '突破买入',
    entry_conditions: '放量突破近期平台高点',
    target_price: 45.80,
    position_ratio: 12,
    stop_loss_price: 42.50,
    stop_loss_ratio: 7,
    take_profit_price: 52.00,
    take_profit_ratio: 15,
    scenario_responses: {
      break_up: '持有为主，接近前高时考虑部分止盈',
      break_down: '跌破平台支撑无条件止损',
      consolidate: '保持底仓，高抛低吸',
      volume_surge: '量能异常放大需警惕，考虑减仓',
      news_impact: '利好兑现可考虑分批卖出',
    },
    logic: '光伏储能行业景气度高，公司订单饱满，业绩确定性强；技术面放量突破有望开启新一轮上涨。',
    confidence: 78,
    risk_notes: '光伏行业竞争激烈，关注成本端变化',
  },
  {
    stock_code: '301567',
    stock_name: '中芯国际',
    sector: '半导体',
    trade_mode: '低吸',
    entry_type: '分时低吸',
    entry_conditions: '分时图出现企稳信号且有资金流入',
    target_price: 52.00,
    position_ratio: 10,
    stop_loss_price: 48.50,
    stop_loss_ratio: 7,
    take_profit_price: 60.00,
    take_profit_ratio: 15,
    scenario_responses: {
      break_up: '持有待涨，突破压力位后可加仓',
      break_down: '有效跌破50元整数关止损',
      consolidate: '区间震荡，高抛低吸降低成本',
      volume_surge: '量能急剧放大需警惕冲高回落',
      news_impact: '国产替代加速，利好持续发酵',
    },
    logic: '半导体国产替代龙头，受益于政策支持；当前估值处于历史低位，安全边际充足。',
    confidence: 72,
    risk_notes: '半导体周期波动大，需关注行业景气度',
  },
];

export interface PlanGenerationParams {
  market_sentiment: string;
  hot_sectors: string[];
  focus_stocks?: string[];
  account_balance: number;
  risk_preference: '保守' | '稳健' | '激进';
}

export interface GeneratedPlan {
  stock_code: string;
  stock_name: string;
  sector: string;
  trade_mode: string;
  entry_type: string;
  entry_conditions: string;
  target_price: number;
  position_ratio: number;
  stop_loss_price: number;
  stop_loss_ratio: number;
  take_profit_price: number;
  take_profit_ratio: number;
  scenario_responses: {
    break_up: string;
    break_down: string;
    consolidate: string;
    volume_surge: string;
    news_impact: string;
  };
  logic: string;
  confidence: number;
  risk_notes: string;
}

export const aiPlanApi = {
  generatePlan: async (params: PlanGenerationParams) => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    const plans = MOCK_PLANS.map(plan => ({
      ...plan,
      confidence: Math.min(95, plan.confidence + Math.floor(Math.random() * 10 - 5)),
    }));
    return { data: { plans } };
  },
  
  analyzeStock: (stock_code: string) =>
    api.get(`/ai/analyze-stock/${stock_code}`),
  
  getMarketSentiment: () =>
    api.get('/ai/market-sentiment'),
  
  getHotSectors: () =>
    api.get('/ai/hot-sectors'),
  
  screenStocks: (criteria: {
    sector?: string;
    min_price?: number;
    max_price?: number;
    volume_ratio?: number;
    turnover_rate?: number;
  }) => api.post('/ai/screen-stocks', criteria),
};
