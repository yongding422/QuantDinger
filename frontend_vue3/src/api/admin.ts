import request from './request'

export interface User {
  id: number
  username: string
  email: string
  role: 'admin' | 'user' | 'guest'
  isActive: boolean
  plan?: string
  createdAt: string
  lastLogin?: string
}

export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'down'
  uptime: number
  cpuPercent: number
  memoryPercent: number
  diskPercent: number
  activeConnections: number
  version: string
  services: { name: string; status: 'up' | 'down' | 'degraded'; latencyMs?: number }[]
}

export interface AuditLog {
  id: number
  userId: number
  userName: string
  action: string
  resource: string
  timestamp: string
  ipAddress?: string
}

export interface SystemMetrics {
  totalUsers: number
  activeUsers: number
  totalTrades: number
  totalApiCalls: number
  dailyActiveUsers: { date: string; count: number }[]
}

export const adminApi = {
  // Users
  getUsers: (params?: { page?: number; pageSize?: number; search?: string }) =>
    request.get<{ data: { items: User[]; total: number } }>('/admin/users', { params }),

  getUser: (id: number) =>
    request.get<{ data: User }>(`/admin/users/${id}`),

  updateUser: (id: number, data: Partial<Pick<User, 'role' | 'isActive' | 'plan'>>) =>
    request.put<{ data: User }>(`/admin/users/${id}`, data),

  deleteUser: (id: number) =>
    request.delete(`/admin/users/${id}`),

  resetUserPassword: (id: number, newPassword: string) =>
    request.post(`/admin/users/${id}/reset-password`, { new_password: newPassword }),

  // System health & metrics
  getSystemHealth: () =>
    request.get<{ data: SystemHealth }>('/admin/system/health'),

  getSystemMetrics: () =>
    request.get<{ data: SystemMetrics }>('/admin/system/metrics'),

  // Audit logs
  getAuditLogs: (params?: { page?: number; pageSize?: number; userId?: number; action?: string }) =>
    request.get<{ data: { items: AuditLog[]; total: number } }>('/admin/audit-logs', { params }),
}
