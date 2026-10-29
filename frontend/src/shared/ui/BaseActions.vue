<script setup lang="ts">
import { useSlots } from 'vue'

import { useBreakpoint } from '@shared/composables/breakpoint'

// Actions of a form or dialog. The primary action comes first in the slot: on phones it is on
// top, from tablet up on the right. Secondary actions such as Back follow.
// From tablet up the component reverses the order in the markup instead of only mirroring it
// with CSS, so the tab order follows the visual order from left to right.
const slots = useSlots()
const { isTablet } = useBreakpoint()

function OrderedActions() {
	const actions = slots.default?.() ?? []

	return isTablet.value ? actions.toReversed() : actions
}
</script>

<template>
	<div class="actions">
		<OrderedActions />
	</div>
</template>
