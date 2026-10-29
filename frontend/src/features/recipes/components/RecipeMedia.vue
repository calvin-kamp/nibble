<script setup lang="ts">
// Image area of a recipe: the photo or, while there is none, an empty plate.
// Background color and aspect ratio are passed in via class.
interface Props {
	imageUrl?: string
}

const props = withDefaults(defineProps<Props>(), {
	imageUrl: undefined,
})
</script>

<template>
	<div class="relative flex items-center justify-center overflow-hidden">
		<!-- Empty alt text: the title is right next to it -->
		<img
			v-if="props.imageUrl"
			:src="props.imageUrl"
			alt=""
			class="absolute inset-0 size-full object-cover"
		/>

		<!-- The height follows the area, so the plate fits both 4:3 and 21:9 -->
		<span
			v-else
			class="h-[72%] aspect-square rounded-full bg-[radial-gradient(circle_closest-side,#f3efe7_76%,#fff_76.5%)]"
			aria-hidden="true"
		/>
	</div>
</template>
