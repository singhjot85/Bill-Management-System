import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router, { setupRoutes } from './router'
import vuetify from './plugins/vuetify'
import { useAuthStore } from './stores/authStore'
import { useTenantStore } from './stores/tenantStore'
import { useBrandingStore } from './stores/brandingStore'

import './assets/css/main.css'

async function initApp() {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  // 1. Resolve Tenant first
  const tenantStore = useTenantStore(pinia)
  tenantStore.resolveTenant()

  // 2. Setup dynamic routes based on tenant
  setupRoutes()
  app.use(router)

  app.use(vuetify)

  // 3. Initialize auth and branding in parallel
  const authStore = useAuthStore(pinia)
  const brandingStore = useBrandingStore(pinia)

  await Promise.all([
    authStore.refreshToken(),
    brandingStore.fetchBranding()
  ])

  app.mount('#app')
}

initApp()
