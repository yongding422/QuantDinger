<template>
  <a-layout-header class="app-header">
    <!-- Left: collapse toggle + breadcrumb -->
    <div class="header-left">
      <MenuFoldOutlined class="trigger" @click="toggleSidebar" />
    </div>

    <!-- Right: language, theme, user menu -->
    <div class="header-right">
      <!-- Language switcher -->
      <a-select
        :value="appStore.language"
        size="small"
        class="lang-select"
        @change="handleLanguageChange"
      >
        <a-select-option v-for="loc in SUPPORTED_LOCALES" :key="loc.value" :value="loc.value">
          {{ loc.label }}
        </a-select-option>
      </a-select>

      <!-- Theme toggle -->
      <a-tooltip :title="appStore.theme === 'dark' ? 'Switch to Light' : 'Switch to Dark'">
        <a-button type="text" class="theme-btn" @click="appStore.toggleTheme">
          {{ appStore.theme === 'dark' ? '🌙' : '☀️' }}
        </a-button>
      </a-tooltip>

      <!-- User dropdown -->
      <a-dropdown>
        <div class="user-info">
          <a-avatar :src="authStore.user?.avatar || '/avatar2.jpg'" size="small" />
          <span class="username">{{ authStore.user?.nickname || authStore.user?.username }}</span>
          <DownOutlined />
        </div>
        <template #overlay>
          <a-menu>
            <a-menu-item key="profile" @click="$router.push('/settings')">
              <UserOutlined /> {{ $t('user.profile') }}
            </a-menu-item>
            <a-menu-divider />
            <a-menu-item key="logout" @click="handleLogout">
              <LogoutOutlined /> {{ $t('auth.logout') }}
            </a-menu-item>
          </a-menu>
        </template>
      </a-dropdown>
    </div>
  </a-layout-header>
</template>

<script setup lang="ts">
import { MenuFoldOutlined, DownOutlined, UserOutlined, LogoutOutlined } from '@ant-design/icons-vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import { SUPPORTED_LOCALES, setLocale } from '@/i18n'
import type { SupportedLocale } from '@/i18n'

const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

function toggleSidebar() {
  appStore.toggleSidebar()
}

function handleLanguageChange(locale: SupportedLocale) {
  appStore.setLanguage(locale)
  setLocale(locale)
}

function handleLogout() {
  authStore.logout()
  router.push('/user/login')
}
</script>

<style scoped>
.app-header {
  background: var(--color-bg-layout) !important;
  padding: 0 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 99;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.trigger {
  font-size: 18px;
  cursor: pointer;
  color: var(--color-text-secondary);
  padding: 4px;
}

.trigger:hover {
  color: var(--color-text-primary);
}

.lang-select {
  min-width: 100px;
}

.theme-btn {
  font-size: 16px;
  color: var(--color-text-secondary);
}

.theme-btn:hover {
  color: var(--color-text-primary);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.user-info:hover {
  background: var(--color-bg-hover);
}

.username {
  color: var(--color-text-primary);
  font-size: 14px;
}
</style>
