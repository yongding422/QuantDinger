<template>
  <div class="login-page">
    <a-row justify="center" align="middle" class="login-row">
      <a-col :xs="24" :sm="18" :md="14" :lg="10" :xl="8">
        <a-card class="login-card" :bordered="false">
          <!-- Logo -->
          <div class="logo-area">
            <img src="/logo.png" alt="QuantDinger" height="48" />
            <h1 class="app-name">QuantDinger</h1>
            <p class="app-tagline">All-in-One Quant Workspace</p>
          </div>

          <!-- Login tabs -->
          <a-tabs v-model:activeKey="activeTab" centered class="login-tabs">
            <a-tab-pane key="password" :tab="$t('auth.loginWithPassword')" />
            <a-tab-pane key="code" :tab="$t('auth.loginWithCode')" />
          </a-tabs>

          <!-- Password login form -->
          <a-form
            v-if="activeTab === 'password'"
            layout="vertical"
            class="login-form"
            :model="loginForm"
            @finish="handlePasswordLogin"
          >
            <a-form-item :label="$t('auth.email')" name="username">
              <a-input
                v-model:value="loginForm.username"
                size="large"
                :placeholder="$t('auth.email')"
                autocomplete="username"
              >
                <template #prefix><MailOutlined /></template>
              </a-input>
            </a-form-item>

            <a-form-item :label="$t('auth.password')" name="password">
              <a-input-password
                v-model:value="loginForm.password"
                size="large"
                :placeholder="$t('auth.password')"
                autocomplete="current-password"
              >
                <template #prefix><LockOutlined /></template>
              </a-input-password>
            </a-form-item>

            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                size="large"
                block
                :loading="loginLoading"
              >
                {{ $t('auth.login') }}
              </a-button>
            </a-form-item>
          </a-form>

          <!-- Code login form -->
          <a-form
            v-else
            layout="vertical"
            class="login-form"
            :model="codeForm"
            @finish="handleCodeLogin"
          >
            <a-form-item :label="$t('auth.email')" name="email">
              <a-input
                v-model:value="codeForm.email"
                size="large"
                :placeholder="$t('auth.email')"
              >
                <template #prefix><MailOutlined /></template>
              </a-input>
            </a-form-item>

            <a-form-item :label="$t('auth.code')" name="code">
              <a-input-search
                v-model:value="codeForm.code"
                size="large"
                :placeholder="$t('auth.code')"
                :enter-button="$t('auth.sendCode')"
                @search="handleSendCode"
              >
                <template #prefix><SafetyOutlined /></template>
              </a-input-search>
            </a-form-item>

            <a-form-item>
              <a-button
                type="primary"
                html-type="submit"
                size="large"
                block
                :loading="loginLoading"
              >
                {{ $t('auth.login') }}
              </a-button>
            </a-form-item>
          </a-form>

          <!-- OAuth buttons -->
          <a-divider>{{ $t('auth.loginWithOAuth') }}</a-divider>
          <div class="oauth-buttons">
            <a-button size="large" @click="handleGithubLogin">
              <GithubOutlined /> {{ $t('auth.github') }}
            </a-button>
            <a-button size="large" @click="handleGoogleLogin">
              <GoogleOutlined /> {{ $t('auth.google') }}
            </a-button>
          </div>

          <!-- Register link -->
          <div class="register-link">
            {{ $t('auth.noAccount') }}
            <router-link to="/user/register">{{ $t('auth.registerNow') }}</router-link>
          </div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  MailOutlined,
  LockOutlined,
  SafetyOutlined,
  GithubOutlined,
  GoogleOutlined,
} from '@ant-design/icons-vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/stores/auth'
import request from '@/api/request'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { t } = useI18n()

const activeTab = ref<'password' | 'code'>('password')
const loginLoading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const codeForm = reactive({
  email: '',
  code: '',
})

// Handle password login
async function handlePasswordLogin() {
  loginLoading.value = true
  try {
    const res = await request.post('/auth/login', {
      account: loginForm.username,
      password: loginForm.password,
    })
    const data = res.data.data as { token: string; userinfo: unknown }
    authStore.setAuth(data.token, data.userinfo as never)
    message.success(t('auth.loginSuccess'))
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  } catch (err: unknown) {
    const e = err as { msg?: string }
    message.error(e.msg || t('auth.loginFailed'))
  } finally {
    loginLoading.value = false
  }
}

// Handle code login
async function handleSendCode() {
  try {
    await request.post('/auth/send-code', {
      email: codeForm.email,
      type: 'login',
    })
    message.success(t('auth.codeSent'))
  } catch (err: unknown) {
    const e = err as { msg?: string }
    message.error(e.msg || t('errors.serverError'))
  }
}

async function handleCodeLogin() {
  loginLoading.value = true
  try {
    const res = await request.post('/auth/login-code', {
      email: codeForm.email,
      code: codeForm.code,
    })
    const data = res.data.data as { token: string; userinfo: unknown }
    authStore.setAuth(data.token, data.userinfo as never)
    message.success(t('auth.loginSuccess'))
    const redirect = (route.query.redirect as string) || '/dashboard'
    router.push(redirect)
  } catch (err: unknown) {
    const e = err as { msg?: string }
    message.error(e.msg || t('auth.loginFailed'))
  } finally {
    loginLoading.value = false
  }
}

// OAuth redirects
function handleGithubLogin() {
  window.location.href = '/api/auth/oauth/github'
}

function handleGoogleLogin() {
  window.location.href = '/api/auth/oauth/google'
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
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

.login-form {
  margin-top: 24px;
}

.oauth-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.register-link {
  text-align: center;
  margin-top: 16px;
  color: var(--color-text-secondary);
}

.register-link a {
  color: #1677ff;
  margin-left: 4px;
}
</style>
