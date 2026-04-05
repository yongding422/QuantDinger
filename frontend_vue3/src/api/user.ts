import request from './request'

export interface UserProfile {
  id: number
  username: string
  nickname: string
  email?: string
  avatar: string
  timezone: string
  role: { id: string; permissions: string[] }
  status?: string
  credits?: number
  createdAt?: string
  lastLogin?: string
}

export interface NotificationSettings {
  emailEnabled: boolean
  telegramEnabled: boolean
  strategyAlerts: boolean
  portfolioAlerts: boolean
  marketAlerts: boolean
  aiAnalysisAlerts: boolean
}

export const userApi = {
  getProfile: () => request.get<{ data: UserProfile }>('/users/profile'),
  updateProfile: (data: Partial<{ nickname: string; timezone: string }>) =>
    request.put('/users/profile/update', data),
  getNotificationSettings: () => request.get<{ data: NotificationSettings }>('/users/notification-settings'),
  updateNotificationSettings: (data: Partial<NotificationSettings>) =>
    request.put('/users/notification-settings', data),
  testNotification: () => request.post('/users/notification-settings/test', {}),
  changePassword: (code: string, newPassword: string) =>
    request.post('/users/change-password', { code, new_password: newPassword }),
  getCreditsLog: (params?: { page?: number; pageSize?: number }) =>
    request.get('/users/my-credits-log', { params }),
  getReferrals: () => request.get('/users/my-referrals'),
}
