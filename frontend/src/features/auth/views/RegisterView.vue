<script setup lang="ts">
import RegisterForm from '@features/auth/components/RegisterForm.vue'
import AuthLayout from '@layouts/AuthLayout.vue'
import { BaseLink } from '@shared/ui'
</script>

<template>
	<AuthLayout
		title="Konto erstellen"
		lead="In einer Minute startklar."
	>
		<RegisterForm />

		<p class="pt-5 border-t border-divider text-ink-soft">
			Schon ein Konto?
			<BaseLink
				route-name="auth-login"
				variant="inline"
				>Anmelden</BaseLink
			>
		</p>

		<p>
			<BaseLink route-name="calorie-calculator"
				>Erst den Kalorienrechner ausprobieren</BaseLink
			>
		</p>
	</AuthLayout>
</template>
