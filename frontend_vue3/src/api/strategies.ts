import request from './request'

export type StrategyStatus = 'running' | 'stopped' | 'pending'
export type MarketType = 'spot' | 'margin' | 'futures' | 'stock' | 'forex' | 'crypto'
export type Side = 'buy' | 'sell'

export interface StrategyConfig {
  stopLoss?: number
  takeProfit?: number
  maxPositions?: number
  leverage?: number
  amount?: number
  indicators?: Record<string, unknown>[]
  triggers?: Record<string, unknown>[]
}

export interface Strategy {
  id: number
  name: string
  status: StrategyStatus
  exchange: string
  symbol: string
  marketType: MarketType
  config: StrategyConfig
  createdAt?: string
  updatedAt?: string
}

export interface Trade {
  id: number
  symbol: string
  side: Side
  price: number
  quantity: number
  time: string
  pnl?: number
  commission?: number
}

export interface EquityCurvePoint {
  date: string
  equity: number
  drawdown?: number
}

export interface BacktestResult {
  id: number
  strategyId: number
  initialCapital: number
  finalCapital: number
  profit: number
  profitPercent: number
  winRate: number
  sharpeRatio: number
  maxDrawdown: number
  maxDrawdownPercent: number
  totalTrades: number
  winningTrades: number
  losingTrades: number
  avgProfit: number
  avgLoss: number
  avgTrade: number
  profitFactor: number
  status: 'completed' | 'failed' | 'running'
  startDate: string
  endDate: string
  createdAt: string
  equityCurve?: EquityCurvePoint[]
  trades?: Trade[]
}

export interface BacktestParams {
  startDate: string
  endDate: string
  initialCapital: number
}

export interface Notification {
  id: number
  type: string
  title: string
  message: string
  read: boolean
  createdAt: string
  strategyId?: number
}

export interface StrategyUpdatePayload {
  name?: string
  status?: StrategyStatus
  config?: Partial<StrategyConfig>
}

export const strategiesApi = {
  list: () => request.get<{ data: Strategy[] }>('/strategies'),
  getById: (id: number) => request.get<{ data: Strategy }>(`/strategies/${id}`),
  create: (data: Omit<Strategy, 'id'>) => request.post<{ data: Strategy }>('/strategies', data),
  update: (id: number, data: StrategyUpdatePayload) =>
    request.put<{ data: Strategy }>(`/strategies/${id}`, data),
  delete: (id: number) => request.delete(`/strategies/${id}`),
  start: (id: number) => request.post<{ data: Strategy }>(`/strategies/${id}/start`),
  stop: (id: number) => request.post<{ data: Strategy }>(`/strategies/${id}/stop`),

  getTrades: (id: number) => request.get<{ data: Trade[] }>(`/strategies/${id}/trades`),
  getEquityCurve: (id: number) =>
    request.get<{ data: EquityCurvePoint[] }>(`/strategies/${id}/equity-curve`),
  getBacktestHistory: (id: number) =>
    request.get<{ data: BacktestResult[] }>(`/strategies/${id}/backtests`),
  runBacktest: (id: number, params: BacktestParams) =>
    request.post<{ data: BacktestResult }>(`/strategies/${id}/backtest`, params),

  getNotifications: () => request.get<{ data: Notification[] }>('/notifications'),
  markRead: (id: number) => request.put(`/notifications/${id}/read`),
  markAllRead: () => request.put('/notifications/read-all'),
}
