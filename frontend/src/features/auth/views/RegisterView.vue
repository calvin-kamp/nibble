<script setup lang="ts">
import RegisterForm from '@features/auth/components/RegisterForm.vue'
import AuthLayout from '@layouts/AuthLayout.vue'
import { BaseLink } from '@shared/ui'
</script>

<template>
	<AuthLayout
		title="Konto erstellen"
		lead="In einer Minute startklar."
		aside-title="Schön, dass du da bist."
	>
		<RegisterForm />

		<p class="pt-5 border-t border-divider text-foreground/80">
			Schon ein Konto?

			<BaseLink
				route-name="auth-login"
				variant="inline"
			>
				Anmelden
			</BaseLink>
		</p>

		<p>
			<BaseLink route-name="calorie-calculator">
				Kalorienrechner ausprobieren
			</BaseLink>
		</p>
	</AuthLayout>
</template>
