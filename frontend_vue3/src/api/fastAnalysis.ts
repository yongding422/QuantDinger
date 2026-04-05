import request from './request'

export interface FastAnalysisResult {
  id?: number
  symbol: string
  confidence: number       // 0-100
  confirmation: 'high' | 'medium' | 'low'
  recommendation: string
  entryPrice?: number
  targetPrice?: number
  stopLoss?: number
  analysis: string
  factors: string[]
  createdAt?: string
}

export interface SimilarPattern {
  date: string
  symbol: string
  similarity: number
  outcome: string
}

export interface PerformanceStats {
  totalAnalyses: number
  avgConfidence: number
  accuracy?: number
}

export const fastAnalysisApi = {
  analyze: (data: { symbol: string; exchange?: string }) =>
    request.post<{ data: FastAnalysisResult }>('/fast-analysis/analyze', data),
  getHistory: (symbol?: string) =>
    request.get<{ data: FastAnalysisResult[] }>('/fast-analysis/history', { params: { symbol } }),
  getAllHistory: (params?: { page?: number; pageSize?: number }) =>
    request.get<{ data: { items: FastAnalysisResult[]; total: number } }>('/fast-analysis/history/all', { params }),
  deleteHistory: (memoryId: number) =>
    request.delete(`/fast-analysis/history/${memoryId}`),
  submitFeedback: (data: { analysisId: number; helpful: boolean; comment?: string }) =>
    request.post('/fast-analysis/feedback', data),
  getPerformance: () =>
    request.get<{ data: PerformanceStats }>('/fast-analysis/performance'),
  getSimilarPatterns: (symbol: string) =>
    request.get<{ data: SimilarPattern[] }>('/fast-analysis/similar-patterns', { params: { symbol } }),
}
