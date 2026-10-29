import { defineConfigWithVueTs, vueTsConfigs } from '@vue/eslint-config-typescript'
import skipFormatting from 'eslint-config-prettier/flat'
import betterTailwindcss from 'eslint-plugin-better-tailwindcss'
import pluginOxlint from 'eslint-plugin-oxlint'
import pluginPerfectionist from 'eslint-plugin-perfectionist'
import pluginVue from 'eslint-plugin-vue'
import pluginVueA11y from 'eslint-plugin-vuejs-accessibility'
import { globalIgnores } from 'eslint/config'

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
)
