import request from './request'

export interface Indicator {
  id: number
  name: string
  code: string
  type: string
  params?: Record<string, number>
  createdAt?: string
  updatedAt?: string
}

export interface IndicatorRunParams {
  indicator: string
  params: Record<string, number>
  symbol: string
  exchange?: string
  startDate?: string
  endDate?: string
}

export interface IndicatorResult {
  indicator: string
  values: { time: string; [key: string]: number | string }[]
}

export const indicatorApi = {
  getIndicators: () =>
    request.get<{ data: Indicator[] }>('/indicator/getIndicators'),
  saveIndicator: (data: Partial<Indicator>) =>
    request.post<{ data: Indicator }>('/indicator/saveIndicator', data),
  deleteIndicator: (id: number) =>
    request.post('/indicator/deleteIndicator', { id }),
  getIndicatorParams: (indicator: string) =>
    request.get('/indicator/getIndicatorParams', { params: { indicator } }),
  verifyCode: (code: string) =>
    request.post('/indicator/verifyCode', { code }),
  aiGenerate: (data: { description: string; symbol?: string }) =>
    request.post<{ data: { code: string } }>('/indicator/aiGenerate', data),
  callIndicator: (data: IndicatorRunParams) =>
    request.post<{ data: IndicatorResult }>('/indicator/callIndicator', data),
}
