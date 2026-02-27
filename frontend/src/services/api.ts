import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const marketApi = {
  getIndices: () => api.get('/market/indices'),
  getLimitUp: () => api.get('/market/limit-up'),
  getDragonList: () => api.get('/market/dragon-list'),
  getCapitalFlow: () => api.get('/market/capital-flow'),
  getNorthMoney: () => api.get('/market/north-money'),
  getSectorStrength: () => api.get('/market/sector-strength'),
  getNews: () => api.get('/market/news'),
  getSentiment: () => api.get('/market/sentiment'),
};

export const watchStockApi = {
  getAll: () => api.get('/watch-stock'),
  create: (data: any) => api.post('/watch-stock', data),
  update: (id: number, data: any) => api.put(`/watch-stock/${id}`, data),
  delete: (id: number) => api.delete(`/watch-stock/${id}`),
};

export const tradeApi = {
  getAll: (params?: {
    trade_type?: string;
    stock_code?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }) => api.get('/trades', { params }),
  getById: (id: number) => api.get(`/trades/${id}`),
  create: (data: any) => api.post('/trades', data),
  update: (id: number, data: any) => api.put(`/trades/${id}`, data),
  delete: (id: number) => api.delete(`/trades/${id}`),
  getSummary: (params?: { start_date?: string; end_date?: string }) =>
    api.get('/trades/summary', { params }),
};

export const tradesApi = tradeApi;

export const planApi = {
  getPre: () => api.get('/plan/pre'),
  savePre: (data: any) => api.put('/plan/pre', data),
  getPost: () => api.get('/plan/post'),
  savePost: (data: any) => api.put('/plan/post', data),
};

export const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary'),
};

export const positionApi = {
  getAll: (params?: { status?: string }) => api.get('/positions', { params }),
  getById: (id: number) => api.get(`/positions/${id}`),
  create: (data: any) => api.post('/positions', data),
  update: (id: number, data: any) => api.put(`/positions/${id}`, data),
  delete: (id: number) => api.delete(`/positions/${id}`),
  close: (id: number) => api.post(`/positions/${id}/close`),
  updatePrice: (id: number, currentPrice: number) =>
    api.put(`/positions/${id}/update-price`, null, { params: { current_price: currentPrice } }),
};

export const positionsApi = positionApi;

export const alertApi = {
  getAll: () => api.get('/alerts'),
  create: (data: any) => api.post('/alerts', data),
  trigger: (id: number, currentPrice: number) => api.post(`/alerts/${id}/trigger`, null, { params: { current_price: currentPrice } }),
  delete: (id: number) => api.delete(`/alerts/${id}`),
};

export const strategyApi = {
  getAll: (params?: { is_active?: boolean; is_template?: boolean; trade_mode?: string }) =>
    api.get('/strategies', { params }),
  getById: (id: number) => api.get(`/strategies/${id}`),
  create: (data: any) => api.post('/strategies', data),
  update: (id: number, data: any) => api.put(`/strategies/${id}`, data),
  delete: (id: number) => api.delete(`/strategies/${id}`),
  copy: (id: number, newName?: string) =>
    api.post(`/strategies/${id}/copy`, null, { params: { new_name: newName } }),
  getModes: () => api.get('/strategies/modes/list'),
};

export const reviewApi = {
  getAll: (params?: {
    review_date?: string;
    market_cycle?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }) => api.get('/reviews', { params }),
  getById: (id: number) => api.get(`/reviews/${id}`),
  create: (data: any) => api.post('/reviews', data),
  update: (id: number, data: any) => api.put(`/reviews/${id}`, data),
  delete: (id: number) => api.delete(`/reviews/${id}`),
  getLatest: () => api.get('/reviews/latest'),
  getCount: (params?: { start_date?: string; end_date?: string }) =>
    api.get('/reviews/count', { params }),
};

export const settingsApi = {
  getAccount: () => api.get('/settings/account'),
  updateAccount: (data: any) => api.put('/settings/account', data),
  getRisk: () => api.get('/settings/risk'),
  updateRisk: (data: any) => api.put('/settings/risk', data),
  getNotification: () => api.get('/settings/notification'),
  updateNotification: (data: any) => api.put('/settings/notification', data),
  getAll: async () => {
    const [account, risk, notification] = await Promise.all([
      api.get('/settings/account'),
      api.get('/settings/risk'),
      api.get('/settings/notification'),
    ]);
    return {
      data: {
        account: {
          total_assets: account.data.initial_capital,
          available_cash: account.data.current_capital,
        },
        risk_config: {
          max_position_ratio: risk.data.max_single_stock,
          max_positions: risk.data.max_trades_per_day,
          daily_loss_limit: risk.data.stop_loss_ratio,
          default_stop_loss: -risk.data.stop_loss_ratio,
          default_take_profit: risk.data.take_profit_ratio,
          weekly_loss_limit: 10,
          monthly_loss_limit: 20,
          trailing_stop: false,
          trailing_stop_percent: 3,
          position_size_by_win_rate: true,
          min_win_rate: 45,
          allow_add_position: false,
          max_add_position: 1,
          force_close_on_risk: true,
          cooling_period_minutes: 30,
        },
        notification_config: {
          signal_notify: notification.data.enable_price_alert,
          trade_notify: notification.data.enable_trade_alert,
          stop_loss_notify: notification.data.enable_price_alert,
        },
        app_config: {
          theme: 'light',
        },
      },
    };
  },
};

// ==================== 持仓/成交扩展 API ====================

// 持仓扩展 API (支持止盈止损)
export const tradingPositionApi = {
  setStopLoss: (id: number, stopLoss: number) =>
    api.put(`/positions/${id}/stop-loss`, null, { params: { stop_loss: stopLoss } }),
  setTakeProfit: (id: number, takeProfit: number) =>
    api.put(`/positions/${id}/take-profit`, null, { params: { take_profit: takeProfit } }),
  close: (id: number, closePrice: number) =>
    api.post(`/positions/${id}/close`, null, { params: { close_price: closePrice } }),
  getStats: () => api.get('/positions/stats/summary'),
};

export default api;
