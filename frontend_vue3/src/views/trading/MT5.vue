<template>
  <div class="page-placeholder">
    <a-result title="Coming Soon" sub-title="This page is under construction.">
      <template #extra>
        <a-button type="primary" @click="$router.push('/dashboard')">{{ $t('common.back') }}</a-button>
      </template>
    </a-result>
  </div>
</template>
<style scoped>
.page-placeholder { padding: 24px; }
</style>
