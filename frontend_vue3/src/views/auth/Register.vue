<template>
  <div class="register-page">
    <a-row justify="center" align="middle">
      <a-col :xs="24" :sm="18" :md="14" :lg="10" :xl="8">
        <a-card class="register-card" :bordered="false">
          <div class="logo-area">
            <img src="/logo.png" alt="QuantDinger" height="48" />
            <h1 class="app-name">QuantDinger</h1>
            <p class="app-tagline">Create your account</p>
          </div>

          <a-form layout="vertical" @finish="handleRegister">
            <a-form-item :label="$t('auth.username')" name="username">
              <a-input v-model:value="form.username" size="large" :placeholder="$t('auth.username')">
                <template #prefix><UserOutlined /></template>
              </a-input>
            </a-form-item>

            <a-form-item :label="$t('auth.email')" name="email">
              <a-input v-model:value="form.email" size="large" :placeholder="$t('auth.email')">
                <template #prefix><MailOutlined /></template>
              </a-input>
            </a-form-item>

            <a-form-item :label="$t('auth.password')" name="password">
              <a-input-password v-model:value="form.password" size="large" :placeholder="$t('auth.password')">
                <template #prefix><LockOutlined /></template>
              </a-input-password>
            </a-form-item>

            <a-form-item :label="$t('auth.code')" name="code">
              <a-input-search
                v-model:value="form.code"
                size="large"
                :placeholder="$t('auth.code')"
                :enter-button="$t('auth.sendCode')"
                @search="handleSendCode"
              >
                <template #prefix><SafetyOutlined /></template>
              </a-input-search>
            </a-form-item>

            <a-form-item>
              <a-button type="primary" html-type="submit" size="large" block :loading="loading">
                {{ $t('auth.register') }}
              </a-button>
            </a-form-item>
          </a-form>

          <div class="login-link">
            {{ $t('auth.hasAccount') }}
            <router-link to="/user/login">{{ $t('auth.login') }}</router-link>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { UserOutlined, MailOutlined, LockOutlined, SafetyOutlined } from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import request from '@/api/request'

const router = useRouter()
const authStore = useAuthStore()
const { t } = useI18n()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  code: '',
})

async function handleSendCode() {
  try {
    await request.post('/auth/send-code', {
      email: form.email,
      type: 'register',
    })
    message.success(t('auth.codeSent'))
  } catch (err: unknown) {
    const e = err as { msg?: string }
    message.error(e.msg || t('errors.serverError'))
  }
}

async function handleRegister() {
  loading.value = true
  try {
    const res = await request.post('/auth/register', {
      username: form.username,
      email: form.email,
      password: form.password,
      code: form.code,
    })
    const data = res.data.data as { token: string; userinfo: unknown }
    authStore.setAuth(data.token, data.userinfo as never)
    message.success(t('auth.registerSuccess'))
    router.push('/dashboard')
  } catch (err: unknown) {
    const e = err as { msg?: string }
    message.error(e.msg || t('auth.registerFailed'))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.register-card {
  padding: 40px 32px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  min-width: 380px;
  max-width: 480px;
  margin: 0 auto;
}

.logo-area {
  text-align: center;
  margin-bottom: 24px;
}

.app-name {
  font-size: 24px;
  font-weight: 700;
  margin: 8px 0 4px;
  color: var(--color-text-primary);
}

.app-tagline {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 0;
}

.login-link {
  text-align: center;
  margin-top: 16px;
  color: var(--color-text-secondary);
}

.login-link a {
  color: #1677ff;
  margin-left: 4px;
}
</style>
