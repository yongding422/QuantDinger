import request from './request'

export interface MarketConfig {
  exchanges: { id: string; name: string }[]
  marketTypes: string[]
}

export interface Symbol {
  symbol: string
  name?: string
  exchange?: string
}

export interface WatchlistItem {
  id: number
  symbol: string
  exchange: string
  price?: number
  change24h?: number
  changePercent24h?: number
  volume24h?: number
  addedAt?: string
}

export interface GlobalMarketOverview {
  fearGreed?: { value: number; classification: string }
  indices: { name: string; value: number; change: number }[]
  forex: { pair: string; rate: number; change: number }[]
  crypto: { name: string; symbol: string; price: number; change24h: number; marketCap: number }[]
  commodities: { name: string; price: number; change: number }[]
}

export interface HeatmapItem {
  symbol: string
  name?: string
  price?: number
  changePercent: number
  volume?: number
  category?: string
}

export const marketApi = {
  // Config
  getConfig: () => request.get<{ data: MarketConfig }>('/market/config'),

  // Symbols
  searchSymbols: (q: string, exchange?: string) =>
    request.get<{ data: Symbol[] }>('/market/symbols/search', { params: { q, exchange } }),
  getHotSymbols: (exchange?: string) =>
    request.get<{ data: Symbol[] }>('/market/symbols/hot', { params: { exchange } }),

  // Watchlist (JWT required)
  getWatchlist: () => request.get<{ data: WatchlistItem[] }>('/market/watchlist/get'),
  addToWatchlist: (symbol: string, exchange: string) =>
    request.post('/market/watchlist/add', { symbol, exchange }),
  removeFromWatchlist: (symbol: string, exchange: string) =>
    request.post('/market/watchlist/remove', { symbol, exchange }),
  getWatchlistPrices: (symbols: string[]) =>
    request.get<{ data: Record<string, { price: number; change24h: number }> }>('/market/watchlist/prices', { params: { symbols: symbols.join(',') } }),

  // Price
  getPrice: (symbol: string, exchange?: string) =>
    request.get('/market/price', { params: { symbol, exchange } }),
}

export const globalMarketApi = {
  getOverview: () => request.get<{ data: GlobalMarketOverview }>('/global-market/overview'),
  getHeatmap: (category?: string) =>
    request.get<{ data: HeatmapItem[] }>('/global-market/heatmap', { params: { category } }),
  getNews: (params?: { page?: number; pageSize?: number }) =>
    request.get('/global-market/news', { params }),
  getCalendar: (params?: { startDate?: string; endDate?: string }) =>
    request.get('/global-market/calendar', { params }),
  getSentiment: () => request.get('/global-market/sentiment'),
  getOpportunities: () => request.get('/global-market/opportunities'),
  refreshCache: () => request.post('/global-market/refresh'),
}
