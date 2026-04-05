# Tasks: QuantDinger Frontend Vue 3 Rewrite

## How to Use These Tasks

1. Each epic is a build phase
2. Each task is a discrete unit of work
3. Tasks within an epic can be done in parallel by different agents
4. Mark tasks complete in Beads: `bd close <id>` after implementation

---

## Epic 0: API Contract & Backend Swagger

**Goal:** Generate a complete OpenAPI 3.0 spec from the Flask backend for frontend type generation

### Task 0.1 — Add Swagger Dependencies
- **File:** `backend_api_python/requirements.txt`
- **Action:** Add `flasgger==0.9.7.1` to requirements
- **Verify:** `pip install -r requirements.txt` succeeds

### Task 0.2 — Initialize Flasgger in Flask App
- **File:** `backend_api_python/app/__init__.py`
- **Action:** Import and register Flasgger/Swagger at `/apidocs/` and `/swagger.json`
- **Verify:** `GET /apidocs/` returns Swagger UI in browser

### Task 0.3 — Annotate Auth Routes
- **File:** `backend_api_python/app/routes/auth.py`
- **Action:** Add Flasgger docstrings to all 14 auth endpoints
  - `@swag_from` decorator or YAML inline spec
  - Document request body schemas, response schemas, auth requirements
- **Verify:** Swagger UI shows auth endpoints with correct schemas

### Task 0.4 — Annotate Dashboard & Strategy Routes
- **Files:** `backend_api_python/app/routes/dashboard.py`, `strategy.py`
- **Action:** Add docstrings to all ~25 endpoints
- **Verify:** Swagger UI shows all strategy/dashboard endpoints

### Task 0.5 — Annotate Portfolio, Market, QuickTrade Routes
- **Files:** `backend_api_python/app/routes/portfolio.py`, `market.py`, `quick_trade.py`
- **Action:** Add docstrings to all ~30 endpoints
- **Verify:** Swagger UI shows all portfolio/market/trade endpoints

### Task 0.6 — Annotate Remaining Routes (AI, Indicators, Admin)
- **Files:** `ai_chat.py`, `fast_analysis.py`, `indicator.py`, `backtest.py`, `global_market.py`, `settings.py`, `billing.py`, `community.py`, `user.py`, `credentials.py`, `polymarket.py`, `ibkr.py`, `mt5.py`
- **Action:** Add docstrings to all remaining ~40 endpoints
- **Verify:** All 80 endpoints visible in Swagger UI

### Task 0.7 — Export OpenAPI YAML
- **File:** `openapi.yaml` (root of repo)
- **Action:** Export complete spec as YAML from Flasgger or manually write from route annotations
- **Verify:** `openapi.yaml` contains all 80 endpoints with request/response schemas

### Task 0.8 — Commit & Create PR
- **Action:** 
  - Create branch `feat/openapi-spec`
  - Commit all swagger annotation changes
  - Push to fork and create PR to `main`
- **Verify:** PR is open and CI passes

---

## Epic 1: Project Scaffold

**Goal:** Fully working project shell with layout, routing, auth, i18n, and typed API layer. No features yet.

### Task 1.1 — Initialize Vite Project
- **Command:** `npm create vite@latest frontend_vue3 -- --template vue-ts`
- **Action:** Install dependencies (vue-router, pinia, ant-design-vue, vue-i18n, axios)
- **Verify:** `npm run dev` starts without errors

### Task 1.2 — Configure Vite
- **File:** `frontend_vue3/vite.config.ts`
- **Action:** 
  - Set `base: '/'`
  - Add API proxy to `http://localhost:5000`
  - Configure `unplugin-vue-components` for AntD auto-import
  - Add path alias `@/` → `src/`
- **Verify:** `npm run dev` and `npm run build` both work

### Task 1.3 — Configure TypeScript
- **File:** `frontend_vue3/tsconfig.json`
- **Action:** Enable strict mode, add path aliases
- **Verify:** `npx vue-tsc --noEmit` shows zero errors

### Task 1.4 — Set Up Axios Request Utility
- **File:** `frontend_vue3/src/api/request.ts`
- **Action:** 
  - Create Axios instance with baseURL `/api`
  - Add JWT interceptor (reads `localStorage.token`)
  - Add response interceptor (unwrap `{ code, msg, data }` envelope)
  - Handle 401 → logout + redirect
- **Verify:** API calls attach JWT and unwrap response correctly

### Task 1.5 — Generate TypeScript Types from OpenAPI
- **Command:** `npx otgc -i openapi.yaml -o src/types/api.ts`
- **Action:** Generate types, fix any TypeScript errors manually
- **Verify:** `src/types/api.ts` contains all interface definitions

### Task 1.6 — Set Up Vue Router
- **File:** `frontend_vue3/src/router/index.ts`
- **Action:** 
  - Configure hash mode router
  - Define all route paths (from design.md)
  - Add navigation guard (requires auth check)
  - Lazy-load all page components
- **Verify:** Direct navigation to `/#/dashboard` shows page, `/#/user/login` is accessible

### Task 1.7 — Set Up Pinia Stores
- **Files:** `frontend_vue3/src/stores/auth.ts`, `app.ts`
- **Action:** 
  - `auth` store: token, user, login(), logout(), fetchUser()
  - `app` store: theme, sidebarCollapsed, language
- **Verify:** Stores work correctly, persist to localStorage

### Task 1.8 — Create Layout Components
- **Files:** `src/components/layout/AppLayout.vue`, `Sidebar.vue`, `Header.vue`, `Footer.vue`
- **Action:**
  - AppLayout with Ant Design layout structure
  - Sidebar with `<a-menu>` matching route list
  - Header with language switcher, theme toggle, user dropdown
  - Footer with version
- **Verify:** Sidebar collapses, header controls work, footer visible

### Task 1.9 — Set Up i18n
- **Files:** `src/i18n/locales/en-US.json` + 9 other languages
- **Action:** 
  - Extract all English strings from components into locale files
  - Set up vue-i18n with 10 languages
  - Persist language preference
- **Verify:** All 10 languages selectable and switch UI text

### Task 1.10 — Set Up Theme System
- **Action:**
  - Configure Ant Design dark/light theme via ConfigProvider
  - Theme toggle in header
  - Persist theme in localStorage
- **Verify:** Toggle between dark and light without page reload, no flash on load

### Task 1.11 — Set Up Login Page
- **File:** `src/views/auth/Login.vue`
- **Action:**
  - Email + password form
  - Calls `authApi.login()`
  - Stores JWT + redirects
  - Error handling
- **Verify:** Can log in with valid credentials, error shown for invalid

### Task 1.12 — Set Up Register Page
- **File:** `src/views/auth/Register.vue`
- **Action:** Registration form calling `authApi.register()`
- **Verify:** Can register, then login

### Task 1.13 — Commit & PR (Scaffold)
- **Branch:** `feat/frontend-scaffold`
- **Verify:** PR open, `npm run build` passes in CI

---

## Epic 2: Auth + Dashboard + Portfolio

**Goal:** User can register, login, see dashboard, and manage portfolio positions

### Task 2.1 — Dashboard API + Store + Page
- **Files:** `src/api/dashboard.ts`, `src/stores/dashboard.ts`, `src/views/dashboard/Dashboard.vue`
- **Action:** Summary, recent trades, pending orders, running strategies
- **Verify:** Dashboard matches existing app data

### Task 2.2 — Portfolio API + Store
- **Files:** `src/api/portfolio.ts`, `src/stores/portfolio.ts`
- **Action:** Positions, monitors, alerts, groups, summary endpoints
- **Verify:** All CRUD operations work

### Task 2.3 — Portfolio Page (Positions)
- **File:** `src/views/portfolio/Portfolio.vue`
- **Action:** Positions table with add/edit/delete modals
- **Verify:** Can add a position, see P&L, delete it

### Task 2.4 — Portfolio Monitors & Alerts
- **Action:** Monitors list + alerts list with create/edit/delete
- **Verify:** Can create a price alert, see it trigger (manual test)

### Task 2.5 — User Profile + Notification Settings
- **Files:** `src/api/user.ts`, `src/views/user/Profile.vue`
- **Action:** View/edit profile, notification settings
- **Verify:** Settings save correctly

### Task 2.6 — Commit & PR (Phase 2)
- **Branch:** `feat/auth-dashboard-portfolio`

---

## Epic 3: Strategy Management

**Goal:** Full strategy CRUD with start/stop and performance views

### Task 3.1 — Strategy API + Store
- **Files:** `src/api/strategy.ts`, `src/stores/strategies.ts`
- **Action:** All 20+ strategy endpoints
- **Verify:** All CRUD + start/stop operations work

### Task 3.2 — Strategy List Page
- **File:** `src/views/strategies/StrategyList.vue`
- **Action:** Table with status badges, batch actions, create button
- **Verify:** Matches existing strategy list

### Task 3.3 — Strategy Create/Edit Form
- **File:** `src/views/strategies/StrategyCreate.vue`
- **Action:** Full form with exchange selector, symbol search, indicator config, trigger conditions, risk controls
- **Verify:** Can create a strategy with all fields

### Task 3.4 — Strategy Detail Page
- **File:** `src/views/strategies/StrategyDetail.vue`
- **Action:** Config display, trades table, equity curve, notifications
- **Verify:** Shows same data as existing app

### Task 3.5 — Strategy Backtest Integration
- **Action:** Backtest form + history list + results display
- **Verify:** Can run backtest and see results

### Task 3.6 — Commit & PR (Phase 3)
- **Branch:** `feat/strategy-management`

---

## Epic 4: Trading + Market Data

**Goal:** Quick trade execution and full market data views

### Task 4.1 — Quick Trade API + Page
- **Files:** `src/api/quickTrade.ts`, `src/views/quick-trade/QuickTrade.vue`
- **Action:** Balance display, order form, position display, order history
- **Verify:** Can place a market order and see position

### Task 4.2 — Global Market Page
- **File:** `src/views/market/GlobalMarket.vue`
- **Action:** Fear & Greed, indices, forex, crypto, commodities panels
- **Verify:** Matches existing app market overview

### Task 4.3 — Watchlist
- **Action:** Add/remove symbols, price ticker, watchlist prices refresh
- **Verify:** Watchlist persists and prices update

### Task 4.4 — IBKR Page
- **File:** `src/views/trading/IBKR.vue`
- **Action:** Connect/disconnect, account, positions, orders, place order
- **Verify:** IBKR panel matches existing app

### Task 4.5 — MT5 Page
- **File:** `src/views/trading/MT5.vue`
- **Action:** Same as IBKR page for MT5
- **Verify:** MT5 panel works

### Task 4.6 — Commit & PR (Phase 4)
- **Branch:** `feat/trading-market-data`

---

## Epic 5: AI Analysis + Indicators

**Goal:** AI multi-agent chat, fast analysis, and indicator backtesting

### Task 5.1 — AI Chat API + Store
- **Files:** `src/api/aiChat.ts`, `src/stores/aiChat.ts`
- **Action:** Chat message, history list, history save
- **Verify:** Chat messages send and receive responses

### Task 5.2 — AI Analysis Page
- **File:** `src/views/ai-analysis/AIAnalysis.vue`
- **Action:** Multi-agent panel, chat history, message input
- **Verify:** Matches existing app AI chat experience

### Task 5.3 — Fast Analysis Page
- **File:** `src/views/ai-analysis/FastAnalysis.vue`
- **Action:** Symbol input, analysis trigger, results display
- **Verify:** Fast analysis results display correctly

### Task 5.4 — Indicator API + Page
- **Files:** `src/api/indicator.ts`, `src/views/indicators/Indicators.vue`
- **Action:** Indicator list, code editor, save/delete, AI generate
- **Verify:** Can create and save a custom indicator

### Task 5.5 — Indicator Backtest Page
- **File:** `src/views/backtest/Backtest.vue`
- **Action:** Run backtest, history list, precision info, AI analyze
- **Verify:** Backtest runs and results display

### Task 5.6 — Commit & PR (Phase 5)
- **Branch:** `feat/ai-analysis-indicators`

---

## Epic 6: Admin + Settings + Billing + Community

**Goal:** Complete remaining pages for full feature parity

### Task 6.1 — Settings Page
- **Files:** `src/api/settings.ts`, `src/views/settings/Settings.vue`
- **Action:** Schema display, values, save, OpenRouter balance
- **Verify:** Settings save and persist

### Task 6.2 — Exchange Credentials
- **File:** `src/views/settings/Credentials.vue`
- **Action:** List/create/delete credentials, egress IP
- **Verify:** Credentials are created and listed

### Task 6.3 — Billing Page
- **File:** `src/views/billing/Billing.vue`
- **Action:** Plans display, purchase flow, USDT payment
- **Verify:** Plans and payment UI render

### Task 6.4 — Community Page
- **File:** `src/views/community/Community.vue`
- **Action:** Browse indicators, purchases, comments
- **Verify:** Community features accessible

### Task 6.5 — User Management (Admin)
- **File:** `src/views/admin/UserManagement.vue`
- **Action:** CRUD users, roles, credits, VIP
- **Verify:** Admin can manage users

### Task 6.6 — Polymarket Page
- **File:** `src/views/polymarket/Polymarket.vue`
- **Action:** Analysis and history
- **Verify:** Polymarket integration works

### Task 6.7 — Commit & PR (Phase 6)
- **Branch:** `feat/admin-settings-billing`

---

## Epic 7: Testing & Verification

**Goal:** Automated test suite ensuring no regressions

### Task 7.1 — TypeScript Strict Check
- **Command:** `vue-tsc --noEmit`
- **Fix:** All TypeScript errors resolved
- **Verify:** Zero errors

### Task 7.2 — Unit Tests (Vitest)
- **Files:** `tests/unit/stores/auth.spec.ts`, `*.spec.ts`
- **Action:** Test auth store, format utilities, key components
- **Verify:** All tests pass

### Task 7.3 — E2E Tests (Playwright)
- **Files:** `tests/e2e/auth.spec.ts`, `dashboard.spec.ts`, `strategy.spec.ts`, `portfolio.spec.ts`
- **Action:** Automate key user flows
- **Verify:** All E2E tests pass in CI

### Task 7.4 — Feature Parity Checklist
- **Action:** Run existing app and new app side-by-side, check every item
- **Document:** Any discrepancies, fix them
- **Verify:** 100% feature parity confirmed

### Task 7.5 — i18n Completeness Check
- **Action:** Verify all 10 languages have all keys
- **Fix:** Any missing translation keys
- **Verify:** All languages render without `MISSING_TRANSLATION` warnings

### Task 7.6 — Performance Check
- **Action:** Lighthouse audit on key pages
- **Verify:** LCP < 2.5s, no major layout shifts

### Task 7.7 — Commit & PR (Phase 7)
- **Branch:** `feat/testing-verification`

---

## Epic 8: Deployment

**Goal:** Production deployment with zero downtime

### Task 8.1 — Production Build
- **Command:** `npm run build`
- **Verify:** `dist/` builds with no errors

### Task 8.2 — Docker Build
- **File:** `Dockerfile` in `frontend_vue3/`
- **Action:** Multi-stage build (Node → nginx)
- **Verify:** Docker image builds and runs

### Task 8.3 — Deploy to Staging
- **Action:** Deploy to staging port (8889) or environment
- **Verify:** Smoke test in staging

### Task 8.4 — Production Deploy
- **Action:** Either swap `frontend/dist/` or cut over to new nginx config
- **Verify:** Production URL works

### Task 8.5 — Final Verification
- **Action:** Run E2E tests against production
- **Verify:** All tests green, user feedback positive
