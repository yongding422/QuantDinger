import request from './request'

export interface BacktestParams {
  indicator: string
  symbol: string
  exchange?: string
  startDate: string
  endDate: string
  initialCapital?: number
}

export interface BacktestResult {
  id?: number
  indicator: string
  symbol: string
  startDate: string
  endDate: string
  initialCapital: number
  finalCapital: number
  totalTrades: number
  winRate: number
  profit: number
  profitPercent: number
  sharpeRatio?: number
  maxDrawdown: number
  profitFactor?: number
  createdAt?: string
}

export interface PrecisionInfo {
  indicator: string
  avgDiff: number
  hitRate: number
  sampleSize: number
}

export const backtestApi = {
  runBacktest: (data: BacktestParams) =>
    request.post<{ data: BacktestResult }>('/indicator/backtest', data),
  getHistory: (params?: { page?: number; pageSize?: number }) =>
    request.get<{ data: { items: BacktestResult[]; total: number } }>('/indicator/backtest/history', { params }),
  getRun: (runId: number) =>
    request.get<{ data: BacktestResult }>(`/indicator/backtest/get?runId=${runId}`),
  getPrecisionInfo: () =>
    request.get<{ data: PrecisionInfo[] }>('/indicator/backtest/precision-info'),
  aiAnalyze: (runId: number) =>
    request.post<{ data: { analysis: string } }>('/indicator/backtest/aiAnalyze', { runId }),
}
