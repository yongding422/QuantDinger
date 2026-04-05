<template>
  <div class="settings-page">
    <h1>{{ $t('settings.title') }}</h1>

    <a-row :gutter="24">
      <!-- Left: Profile form -->
      <a-col :xs="24" :md="12">
        <a-card :title="$t('user.profile')" class="settings-card">
          <a-form layout="vertical" :model="profileForm">
            <a-form-item :label="$t('auth.username')">
              <a-input :value="profile?.username" disabled />
            </a-form-item>
            <a-form-item :label="$t('auth.email')">
              <a-input :value="profile?.email" disabled />
            </a-form-item>
            <a-form-item :label="$t('auth.nickname')">
              <a-input v-model:value="profileForm.nickname" />
            </a-form-item>
            <a-form-item label="Timezone">
              <a-select v-model:value="profileForm.timezone" placeholder="Select timezone">
                <a-select-option value="America/New_York">America/New_York (EST)</a-select-option>
                <a-select-option value="America/Los_Angeles">America/Los_Angeles (PST)</a-select-option>
                <a-select-option value="America/Chicago">America/Chicago (CST)</a-select-option>
                <a-select-option value="Europe/London">Europe/London (GMT)</a-select-option>
                <a-select-option value="Europe/Berlin">Europe/Berlin (CET)</a-select-option>
                <a-select-option value="Asia/Shanghai">Asia/Shanghai (CST)</a-select-option>
                <a-select-option value="Asia/Tokyo">Asia/Tokyo (JST)</a-select-option>
                <a-select-option value="Asia/Singapore">Asia/Singapore (SGT)</a-select-option>
              </a-select>
            </a-form-item>
            <a-form-item>
              <a-button type="primary" :loading="saving" @click="saveProfile">
                {{ $t('common.save') }}
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- Change password -->
        <a-card :title="$t('auth.changePassword')" class="settings-card" style="margin-top: 16px;">
          <a-form layout="vertical" :model="pwdForm">
            <a-form-item :label="$t('auth.email')">
              <a-input v-model:value="pwdForm.email" :placeholder="$t('auth.email')" />
            </a-form-item>
            <a-form-item :label="$t('auth.code')">
              <a-input-search
                v-model:value="pwdForm.code"
                :enter-button="$t('auth.sendCode')"
                :loading="sendingCode"
                @search="sendCode"
              />
            </a-form-item>
            <a-form-item :label="$t('auth.newPassword')">
              <a-input-password v-model:value="pwdForm.newPassword" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" :loading="changingPwd" @click="changePassword">
                {{ $t('auth.changePassword') }}
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>
      </a-col>

      <!-- Right: Notification settings -->
      <a-col :xs="24" :md="12">
        <a-card :title="$t('user.notificationSettings')" class="settings-card">
          <a-form layout="vertical" :model="notifForm">
            <a-form-item :label="$t('common.enabled')">
              <a-switch v-model:checked="notifForm.emailEnabled" />
              <span style="margin-left: 8px">Email notifications</span>
            </a-form-item>
            <a-divider />
            <a-form-item label="Strategy Alerts">
              <a-switch v-model:checked="notifForm.strategyAlerts" />
            </a-form-item>
            <a-form-item label="Portfolio Alerts">
              <a-switch v-model:checked="notifForm.portfolioAlerts" />
            </a-form-item>
            <a-form-item label="Market Alerts">
              <a-switch v-model:checked="notifForm.marketAlerts" />
            </a-form-item>
            <a-form-item label="AI Analysis Alerts">
              <a-switch v-model:checked="notifForm.aiAnalysisAlerts" />
            </a-form-item>
            <a-form-item>
              <a-button type="primary" :loading="savingNotif" @click="saveNotifications">
                {{ $t('common.save') }}
              </a-button>
              <a-button style="margin-left: 8px" @click="testNotification">
                {{ $t('user.testNotification') }}
              </a-button>
            </a-form-item>
          </a-form>
        </a-card>

        <!-- Credits info -->
        <a-card
          v-if="profile?.credits !== undefined"
          :title="$t('user.credits')"
          class="settings-card"
          style="margin-top: 16px;"
        >
          <a-statistic :value="profile.credits" suffix="credits" />
          <a-divider />
          <a-button size="small" @click="openCreditsLog">View credits log</a-button>
        </a-card>
      </a-col>
    </a-row>

    <!-- Credits log modal -->
    <a-modal
      v-model:open="showCreditsLog"
      title="Credits Log"
      width="700px"
      :footer="null"
    >
      <a-table
        :columns="creditsColumns"
        :data-source="creditsLog"
        :pagination="{ pageSize: 10 }"
        :loading="loadingCreditsLog"
        row-key="id"
        size="small"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'action'">
            <span>{{ record.action?.replace(/_/g, ' ') }}</span>
          </template>
          <template v-if="column.key === 'amount'">
            <span :style="{ color: record.amount >= 0 ? '#52c41a' : '#ff4d4f' }">
              {{ record.amount >= 0 ? '+' : '' }}{{ record.amount }}
            </span>
          </template>
        </template>
      </a-table>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { userApi, type UserProfile, type NotificationSettings } from '@/api/user'
import request from '@/api/request'

const profile = ref<UserProfile | null>(null)
const saving = ref(false)
const savingNotif = ref(false)
const changingPwd = ref(false)
const sendingCode = ref(false)
const showCreditsLog = ref(false)
const creditsLog = ref<unknown[]>([])
const loadingCreditsLog = ref(false)

const profileForm = reactive({ nickname: '', timezone: '' })
const pwdForm = reactive({ email: '', code: '', newPassword: '' })
const notifForm = reactive<NotificationSettings>({
  emailEnabled: false,
  telegramEnabled: false,
  strategyAlerts: true,
  portfolioAlerts: true,
  marketAlerts: false,
  aiAnalysisAlerts: false,
})

const creditsColumns = [
  { title: 'Action', key: 'action' },
  { title: 'Amount', key: 'amount' },
  { title: 'Remark', dataIndex: 'remark', key: 'remark' },
  { title: 'Date', dataIndex: 'createdAt', key: 'createdAt' },
]

onMounted(async () => {
  try {
    const [profileRes, notifRes] = await Promise.all([
      userApi.getProfile(),
      userApi.getNotificationSettings(),
    ])
    profile.value = profileRes.data.data?.data ?? null
    if (profile.value) {
      profileForm.nickname = profile.value.nickname || ''
      profileForm.timezone = profile.value.timezone || 'America/New_York'
      pwdForm.email = profile.value.email || ''
    }
    const ns = notifRes.data.data?.data
    if (ns) {
      Object.assign(notifForm, ns)
    }
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Failed to load profile')
  }
})

async function saveProfile() {
  saving.value = true
  try {
    await userApi.updateProfile({
      nickname: profileForm.nickname,
      timezone: profileForm.timezone,
    })
    message.success('Profile saved')
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Failed to save profile')
  } finally {
    saving.value = false
  }
}

async function saveNotifications() {
  savingNotif.value = true
  try {
    await userApi.updateNotificationSettings({ ...notifForm })
    message.success('Notification settings saved')
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Failed to save notification settings')
  } finally {
    savingNotif.value = false
  }
}

async function testNotification() {
  try {
    await userApi.testNotification()
    message.success('Test notification sent')
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Failed to send test notification')
  }
}

async function sendCode() {
  if (!pwdForm.email) {
    message.warning('Please enter your email')
    return
  }
  sendingCode.value = true
  try {
    await request.post('/users/send-reset-code', { email: pwdForm.email })
    message.success('Verification code sent')
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Failed to send code')
  } finally {
    sendingCode.value = false
  }
}

async function changePassword() {
  if (!pwdForm.code || !pwdForm.newPassword) {
    message.warning('Please fill in all fields')
    return
  }
  changingPwd.value = true
  try {
    await userApi.changePassword(pwdForm.code, pwdForm.newPassword)
    message.success('Password changed successfully')
    pwdForm.code = ''
    pwdForm.newPassword = ''
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Failed to change password')
  } finally {
    changingPwd.value = false
  }
}

async function openCreditsLog() {
  showCreditsLog.value = true
  if (creditsLog.value.length > 0) return
  loadingCreditsLog.value = true
  try {
    const res = await userApi.getCreditsLog()
    creditsLog.value = (res.data as { data?: { data?: unknown[] } })?.data?.data ?? []
  } catch (err: unknown) {
    const e = err as Error
    message.error(e.message || 'Failed to load credits log')
  } finally {
    loadingCreditsLog.value = false
  }
}
</script>

<style scoped>
.settings-page {
  padding: 24px;
}
.settings-card {
  border-radius: 8px;
}
</style>
