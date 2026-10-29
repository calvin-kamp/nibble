<script setup lang="ts">
import {
	DrawerContent,
	DrawerDescription,
	DrawerHandle,
	DrawerOverlay,
	DrawerPortal,
	DrawerRoot,
	DrawerTitle,
} from 'reka-ui'

interface Props {
	title: string
	description?: string
}

defineOptions({
	inheritAttrs: false,
})

const props = withDefaults(defineProps<Props>(), {
	description: undefined,
})

const open = defineModel<boolean>('open')
</script>

<template>
	<DrawerRoot v-model:open="open">
		<DrawerPortal>
			<DrawerOverlay class="backdrop" />

			<DrawerContent
				v-bind="$attrs"
				class="drawer"
			>
				<DrawerHandle class="drawer__handle" />

				<div class="drawer__content">
					<div class="drawer__header">
						<DrawerTitle class="drawer__title">{{ props.title }}</DrawerTitle>

						<DrawerDescription
							v-if="props.description"
							class="drawer__description"
						>
							{{ props.description }}
						</DrawerDescription>
					</div>

					<div class="drawer__body">
						<slot />
					</div>
				</div>

				<!-- Stays at the bottom while the content scrolls, e.g. for actions -->
				<div
					v-if="$slots.footer"
					class="drawer__footer"
				>
					<slot name="footer" />
				</div>
			</DrawerContent>
		</DrawerPortal>
	</DrawerRoot>
</template>
