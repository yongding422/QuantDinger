import request from './request'

export interface IBKRStatus {
  connected: boolean
  serverVersion?: string
  serverTime?: string
  error?: string
}

export interface IBKRAccount {
  accountId: string
  accountType: string
  cash: number
  buyingPower: number
  equity: number
  positionsValue: number
}

export interface IBKRPosition {
  symbol: string
  description: string
  exchange: string
  quantity: number
  avgCost: number
  lastPrice: number
  marketValue: number
  unrealizedPnl: number
}

export interface IBKROrder {
  id: number
  symbol: string
  action: 'BUY' | 'SELL'
  orderType: string
  quantity: number
  lmtPrice?: number
  status: string
  filledQuantity: number
  avgFillPrice?: number
  submittedAt: string
}

export interface IBKRQuote {
  symbol: string
  bid: number
  ask: number
  last: number
  volume: number
}

export const ibkrApi = {
  getStatus: () => request.get<{ data: IBKRStatus }>('/ibkr/status'),
  connect: () => request.post('/ibkr/connect'),
  disconnect: () => request.post('/ibkr/disconnect'),
  getAccount: () => request.get<{ data: IBKRAccount }>('/ibkr/account'),
  getPositions: () => request.get<{ data: IBKRPosition[] }>('/ibkr/positions'),
  getOrders: () => request.get<{ data: IBKROrder[] }>('/ibkr/orders'),
  placeOrder: (data: {
    symbol: string
    action: 'BUY' | 'SELL'
    quantity: number
    orderType?: string
    lmtPrice?: number
  }) => request.post('/ibkr/place-order', data),
  cancelOrder: (orderId: number) => request.delete(`/ibkr/orders/${orderId}`),
  getQuote: (symbol: string) =>
    request.get<{ data: IBKRQuote }>('/ibkr/quote', { params: { symbol } }),
}
