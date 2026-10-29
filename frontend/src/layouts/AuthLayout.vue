<script setup lang="ts">
interface Props {
	title: string
	lead?: string
}

const props = withDefaults(defineProps<Props>(), {
	lead: undefined,
})
</script>

<template>
	<!-- Own element for the two-column layout. main comes before aside in the DOM so the h1 is
       the first heading. The CSS handles the visual order. -->
	<!-- Full height minus the fixed header -->
	<div class="grid grid-cols-12 min-h-[calc(100svh-var(--site-header-height))]">
		<main
			class="flex flex-col justify-center gap-5 col-span-12 w-full max-w-md px-4 py-10 mx-auto md:col-span-6 xl:col-span-7"
		>
			<div class="flex flex-col gap-3">
				<h1>{{ props.title }}</h1>

				<p
					v-if="props.lead"
					class="text-lg text-ink-soft"
				>
					{{ props.lead }}
				</p>
			</div>

			<slot />
		</main>

		<aside
			class="flex flex-col gap-4 order-first col-span-12 px-4 py-6 bg-forest text-on-forest-muted md:justify-center md:gap-6 md:px-12 md:col-span-6 xl:col-span-5"
		>
			<p
				class="font-display text-3xl/tight font-extrabold  tracking-tighter text-white md:text-5xl"
			>
				Schön, dass du da bist.
			</p>

			<p class="max-w-sm text-lg">
				Trag dein Essen ein, behalte dein Gewicht im Blick und sammle Rezepte, die dir
				guttun.
			</p>
		</aside>
	</div>
</template>
