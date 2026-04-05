import request from './request'

export interface Balance {
  asset: string
  free: number
  locked: number
  total: number
}

export interface Position {
  symbol: string
  side: 'long' | 'short'
  size: number
  entryPrice: number
  markPrice: number
  unrealizedPnl: number
  leverage: number
}

export interface Order {
  id: string
  symbol: string
  side: 'buy' | 'sell'
  type: 'market' | 'limit' | 'stop'
  price?: number
  quantity: number
  status: 'pending' | 'filled' | 'cancelled' | 'rejected'
  filledQty: number
  avgFillPrice?: number
  commission: number
  createdAt: string
}

export interface OrderParams {
  exchange: string
  symbol: string
  side: 'buy' | 'sell'
  type: 'market' | 'limit'
  price?: number
  quantity: number
}

export const quickTradeApi = {
  // Balance
  getBalance: (exchange: string) =>
    request.get<{ data: Balance[] }>('/quick-trade/balance', { params: { exchange } }),

  // Position
  getPosition: (exchange: string, symbol: string) =>
    request.get<{ data: Position | null }>('/quick-trade/position', { params: { exchange, symbol } }),

  // Place order
  placeOrder: (data: OrderParams) =>
    request.post<{ data: Order }>('/quick-trade/place-order', data),

  // Close position
  closePosition: (exchange: string, symbol: string) =>
    request.post('/quick-trade/close-position', { exchange, symbol }),

  // Order history
  getHistory: (params?: { page?: number; pageSize?: number; exchange?: string; symbol?: string }) =>
    request.get<{ data: { items: Order[]; total: number } }>('/quick-trade/history', { params }),
}
