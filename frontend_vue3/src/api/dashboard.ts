import request from './request'

export interface DashboardSummary {
  totalBalance: number
  todayPnl: number
  totalPnl: number
  runningStrategies: number
  totalStrategies: number
  totalPositions: number
  dayChart: { date: string; value: number }[]
}

export interface Trade {
  id: number
  symbol: string
  side: 'buy' | 'sell'
  price: number
  quantity: number
  time: string
  pnl?: number
}

export interface PendingOrder {
  id: number
  symbol: string
  side: 'buy' | 'sell'
  type: 'market' | 'limit'
  price: number
  quantity: number
  time: string
}

export const dashboardApi = {
  getSummary: () => request.get<{ data: DashboardSummary }>('/dashboard/summary'),
  getRecentTrades: (limit = 10) => request.get<{ data: Trade[] }>('/dashboard/recentTrades', { params: { limit } }),
  getPendingOrders: () => request.get<{ data: PendingOrder[] }>('/dashboard/pendingOrders'),
  deletePendingOrder: (orderId: number) => request.delete(`/dashboard/pendingOrders/${orderId}`),
}
