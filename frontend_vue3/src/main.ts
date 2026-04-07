import { createApp } from 'vue'
import { createPinia } from 'pinia'
import {
  ConfigProvider,
  theme,
  type GlobalThemeAlgorithm,
} from 'ant-design-vue'
import router from './router'
import { i18n } from './i18n'
import App from './App.vue'
import './styles/global.less'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)

// Mount the app
app.mount('#app')

// Ant Design Vue ConfigProvider with dark/light theme
// Will be used in App.vue
export { app, pinia }
