<script setup lang="ts">
import { BaseButton } from '@shared/ui'

import { useRecipeListLocation } from '@features/recipes/composables/recipe-filters'

interface Props {
	title?: string
	message?: string
}

const props = withDefaults(defineProps<Props>(), {
	title: 'Rezept nicht gefunden',
	message: 'Vielleicht wurde es gelöscht, oder der Link ist nicht vollständig.',
})

const listLocation = useRecipeListLocation()
</script>

<template>
	<div class="flex flex-col items-start gap-4 py-10">
		<h1>{{ props.title }}</h1>

		<p class="max-w-2xl text-lg text-ink-soft">{{ props.message }}</p>

		<BaseButton
			route-name="recipe-list"
			:query="listLocation.query"
			>Zu den Rezepten</BaseButton
		>
	</div>
</template>
