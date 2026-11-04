<script setup lang="ts">
interface Props {
	imageUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
	imageUrl: undefined,
})
</script>

<template>
	<div class="recipe-media">
		<img
			v-if="props.imageUrl"
			:src="props.imageUrl"
			alt=""
			class="absolute inset-0 size-full object-cover"
		/>

		<span
			v-else
			class="recipe-media__plate"
			aria-hidden="true"
		/>
	</div>
</template>
