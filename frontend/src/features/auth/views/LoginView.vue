<script setup lang="ts">
import LoginForm from '@features/auth/components/LoginForm.vue'
import AuthLayout from '@layouts/AuthLayout.vue'
import { BaseLink } from '@shared/ui'
</script>

<template>
	<AuthLayout
		title="Anmelden"
		lead="Schön, dich wiederzusehen."
		aside-title="Dein Tagebuch wartet."
		aside-text="Melde dich an und mach da weiter, wo du aufgehört hast."
	>
		<LoginForm />

		<p class="pt-5 border-t border-divider text-foreground/80">
			Noch kein Konto?

			<BaseLink
				class="whitespace-nowrap"
				route-name="auth-register"
				variant="inline"
			>
				Konto erstellen
			</BaseLink>
		</p>

		<p>
			<BaseLink route-name="calorie-calculator">
				Kalorienrechner ausprobieren
			</BaseLink>
		</p>
	</AuthLayout>
</template>
