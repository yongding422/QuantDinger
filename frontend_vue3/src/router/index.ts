/**
 * Vue Router — hash mode, lazy-loaded pages, auth guard.
 */
import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

// Lazy-loaded page components
const Login = () => import('@/views/auth/Login.vue')
const Register = () => import('@/views/auth/Register.vue')
const Dashboard = () => import('@/views/dashboard/Dashboard.vue')
const Portfolio = () => import('@/views/portfolio/Portfolio.vue')
const StrategyList = () => import('@/views/strategies/StrategyList.vue')
const StrategyCreate = () => import('@/views/strategies/StrategyCreate.vue')
const StrategyDetail = () => import('@/views/strategies/StrategyDetail.vue')
const QuickTrade = () => import('@/views/quick-trade/QuickTrade.vue')
const GlobalMarket = () => import('@/views/market/GlobalMarket.vue')
const AIAnalysis = () => import('@/views/ai-analysis/AIAnalysis.vue')
const Indicators = () => import('@/views/indicators/Indicators.vue')
const Backtest = () => import('@/views/backtest/Backtest.vue')
const Polymarket = () => import('@/views/polymarket/Polymarket.vue')
const Settings = () => import('@/views/settings/Profile.vue')
const Billing = () => import('@/views/billing/Billing.vue')
const Community = () => import('@/views/community/Community.vue')
const UserManagement = () => import('@/views/user/UserManagement.vue')
const IBKR = () => import('@/views/trading/IBKR.vue')
const MT5 = () => import('@/views/trading/MT5.vue')

const routes: RouteRecordRaw[] = [
  // Auth — public
  { path: '/user/login', name: 'login', component: Login },
  { path: '/user/register', name: 'register', component: Register },

  // Default redirect
  { path: '/', redirect: '/dashboard' },

  // Authenticated pages
  {
    path: '/dashboard',
    name: 'dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/portfolio',
    name: 'portfolio',
    component: Portfolio,
    meta: { requiresAuth: true },
  },
  {
    path: '/strategies',
    name: 'strategies',
    component: StrategyList,
    meta: { requiresAuth: true },
  },
  {
    path: '/strategies/new',
    name: 'strategy-create',
    component: StrategyCreate,
    meta: { requiresAuth: true },
  },
  {
    path: '/strategies/:id',
    name: 'strategy-detail',
    component: StrategyDetail,
    meta: { requiresAuth: true },
  },
  {
    path: '/quick-trade',
    name: 'quick-trade',
    component: QuickTrade,
    meta: { requiresAuth: true },
  },
  {
    path: '/market',
    name: 'global-market',
    component: GlobalMarket,
    meta: { requiresAuth: true },
  },
  {
    path: '/ai-analysis',
    name: 'ai-analysis',
    component: AIAnalysis,
    meta: { requiresAuth: true },
  },
  {
    path: '/indicators',
    name: 'indicators',
    component: Indicators,
    meta: { requiresAuth: true },
  },
  {
    path: '/backtest',
    name: 'backtest',
    component: Backtest,
    meta: { requiresAuth: true },
  },
  {
    path: '/polymarket',
    name: 'polymarket',
    component: Polymarket,
    meta: { requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'settings',
    component: Settings,
    meta: { requiresAuth: true },
  },
  {
    path: '/billing',
    name: 'billing',
    component: Billing,
    meta: { requiresAuth: true },
  },
  {
    path: '/community',
    name: 'community',
    component: Community,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/users',
    name: 'user-management',
    component: UserManagement,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/trading/ibkr',
    name: 'ibkr',
    component: IBKR,
    meta: { requiresAuth: true },
  },
  {
    path: '/trading/mt5',
    name: 'mt5',
    component: MT5,
    meta: { requiresAuth: true },
  },

  // 404
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

// Navigation guard
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if ((to.name === 'login' || to.name === 'register') && token) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
