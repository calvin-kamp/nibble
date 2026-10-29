<script setup lang="ts">
import { useId } from 'vue'

import { BaseLink } from '@shared/ui'

// Logo mark (a bitten circle) and wordmark. Links to the start page.
interface Props {
	routeName?: string
}

const props = withDefaults(defineProps<Props>(), {
	routeName: 'home',
})

// The logo renders in the sidebar and the header at once, and a mask id has to be unique.
// With a duplicate id the browser may resolve the hidden copy and drop the mark entirely.
const maskId = `app-logo-bite-${useId()}`
</script>

<template>
	<BaseLink
		:route-name="props.routeName"
		variant="no-decoration"
		class="gap-2 self-start font-display text-3xl font-extrabold tracking-tighter text-forest"
	>
		<svg
			class="size-7 shrink-0"
			viewBox="0 0 28 28"
			aria-hidden="true"
		>
			<mask :id="maskId">
				<rect
					width="28"
					height="28"
					fill="#fff"
				/>

				<circle
					cx="25"
					cy="5"
					r="6"
					fill="#000"
				/>

				<circle
					cx="27.5"
					cy="13"
					r="4"
					fill="#000"
				/>
			</mask>

			<circle
				cx="13"
				cy="15"
				r="12"
				fill="currentColor"
				:mask="`url(#${maskId})`"
			/>
		</svg>
		nibble
	</BaseLink>
</template>
