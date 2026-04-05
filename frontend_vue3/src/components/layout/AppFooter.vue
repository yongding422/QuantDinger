<template>
  <a-layout-footer class="app-footer">
    <span>QuantDinger v3.0.1</span>
    <span class="separator">·</span>
    <a href="https://github.com/yongding422/QuantDinger" target="_blank" rel="noopener">GitHub</a>
  </a-layout-footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.app-footer {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 13px;
  background: var(--color-bg-layout) !important;
  border-top: 1px solid var(--color-border);
}

.separator {
  margin: 0 8px;
}

a {
  color: var(--color-text-secondary);
  text-decoration: none;
}

a:hover {
  color: var(--color-text-primary);
}
</style>
