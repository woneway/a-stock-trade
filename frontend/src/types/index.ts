export interface TradingPlan {
  id: number;
  plan_date: string;
  market_sentiment?: string;
  hot_sectors?: string[];
  daily_strategy?: string;

  stock_code: string;
  stock_name: string;
  stock_type?: string;
  sector?: string;

  trade_mode: string;
  entry_type?: string;
  entry_conditions?: string;

  target_price: number;
  position_ratio: number;

  stop_loss_price?: number;
  stop_loss_ratio?: number;
  take_profit_price?: number;
  take_profit_ratio?: number;

  add_position_triggers?: Array<{
    price: number;
    ratio: number;
    reason: string;
  }>;
  sell_triggers?: Array<{
    condition: string;
    ratio: number;
    reason: string;
  }>;

  scenario_responses?: {
    break_up?: string;
    break_down?: string;
    consolidate?: string;
    volume_surge?: string;
    news_impact?: string;
  };

  risk_notes?: string;
  emotional_checklist?: string[];

  logic?: string;
  status: string;
  execute_result?: string;
  created_at: string;
  updated_at: string;
}

export interface Position {
  id: number;
  stock_code: string;
  stock_name: string;
  quantity: number;
  available_quantity: number;
  cost_price: number;
  current_price?: number;
  profit_amount?: number;
  profit_ratio?: number;
  stop_loss_price?: number;
  take_profit_price?: number;
  plan_id?: number;
  status: string;
  opened_at: string;
  created_at: string;
  updated_at: string;
}

export interface Trade {
  id: number;
  stock_code: string;
  stock_name: string;
  trade_type: string;
  quantity: number;
  price: number;
  amount: number;
  fee: number;
  stamp_duty: number;
  reason?: string;
  position_id?: number;
  plan_id?: number;
  trade_date: string;
  trade_time?: string;
  notes?: string;
  created_at: string;
}

export interface DailyReview {
  id: number;
  review_date: string;
  limit_up_stocks?: Array<{ code: string; name: string; reason?: string; sector?: string }>;
  broken_stocks?: Array<{ code: string; name: string; reason?: string }>;
  yesterday_limit_up_performance?: Array<{ code: string; name: string; change_pct?: number }>;
  hot_sectors?: string[];
  sentiment_cycle?: string;
  tomorrow_strategy?: { position_pct?: number; focus_sectors?: string[] };
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface TargetStock {
  id: number;
  stock_code: string;
  stock_name: string;
  sector?: string;
  reason?: string;
  priority: string;
  review_date: string;
  created_at: string;
}

export interface MonitoredStock {
  id: number;
  stock_code: string;
  stock_name: string;
  monitor_type: string;
  target_price?: number;
  current_price?: number;
  alert_enabled: boolean;
  created_at: string;
}

export interface PriceAlert {
  id: number;
  stock_code: string;
  stock_name: string;
  alert_type: string;
  target_price?: number;
  current_price?: number;
  triggered: boolean;
  triggered_at?: string;
  created_at: string;
}

export interface Account {
  id: number;
  total_assets: number;
  available_cash: number;
  market_value: number;
  today_profit: number;
  today_profit_ratio: number;
  total_profit: number;
  total_profit_ratio: number;
  updated_at: string;
}

export interface RiskConfig {
  id: number;
  max_position_ratio: number;
  daily_loss_limit: number;
  default_stop_loss: number;
  default_take_profit: number;
  max_positions: number;
  updated_at: string;
}

export interface NotificationConfig {
  id: number;
  signal_notify: boolean;
  trade_notify: boolean;
  stop_loss_notify: boolean;
  updated_at: string;
}

export interface AppConfig {
  id: number;
  theme: string;
  updated_at: string;
}

export interface DashboardData {
  total_assets: number;
  available_cash: number;
  market_value: number;
  today_profit: number;
  today_profit_ratio: number;
  total_profit: number;
  total_profit_ratio: number;
  position_count: number;
}

export interface Signal {
  type: string;
  message: string;
  stock_code: string;
}

// ===== 新增类型 =====

export interface Strategy {
  id: number;
  name: string;
  description?: string;
  trade_mode?: string;
  entry_conditions?: Record<string, unknown>;
  exit_conditions?: Record<string, unknown>;
  stop_loss_ratio: number;
  take_profit_ratio: number;
  max_position_ratio: number;
  scenario_handling?: Record<string, unknown>;
  discipline?: Record<string, unknown>;
  is_active: boolean;
  is_template: boolean;
  created_at: string;
  updated_at: string;
}

export interface ReviewListItem {
  id: number;
  review_date: string;
  market_cycle?: string;
  position_advice?: string;
  risk_warning?: string;
  hot_sectors?: string[];
  up_count?: number;
  turnover?: number;
  created_at: string;
}

export interface PositionWithTrades extends Position {
  trades: Trade[];
}

export interface TradeStatistics {
  total_trades: number;
  buy_count: number;
  sell_count: number;
  total_buy_amount: number;
  total_sell_amount: number;
  total_fees: number;
  net_profit: number;
}
