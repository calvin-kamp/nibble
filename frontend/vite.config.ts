import type { NodeTransform } from '@vue/compiler-core'

import { fileURLToPath, URL } from 'node:url'

import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'
import { ElementTypes, NodeTypes } from '@vue/compiler-core'
import { defineConfig } from 'vite'
import vueDevTools from 'vite-plugin-vue-devtools'

// Templates put element content on its own line (see eslint.config.ts). Vue would keep the line
// breaks as a space inside the element, e.g. "gelöscht ." before a period, so text is trimmed at
// the start and end of every element. <template> is a fragment and stays as written.
const trimElementText: NodeTransform = (node) => {
	if (node.type !== NodeTypes.ELEMENT || node.tagType === ElementTypes.TEMPLATE) return
	if (node.tag === 'pre' || node.tag === 'textarea') return

	const first = node.children[0]
	const last = node.children.at(-1)

	if (first?.type === NodeTypes.TEXT) first.content = first.content.trimStart()
	if (last?.type === NodeTypes.TEXT) last.content = last.content.trimEnd()

	node.children = node.children.filter((child) => child.type !== NodeTypes.TEXT || child.content)
}

// https://vite.dev/config/
export default defineConfig({
	plugins: [
		vue({ template: { compilerOptions: { nodeTransforms: [trimElementText] } } }),
		vueDevTools(),
		tailwindcss(),
	],
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
