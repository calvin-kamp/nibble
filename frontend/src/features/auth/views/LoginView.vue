<script setup lang="ts">
import LoginForm from '@features/auth/components/LoginForm.vue'
import AuthLayout from '@layouts/AuthLayout.vue'
import { BaseLink } from '@shared/ui'
</script>

<template>
	<AuthLayout
		title="Anmelden"
		lead="Schön, dich wiederzusehen."
	>
		<LoginForm />

		<p class="pt-5 border-t border-divider text-ink-soft">
			Noch kein Konto?
			<BaseLink
				route-name="auth-register"
				variant="inline"
				>Konto erstellen</BaseLink
			>
		</p>

		<p>
			<BaseLink route-name="calorie-calculator"
				>Erst den Kalorienrechner ausprobieren</BaseLink
			>
		</p>
	</AuthLayout>
</template>
