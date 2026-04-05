import request from './request'

// ─── Shared types ──────────────────────────────────────────────────────────────

export interface StrategyIndicator {
  name: string
  params: Record<string, number>
}

export interface StrategyTrigger {
  indicator: string
  condition: string  // e.g. "crosses_above", ">"
  value: number
  params?: Record<string, number>
}

export interface StrategyRiskControl {
  stopLoss?: number      // percentage, e.g. 2.0
  takeProfit?: number     // percentage
  maxPositions?: number
  maxDrawdown?: number    // percentage
}

export interface StrategyConfig {
  exchange: string
  symbol: string
  marketType: 'spot' | 'margin' | 'futures'
  indicators: StrategyIndicator[]
  triggers: StrategyTrigger[]
  positionSizing: {
    amount?: number
    leverage?: number
    mode?: 'fixed' | 'percentage'
  }
  riskControl?: StrategyRiskControl
  virtual?: boolean       // virtual position mode
}

export interface Strategy {
  id: number
  name: string
  status: 'running' | 'stopped' | 'error'
  exchange: string
  symbol: string
  marketType: string
  createdAt?: string
  updatedAt?: string
  // full config nested
  config?: StrategyConfig
}

export interface StrategyTrade {
  id: number
  strategyId: number
  symbol: string
  side: 'buy' | 'sell'
  price: number
  quantity: number
  pnl?: number
  commission?: number
  time: string
}

export interface StrategyNotification {
  id: number
  strategyId: number
  type: string
  message: string
  read: boolean
  createdAt: string
}

export interface BacktestResult {
  id: number
  strategyId: number
  symbol: string
  startDate: string
  endDate: string
  totalTrades: number
  winRate: number
  profit: number
  sharpeRatio?: number
  maxDrawdown: number
  profitFactor?: number
}

export interface EquityPoint {
  date: string
  equity: number
  drawdown?: number
}

// ─── API ───────────────────────────────────────────────────────────────────────

export const strategyApi = {
  // List & CRUD
  list: (params?: { page?: number; pageSize?: number }) =>
    request.get<{ data: Strategy[] }>('/strategies/list', { params }),
  get: (id: number) =>
    request.get<{ data: Strategy }>(`/strategies/${id}`),
  create: (data: Partial<StrategyConfig & { name: string }>) =>
    request.post<{ data: { id: number } }>('/strategies/create', data),
  update: (id: number, data: Partial<StrategyConfig & { name: string }>) =>
    request.put(`/strategies/${id}`, data),
  delete: (id: number) =>
    request.delete(`/strategies/${id}`),

  // Batch
  batchCreate: (strategies: Partial<StrategyConfig & { name: string }>[]) =>
    request.post<{ data: { ids: number[] } }>('/strategies/batch_create', { strategies }),
  batchStart: (ids: number[]) =>
    request.post('/strategies/batch_start', { ids }),
  batchStop: (ids: number[]) =>
    request.post('/strategies/batch_stop', { ids }),
  batchDelete: (ids: number[]) =>
    request.delete('/strategies/batch_delete', { ids }),

  // Control
  start: (id: number) =>
    request.post(`/strategies/${id}/start`),
  stop: (id: number) =>
    request.post(`/strategies/${id}/stop`),

  // Data
  getTrades: (id: number, params?: { page?: number; pageSize?: number }) =>
    request.get<{ data: StrategyTrade[] }>(`/strategies/${id}/trades`, { params }),
  getPositions: (id: number) =>
    request.get<{ data: unknown[] }>(`/strategies/${id}/positions`),
  getEquityCurve: (id: number, params?: { startDate?: string; endDate?: string }) =>
    request.get<{ data: EquityPoint[] }>(`/strategies/${id}/equityCurve`, { params }),
  getPerformance: (id: number) =>
    request.get(`/strategies/${id}/performance`),

  // Backtest
  runBacktest: (id: number, params?: { startDate?: string; endDate?: string; initialCapital?: number }) =>
    request.post<{ data: BacktestResult }>(`/strategies/${id}/backtest`, params || {}),
  getBacktestHistory: (id: number) =>
    request.get<{ data: BacktestResult[] }>(`/strategies/${id}/backtest_history`),
  getBacktestRun: (id: number, runId: number) =>
    request.get<{ data: BacktestResult }>(`/strategies/${id}/backtest_history/${runId}`),

  // Notifications
  getNotifications: (params?: { page?: number; pageSize?: number }) =>
    request.get<{ data: StrategyNotification[] }>('/strategies/notifications', { params }),
  getUnreadCount: () =>
    request.get<{ data: { count: number } }>('/strategies/unread_count'),
  markRead: (id: number) =>
    request.post(`/strategies/notifications/${id}/read`),
  markAllRead: () =>
    request.post('/strategies/notifications/read_all'),
  clearNotifications: (id: number) =>
    request.delete(`/strategies/notifications/${id}`),

  // Code helpers
  testConnection: (exchange: string) =>
    request.post('/strategies/test_connection', { exchange }),
  getSymbols: (exchange: string, marketType?: string) =>
    request.get<{ data: string[] }>('/strategies/symbols', { params: { exchange, marketType } }),
  verifyCode: (code: string) =>
    request.post('/strategies/verify_code', { code }),
  previewCompile: (id: number) =>
    request.post(`/strategies/${id}/preview_compile`),
}
