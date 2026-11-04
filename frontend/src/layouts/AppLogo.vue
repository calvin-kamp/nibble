<script setup lang="ts">
import { BaseLink } from '@shared/ui'

import { MARK_PATH, MARK_VIEWBOX, WORDMARK_PATH, WORDMARK_VIEWBOX } from '@layouts/logo-paths'

interface Props {
	routeName?: string
	variant?: 'wordmark' | 'mark'
	size?: 'default' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
	routeName: 'home',
	variant: 'wordmark',
	size: 'default',
})
</script>

<template>
	<BaseLink
		:route-name="props.routeName"
		variant="no-decoration"
		class="app-logo"
		:class="`app-logo--${props.size}`"
	>
		<svg
			class="app-logo__svg"
			:viewBox="props.variant === 'mark' ? MARK_VIEWBOX : WORDMARK_VIEWBOX"
			aria-hidden="true"
		>
			<path
				:d="props.variant === 'mark' ? MARK_PATH : WORDMARK_PATH"
				fill="currentColor"
				fill-rule="evenodd"
			/>
		</svg>

		<span class="sr-only">
			nibble, zur Startseite
		</span>
	</BaseLink>
</template>
