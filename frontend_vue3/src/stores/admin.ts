import { defineStore } from 'pinia'
import { ref } from 'vue'
import { adminApi, type User, type SystemHealth, type SystemMetrics, type AuditLog } from '@/api/admin'

export const useAdminStore = defineStore('admin', () => {
  // Users
  const users = ref<User[]>([])
  const usersTotal = ref(0)
  const usersLoading = ref(false)

  // System health
  const systemHealth = ref<SystemHealth | null>(null)
  const healthLoading = ref(false)

  // System metrics
  const systemMetrics = ref<SystemMetrics | null>(null)
  const metricsLoading = ref(false)

  // Audit logs
  const auditLogs = ref<AuditLog[]>([])
  const auditLogsTotal = ref(0)
  const auditLogsLoading = ref(false)

  async function fetchUsers(params?: { page?: number; pageSize?: number; search?: string }) {
    usersLoading.value = true
    try {
      const res = await adminApi.getUsers(params)
      const d = res.data as { data?: { data?: { items: User[]; total: number } } }
      users.value = d.data?.data?.items ?? []
      usersTotal.value = d.data?.data?.total ?? 0
    } finally {
      usersLoading.value = false
    }
  }

  async function updateUser(
    id: number,
    data: Partial<Pick<User, 'role' | 'isActive' | 'plan'>>
  ) {
    const res = await adminApi.updateUser(id, data)
    const d = res.data as { data?: { data?: User } }
    const updated = d.data?.data
    if (updated) {
      const idx = users.value.findIndex((u) => u.id === id)
      if (idx !== -1) users.value[idx] = updated
    }
    return updated
  }

  async function deleteUser(id: number) {
    await adminApi.deleteUser(id)
    users.value = users.value.filter((u) => u.id !== id)
    usersTotal.value--
  }

  async function resetUserPassword(id: number, newPassword: string) {
    await adminApi.resetUserPassword(id, newPassword)
  }

  async function fetchSystemHealth() {
    healthLoading.value = true
    try {
      const res = await adminApi.getSystemHealth()
      const d = res.data as { data?: { data?: SystemHealth } }
      systemHealth.value = d.data?.data ?? null
    } finally {
      healthLoading.value = false
    }
  }

  async function fetchSystemMetrics() {
    metricsLoading.value = true
    try {
      const res = await adminApi.getSystemMetrics()
      const d = res.data as { data?: { data?: SystemMetrics } }
      systemMetrics.value = d.data?.data ?? null
    } finally {
      metricsLoading.value = false
    }
  }

  async function fetchAuditLogs(params?: { page?: number; pageSize?: number; userId?: number; action?: string }) {
    auditLogsLoading.value = true
    try {
      const res = await adminApi.getAuditLogs(params)
      const d = res.data as { data?: { data?: { items: AuditLog[]; total: number } } }
      auditLogs.value = d.data?.data?.items ?? []
      auditLogsTotal.value = d.data?.data?.total ?? 0
    } finally {
      auditLogsLoading.value = false
    }
  }

  return {
    users,
    usersTotal,
    usersLoading,
    systemHealth,
    healthLoading,
    systemMetrics,
    metricsLoading,
    auditLogs,
    auditLogsTotal,
    auditLogsLoading,
    fetchUsers,
    updateUser,
    deleteUser,
    resetUserPassword,
    fetchSystemHealth,
    fetchSystemMetrics,
    fetchAuditLogs,
  }
})
