import { createPinia } from 'pinia'
import { createApp } from 'vue'
import '@assets/styles/main.css'
import { useAuthStore } from '@stores/auth.store'
import App from './App.vue'
import router from './router'

async function bootstrap(): Promise<void> {
  const app = createApp(App)
  const pinia = createPinia()

  app.use(pinia)

  await useAuthStore(pinia).restoreSession()

  app.use(router)
  app.mount('#app')
}

bootstrap()
