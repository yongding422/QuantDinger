# Specs: Phase 1 — Project Scaffold

## 1. Project Initialization

### 1.1 Initialize Vite + Vue 3 + TypeScript

```bash
npm create vite@latest frontend_vue3 -- --template vue-ts
cd frontend_vue3
npm install
npm install vue-router@4 pinia @ant-design/icons-vue ant-design-vue@4 vue-i18n@9 axios
npm install -D @types/node typescript vite-plugin-components unplugin-vue-components
```

### 1.2 Configure vite.config.ts
- Set `base: '/'` (for SPA routing with nginx proxy)
- Configure `unplugin-vue-components` for Ant Design Vue auto-import
- Configure `server.proxy` to forward `/api` to `http://localhost:5000`
- Configure `build` with proper chunking strategy

### 1.3 Configure TypeScript (tsconfig.json)
- Strict mode enabled
- Path aliases: `@/` → `src/`
- `jsx: preserve` for Vue SFC compatibility

### 1.4 Configure Ant Design Vue 4
- Dark theme via CSS variables
- ConfigProvider with i18n support
- Locale: date-fns for date formatting

---

## 2. API Layer

### 2.1 Axios Instance (src/utils/request.ts)

```typescript
// Base configuration
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE || '/api',
  timeout: 60000,
})

// Request interceptor: attach JWT
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Response interceptor: unwrap { code, msg, data } envelope
// Handle 401 → redirect to login
```

### 2.2 API Client Files (src/api/*.ts)

One file per domain, each exporting typed functions:

```typescript
// Example: src/api/auth.ts
export const authApi = {
  login: (data: { email: string; password: string }) =>
    request.post<{ token: string; user: User }>('/auth/login', data),
  register: (data: RegisterDto) => request.post('/auth/register', data),
  getUserInfo: () => request.get<User>('/auth/info'),
  // ...
}
```

All API files use TypeScript interfaces generated from openapi.yaml.

### 2.3 OpenAPI Type Generation

```bash
npm install -D openapi-typescript-code-gen
npx otgc -i ../openapi.yaml -o src/types/api.ts
```

---

## 3. State Management (Pinia)

### 3.1 App Store (src/stores/app.ts)
```typescript
{
  theme: 'dark' | 'light',
  sidebarCollapsed: boolean,
  language: string,  // 'en-US' | 'zh-CN' | etc.
  user: User | null,
}
```

### 3.2 Auth Store (src/stores/auth.ts)
```typescript
{
  token: string | null,
  user: User | null,
  isAuthenticated: boolean,
  login(), logout(), fetchUser()
}
```

### 3.3 Domain Stores
- `portfolio.ts` — positions, monitors, alerts
- `strategies.ts` — strategy list, current strategy
- `market.ts` — watchlist, prices
- `aiChat.ts` — chat messages, history

---

## 4. Router

### 4.1 Routes (src/router/index.ts)

Hash mode router with these top-level routes:

```
/user/login          → LoginPage
/user/register       → RegisterPage
/dashboard           → DashboardPage (default after login)
/portfolio           → PortfolioPage
/strategies          → StrategyListPage
/strategies/new      → StrategyCreatePage
/strategies/:id      → StrategyDetailPage
/quick-trade         → QuickTradePage
/market              → GlobalMarketPage
/ai-analysis         → AIAnalysisPage
/indicators          → IndicatorListPage
/backtest            → BacktestPage
/polymarket          → PolymarketPage
/settings            → SettingsPage
/billing             → BillingPage
/community           → CommunityPage
/admin/users         → UserManagementPage
/trading/ibkr        → IBKRPage
/trading/mt5         → MT5Page
```

All routes except `/user/login` and `/user/register` require authentication via navigation guard.

---

## 5. Layout

### 5.1 AppLayout (src/components/layout/AppLayout.vue)
- `<a-layout>` with `<a-layout-sider>` (collapsible sidebar) + `<a-layout-content>` + `<a-layout-header>`
- Sidebar collapses on toggle or breakpoint < 768px
- Header: logo, breadcrumb, language switcher, theme toggle, user dropdown

### 5.2 Sidebar Navigation (src/components/layout/Sidebar.vue)
- `<a-menu>` with items from routes
- Active item highlighted
- Icon + label per item (Ant Design icons)
- Collapsed mode: icons only with tooltips

### 5.3 Header (src/components/layout/Header.vue)
- `<a-dropdown>` user menu: profile, settings, logout
- `<a-select>` language switcher (10 languages)
- `<a-switch>` theme toggle (sun/moon icons)

### 5.4 Footer (src/components/layout/Footer.vue)
- Version number
- Links: GitHub, Docs

---

## 6. i18n Setup

### 6.1 Locale Files (src/i18n/locales/*.json)

10 languages with these keys (subset):
```json
{
  "nav": { "dashboard": "", "portfolio": "", "strategies": "", ... },
  "auth": { "login": "", "register": "", "email": "", "password": "", ... },
  "common": { "save": "", "cancel": "", "delete": "", "edit": "", "confirm": "", ... },
  "dashboard": { "title": "", "totalBalance": "", "todayPnl": "", ... },
  ...
}
```

English (en-US) is the source. Other locales are translations.

### 6.2 i18n Configuration (src/i18n/index.ts)
```typescript
const i18n = createI18n({
  legacy: false,
  locale: storedLocale || 'en-US',
  fallbackLocale: 'en-US',
  messages: { enUS, zhCN, ... },
})
```

---

## 7. Theme System

### 7.1 Dark/Light Mode
- Ant Design Vue 4 uses CSS variables
- Toggle via `ant-design-vue/es/config-provider/context.js` ConfigProvider
- Store preference in localStorage
- Apply on app mount (before first render to prevent flash)

---

## 8. Entry Points

### 8.1 src/main.ts
```typescript
const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(i18n)
app.use(Antd)
app.mount('#app')
```

### 8.2 src/App.vue
- `<ConfigProvider>` wrapping `<RouterView>`
- Theme and locale from app store

---

## 9. Environment Variables (.env)

```bash
VITE_API_BASE=/api
VITE_APP_TITLE=QuantDinger
```

---

## 10. Build & Dev Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "typecheck": "vue-tsc --noEmit",
    "test": "vitest",
    "test:e2e": "playwright test"
  }
}
```

---

## 11. Acceptance Criteria

- [ ] `npm run dev` starts the Vite dev server on port 5173
- [ ] `npm run build` produces a production dist/ folder with zero TypeScript errors
- [ ] Login page renders at `/#/user/login`
- [ ] After login, redirect to `/#/dashboard` works
- [ ] Sidebar navigation is visible and functional
- [ ] Language switcher changes all UI text
- [ ] Dark/light theme toggle works without page reload
- [ ] All 10 languages have at least the scaffold strings
- [ ] Axios requests are proxied to backend (check Network tab)
- [ ] JWT token is stored and attached to subsequent requests
