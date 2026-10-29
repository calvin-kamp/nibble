import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
	plugins: [vue(), vueDevTools(), tailwindcss()],
	resolve: {
		alias: {
			'@assets': fileURLToPath(new URL('./src/assets', import.meta.url)),
			'@features': fileURLToPath(new URL('./src/features', import.meta.url)),
			'@layouts': fileURLToPath(new URL('./src/layouts', import.meta.url)),
			'@shared': fileURLToPath(new URL('./src/shared', import.meta.url)),
			'@styles': fileURLToPath(new URL('./src/styles', import.meta.url)),
		},
	},
})
