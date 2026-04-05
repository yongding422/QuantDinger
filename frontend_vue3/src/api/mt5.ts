import request from './request'

export interface MT5Status {
  connected: boolean
  serverVersion?: string
  serverTime?: string
  error?: string
}

export interface MT5Account {
  accountId: string
  accountType: string
  balance: number
  equity: number
  margin: number
  freeMargin: number
  leverage: number
  currency: string
}

export interface MT5Position {
  ticket: number
  symbol: string
  type: 'buy' | 'sell'
  volume: number
  openPrice: number
  currentPrice: number
  stopLoss: number
  takeProfit: number
  profit: number
  comment: string
  openTime: string
}

export interface MT5Order {
  ticket: number
  symbol: string
  type: 'buy' | 'sell'
  volume: number
  price: number
  status: string
  typeFilling: string
  createdTime: string
  filledVolume: number
  averagePrice: number
}

export interface MT5Symbol {
  symbol: string
  description: string
  bid: number
  ask: number
  last: number
  high: number
  low: number
  volume: number
  digits: number
}

export const mt5Api = {
  getStatus: () => request.get<{ data: MT5Status }>('/mt5/status'),
  connect: () => request.post('/mt5/connect'),
  disconnect: () => request.post('/mt5/disconnect'),
  getAccount: () => request.get<{ data: MT5Account }>('/mt5/account'),
  getPositions: () => request.get<{ data: MT5Position[] }>('/mt5/positions'),
  getOrders: () => request.get<{ data: MT5Order[] }>('/mt5/orders'),
  getSymbols: () => request.get<{ data: MT5Symbol[] }>('/mt5/symbols'),
  placeOrder: (data: {
    symbol: string
    action: 'buy' | 'sell'
    volume: number
    orderType?: string
    price?: number
    stopLoss?: number
    takeProfit?: number
  }) => request.post('/mt5/place-order', data),
  closePosition: (ticket: number, volume?: number) =>
    request.post('/mt5/close-position', { ticket, volume }),
  cancelOrder: (ticket: number) => request.delete(`/mt5/orders/${ticket}`),
  getQuote: (symbol: string) =>
    request.get<{ data: MT5Symbol }>('/mt5/quote', { params: { symbol } }),
}
