# Design: QuantDinger Frontend Vue 3 Rewrite

## 1. Design Principles

1. **Match existing UX first, improve second** — The existing app has established interaction patterns. Don't deviate until Phase 7 unless the improvement is obvious and low-risk.
2. **Type safety everywhere** — TypeScript strict mode. No `any`. All API responses typed. All component props typed.
3. **Component composition** — Small, focused components. Pages composed of reusable pieces.
4. **Consistent state** — Pinia stores own domain state. Components only own local UI state.
5. **Fail gracefully** — Loading states, empty states, error states for every async operation.

---

## 2. Design Language

### 2.1 Visual Style
- **Aesthetic:** Professional trading terminal — clean, data-dense, dark-first
- **Reference:** Ant Design Pro Finance style (the existing app's direction)
- **Typography:** System fonts via Ant Design defaults + monospace for prices/numbers

### 2.2 Color Palette

#### Dark Theme (default)
```
--color-bg-base:        #141414   (main background)
--color-bg-layout:      #1a1a1a   (sidebar, header)
--color-bg-card:        #1f1f1f   (cards, panels)
--color-bg-hover:       #262626   (hover states)
--color-primary:       #1677ff   (Ant Design blue)
--color-success:        #52c41a
--color-warning:        #faad14
--color-error:          #ff4d4f
--color-text-primary:   #ffffff
--color-text-secondary: #a6a6a6
--color-border:         #303030
```

#### Light Theme
```
--color-bg-base:        #f5f5f5
--color-bg-layout:      #ffffff
--color-bg-card:        #ffffff
--color-bg-hover:       #f0f0f0
--color-primary:        #1677ff
--color-text-primary:   #262626
--color-text-secondary: #8c8c8c
--color-border:         #d9d9d9
```

### 2.3 Spacing System
- Base unit: 8px (Ant Design default)
- Card padding: 16px or 24px
- Section gaps: 24px
- Table cell padding: 12px 16px

### 2.4 Number/Price Formatting
- Prices: 2-8 decimal places based on asset (BTC=2, altcoins=4-8)
- P&L: color-coded (green positive, red negative)
- Percentages: ±X.XX% with color
- Large numbers: comma-separated, abbreviated (1.2M, 3.5B)

---

## 3. Component Architecture

### 3.1 Component Hierarchy

```
AppLayout
├── Sidebar
├── Header
│   ├── LanguageSwitcher
│   ├── ThemeToggle
│   └── UserMenu
├── MainContent
│   └── <RouterView>
│       ├── DashboardPage
│       │   ├── SummaryCards
│       │   ├── RecentTradesTable
│       │   └── PendingOrdersTable
│       ├── PortfolioPage
│       │   ├── PositionsTable
│       │   ├── PositionForm (modal)
│       │   ├── MonitorsList
│       │   ├── AlertsList
│       │   └── PortfolioSummary
│       ├── StrategyListPage
│       │   ├── StrategyTable
│       │   ├── StrategyForm (create/edit)
│       │   └── BatchActions
│       ├── StrategyDetailPage
│       │   ├── StrategyConfig
│       │   ├── TradesTable
│       │   ├── EquityCurveChart
│       │   └── NotificationsList
│       └── ...
└── Footer
```

### 3.2 Shared Component Patterns

**DataTable (src/components/common/DataTable.vue)**
```typescript
Props: {
  columns: ColumnDef[],
  dataSource: T[],
  loading: boolean,
  pagination: PaginationConfig,
  rowKey: keyof T,
  onSort: (column, order) => void,
  onChange: (pagination, filters, sorter) => void,
}
```

**FormModal (src/components/common/FormModal.vue)**
```typescript
Props: {
  title: string,
  visible: boolean,
  loading: boolean,
  form: Record<string, any>,
  schema: FormSchema,
  width: number,
}
Emits: submit, cancel
```

**StatusBadge (src/components/common/StatusBadge.vue)**
```typescript
// Renders colored badge: running=green, stopped=gray, error=red
Props: { status: string, type: 'strategy' | 'position' | 'order' }
```

**PriceDisplay (src/components/common/PriceDisplay.vue)**
```typescript
// Formatted price with color based on change
Props: { value: number, prevValue?: number, decimals?: number }
```

**LoadingSkeleton (src/components/common/LoadingSkeleton.vue)**
```typescript
// Animated skeleton for cards, tables, charts
Props: { type: 'card' | 'table' | 'chart', rows?: number }
```

---

## 4. API Integration Pattern

### 4.1 Request → Store → Component Flow

```
Component (calls store action)
  → Store action (calls API)
    → API function (request.post/get)
      → Axios (attaches JWT, unwraps response)
        → Flask Backend
```

### 4.2 Error Handling
- API functions throw on non-2xx or `code !== 1`
- Store actions catch and set `error` state
- Components show `<a-alert>` or `<a-result>` on error
- 401 errors trigger auth store logout + redirect

### 4.3 Loading States
- Store holds `loading: boolean` per domain
- Components show `<a-spin>` overlay or skeleton
- Buttons show `<a-button loading>` during submit

### 4.4 Pagination
- Table pagination via `<a-table>` built-in
- API pagination params: `page`, `pageSize` (20 default)
- Response shape: `{ items: T[], total: number, page: number, pageSize: number }`

---

## 5. Chart Integration

### 5.1 Equity Curve (src/components/charts/EquityCurve.vue)
- Use `vue-chartjs` + `chart.js`
- Line chart: date (x) vs equity (y)
- Dark/light theme colors
- Tooltip: date, equity, % change

### 5.2 Heatmap (src/components/charts/MarketHeatmap.vue)
- Use `vue-gridheatmap` or custom SVG
- Color: green (gain) to red (loss)
- Cell: symbol + % change

### 5.3 Price Charts (Candlestick)
- Use `lightweight-charts` (TradingView library, works in both themes)
- Integrates well with Vue 3

---

## 6. Form Design

### 6.1 Strategy Form Fields
- Exchange: `<a-select>` (exchange list from market config)
- Symbol: `<a-select>` with search (symbol search API)
- Market type: `<a-select>` (spot, margin, futures)
- Indicator: `<a-select>` with parameters
- Trigger conditions: dynamic form array
- Position sizing: amount + leverage inputs
- Risk controls: stop loss %, take profit %, max positions

### 6.2 Validation
- All forms use `<a-form>` with rules
- Required fields: exchange, symbol, at least one indicator
- Numeric fields: min/max constraints
- Real-time validation feedback

---

## 7. Auth Flow

### 7.1 JWT Handling
- Token stored in `localStorage.token`
- Refresh: not implemented in backend (short-lived tokens acceptable)
- On 401: clear token, redirect to `/#/user/login?redirect=<current route>`

### 7.2 Route Guards
```typescript
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ path: '/user/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})
```

### 7.3 OAuth Flow
- Redirect to backend `/api/auth/oauth/github` or `/api/auth/oauth/google`
- Backend redirects to `/{frontend_url}/#/user/login?token=<jwt>&user=<profile>`
- Frontend reads token from URL query, stores it, redirects to dashboard

---

## 8. Performance Considerations

1. **Code splitting** — Per-route chunks via Vite dynamic imports
2. **Lazy loading** — Pages loaded on demand, not upfront
3. **Table pagination** — Never load more than 100 rows at once
4. **Chart rendering** — Only render when in viewport (Intersection Observer)
5. **API caching** — Market data cached in Pinia store with TTL (30s for prices, 5min for config)
6. **Virtual scrolling** — For long trade/order history tables

---

## 9. i18n Implementation

### 9.1 Translation Keys Structure
```
src/i18n/locales/
├── en-US.json    (source)
├── zh-CN.json
├── zh-TW.json
├── ja-JP.json
├── ko-KR.json
├── de-DE.json
├── fr-FR.json
├── es-ES.json
├── ar-SA.json
├── th-TH.json
└── vi-VN.json
```

### 9.2 Key Naming Convention
- `nav.<page>` — Navigation items
- `<page>.<section>.<item>` — Page content
- `common.<action>` — Reusable actions (save, cancel, delete, etc.)
- `error.<code>` — Error messages by code
- `success.<action>` — Success messages

---

## 10. Testing Strategy

### 10.1 Unit Tests (Vitest)
- Each Pinia store: actions, getters, state mutations
- Utility functions: formatPrice, formatPercent, parseJwt
- Component tests: FormModal, StatusBadge, DataTable

### 10.2 E2E Tests (Playwright)
- Auth flows: register, login, logout, OAuth
- Dashboard: loads with correct data
- Strategy: create → start → stop → delete
- Portfolio: add position → view P&L → delete position
- Settings: save settings → verify values

### 10.3 Test Data
- Use the existing backend's seeded test data
- Each test resets to known state

---

## 11. Build & Deployment

### 11.1 Production Build
```bash
npm run build
# Output: frontend_vue3/dist/
```

### 11.2 Docker Integration
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY frontend_vue3/ .
RUN npm ci && npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### 11.3 Deployment Options
- **Option A (replace):** Copy `dist/` to `frontend/dist/` → nginx serves as-is
- **Option B (new port):** Build to `frontend_vue3/dist/` → nginx serves at `:8889`
- Default: Option B until parity confirmed

---

## 12. Directory Structure

```
frontend_vue3/
├── public/
│   ├── favicon.ico
│   └── logo.png
├── src/
│   ├── api/
│   │   ├── request.ts         # Axios instance
│   │   ├── auth.ts
│   │   ├── dashboard.ts
│   │   ├── portfolio.ts
│   │   ├── strategy.ts
│   │   ├── quickTrade.ts
│   │   ├── market.ts
│   │   ├── indicator.ts
│   │   ├── backtest.ts
│   │   ├── aiChat.ts
│   │   ├── fastAnalysis.ts
│   │   ├── globalMarket.ts
│   │   ├── polymarket.ts
│   │   ├── settings.ts
│   │   ├── billing.ts
│   │   ├── community.ts
│   │   ├── credentials.ts
│   │   ├── user.ts
│   │   ├── ibkr.ts
│   │   └── mt5.ts
│   ├── assets/
│   │   └── styles/
│   │       └── global.less
│   ├── components/
│   │   ├── charts/
│   │   │   ├── EquityCurve.vue
│   │   │   ├── MarketHeatmap.vue
│   │   │   └── PriceChart.vue
│   │   ├── common/
│   │   │   ├── DataTable.vue
│   │   │   ├── FormModal.vue
│   │   │   ├── StatusBadge.vue
│   │   │   ├── PriceDisplay.vue
│   │   │   └── LoadingSkeleton.vue
│   │   └── layout/
│   │       ├── AppLayout.vue
│   │       ├── Sidebar.vue
│   │       ├── Header.vue
│   │       └── Footer.vue
│   ├── i18n/
│   │   ├── index.ts
│   │   └── locales/
│   │       ├── en-US.json
│   │       └── ... (9 more)
│   ├── router/
│   │   └── index.ts
│   ├── stores/
│   │   ├── app.ts
│   │   ├── auth.ts
│   │   ├── portfolio.ts
│   │   ├── strategies.ts
│   │   ├── market.ts
│   │   └── aiChat.ts
│   ├── types/
│   │   ├── api.ts             # Generated from OpenAPI
│   │   └── shims-vue.d.ts
│   ├── utils/
│   │   ├── format.ts           # formatPrice, formatPercent, formatDate
│   │   └── storage.ts         # localStorage helpers
│   ├── views/
│   │   ├── auth/
│   │   │   ├── Login.vue
│   │   │   └── Register.vue
│   │   ├── dashboard/
│   │   │   └── Dashboard.vue
│   │   ├── portfolio/
│   │   │   └── Portfolio.vue
│   │   ├── strategies/
│   │   │   ├── StrategyList.vue
│   │   │   ├── StrategyCreate.vue
│   │   │   └── StrategyDetail.vue
│   │   ├── quick-trade/
│   │   │   └── QuickTrade.vue
│   │   ├── market/
│   │   │   └── GlobalMarket.vue
│   │   ├── ai-analysis/
│   │   │   └── AIAnalysis.vue
│   │   ├── indicators/
│   │   │   └── Indicators.vue
│   │   ├── backtest/
│   │   │   └── Backtest.vue
│   │   ├── polymarket/
│   │   │   └── Polymarket.vue
│   │   ├── settings/
│   │   │   └── Settings.vue
│   │   ├── billing/
│   │   │   └── Billing.vue
│   │   ├── community/
│   │   │   └── Community.vue
│   │   ├── user/
│   │   │   └── UserManagement.vue
│   │   └── trading/
│   │       ├── IBKR.vue
│   │       └── MT5.vue
│   ├── App.vue
│   └── main.ts
├── tests/
│   ├── unit/
│   │   ├── stores/
│   │   ├── utils/
│   │   └── components/
│   └── e2e/
│       ├── auth.spec.ts
│       ├── dashboard.spec.ts
│       ├── strategy.spec.ts
│       └── portfolio.spec.ts
├── .env
├── .env.production
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
└── package.json
```
