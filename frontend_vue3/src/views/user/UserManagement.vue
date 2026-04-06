<template>
  <div class="user-management-page">
    <div class="page-header">
      <h2>{{ $t('user.title') }}</h2>
      <a-button type="primary" @click="refresh">
        <template #icon><ReloadOutlined /></template>
        {{ $t('common.refresh') }}
      </a-button>
    </div>

    <!-- User stats -->
    <a-row :gutter="16" style="margin-bottom: 24px">
      <a-col :span="6">
        <a-card size="small">
          <a-statistic title="Total Users" :value="adminStore.usersTotal" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small">
          <a-statistic title="Active Users" :value="adminMetrics?.activeUsers ?? 0" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small">
          <a-statistic title="Total Trades" :value="adminMetrics?.totalTrades ?? 0" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card size="small">
          <a-statistic title="Total API Calls" :value="adminMetrics?.totalApiCalls ?? 0" />
        </a-card>
      </a-col>
    </a-row>

    <!-- Filters + table -->
    <a-card>
      <div class="table-toolbar">
        <a-input-search
          v-model:value="search"
          :placeholder="$t('common.search') + ' username or email'"
          style="width: 280px"
          @search="onSearch"
          allow-clear
        />
        <a-select
          v-model:value="filterRole"
          :placeholder="$t('user.roles')"
          style="width: 140px"
          allow-clear
          @change="loadUsers"
        >
          <a-select-option value="admin">{{ $t('user.admin') }}</a-select-option>
          <a-select-option value="user">{{ $t('user.user') }}</a-select-option>
          <a-select-option value="guest">{{ $t('user.guest') }}</a-select-option>
        </a-select>
        <a-select
          v-model:value="filterStatus"
          :placeholder="$t('user.status')"
          style="width: 140px"
          allow-clear
          @change="loadUsers"
        >
          <a-select-option value="active">{{ $t('user.active') }}</a-select-option>
          <a-select-option value="disabled">{{ $t('user.disabled') }}</a-select-option>
        </a-select>
      </div>

      <a-table
        :columns="columns"
        :data-source="filteredUsers"
        :loading="adminStore.usersLoading"
        :pagination="pagination"
        row-key="id"
        size="small"
        style="margin-top: 16px"
        @change="onTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'role'">
            <a-tag :color="roleColor(record.role)">{{ record.role }}</a-tag>
          </template>
          <template v-else-if="column.key === 'isActive'">
            <a-badge :status="record.isActive ? 'success' : 'error'" :text="record.isActive ? $t('user.active') : $t('user.disabled')" />
          </template>
          <template v-else-if="column.key === 'lastLogin'">
            {{ record.lastLogin ? formatDate(record.lastLogin) : '-' }}
          </template>
          <template v-else-if="column.key === 'actions'">
            <a-space>
              <a-button size="small" @click="openEdit(record)">{{ $t('common.edit') }}</a-button>
              <a-button size="small" danger :loading="resettingPwdId === record.id" @click="openResetPwd(record)">
                {{ $t('user.resetPassword') }}
              </a-button>
              <a-popconfirm
                :title="$t('common.confirmDelete')"
                :ok-text="$t('common.yes')"
                :cancel-text="$t('common.no')"
                @confirm="handleDelete(record.id)"
              >
                <a-button size="small" danger :loading="deletingId === record.id">
                  {{ $t('common.delete') }}
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- Edit user modal -->
    <a-modal
      v-model:open="editVisible"
      :title="$t('user.update')"
      @ok="submitEdit"
      :confirm-loading="editSaving"
    >
      <a-form layout="vertical" :model="editForm">
        <a-form-item label="Username">
          <a-input v-model:value="editForm.username" disabled />
        </a-form-item>
        <a-form-item label="Email">
          <a-input v-model:value="editForm.email" disabled />
        </a-form-item>
        <a-form-item :label="$t('user.roles')">
          <a-select v-model:value="editForm.role">
            <a-select-option value="admin">{{ $t('user.admin') }}</a-select-option>
            <a-select-option value="user">{{ $t('user.user') }}</a-select-option>
            <a-select-option value="guest">{{ $t('user.guest') }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="Plan">
          <a-input v-model:value="editForm.plan" placeholder="e.g. free, pro, enterprise" />
        </a-form-item>
        <a-form-item :label="$t('user.status')">
          <a-switch v-model:checked="editForm.isActive" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- Reset password modal -->
    <a-modal
      v-model:open="resetPwdVisible"
      title="Reset Password"
      @ok="submitResetPwd"
      :confirm-loading="resettingPwd"
    >
      <a-form layout="vertical">
        <a-form-item label="New Password">
          <a-input-password v-model:value="newPassword" placeholder="Enter new password" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useAdminStore } from '@/stores/admin'
import type { User } from '@/api/admin'

const adminStore = useAdminStore()

const search = ref('')
const filterRole = ref<string | undefined>()
const filterStatus = ref<string | undefined>()
const page = ref(1)
const pageSize = ref(20)

const pagination = computed(() => ({
  current: page.value,
  pageSize: pageSize.value,
  total: adminStore.usersTotal,
  showSizeChanger: true,
  showTotal: (total: number) => `Total ${total} users`,
}))

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 60 },
  { title: 'Username', dataIndex: 'username', key: 'username' },
  { title: 'Email', dataIndex: 'email', key: 'email' },
  { title: 'Role', dataIndex: 'role', key: 'role' },
  { title: 'Plan', dataIndex: 'plan', key: 'plan' },
  { title: 'Status', dataIndex: 'isActive', key: 'isActive' },
  { title: 'Last Login', dataIndex: 'lastLogin', key: 'lastLogin' },
  { title: 'Actions', key: 'actions', fixed: 'right' as const, width: 260 },
]



const filteredUsers = computed(() => {
  let list = adminStore.users
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(
      (u) => u.username.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    )
  }
  if (filterRole.value) {
    list = list.filter((u) => u.role === filterRole.value)
  }
  if (filterStatus.value) {
    const isActive = filterStatus.value === 'active'
    list = list.filter((u) => u.isActive === isActive)
  }
  return list
})

const adminMetrics = computed(() => adminStore.systemMetrics)

// Edit
const editVisible = ref(false)
const editSaving = ref(false)
const editingUser = ref<User | null>(null)
const editForm = reactive({ username: '', email: '', role: 'user' as User['role'], plan: '', isActive: true })

function openEdit(user: User) {
  editingUser.value = user
  editForm.username = user.username
  editForm.email = user.email
  editForm.role = user.role
  editForm.plan = user.plan ?? ''
  editForm.isActive = user.isActive
  editVisible.value = true
}

async function submitEdit() {
  editSaving.value = true
  try {
    await adminStore.updateUser(editingUser.value!.id, {
      role: editForm.role,
      plan: editForm.plan || undefined,
      isActive: editForm.isActive,
    })
    message.success('User updated')
    editVisible.value = false
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Update failed')
  } finally {
    editSaving.value = false
  }
}

// Reset password
const resetPwdVisible = ref(false)
const resettingPwdId = ref<number | null>(null)
const resettingPwd = ref(false)
const newPassword = ref('')
const pwdTargetId = ref<number | null>(null)

function openResetPwd(user: User) {
  pwdTargetId.value = user.id
  resettingPwdId.value = user.id
  newPassword.value = ''
  resetPwdVisible.value = true
}

async function submitResetPwd() {
  if (!newPassword.value) {
    message.warning('Please enter a new password')
    return
  }
  resettingPwd.value = true
  try {
    await adminStore.resetUserPassword(pwdTargetId.value!, newPassword.value)
    message.success('Password reset successfully')
    resetPwdVisible.value = false
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Reset failed')
  } finally {
    resettingPwd.value = false
    resettingPwdId.value = null
  }
}

// Delete
const deletingId = ref<number | null>(null)

async function handleDelete(id: number) {
  deletingId.value = id
  try {
    await adminStore.deleteUser(id)
    message.success('User deleted')
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Delete failed')
  } finally {
    deletingId.value = null
  }
}

function loadUsers() {
  adminStore.fetchUsers({ page: page.value, pageSize: pageSize.value, search: search.value || undefined })
}

function onSearch() {
  page.value = 1
  loadUsers()
}

function onTableChange(pag: { current: number; pageSize: number }) {
  page.value = pag.current
  pageSize.value = pag.pageSize
  loadUsers()
}

function refresh() {
  loadUsers()
  adminStore.fetchSystemMetrics()
}

function roleColor(role: string) {
  if (role === 'admin') return 'red'
  if (role === 'guest') return 'orange'
  return 'blue'
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleString()
}

onMounted(async () => {
  loadUsers()
  await adminStore.fetchSystemMetrics()
})
</script>

<style scoped>
.user-management-page {
  padding: 24px;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.table-toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
