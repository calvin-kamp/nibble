<script setup lang="ts">
import { BaseButton } from '@shared/ui'
</script>

<template>
	<div class="flex flex-col items-start gap-4 py-10">
		<h1>Mahlzeit nicht gefunden</h1>

		<p class="max-w-2xl text-lg text-ink-soft">
			Vielleicht wurde sie gelöscht, oder der Link ist nicht vollständig.
		</p>

		<BaseButton route-name="own-meals">Zu meinen Mahlzeiten</BaseButton>
	</div>
</template>
