<script setup lang="ts">
import { MARK_PATH, MARK_VIEWBOX } from '@layouts/logo-paths'

interface Props {
	title: string
	lead?: string
	asideTitle?: string
	asideText?: string
}

const props = withDefaults(defineProps<Props>(), {
	lead: undefined,
	asideTitle: 'Schön, dass du da bist.',
	asideText:
		'Trag dein Essen ein, behalte dein Gewicht im Blick und sammle Rezepte, die dir guttun.',
})
</script>

<template>
	<!-- Own element for the two-column layout. main comes before aside in the DOM so the h1 is
       the first heading. The CSS puts the forest first: above on phones, on the left from tablet up. -->
	<div class="auth">
		<main class="auth__main">
			<div class="auth__panel">
				<div class="flex flex-col gap-3">
					<h1 class="auth__title">
						{{ props.title }}
					</h1>

					<p
						v-if="props.lead"
						class="text-lg text-foreground/80"
					>
						{{ props.lead }}
					</p>
				</div>

				<slot />
			</div>
		</main>

		<aside class="auth__aside on-forest">
			<p class="auth__statement">
				{{ props.asideTitle }}
			</p>

			<p class="auth__text">
				{{ props.asideText }}
			</p>

			<svg
				class="auth__mark"
				:viewBox="MARK_VIEWBOX"
				aria-hidden="true"
			>
				<path
					:d="MARK_PATH"
					fill="currentColor"
					fill-rule="evenodd"
				/>
			</svg>
		</aside>
	</div>
</template>
