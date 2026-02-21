import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

export const dashboardApi = {
  getSummary: () => api.get('/dashboard/summary'),
  getTodayPlans: () => api.get('/dashboard/today-plans'),
  getPositionsSummary: () => api.get('/dashboard/positions-summary'),
  getSignals: () => api.get('/dashboard/signals'),
};

export const plansApi = {
  getAll: (params?: { status?: string; plan_date?: string }) => api.get('/plans', { params }),
  getById: (id: number) => api.get(`/plans/${id}`),
  create: (data: any) => api.post('/plans', data),
  update: (id: number, data: any) => api.put(`/plans/${id}`, data),
  delete: (id: number) => api.delete(`/plans/${id}`),
  execute: (id: number, result: string) => api.post(`/plans/${id}/execute`, null, { params: { execute_result: result } }),
  abandon: (id: number, reason?: string) => api.post(`/plans/${id}/abandon`, null, { params: { reason } }),
};

export const positionsApi = {
  getAll: (params?: { status?: string }) => api.get('/positions', { params }),
  getById: (id: number) => api.get(`/positions/${id}`),
  create: (data: any) => api.post('/positions', data),
  update: (id: number, data: any) => api.put(`/positions/${id}`, data),
  delete: (id: number) => api.delete(`/positions/${id}`),
  close: (id: number) => api.post(`/positions/${id}/close`),
  updatePrice: (id: number, current_price: number) => api.put(`/positions/${id}/update-price`, null, { params: { current_price } }),
};

export const tradesApi = {
  getAll: (params?: { trade_type?: string; stock_code?: string; start_date?: string; end_date?: string }) => api.get('/trades', { params }),
  getById: (id: number) => api.get(`/trades/${id}`),
  create: (data: any) => api.post('/trades', data),
  update: (id: number, data: any) => api.put(`/trades/${id}`, data),
  delete: (id: number) => api.delete(`/trades/${id}`),
  getStatistics: (params?: { start_date?: string; end_date?: string }) => api.get('/trades/statistics/summary', { params }),
};

export const reviewApi = {
  getAll: (params?: { review_date?: string; sentiment_cycle?: string }) => api.get('/reviews', { params }),
  getById: (id: number) => api.get(`/reviews/${id}`),
  create: (data: any) => api.post('/reviews', data),
  update: (id: number, data: any) => api.put(`/reviews/${id}`, data),
  getLatest: () => api.get('/reviews/latest'),
  getTargetPool: (params?: { review_date?: string; priority?: string }) => api.get('/target-pool', { params }),
  addToTargetPool: (data: any) => api.post('/target-pool', data),
  removeFromTargetPool: (id: number) => api.delete(`/target-pool/${id}`),
};

export const monitorApi = {
  getMonitoredStocks: () => api.get('/monitored-stocks'),
  addMonitoredStock: (data: any) => api.post('/monitored-stocks', data),
  removeMonitoredStock: (id: number) => api.delete(`/monitored-stocks/${id}`),
  getAlerts: (params?: { triggered?: boolean }) => api.get('/alerts', { params }),
  createAlert: (data: { stock_code: string; stock_name: string; alert_type: string; target_price: number }) => api.post('/alerts', null, { params: data }),
  triggerAlert: (id: number, current_price: number) => api.post(`/alerts/${id}/trigger`, null, { params: { current_price } }),
  deleteAlert: (id: number) => api.delete(`/alerts/${id}`),
  getPrice: (stock_code: string) => api.get(`/price/${stock_code}`),
  updatePrice: (id: number, current_price: number) => api.put(`/monitored-stocks/${id}/update-price`, null, { params: { current_price } }),
};

export const settingsApi = {
  getAccount: () => api.get('/account'),
  updateAccount: (data: any) => api.put('/account', data),
  getRiskConfig: () => api.get('/risk-config'),
  updateRiskConfig: (data: any) => api.put('/risk-config', data),
  getNotificationConfig: () => api.get('/notification-config'),
  updateNotificationConfig: (data: any) => api.put('/notification-config', data),
  getAppConfig: () => api.get('/app-config'),
  updateAppConfig: (data: any) => api.put('/app-config', data),
  getAll: () => api.get('/all-settings'),
};

export default api;
