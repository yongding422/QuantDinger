import request from './request'

export interface Position {
  id: number
  symbol: string
  exchange: string
  side: 'long' | 'short' | 'spot'
  entryPrice: number
  currentPrice?: number
  quantity: number
  pnl?: number
  pnlPercent?: number
  group?: string
  note?: string
  createdAt?: string
}

export interface PortfolioMonitor {
  id: number
  name: string
  exchange: string
  symbol: string
  strategyType: string
  status: 'running' | 'stopped'
  lastRun?: string
}

export interface Alert {
  id: number
  symbol: string
  condition: string  // e.g. ">100000", "<0.5"
  triggered: boolean
  triggeredAt?: string
  createdAt?: string
}

export interface PortfolioSummary {
  totalValue: number
  totalPnl: number
  totalPositions: number
}

export const portfolioApi = {
  // Positions
  getPositions: () => request.get<{ data: Position[] }>('/portfolio/positions'),
  addPosition: (data: Partial<Position>) => request.post('/portfolio/positions', data),
  updatePosition: (id: number, data: Partial<Position>) => request.put(`/portfolio/positions/${id}`, data),
  deletePosition: (id: number) => request.delete(`/portfolio/positions/${id}`),
  // Monitors
  getMonitors: () => request.get<{ data: PortfolioMonitor[] }>('/portfolio/monitors'),
  createMonitor: (data: Partial<PortfolioMonitor>) => request.post('/portfolio/monitors', data),
  updateMonitor: (id: number, data: Partial<PortfolioMonitor>) => request.put(`/portfolio/monitors/${id}`, data),
  deleteMonitor: (id: number) => request.delete(`/portfolio/monitors/${id}`),
  runMonitor: (id: number) => request.post(`/portfolio/monitors/${id}/run`, {}),
  // Alerts
  getAlerts: () => request.get<{ data: Alert[] }>('/portfolio/alerts'),
  createAlert: (data: Partial<Alert>) => request.post('/portfolio/alerts', data),
  updateAlert: (id: number, data: Partial<Alert>) => request.put(`/portfolio/alerts/${id}`, data),
  deleteAlert: (id: number) => request.delete(`/portfolio/alerts/${id}`),
  // Groups
  getGroups: () => request.get('/portfolio/groups'),
  renameGroup: (oldName: string, newName: string) => request.post('/portfolio/groups/rename', { oldName, newName }),
  // Summary
  getSummary: () => request.get<{ data: PortfolioSummary }>('/portfolio/summary'),
}
