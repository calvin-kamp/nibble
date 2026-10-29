import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'

import router from './router'
import { useAuthStore } from '@features/auth/auth.store'
import { expireSession } from '@features/auth/auth.utils'
import { setSessionExpiredHandler } from '@shared/api/client'

import './main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

const auth = useAuthStore()

// Only users who were signed in get the notice. Guests already end up here on app start.
setSessionExpiredHandler(() => {
	if (auth.isLoggedIn) void expireSession(router)
})

// Wait until it is known who is signed in, otherwise the guest view flashes briefly
void auth.init().finally(() => app.mount('#app'))
