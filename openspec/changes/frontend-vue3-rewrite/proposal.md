# Proposal: QuantDinger Frontend Vue 3 Rewrite

## 1. Concept & Vision

**QuantDinger** is an all-in-one local-first quantitative trading workspace supporting Crypto, Stocks, Forex, and Futures. The existing frontend is a compiled Vue 2 app with no source code — any customization, bug fix, or feature addition requires reverse-engineering minified bundles.

This project rewrites the frontend from scratch using modern Vue 3, giving the team a maintainable, typed, source-controlled codebase. The new frontend must achieve complete functional parity with the existing app while establishing a clean architecture foundation for future development.

---

## 2. Problem Statement

1. **No source code** — The frontend exists only as compiled Vue 2 + Ant Design dist bundles. Any development is trial-and-error against minified JS.
2. **API contract is undocumented** — ~80 REST endpoints exist with no formal spec. Frontend and backend evolve independently with no shared truth.
3. **Tech stack is dated** — Vue 2 is EOL. No TypeScript. No modern tooling.
4. **No test coverage** — No automated way to verify feature parity or catch regressions.

---

## 3. Goals

### Primary
- Achieve **100% feature parity** with the existing compiled frontend
- Establish a **typed API contract** (OpenAPI 3.0) shared by frontend and backend
- Deliver a **maintainable codebase** — clean architecture, TypeScript throughout, component tests

### Secondary
- Modern UI/UX polish (dark/light theme improvements)
- Better i18n support (10 languages already exist in locale bundles)
- Improved performance (Vite dev experience, code splitting)

### Out of Scope (for this rewrite)
- Backend changes
- Database schema changes
- New features not in the existing app
- Mobile-specific UI (responsive web only)

---

## 4. Technical Stack

| Layer | Technology |
|-------|-----------|
| Framework | Vue 3 (Composition API + `<script setup>`) |
| Build | Vite 5 |
| Language | TypeScript 5 (strict mode) |
| UI Library | Ant Design Vue 4 |
| State | Pinia |
| Router | Vue Router 4 (hash mode, for SPA compat) |
| HTTP Client | Axios (typed interceptors, JWT handling) |
| i18n | vue-i18n 9 |
| Testing | Vitest + @vue/test-utils + Playwright |
| API Contract | OpenAPI 3.0 (flasgger + manual YAML) |

---

## 5. Backend API Summary

The backend is a Flask REST API running on port 5000 (Docker: `backend:5000`). ~80 endpoints across 20 route modules:

| Domain | Routes | Auth |
|--------|--------|------|
| Auth | login, register, OAuth, logout, info, change-password | Public + JWT |
| Dashboard | summary, pendingOrders | JWT |
| Portfolio | positions, monitors, alerts, groups | JWT |
| Strategy | CRUD, start/stop, backtest, trades, equityCurve, notifications | JWT |
| Quick Trade | place-order, balance, position, close-position, history | JWT |
| Market | config, symbols, watchlist, prices | Public + JWT |
| Indicator | getIndicators, saveIndicator, deleteIndicator, backtest, aiGenerate | JWT |
| Backtest | run, history, precision-info, aiAnalyze | JWT |
| AI Chat | chat/message, chat/history, chat/history/save | JWT |
| Fast Analysis | analyze, history, feedback, performance | JWT |
| Global Market | overview, heatmap, news, calendar, sentiment | Public |
| Polymarket | analyze, history | JWT |
| Settings | schema, values, save, openrouter-balance | JWT |
| Billing | plans, purchase, usdt/create, usdt/order | JWT |
| Community | indicators, my-purchases, comments, admin reviews | JWT |
| Credentials | list, create, delete, get, egress-ip | JWT |
| User (admin) | list, detail, create, update, delete, roles, set-credits | JWT |
| IBKR | status, connect, disconnect, account, positions, orders, place-order | JWT |
| MT5 | status, connect, disconnect, account, positions, orders, symbols | JWT |

**API base URL:** `/api/` proxied through nginx on port 8888

**Response envelope:**
```json
{ "code": 1, "msg": "success", "data": { ... } }
```

**Authentication:** JWT Bearer token in `Authorization` header, issued by `/api/auth/login`

---

## 6. Feature Parity Checklist

### Auth & User
- [ ] Login (email/password)
- [ ] Register
- [ ] Send verification code
- [ ] Login with code
- [ ] Change password
- [ ] Reset password
- [ ] OAuth: GitHub
- [ ] OAuth: Google
- [ ] Logout
- [ ] User info / profile
- [ ] Notification settings

### Layout & Shell
- [ ] Sidebar navigation (collapsed/expanded)
- [ ] Header (logo, language switcher, theme toggle, user menu)
- [ ] Footer
- [ ] SPA routing (all routes fall back to index.html)
- [ ] 10-language i18n (ar-SA, de-DE, fr-FR, ja-JP, ko-KR, th-TH, vi-VN, zh-CN, zh-TW, en-US)
- [ ] Dark / light theme

### Dashboard
- [ ] Summary panel (total balance, today's P&L, running strategies count)
- [ ] Recent trades list
- [ ] Pending orders list
- [ ] Running strategies quick-view

### Portfolio
- [ ] Positions list (add/edit/delete manual positions)
- [ ] Position detail (entry price, current price, P&L, % change)
- [ ] AI monitors (create/edit/delete/run)
- [ ] Alerts (price alerts with conditions)
- [ ] Groups (position grouping/filtering)
- [ ] Portfolio summary (total value, allocation)

### Trading Assistant (Strategies)
- [ ] Strategy list (all strategies with status indicators)
- [ ] Create strategy form (exchange, symbol, indicators, triggers, position sizing, risk controls)
- [ ] Edit strategy
- [ ] Delete strategy (single + batch)
- [ ] Start strategy (single + batch)
- [ ] Stop strategy (single + batch)
- [ ] Strategy detail view (configuration, performance)
- [ ] Trades view (per strategy)
- [ ] Equity curve
- [ ] Backtest results (run backtest, view history)
- [ ] Notifications (read/unread/clear)

### Quick Trade
- [ ] Balance display (exchange wallet balance)
- [ ] Place market order
- [ ] Place limit order
- [ ] Current position display
- [ ] Close position
- [ ] Order history

### Market Data
- [ ] Market overview (Fear & Greed, indices, forex, crypto, commodities)
- [ ] Heatmap
- [ ] Financial news
- [ ] Economic calendar
- [ ] Market sentiment
- [ ] Symbol search
- [ ] Hot symbols
- [ ] Watchlist (add/remove/prices)

### AI Analysis
- [ ] Multi-agent panel (Investment Director, Market Analyst, Quantitative Expert, Risk Manager, Operations Specialist)
- [ ] Chat with AI (send message, receive streamed response)
- [ ] Chat history (list, save, load)
- [ ] Fast analysis (single-symbol analysis with confidence/confirmation levels)
- [ ] Analysis history
- [ ] Feedback submission
- [ ] Performance metrics
- [ ] Similar patterns

### Indicator Backtest
- [ ] My indicators list
- [ ] Indicator code editor
- [ ] Indicator save/delete
- [ ] Indicator parameter configuration
- [ ] AI indicator generation
- [ ] Run backtest (single symbol)
- [ ] Backtest history
- [ ] Precision info
- [ ] AI-analyze backtest runs

### Polymarket
- [ ] Prediction market analysis
- [ ] History

### Settings
- [ ] Settings schema display
- [ ] Settings values display
- [ ] Save settings
- [ ] OpenRouter balance check
- [ ] Test connection
- [ ] Exchange credentials (create/list/delete)

### Billing
- [ ] Membership plans display
- [ ] Purchase membership
- [ ] USDT payment flow (create order, check order status)

### Community
- [ ] Browse indicators
- [ ] Indicator detail
- [ ] Purchase indicator
- [ ] My purchases
- [ ] Comments (read/add/update)
- [ ] Indicator performance
- [ ] Admin: pending indicators review
- [ ] Admin: review stats
- [ ] Admin: approve/reject/unpublish/delete indicators

### User Management (Admin)
- [ ] User list
- [ ] Create user
- [ ] Update user
- [ ] Delete user
- [ ] Reset password
- [ ] Set credits
- [ ] Set VIP
- [ ] Roles display
- [ ] Credits log
- [ ] Referrals
- [ ] My credits log

### IBKR Trading
- [ ] Connect/disconnect
- [ ] Status display
- [ ] Account info
- [ ] Positions
- [ ] Orders (list/cancel)
- [ ] Place order
- [ ] Quote

### MT5 Trading
- [ ] Connect/disconnect
- [ ] Status display
- [ ] Account info
- [ ] Positions
- [ ] Orders (list/cancel)
- [ ] Close position
- [ ] Symbols list
- [ ] Quote

---

## 7. Architecture

```
frontend_vue3/
├── public/
├── src/
│   ├── api/                    # Axios clients, one file per domain
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
│   ├── components/             # Shared/reusable components
│   │   ├── common/             # Buttons, cards, tables, modals
│   │   ├── layout/             # AppLayout, Sidebar, Header, Footer
│   │   └── charts/             # Equity curve, heatmap, price charts
│   ├── views/                  # Page components (one per route)
│   │   ├── auth/               # Login, Register
│   │   ├── dashboard/
│   │   ├── portfolio/
│   │   ├── strategies/
│   │   ├── quick-trade/
│   │   ├── market/
│   │   ├── ai-analysis/
│   │   ├── indicators/
│   │   ├── backtest/
│   │   ├── polymarket/
│   │   ├── settings/
│   │   ├── billing/
│   │   ├── community/
│   │   ├── user/               # Admin: user management
│   │   └── trading/           # IBKR, MT5
│   ├── stores/                 # Pinia stores
│   │   ├── auth.ts
│   │   ├── app.ts              # Theme, sidebar, language
│   │   ├── portfolio.ts
│   │   ├── strategies.ts
│   │   └── ...
│   ├── router/
│   │   └── index.ts
│   ├── i18n/
│   │   ├── locales/            # 10 language JSON files
│   │   └── index.ts
│   ├── types/                  # TypeScript interfaces (generated from OpenAPI)
│   │   └── api.ts
│   ├── utils/
│   │   ├── request.ts          # Axios instance with interceptors
│   │   └── format.ts
│   ├── App.vue
│   └── main.ts
├── tests/
│   ├── unit/                   # Vitest component tests
│   └── e2e/                    # Playwright E2E tests
├── openapi.yaml                # OpenAPI 3.0 spec (source of truth)
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 8. Phases & Milestones

### Phase 0: Backend API Contract
- Add flasgger to backend, annotate endpoints
- Generate openapi.yaml
- Verify API docs at /apidocs/

### Phase 1: Project Scaffold
- Initialize Vite + Vue 3 + TypeScript project
- Configure Ant Design Vue, Pinia, Vue Router, vue-i18n
- Set up Axios with JWT interceptors
- Generate TypeScript types from openapi.yaml
- Implement layout shell (sidebar, header, footer)
- Configure dark/light theme
- Set up i18n with 10 languages
- **Deliverable:** `npm run dev` shows login page, navigating to dashboard works

### Phase 2: Auth + Core Pages
- Login, register, OAuth flows
- JWT storage and refresh
- User profile and notification settings
- Dashboard (summary, recent trades, pending orders, running strategies)
- **Deliverable:** User can register, login, see dashboard

### Phase 3: Portfolio + Strategy (core trading)
- Portfolio positions (CRUD)
- Portfolio monitors and alerts
- Portfolio groups and summary
- Strategy list, create, edit, delete
- Strategy start/stop/batch operations
- Strategy detail, trades, equity curve
- Strategy notifications
- **Deliverable:** User can create and run a strategy

### Phase 4: Trading + Market Data
- Quick trade (place order, balance, positions, history)
- Market overview, heatmap, news, calendar, sentiment
- Watchlist
- Symbol search
- IBKR and MT5 trading panels
- **Deliverable:** User can view markets and place a quick trade

### Phase 5: Intelligence Layer
- AI multi-agent chat panel
- Chat history
- Fast analysis
- Indicator list, editor, save/delete
- Indicator backtest and history
- **Deliverable:** User can chat with AI and run an indicator backtest

### Phase 6: Admin + Polish
- Settings (schema, values, save)
- Exchange credentials management
- Billing/plans display
- Community indicators marketplace
- User management (admin)
- **Deliverable:** All features accessible and functional

### Phase 7: Testing & Verification
- Component unit tests (Vitest)
- E2E smoke tests (Playwright)
- Feature parity comparison
- i18n completeness check
- Build verification
- **Deliverable:** CI passes, feature parity confirmed

### Phase 8: Deploy
- Build production dist
- Swap with existing frontend or deploy on new port
- Smoke test production

---

## 9. Dependencies

### Frontend Development
- Node.js 20+
- npm 10+
- Vite 5
- Vue 3.4+
- TypeScript 5
- Ant Design Vue 4
- Pinia 2
- Vue Router 4
- vue-i18n 9
- Axios
- Vitest + @vue/test-utils
- Playwright

### Backend (for local development)
- Docker + Docker Compose
- PostgreSQL 15 (via Docker)
- Python 3.12
- Flask + existing requirements

---

## 10. Verification Plan

### Automated Tests
| Test | Tool | Coverage |
|------|------|----------|
| TypeScript compile | `tsc --noEmit` | All TypeScript files |
| Build | `npm run build` | Full production build |
| Unit tests | Vitest | Components, stores, utils |
| API contract | supertest + OpenAPI validator | All 80 endpoints |
| E2E smoke | Playwright | Login, dashboard, strategy CRUD, portfolio view |
| Visual regression | Playwright screenshots | Key pages |

### Manual Verification
- Side-by-side comparison with existing app (feature parity)
- i18n spot-check (all 10 languages render)
- Theme toggle (dark/light all pages)
- Empty states (no positions, no strategies)
- Error states (API down, invalid credentials)

---

## 11. Decisions Made

1. **Frontend location**: Single repo at `frontend_vue3/` folder
2. **Deploy strategy**: New port (e.g., `:8889`) — existing system stays running for comparison
3. **Design deviations**: Allow reasonable UI/UX improvements during rewrite
4. **Auth storage**: JWT in `localStorage` for now (httpOnly cookie is a future improvement)
5. **CI/CD**: GitHub Actions for build + test on PR (TODO: implement in Epic 8)
