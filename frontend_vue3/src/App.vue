<template>
  <ConfigProvider :theme="antThemeConfig">
    <AppLayout>
      <RouterView />
    </AppLayout>
  </ConfigProvider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ConfigProvider, theme } from 'ant-design-vue'
import { useAppStore } from '@/stores/app'
import AppLayout from '@/components/layout/AppLayout.vue'

const appStore = useAppStore()

const antThemeConfig = computed(() => ({
  algorithm: appStore.theme === 'dark' ? theme.darkAlgorithm : theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1677ff',
    borderRadius: 6,
  },
}))
</script>

<style>
body {
  transition: background-color 0.3s, color 0.3s;
}
</style>
