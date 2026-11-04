<script setup lang="ts">
import { OPERATOR } from '@features/legal/legal.constants'
</script>

<template>
	<address class="legal__address flex flex-col">
		<span>
			{{ OPERATOR.name }}
		</span>

		<span>
			{{ OPERATOR.street }}
		</span>

		<span>
			{{ OPERATOR.postalCode }} {{ OPERATOR.city }}
		</span>

		<span>
			{{ OPERATOR.country }}
		</span>
	</address>
</template>
