import request from './request'

export interface PolymarketMarket {
  id: string
  question: string
  description?: string
  probabilityYes: number
  probabilityNo: number
  volume?: number
  volumeUsd?: number
  liquidity?: number
  resolve?: string
  resolved?: boolean
  closed?: boolean
  createdAt?: string
  markets?: PolymarketMarket[]
}

export interface PolymarketAnalysis {
  id?: number
  marketId: string
  question: string
  probabilityYes: number
  probabilityNo: number
  volume?: number
  recommendation?: string
  reasoning?: string
  riskLevel?: string
  createdAt?: string
}

export interface PolymarketAnalyzeParams {
  marketId?: string
  question?: string
  probability?: number
}

export const polymarketApi = {
  getMarkets: (params?: { limit?: number; trending?: boolean }) =>
    request.get<{ data: PolymarketMarket[] }>('/polymarket/markets', { params }),
  getTrendingMarkets: (limit = 10) =>
    request.get<{ data: PolymarketMarket[] }>('/polymarket/trending', { params: { limit } }),
  analyzeMarket: (data: PolymarketAnalyzeParams) =>
    request.post<{ data: PolymarketAnalysis }>('/polymarket/analyze', data),
  getAnalysisHistory: (params?: { page?: number; pageSize?: number }) =>
    request.get<{ data: { items: PolymarketAnalysis[]; total: number } }>('/polymarket/history', { params }),
  getMarketDetails: (marketId: string) =>
    request.get<{ data: PolymarketMarket }>(`/polymarket/market/${marketId}`),
  bulkAnalyze: (marketIds: string[]) =>
    request.post<{ data: PolymarketAnalysis[] }>('/polymarket/bulk-analyze', { marketIds }),
}
