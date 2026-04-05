# QuantDinger Frontend Reverse-Engineering Plan

> **Objective:** Reverse-engineer the QuantDinger Vue.js frontend by capturing live API traffic, then build a new frontend from the captured specifications.

---

## 1. Executive Summary

### Approach
Since only the bundled/minified frontend dist is available (no source), the strategy is to **monitor live HTTP/WebSocket traffic** between the existing frontend and the Python/Flask backend, systematically exercise every UI feature, capture all API calls, and build a complete API specification. A new frontend (Vue 3 + TypeScript) is then built against this spec.

### Backend at a Glance
- **Framework:** Python/Flask
- **Auth:** JWT (Bearer token), `login_required` decorator on most endpoints
- **Database:** SQLite or PostgreSQL via `get_db_connection()`
- **WebSocket:** None observed in routes (polling-based)
- **Static file serving:** `dist/` folder (Vue build output)

### API URL Prefix Pattern
```
/api/auth/*        → Authentication (login, register, OAuth)
/api/users/*       → User management (admin only)
/api/market/*      → Market data, watchlists, symbol search
/api/indicator/*   → K-line data, indicators, backtest
/api/dashboard/*   → Dashboard summary, pending orders
/api/*             → Strategy CRUD, start/stop, trades
/api/portfolio/*   → Positions, alerts, monitors
/api/credentials/* → Exchange API key vault
/api/settings/*    → System config (admin only)
/api/global-market/* → Global indices, heatmap, news, sentiment
/api/community/*   → Indicator marketplace
/api/fast-analysis/* → AI-powered symbol analysis
/api/billing/*     → Membership plans, credits
/api/quick-trade/* → Direct order placement
/api/ibkr/*        → Interactive Brokers (US stocks)
/api/mt5/*         → MetaTrader 5
/api/polymarket/*  → Polymarket prediction markets
/api/ai/*          → AI chat (stub)
```

### Key Auth Flow
1. `POST /api/auth/login` → returns `{"token": "...", "userinfo": {...}}`
2. Frontend stores JWT in `localStorage` (or cookie)
3. Subsequent requests: `Authorization: Bearer <token>`
4. Vue Router hash mode: `/#/user/login`

---

## 2. Traffic Monitoring Setup

### Option A: mitmproxy (Recommended — free, scriptable)

**Why:** Handles both HTTP and HTTPS, supports WebSocket traffic, can export to HAR/JSON, scriptable for automated replay.

#### Step 1: Install
```bash
pip install mitmproxy
# or
brew install mitmproxy  # macOS
sudo apt install mitmproxy  # Ubuntu/Debian
```

#### Step 2: Generate & Install CA Certificate (for HTTPS decryption)

```bash
# Start mitmproxy once to generate certificates
mitmproxy --listen-port 8080

# Certificate is stored at:
#   Linux/macOS: ~/.mitmproxy/mitmproxy-ca-cert.pem
#   Windows: %USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.pem
```

**Browser installation (Chrome/Firefox):**
1. Open browser → Settings → Privacy → Certificates → Authorities
2. Import `~/.mitmproxy/mitmproxy-ca-cert.pem`
3. Mark it as "Trusted"

**System-wide (Linux):**
```bash
sudo cp ~/.mitmproxy/mitmproxy-ca-cert.pem /usr/local/share/ca-certificates/mitmproxy.crt
sudo update-ca-certificates
```

#### Step 3: Start mitmproxy for QuantDinger

```bash
# Listen on localhost:8080, reverse-proxy to backend (e.g., localhost:5000)
mitmproxy --listen-port 8080 --listen-host 127.0.0.1 \
  --mode reverse:http://127.0.0.1:5000 \
  -w capture.mitm

# For HTTPS backend, add:
#   --ssl-insecure
```

**Alternative: Transparent proxy mode (intercepts all traffic):**
```bash
# Requires iptables sudo rules
sudo sysctl -w net.ipv4.ip_forward=1
mitmproxy --listen-port 8080 --mode transparent
```

#### Step 4: Configure Frontend to Use Proxy

Set browser/system proxy:
```
HTTP Proxy:  127.0.0.1:8080
HTTPS Proxy: 127.0.0.1:8080
```

For the Vue dev server (`npm run dev` or existing built dist served by nginx):
```nginx
# If serving via nginx, add proxy to backend:
location /api/ {
    proxy_pass http://127.0.0.1:5000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

#### Step 5: Capture WebSocket Traffic
mitmproxy handles WebSocket transparently. If the backend uses WebSockets, they will appear as HTTP Upgrade requests in the flow.

#### Step 6: Export Captured Traffic
```bash
# From mitmproxy UI: press 'w' on a flow → save as HAR
# Or use mitmdump for scripted export:
mitmdump -ns my_script.py -w capture.mitm

# Convert .mitm to HAR using:
#   https://github.com/swoolcock/mitm2har
#   Or: Open mitmproxy → Export → HAR
```

### Option B: Browser DevTools (Simplest — no setup)

**Use when:** You just need to observe, not automate.

1. Open browser DevTools (F12) → **Network** tab
2. Set filter to `Doc` + `XHR` (Fetch API) + **check "WS"** for WebSocket
3. Check **Preserve log** (persists across navigation)
4. Check **Disable cache** (ensures fresh requests)
5. Exercise the UI fully
6. Right-click any row → **Save all as HAR**
7. HAR file can be imported into Postman, Insomnia, or converted to OpenAPI

**DevTools limitations:**
- No request replay
- WebSocket frames hard to inspect (use **Messages** sub-tab)
- Hard to automate UI exploration

### Option C: Charles Proxy (GUI, paid ~$50)

**Use when:** You prefer a GUI and need easy SSL pinning bypass.

1. Proxy → SSL Proxying Settings → Enable SSL Proxying
2. Add location: `localhost:*` and `127.0.0.1:*`
3. Install Charles root certificate in browser/system
4. Recording auto-starts

### Option D: Burp Suite (Free Community)

**Use when:** You need professional-grade interception and security review.

1. Proxy → Options → Proxy Listeners → Add (127.0.0.1:8080)
2. SSL Pass-Through: add backend domains
3. Intercept off; use **Target → Site Map** to review recorded traffic
4. Export: right-click site → **Save all as HAR**

### Recommended Setup for This Project

**Use mitmproxy + browser DevTools in combination:**

```
Phase 1 (Discovery):     Browser DevTools → export HAR → understand UI structure
Phase 2 (Capture):       mitmproxy recording → full UI exercise → export HAR
Phase 3 (Automation):    mitmdump script + Playwright → auto-explore UI
```

---

## 3. Complete API Endpoints

### 3.1 Health & Config (No Auth Required)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | API index (name, version, status) |
| GET | `/health` | Health check |
| GET | `/api/health` | Health check (alternate path) |
| GET | `/api/market/config` | Public config (AI models, app settings) |
| GET | `/api/market/types` | Available market types |
| GET | `/api/market/menuFooterConfig` | Footer/menu config |
| GET | `/api/auth/security-config` | Public security config (turnstile, OAuth) |

### 3.2 Authentication (`/api/auth`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/api/auth/login` | Username/password login | No |
| POST | `/api/auth/login-code` | Email code login (auto-register) | No |
| POST | `/api/auth/send-code` | Send email verification code | No |
| POST | `/api/auth/register` | Register with email+code | No |
| POST | `/api/auth/reset-password` | Reset password via email code | No |
| POST | `/api/auth/change-password` | Change password (logged in) | Yes |
| GET | `/api/auth/oauth/google` | Initiate Google OAuth | No |
| GET | `/api/auth/oauth/google/callback` | Google OAuth callback | No |
| GET | `/api/auth/oauth/github` | Initiate GitHub OAuth | No |
| GET | `/api/auth/oauth/github/callback` | GitHub OAuth callback | No |
| POST | `/api/auth/logout` | Logout (client-side only) | No |
| GET | `/api/auth/info` | Get current user info | Yes |

**Login Request Example:**
```json
POST /api/auth/login
{
  "username": "admin",
  "password": "123456",
  "turnstile_token": "optional"
}
```

**Login Response Example:**
```json
{
  "code": 1,
  "msg": "Login successful",
  "data": {
    "token": "eyJhbGc...",
    "userinfo": {
      "id": 1,
      "username": "admin",
      "nickname": "Admin",
      "avatar": "/avatar2.jpg",
      "is_demo": false,
      "role": {
        "id": "admin",
        "permissions": ["dashboard", "view", "indicator", "backtest", ...]
      }
    }
  }
}
```

**Standard Error Response:**
```json
{ "code": 0, "msg": "Error description", "data": null }
```

### 3.3 Market Data (`/api/market`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/market/config` | Public config (AI models list) | No |
| GET | `/api/market/types` | Available market types | No |
| GET | `/api/market/menuFooterConfig` | Menu/footer config | No |
| GET | `/api/market/symbols/search?q=` | Search symbols by keyword | Yes |
| GET | `/api/market/symbols/hot` | Hot/trending symbols | Yes |
| GET | `/api/market/watchlist/get` | Get user's watchlist | Yes |
| POST | `/api/market/watchlist/add` | Add symbol to watchlist | Yes |
| POST | `/api/market/watchlist/remove` | Remove from watchlist | Yes |
| GET | `/api/market/watchlist/prices` | Get prices for watchlist symbols | Yes |
| GET | `/api/market/price?symbol=&market=` | Get price for specific symbol(s) | Yes |
| POST | `/api/market/stock/name` | Resolve stock symbol to full name | Yes |

### 3.4 K-Line / Indicator Data (`/api/indicator`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/indicator/kline?market=&symbol=&timeframe=&limit=` | OHLCV K-line data | Yes |
| GET | `/api/indicator/getIndicators` | List saved indicators | Yes |
| POST | `/api/indicator/saveIndicator` | Save indicator (Python code) | Yes |
| POST | `/api/indicator/deleteIndicator` | Delete indicator | Yes |
| GET | `/api/indicator/getIndicatorParams?id=` | Get indicator parameters | Yes |
| POST | `/api/indicator/verifyCode` | Validate indicator Python code | Yes |
| POST | `/api/indicator/aiGenerate` | AI-generate indicator from description | Yes |
| POST | `/api/indicator/callIndicator` | Execute indicator on symbol/timeframe | Yes |
| POST | `/api/indicator/backtest` | Run backtest on indicator | Yes |
| GET | `/api/indicator/backtest/history` | Get backtest run history | Yes |
| GET | `/api/indicator/backtest/get?id=` | Get specific backtest result | Yes |
| POST | `/api/indicator/backtest/aiAnalyze` | AI analysis of backtest results | Yes |
| GET | `/api/indicator/backtest/precision-info` | Backtest precision info | Yes |

**K-line Request Example:**
```
GET /api/indicator/kline?market=Crypto&symbol=BTC/USDT&timeframe=1H&limit=300
```

**callIndicator Request Example:**
```json
POST /api/indicator/callIndicator
{
  "indicator_id": 5,
  "market": "Crypto",
  "symbol": "BTC/USDT",
  "timeframe": "1D",
  "params": {"period": 14}
}
```

### 3.5 Strategies (`/api`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/strategies` | List user's strategies | Yes |
| GET | `/api/strategies/detail?id=` | Get strategy detail | Yes |
| POST | `/api/strategies/create` | Create strategy | Yes |
| POST | `/api/strategies/batch-create` | Batch create strategies | Yes |
| POST | `/api/strategies/batch-start` | Start multiple strategies | Yes |
| POST | `/api/strategies/batch-stop` | Stop multiple strategies | Yes |
| DELETE | `/api/strategies/batch-delete` | Delete multiple strategies | Yes |
| PUT | `/api/strategies/update` | Update strategy | Yes |
| DELETE | `/api/strategies/delete?id=` | Delete strategy | Yes |
| GET | `/api/strategies/trades?strategy_id=` | Get strategy trade history | Yes |
| GET | `/api/strategies/positions?strategy_id=` | Get strategy positions | Yes |
| GET | `/api/strategies/equityCurve?strategy_id=` | Equity curve data | Yes |
| POST | `/api/strategies/stop` | Stop strategy | Yes |
| POST | `/api/strategies/start` | Start strategy | Yes |
| POST | `/api/strategies/test-connection` | Test exchange connection | Yes |
| POST | `/api/strategies/get-symbols` | Get symbols for exchange | Yes |
| POST | `/api/strategies/preview-compile` | Preview strategy code compilation | Yes |
| GET | `/api/strategies/notifications` | Get strategy notifications | Yes |
| GET | `/api/strategies/notifications/unread-count` | Unread notification count | Yes |
| POST | `/api/strategies/notifications/read` | Mark notification as read | Yes |
| POST | `/api/strategies/notifications/read-all` | Mark all as read | Yes |
| DELETE | `/api/strategies/notifications/clear` | Clear all notifications | Yes |

### 3.6 Dashboard (`/api/dashboard`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/dashboard/summary` | Dashboard overview (positions, PnL, etc.) | Yes |
| GET | `/api/dashboard/pendingOrders?page=&pageSize=` | Pending orders list | Yes |
| DELETE | `/api/dashboard/pendingOrders/<id>` | Cancel pending order | Yes |

### 3.7 Portfolio (`/api/portfolio`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/portfolio/positions` | Get manual positions | Yes |
| POST | `/api/portfolio/positions` | Add manual position | Yes |
| PUT | `/api/portfolio/positions/<id>` | Update position (e.g., stop loss) | Yes |
| DELETE | `/api/portfolio/positions/<id>` | Delete position | Yes |
| GET | `/api/portfolio/summary` | Portfolio summary with PnL | Yes |
| GET | `/api/portfolio/monitors` | AI monitoring tasks | Yes |
| POST | `/api/portfolio/monitors` | Create monitor task | Yes |
| PUT | `/api/portfolio/monitors/<id>` | Update monitor | Yes |
| DELETE | `/api/portfolio/monitors/<id>` | Delete monitor | Yes |
| POST | `/api/portfolio/monitors/<id>/run` | Run monitor now | Yes |
| GET | `/api/portfolio/alerts` | Get price alerts | Yes |
| POST | `/api/portfolio/alerts` | Create price alert | Yes |
| PUT | `/api/portfolio/alerts/<id>` | Update alert | Yes |
| DELETE | `/api/portfolio/alerts/<id>` | Delete alert | Yes |
| GET | `/api/portfolio/groups` | Get position groups | Yes |
| POST | `/api/portfolio/groups/rename` | Rename group | Yes |

### 3.8 Global Market (`/api/global-market`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/global-market/overview` | Global indices, forex, crypto overview | Yes |
| GET | `/api/global-market/heatmap` | Market heatmap (stocks, crypto, forex) | Yes |
| GET | `/api/global-market/news?lang=` | Financial news | Yes |
| GET | `/api/global-market/calendar` | Economic calendar | Yes |
| GET | `/api/global-market/sentiment` | Fear & Greed, VIX | Yes |
| GET | `/api/global-market/opportunities` | Trading opportunities scanner | Yes |
| POST | `/api/global-market/refresh` | Force refresh cached data | Yes |

### 3.9 Community / Indicator Marketplace (`/api/community`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/community/indicators?page=&keyword=&pricing_type=&sort_by=` | Browse indicators | Yes |
| GET | `/api/community/indicators/<id>` | Indicator detail | Yes |
| POST | `/api/community/indicators/<id>/purchase` | Purchase paid indicator | Yes |
| GET | `/api/community/my-purchases` | User's purchased indicators | Yes |
| GET | `/api/community/indicators/<id>/comments` | Comments on indicator | Yes |
| POST | `/api/community/indicators/<id>/comments` | Add comment | Yes |
| PUT | `/api/community/indicators/<id>/comments/<cid>` | Edit comment | Yes |
| GET | `/api/community/indicators/<id>/my-comment` | User's comment | Yes |
| GET | `/api/community/indicators/<id>/performance` | Indicator performance stats | Yes |
| GET | `/api/community/admin/pending-indicators` | Pending review (admin) | Yes |
| GET | `/api/community/admin/review-stats` | Review stats (admin) | Yes |
| POST | `/api/community/admin/indicators/<id>/review` | Review indicator (admin) | Yes |
| POST | `/api/community/admin/indicators/<id>/unpublish` | Unpublish (admin) | Yes |
| DELETE | `/api/community/admin/indicators/<id>` | Delete (admin) | Yes |

### 3.10 Fast Analysis (`/api/fast-analysis`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/api/fast-analysis/analyze` | AI analysis of symbol | Yes |

**Request Example:**
```json
POST /api/fast-analysis/analyze
{
  "market": "Crypto",
  "symbol": "BTC/USDT",
  "language": "zh-CN",
  "model": "openai/gpt-4o",
  "timeframe": "1D"
}
```

### 3.11 Billing (`/api/billing`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/billing/plans` | Get membership plans + user billing info | Yes |
| POST | `/api/billing/purchase` | Purchase membership (mock) | Yes |
| POST | `/api/billing/usdt/create` | Create USDT payment order | Yes |
| GET | `/api/billing/usdt/order/<id>` | Check USDT order status | Yes |

### 3.12 Quick Trade (`/api/quick-trade`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/api/quick-trade/place-order` | Place market/limit order | Yes |
| GET | `/api/quick-trade/balance` | Get exchange balance | Yes |
| GET | `/api/quick-trade/position?symbol=` | Get position for symbol | Yes |
| POST | `/api/quick-trade/close-position` | Close position | Yes |
| GET | `/api/quick-trade/history?page=&limit=` | Trade history | Yes |

### 3.13 Credentials Vault (`/api/credentials`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/credentials/list` | List stored exchange credentials | Yes |
| POST | `/api/credentials/save` | Save exchange credentials | Yes |
| PUT | `/api/credentials/<id>` | Update credentials | Yes |
| DELETE | `/api/credentials/<id>` | Delete credentials | Yes |
| POST | `/api/credentials/test` | Test credentials | Yes |

### 3.14 Settings (`/api/settings`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/settings/schema` | Config schema (grouped settings) | Yes |
| GET | `/api/settings/values` | Current setting values | Yes |
| POST | `/api/settings/save` | Save settings | Yes (admin) |
| GET | `/api/settings/openrouter-balance` | Check OpenRouter credit balance | Yes |
| POST | `/api/settings/test-connection` | Test API connection | Yes (admin) |

### 3.15 User Management (`/api/users`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/users/list?page=&page_size=&search=` | List users (admin) | Yes (admin) |
| GET | `/api/users/detail?id=` | User detail (admin) | Yes (admin) |
| POST | `/api/users/create` | Create user (admin) | Yes (admin) |
| PUT | `/api/users/update` | Update user (admin) | Yes (admin) |
| DELETE | `/api/users/delete?id=` | Delete user (admin) | Yes (admin) |
| POST | `/api/users/reset-password` | Reset user password (admin) | Yes (admin) |
| GET | `/api/users/roles` | List roles | Yes (admin) |
| POST | `/api/users/set-credits` | Set user credits (admin) | Yes (admin) |
| POST | `/api/users/set-vip` | Set VIP status (admin) | Yes (admin) |
| GET | `/api/users/credits-log` | Credits log (admin) | Yes (admin) |
| GET | `/api/users/profile` | Current user profile | Yes |
| PUT | `/api/users/profile/update` | Update own profile | Yes |
| GET | `/api/users/my-credits-log` | Own credits log | Yes |
| GET | `/api/users/my-referrals` | Own referral info | Yes |
| GET | `/api/users/notification-settings` | Notification preferences | Yes |
| PUT | `/api/users/notification-settings` | Update notification prefs | Yes |
| POST | `/api/users/change-password` | Change own password | Yes |
| GET | `/api/users/system-strategies` | System strategies | Yes |
| GET | `/api/users/admin-orders` | All orders (admin) | Yes (admin) |
| GET | `/api/users/admin-ai-stats` | AI usage stats (admin) | Yes (admin) |

### 3.16 IBKR (`/api/ibkr`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/ibkr/status` | Connection status | Yes |
| POST | `/api/ibkr/connect` | Connect to TWS/IB Gateway | Yes |
| POST | `/api/ibkr/disconnect` | Disconnect | Yes |
| GET | `/api/ibkr/account` | Account info | Yes |
| GET | `/api/ibkr/positions` | IBKR positions | Yes |
| GET | `/api/ibkr/orders` | Open orders | Yes |
| POST | `/api/ibkr/order` | Place order | Yes |
| DELETE | `/api/ibkr/order/<id>` | Cancel order | Yes |
| GET | `/api/ibkr/quote?symbol=` | Get quote | Yes |

### 3.17 MT5 (`/api/mt5`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/api/mt5/status` | MT5 connection status | Yes |
| POST | `/api/mt5/connect` | Connect to MT5 | Yes |
| POST | `/api/mt5/disconnect` | Disconnect | Yes |
| GET | `/api/mt5/account` | MT5 account info | Yes |
| GET | `/api/mt5/positions` | MT5 positions | Yes |
| POST | `/api/mt5/order` | Place order | Yes |
| GET | `/api/mt5/history` | Order history | Yes |

### 3.18 Polymarket (`/api/polymarket`)

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/api/polymarket/analyze` | Analyze Polymarket event | Yes |
| GET | `/api/polymarket/history` | Analysis history | Yes |

### 3.19 AI Chat (`/api/ai`) — Stubs

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| POST | `/api/ai/chat/message` | Send chat message (stub) | Yes |
| GET | `/api/ai/chat/history` | Get chat history (stub) | Yes |
| POST | `/api/ai/chat/history/save` | Save chat (stub) | Yes |

---

## 4. Frontend Reconstruction Strategy

### 4.1 UI Feature Mapping (from Backend Routes)

| UI Page / Feature | API Endpoints Used |
|-------------------|--------------------|
| **Login / Register** | `POST /api/auth/login`, `/login-code`, `/send-code`, `/register`, OAuth flows |
| **Dashboard** | `/api/dashboard/summary`, `/api/dashboard/pendingOrders` |
| **Market Overview** | `/api/market/types`, `/api/market/config`, `/api/market/price`, `/api/global-market/overview` |
| **Watchlist** | `/api/market/watchlist/get`, `/add`, `/remove`, `/prices` |
| **Symbol Search** | `/api/market/symbols/search`, `/symbols/hot` |
| **K-Line Chart** | `/api/indicator/kline` |
| **Indicator Analysis** | `/api/indicator/callIndicator`, `/getIndicators`, `/saveIndicator`, `/verifyCode`, `/aiGenerate` |
| **Backtest** | `/api/indicator/backtest`, `/history`, `/get`, `/aiAnalyze`, `/precision-info` |
| **Strategy List** | `/api/strategies`, `/strategies/detail`, CRUD ops |
| **Strategy Editor** | `/api/strategies/create`, `/preview-compile`, `/test-connection` |
| **Strategy Run** | `/api/strategies/start`, `/stop`, `/trades`, `/positions`, `/equityCurve` |
| **Strategy Notifications** | `/api/strategies/notifications`, `/unread-count`, `/read`, `/read-all`, `/clear` |
| **Portfolio** | `/api/portfolio/positions`, `/summary`, `/groups`, `/monitors`, `/alerts` |
| **Quick Trade** | `/api/quick-trade/place-order`, `/balance`, `/position`, `/close-position`, `/history` |
| **Credentials** | `/api/credentials/list`, `/save`, `/test` |
| **Global Market** | `/api/global-market/overview`, `/heatmap`, `/news`, `/calendar`, `/sentiment`, `/opportunities` |
| **Community / Market** | `/api/community/indicators`, `/purchase`, `/comments` |
| **Fast Analysis** | `/api/fast-analysis/analyze` |
| **Billing** | `/api/billing/plans`, `/purchase` |
| **IBKR Trading** | `/api/ibkr/*` |
| **MT5 Trading** | `/api/mt5/*` |
| **Polymarket** | `/api/polymarket/analyze` |
| **Settings** | `/api/settings/schema`, `/values`, `/save`, `/test-connection` |
| **User Profile** | `/api/users/profile`, `/profile/update`, `/notification-settings`, `/change-password` |
| **Admin Panel** | `/api/users/list`, `/create`, `/update`, `/delete`, `/set-credits`, `/set-vip`, credits logs |
| **Admin Orders** | `/api/users/admin-orders`, `/admin-ai-stats` |

### 4.2 Recommended Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|------------|
| Framework | **Vue 3** (Composition API) + **TypeScript** | Aligns with original; better DX with TS |
| Build tool | **Vite** | Fast HMR, standard for Vue 3 |
| UI Components | **Naive UI** or **Element Plus** | Rich component library, good TS support |
| Charts | **Apache ECharts** (via `vue-echarts`) | K-line charts, heatmaps, equity curves |
| HTTP Client | **Axios** + interceptors for JWT | Standard, handles auth headers cleanly |
| State | **Pinia** | Official Vue 3 state management |
| Router | **Vue Router 4** (hash mode `/#/` paths) | Matches original routing strategy |
| Forms | **VeeValidate** + **Zod** | Robust form validation |
| i18n | **Vue I18n** | Multi-language support |
| Icons | **Iconify** (`@iconify/vue`) | Massive icon library |

### 4.3 Recommended Project Structure

```
src/
├── api/                    # API client layer
│   ├── client.ts           # Axios instance with interceptors
│   ├── auth.ts             # Auth API calls
│   ├── market.ts           # Market API calls
│   ├── indicator.ts        # Indicator/Backtest API calls
│   ├── strategy.ts         # Strategy API calls
│   ├── portfolio.ts        # Portfolio API calls
│   └── ...
├── stores/                 # Pinia stores
│   ├── auth.ts             # Token, userinfo, login/logout
│   ├── market.ts           # Watchlist, prices, search
│   ├── strategy.ts         # Strategy state
│   └── ...
├── views/                  # Page components
│   ├── Login.vue
│   ├── Register.vue
│   ├── Dashboard.vue
│   ├── Market.vue
│   ├── Chart.vue           # K-line chart page
│   ├── IndicatorList.vue
│   ├── IndicatorEditor.vue
│   ├── Backtest.vue
│   ├── StrategyList.vue
│   ├── StrategyEditor.vue
│   ├── Portfolio.vue
│   ├── QuickTrade.vue
│   ├── GlobalMarket.vue
│   ├── Community.vue
│   ├── FastAnalysis.vue
│   ├── Billing.vue
│   ├── Settings.vue
│   ├── Profile.vue
│   └── admin/
│       ├── UserManagement.vue
│       └── SystemSettings.vue
├── components/
│   ├── layout/             # Header, Sidebar, Footer
│   ├── chart/              # KLineChart, EquityCurve
│   ├── market/             # Watchlist, SymbolSearch, PriceTicker
│   └── common/             # Buttons, Modals, Forms
├── router/
│   └── index.ts            # Route definitions (hash mode)
├── i18n/                   # Locale files
├── types/                  # TypeScript interfaces (mirroring API response shapes)
│   └── api.ts              # ApiResponse<T>, UserInfo, Strategy, etc.
├── utils/
│   ├── format.ts           # Number/date formatting
│   └── storage.ts          # localStorage helpers
├── App.vue
└── main.ts
```

### 4.4 API Client Pattern

```typescript
// api/client.ts
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 30000,
})

// Request interceptor: inject JWT
client.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor: handle 401 → redirect to login
client.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.hash = '#/user/login'
    }
    return Promise.reject(err)
  }
)

// Typed API wrapper
export function apiGet<T>(url: string, params?: object) {
  return client.get<{ code: number; msg: string; data: T }>(url, { params })
}

export function apiPost<T>(url: string, data?: object) {
  return client.post<{ code: number; msg: string; data: T }>(url, data)
}

// Usage:
// const { data } = await apiGet<UserInfo>('/auth/info')
// if (data.code === 1) { ... }
```

---

## 5. Systematic UI Exercise Checklist

Use this checklist to ensure every feature is exercised during traffic capture:

### Auth
- [ ] Login with username/password
- [ ] Login with email code
- [ ] Register new account
- [ ] Reset password
- [ ] Google OAuth login flow
- [ ] GitHub OAuth login flow
- [ ] View profile page
- [ ] Change password
- [ ] Update profile (nickname, avatar)
- [ ] Logout

### Dashboard
- [ ] Load dashboard summary
- [ ] View pending orders
- [ ] Cancel pending order

### Market
- [ ] Browse market types
- [ ] Search symbols (crypto, stock, forex)
- [ ] View hot/trending symbols
- [ ] Add symbol to watchlist
- [ ] Remove from watchlist
- [ ] View watchlist prices
- [ ] Get price for specific symbol
- [ ] Resolve stock symbol name

### Charts & Indicators
- [ ] Load K-line data (all timeframes: 1m, 5m, 15m, 30m, 1H, 4H, 1D, 1W)
- [ ] Load K-line for different markets (Crypto, USStock, Forex, Futures)
- [ ] Load K-line with `before_time` pagination (scroll load more)
- [ ] List saved indicators
- [ ] Save new indicator (Python code)
- [ ] Delete indicator
- [ ] Get indicator params
- [ ] Verify indicator code (syntax check)
- [ ] AI generate indicator
- [ ] Call/execute indicator on chart
- [ ] Run backtest
- [ ] View backtest history
- [ ] View backtest result detail
- [ ] AI analyze backtest
- [ ] View backtest precision info

### Strategies
- [ ] List strategies
- [ ] View strategy detail
- [ ] Create strategy
- [ ] Batch create strategies
- [ ] Update strategy
- [ ] Delete strategy
- [ ] Start strategy
- [ ] Stop strategy
- [ ] Batch start
- [ ] Batch stop
- [ ] Batch delete
- [ ] View strategy trades
- [ ] View strategy positions
- [ ] View equity curve
- [ ] Test exchange connection
- [ ] Get symbols for exchange
- [ ] Preview compile strategy
- [ ] View notifications
- [ ] Mark notification read
- [ ] Mark all read
- [ ] Clear notifications

### Portfolio
- [ ] View positions
- [ ] Add manual position
- [ ] Update position (stop loss, take profit)
- [ ] Delete position
- [ ] View portfolio summary
- [ ] View position groups
- [ ] Rename group
- [ ] Create price alert
- [ ] View alerts
- [ ] Update alert
- [ ] Delete alert
- [ ] Create monitor task
- [ ] View monitors
- [ ] Update monitor
- [ ] Delete monitor
- [ ] Run monitor manually

### Quick Trade
- [ ] View balance
- [ ] View position for symbol
- [ ] Place market order
- [ ] Place limit order
- [ ] Close position
- [ ] View trade history

### Global Market
- [ ] Load global overview
- [ ] Load market heatmap (crypto, stock, forex tabs)
- [ ] Load financial news (EN and CN)
- [ ] Load economic calendar
- [ ] Load fear & greed / VIX sentiment
- [ ] Load trading opportunities
- [ ] Force refresh data

### Community
- [ ] Browse indicators (all, free, paid filters)
- [ ] Search indicators by keyword
- [ ] Sort indicators(newest, hot, price, rating)
- [ ] View indicator detail
- [ ] Purchase paid indicator
- [ ] View my purchases
- [ ] Add comment to indicator
- [ ] Edit own comment
- [ ] View own comment
- [ ] View indicator performance stats
- [ ] Admin: review pending indicator
- [ ] Admin: approve/reject indicator
- [ ] Admin: unpublish indicator
- [ ] Admin: delete indicator

### Fast Analysis
- [ ] Request AI analysis for symbol
- [ ] Vary language parameter (zh-CN, en-US)
- [ ] Vary model parameter

### Billing
- [ ] View membership plans
- [ ] View current billing info (credits, plan)
- [ ] Purchase plan (mock)
- [ ] Create USDT payment order
- [ ] Check USDT order status

### Credentials
- [ ] List stored credentials
- [ ] Save new exchange credentials
- [ ] Update credentials
- [ ] Delete credentials
- [ ] Test credentials

### Settings
- [ ] View settings schema (grouped sections)
- [ ] View current values
- [ ] Save settings (admin)
- [ ] Check OpenRouter balance
- [ ] Test connection (admin)

### IBKR
- [ ] Connect to TWS/Gateway
- [ ] Disconnect
- [ ] View connection status
- [ ] View account info
- [ ] View positions
- [ ] View open orders
- [ ] Place order
- [ ] Cancel order
- [ ] Get quote

### MT5
- [ ] Connect to MT5
- [ ] Disconnect
- [ ] View account info
- [ ] View positions
- [ ] Place order
- [ ] View order history

### Polymarket
- [ ] Analyze Polymarket event (by URL)
- [ ] View analysis history

---

## 6. Implementation Timeline

### Phase 1: Traffic Capture (Week 1)
| Day | Task |
|-----|------|
| 1 | Set up mitmproxy with HTTPS cert; verify traffic flows |
| 2 | Login → explore all pages manually in DevTools |
| 3 | Export HAR; begin mapping API calls to UI features |
| 4 | Playwright automation: auto-login, navigate all routes |
| 5 | Review captured traffic; identify any missing endpoints |
| 6-7 | Fill gaps; capture WebSocket if any; final HAR export |

**Deliverable:** `capture.har` (or `.mitm` flow file) + `ENDPOINTS.md`

### Phase 2: API Specification (Week 1-2)
| Day | Task |
|-----|------|
| 1-2 | Parse HAR → OpenAPI 3.0 spec (use `har-to-openapi` or Postman) |
| 3-4 | Fill in request/response schemas from captured data |
| 5-6 | Cross-reference with backend route files for validation |
| 7 | Generate TypeScript interfaces from spec |

**Deliverable:** `openapi.yaml` + TypeScript types in `src/types/api.ts`

### Phase 3: Project Scaffolding (Week 2)
| Day | Task |
|-----|------|
| 1 | Initialize Vue 3 + Vite + TypeScript project |
| 2 | Configure router (hash mode), Pinia stores |
| 3 | Set up Axios client with auth interceptors |
| 4 | Configure Naive UI / Element Plus theme |
| 5 | Set up i18n with locale files |
| 6 | Build layout components (Header, Sidebar, Footer) |

**Deliverable:** Scaffolding project on GitHub; CI runs

### Phase 4: Core Pages (Week 3-4)
| Week | Pages |
|------|-------|
| 3 | Auth (Login, Register, Password Reset, OAuth), Dashboard |
| 3-4 | Market (watchlist, symbol search, prices), K-line chart page |
| 4 | Indicator list, editor, execution; Backtest page |

**Deliverable:** Working frontend with real API calls (pointing at backend)

### Phase 5: Advanced Features (Week 5-6)
| Week | Features |
|------|----------|
| 5 | Strategy CRUD, editor, start/stop, notifications |
| 5 | Portfolio, alerts, monitors |
| 5-6 | Quick Trade, Credentials vault |
| 6 | Global Market, Community, Fast Analysis |

### Phase 6: Admin & Polish (Week 7)
| Week | Features |
|------|----------|
| 7 | Admin panel (users, orders, AI stats) |
| 7 | Settings page, Profile page |
| 7 | IBKR / MT5 integration pages |
| 7 | Polymarket page |

### Phase 7: Testing & Deployment (Week 8)
| Day | Task |
|-----|------|
| 1-2 | E2E tests with Playwright (full UI exercise) |
| 3-4 | Compare against original frontend feature parity |
| 5 | Docker build; deploy to staging |
| 6-7 | Bug fixes; production deployment |

**Total Estimated Timeline: 8 weeks**

---

## 7. Tools and Automation Scripts

### 7.1 mitmproxy Quick-Start Script

```python
# capture_script.py — mitmdump script for automated capture
# Usage: mitmdump -ns capture_script.py -w capture.mitm
from mitmproxy import http, ctx
import json

class TrafficCapture:
    def __init__(self):
        self.requests = []
    
    def request(self, flow: http.HTTPFlow):
        # Skip mitmproxy's own traffic
        if flow.request.host in ("mitmproxy.org",):
            return
        
        entry = {
            "method": flow.request.method,
            "url": flow.request.pretty_url,
            "headers": dict(flow.request.headers),
            "method": flow.request.method,
        }
        
        if flow.request.content:
            try:
                entry["body"] = json.loads(flow.request.content.decode())
            except Exception:
                entry["body_raw"] = flow.request.content.decode(errors="replace")
        
        self.requests.append(entry)
    
    def response(self, flow: http.HTTPFlow):
        if flow.response and flow.response.content:
            try:
                flow.metadata["response_body"] = json.loads(
                    flow.response.content.decode()
                )
            except Exception:
                pass

addons = [TrafficCapture()]
```

### 7.2 Playwright Auto-Explorer Script

```python
# explore_ui.py — Automates UI exploration with Playwright
# Usage: python explore_ui.py
import asyncio
import json
from playwright.async_api import async_playwright

BACKEND_URL = "http://127.0.0.1:5000"
LOGIN_URL = f"{BACKEND_URL}/api/auth/login"
USERNAME = "admin"
PASSWORD = "123456"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            base_url=BACKEND_URL,
            viewport={"width": 1920, "height": 1080},
        )
        
        # 1. Login
        page = await context.new_page()
        resp = await page.request.post(LOGIN_URL, json={
            "username": USERNAME,
            "password": PASSWORD,
        })
        data = await resp.json()
        token = data["data"]["token"]
        
        # Set auth header for all subsequent requests
        await context.set_extra_http_headers({"Authorization": f"Bearer {token}"})
        
        # 2. Navigate all routes (hash mode)
        routes = [
            "/#/",
            "/#/user/login",
            "/#/market",
            "/#/indicator-analysis",
            "/#/backtest",
            "/#/strategy",
            "/#/portfolio",
            "/#/quick-trade",
            "/#/global-market",
            "/#/community",
            "/#/fast-analysis",
            "/#/billing",
            "/#/credentials",
            "/#/settings",
            "/#/profile",
        ]
        
        for route in routes:
            print(f"Navigating: {route}")
            await page.goto(f"{BACKEND_URL}{route}")
            await page.wait_for_load_state("networkidle", timeout=15000)
            await asyncio.sleep(2)  # Let XHR requests settle
        
        await browser.close()
        print("Done. Check DevTools HAR or mitmproxy capture.mitm.")

asyncio.run(main())
```

### 7.3 HAR → OpenAPI Converter

```bash
# Convert captured HAR to OpenAPI spec
npm install -g @apidevtools/har-to-openapi

# Or use the CLI:
npx har-to-openapi capture.har -o openapi.yaml

# Post-process: review generated schema, add TypeScript types
npx openapi2ts -i openapi.yaml -o src/types/api.ts
```

### 7.4 DevTools HAR Export to JSON

```javascript
// In DevTools Console on the page:
copy(JSON.stringify(await (__harviewer__ || { do not use this })))

// Better: use Fetch Export plugin or:
// 1. Network tab → right-click → "Save all as HAR"
// 2. Convert with: har-to-openapi
```

### 7.5 Quick Scripts Needed

| Script | Purpose |
|--------|---------|
| `scripts/har2openapi.ts` | Convert HAR → OpenAPI spec |
| `scripts/gen_types.py` | Generate TypeScript types from OpenAPI |
| `scripts/explore_ui.py` | Playwright auto-explorer |
| `scripts/extract_endpoints.py` | Extract unique endpoints from HAR |
| `scripts/replay_auth.py` | Replay captured requests with fresh token |
| `scripts/compare_apis.py` | Compare backend route list vs. captured traffic |

### 7.6 Install All Dependencies

```bash
# mitmproxy
pip install mitmproxy

# Playwright
pip install playwright
playwright install chromium

# HAR tools
npm install -g har-to-openapi @apidevtools/swagger-cli
npm install -g openapi-typescript

# Vue project (once ready)
npm create vite@latest quantdinger-ui -- --template vue-ts
npm install vue-router@4 pinia naive-ui echarts vue-echarts \
  axios vee-validate @vee-validate/zod zod vue-i18n \
  @iconify/vue
```

---

## 8. Key Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| **Minified JS hides API call patterns** | Capture at network level, not source code |
| **Auth token expires mid-session** | Refresh token before capture sessions; keep backend token TTL long during capture |
| **WebSocket frames lost** | Use mitmproxy (captures WebSocket); DevTools WS tab has limited export |
| **Rate limiting blocks exploration** | Pause between rapid requests; increase backend rate limit during capture |
| **Demo mode blocks some endpoints** | Ensure `IS_DEMO_MODE=false` during capture |
| **Image/font assets pollute capture** | Filter by `Content-Type: application/json` or `X-Requested-With: XMLHttpRequest` |
| **OAuth redirects lose token** | Capture OAuth callback URL from browser address bar after redirect |
| **Strategy code too large for capture** | Capture strategy list/detail separately; editor code from `preview-compile` |
