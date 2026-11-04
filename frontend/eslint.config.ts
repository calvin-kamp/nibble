import type { Rule } from 'eslint'
import type { AST } from 'vue-eslint-parser'

import stylistic from '@stylistic/eslint-plugin'
import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import skipFormatting from 'eslint-config-prettier/flat'
import betterTailwindcss from 'eslint-plugin-better-tailwindcss'
import pluginOxlint from 'eslint-plugin-oxlint'
import pluginPerfectionist from 'eslint-plugin-perfectionist'
import pluginVue from 'eslint-plugin-vue'
import pluginVueA11y from 'eslint-plugin-vuejs-accessibility'
import { globalIgnores } from 'eslint/config'

// Like vue/padding-line-between-tags, but text and {{ }} count as siblings too. Siblings on the
// same line stay together, e.g. a period right after a closing tag.
const paddingLineBetweenSiblings: Rule.RuleModule = {
	meta: { type: 'layout', fixable: 'whitespace', schema: [] },
	create(context) {
		const source = context.sourceCode.text
		const parserServices = context.sourceCode.parserServices as {
			defineTemplateBodyVisitor?: (
				visitor: Record<string, (node: AST.VElement) => void>,
			) => Rule.RuleListener
		}

		const bounds = (node: AST.VElement['children'][number]): [number, number] | null => {
			if (node.type !== 'VText') return node.range
			const text = source.slice(node.range[0], node.range[1])
			if (!text.trim()) return null
			const start = node.range[0] + text.length - text.trimStart().length
			const end = node.range[1] - (text.length - text.trimEnd().length)

			return [start, end]
		}

		return (
			parserServices.defineTemplateBodyVisitor?.({
				VElement(element) {
					if (element.name === 'pre' || element.name === 'textarea') return

					const siblings = element.children.map(bounds).filter((range) => range !== null)

					for (let i = 1; i < siblings.length; i++) {
						const gapStart = siblings[i - 1]![1]
						const gapEnd = siblings[i]![0]
						const gap = source.slice(gapStart, gapEnd)
						const newline = gap.indexOf('\n')

						if (gap.trim()) continue

						// A space before punctuation would be rendered, so it sticks to the tag
						if (gap && /^[.,:;!?)]/.test(source.slice(gapEnd, gapEnd + 1))) {
							context.report({
								loc: context.sourceCode.getLocFromIndex(gapEnd),
								message: 'Punctuation belongs directly after the previous sibling.',
								fix: (fixer) => fixer.removeRange([gapStart, gapEnd]),
							})
							continue
						}

						if (newline === -1 || gap.indexOf('\n', newline + 1) !== -1) continue

						context.report({
							loc: context.sourceCode.getLocFromIndex(gapEnd),
							message: 'Expected a blank line before this sibling.',
							fix: (fixer) =>
								fixer.replaceTextRange(
									[gapStart, gapEnd],
									`\n${gap.slice(newline)}`,
								),
						})
					}
				},
			}) ?? {}
		)
	},
}

export default defineConfigWithVueTs(
	{
		name: 'app/files-to-lint',
		files: ['**/*.{vue,ts,mts,tsx}'],
	},

	globalIgnores(['**/dist/**', '**/dist-ssr/**', '**/coverage/**']),

	...pluginVue.configs['flat/recommended'],
	vueTsConfigs.recommended,

	...pluginVueA11y.configs['flat/recommended'],

	{
		name: 'app/vue-rules',
		files: ['**/*.vue'],
		rules: {
			// A label either wraps its control or points at it via for, both are valid HTML.
			// The default demands both at once.
			'vuejs-accessibility/label-has-for': [
				'error',
				{ required: { some: ['nesting', 'id'] } },
			],

			'vue/component-name-in-template-casing': [
				'error',
				'PascalCase',
				{ registeredComponentsOnly: false },
			],

			'vue/no-undef-components': 'error',

			'vue/no-unused-properties': [
				'error',
				{ groups: ['props', 'setup'], deepData: false, ignorePublicMembers: true },
			],

			'vue/define-macros-order': [
				'error',
				{
					order: [
						'defineOptions',
						'defineProps',
						'defineEmits',
						'defineSlots',
						'defineModel',
					],
				},
			],

			'vue/no-ref-object-reactivity-loss': 'error',

			'vue/require-typed-ref': 'error',

			'vue/no-required-prop-with-default': 'error',

			'vue/prefer-true-attribute-shorthand': ['error', 'always'],

			'vue/prefer-prop-type-boolean-first': 'error',

			// No component has a style block: styles live in src/styles and Tailwind classes
			'vue/block-lang': ['error', { script: { lang: 'ts' } }],

			'vue/block-order': ['error', { order: ['script', 'template'] }],

			'vue/no-empty-component-block': 'warn',

			'vue/component-api-style': ['error', ['script-setup']],

			'vue/define-props-declaration': ['error', 'type-based'],

			'vue/no-unused-refs': 'error',

			'vue/no-useless-v-bind': 'error',

			'vue/html-button-has-type': 'error',

			// Sibling elements are always separated by an empty line
			'vue/padding-line-between-tags': [
				'error',
				[{ blankLine: 'always', prev: '*', next: '*' }],
			],

			'vue/padding-line-between-blocks': ['error', 'always'],
		},
	},

	{
		name: 'app/imports',
		files: ['**/*.{vue,ts,mts,tsx}'],
		plugins: { perfectionist: pluginPerfectionist },
		rules: {
			// Types always in their own `import type` statement, never mixed with values.
			'@typescript-eslint/consistent-type-imports': [
				'error',
				{ prefer: 'type-imports', fixStyle: 'separate-type-imports' },
			],

			// Groups separated by one empty line:
			// types → node builtins → packages → components → composables → own modules → styles
			'perfectionist/sort-imports': [
				'error',
				{
					type: 'natural',
					internalPattern: ['^@(assets|features|layouts|shared|styles|views)/'],
					customGroups: [
						{ groupName: 'types', modifiers: ['type'] },
						{
							groupName: 'components',
							elementNamePattern: ['^@shared/ui$', '\\.vue$'],
						},
						{ groupName: 'composables', elementNamePattern: '/composables/' },
					],
					groups: [
						'types',
						'builtin',
						'external',
						'components',
						'composables',
						['internal', 'parent', 'sibling', 'index'],
						'side-effect-style',
						'unknown',
					],
					newlinesBetween: 1,
				},
			],
		},
	},

	{
		name: 'app/tailwind',
		files: ['**/*.{vue,ts}'],
		plugins: {
			'better-tailwindcss': betterTailwindcss,
		},
		rules: {
			'better-tailwindcss/no-deprecated-classes': 'warn',
			'better-tailwindcss/enforce-canonical-classes': 'warn',
		},
		settings: {
			'better-tailwindcss': {
				entryPoint: 'src/main.css',
			},
		},
	},

	...pluginOxlint.buildFromOxlintConfigFile('.oxlintrc.json'),

	skipFormatting,

	// Prettier ignores .vue files: it cannot keep element content on its own line, so ESLint
	// formats them. The script rules mirror .prettierrc.json.
	{
		name: 'app/vue-formatting',
		files: ['**/*.vue'],
		plugins: {
			'@stylistic': stylistic,
			app: { rules: { 'padding-line-between-siblings': paddingLineBetweenSiblings } },
		},
		rules: {
			'app/padding-line-between-siblings': 'error',

			...stylistic.configs.customize({
				indent: 'tab',
				quotes: 'single',
				semi: false,
				commaDangle: 'always-multiline',
				braceStyle: '1tbs',
				arrowParens: true,
				quoteProps: 'as-needed',
				jsx: false,
			}).rules,

			'@stylistic/operator-linebreak': [
				'error',
				'after',
				{ overrides: { '?': 'before', ':': 'before', '|': 'before', '&': 'before' } },
			],
			'@stylistic/member-delimiter-style': [
				'error',
				{
					multiline: { delimiter: 'none' },
					singleline: { delimiter: 'semi', requireLast: false },
				},
			],

			'vue/html-indent': ['error', 'tab'],
			'vue/max-attributes-per-line': ['error', { singleline: 1, multiline: 1 }],
			'vue/first-attribute-linebreak': [
				'error',
				{ singleline: 'beside', multiline: 'below' },
			],
			'vue/html-closing-bracket-newline': [
				'error',
				{ singleline: 'never', multiline: 'always' },
			],
			'vue/html-closing-bracket-spacing': 'error',
			'vue/html-self-closing': [
				'error',
				{ html: { void: 'always', normal: 'always', component: 'always' } },
			],
			'vue/html-quotes': ['error', 'double'],
			'vue/mustache-interpolation-spacing': 'error',
			'vue/no-multi-spaces': 'error',
			'vue/no-spaces-around-equal-signs-in-attribute': 'error',
			'vue/singleline-html-element-content-newline': [
				'error',
				{ ignoreWhenNoAttributes: false, ignores: ['pre', 'textarea'] },
			],
			'vue/multiline-html-element-content-newline': [
				'error',
				{ ignores: ['pre', 'textarea'] },
			],
		},
	},
)
