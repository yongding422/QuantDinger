import request from './request'

export interface Plan {
  id: string
  name: string
  price: number
  interval: 'month' | 'year'
  features: string[]
  apiCallsLimit: number
  isCurrentPlan?: boolean
}

export interface UsageStats {
  apiCallsUsed: number
  apiCallsLimit: number
  storageUsedMb: number
  storageLimitMb: number
  backtestsRun: number
  backtestsLimit: number
}

export interface Invoice {
  id: string
  amount: number
  status: 'paid' | 'pending' | 'failed'
  date: string
  description: string
}

export const billingApi = {
  getPlans: () =>
    request.get<{ data: Plan[] }>('/billing/plans'),
  getCurrentPlan: () =>
    request.get<{ data: Plan }>('/billing/current'),
  getUsage: () =>
    request.get<{ data: UsageStats }>('/billing/usage'),
  getInvoices: (params?: { page?: number; pageSize?: number }) =>
    request.get<{ data: { items: Invoice[]; total: number } }>('/billing/invoices', { params }),
  subscribe: (planId: string) =>
    request.post('/billing/subscribe', { planId }),
  cancelSubscription: () =>
    request.post('/billing/cancel'),
}
