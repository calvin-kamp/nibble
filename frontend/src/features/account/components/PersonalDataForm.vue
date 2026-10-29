<script setup lang="ts">
import type { PersonalProfile } from '@features/auth/auth.types'

import { useForm } from 'vee-validate'

import { BaseActions, BaseButton } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { updateProfile } from '@features/account/account.api'
import { personalSchema } from '@features/account/account.schema'
import { useAuthStore } from '@features/auth/auth.store'
import { SEX_OPTIONS } from '@features/calorie-calculator/calorie-calculator.constants'
import { DateField, focusFirstError, NumberField, RadioField } from '@shared/forms'
import { toIsoDate } from '@shared/utils/date'

// All personal details in one form that is always open. Empty fields are left out, so a single
// detail can be saved without the others.
const auth = useAuthStore()
const toast = useToast()

const profile = auth.user?.profile

const { handleSubmit, isSubmitting } = useForm<Partial<PersonalProfile>>({
	validationSchema: personalSchema,
	initialValues: {
		birthDate: profile?.birthDate ?? undefined,
		heightCm: profile?.heightCm ?? undefined,
		sex: profile?.sex ?? undefined,
	},
})

const onSubmit = handleSubmit(
	async (values) => {
		const patch = Object.fromEntries(
			Object.entries(values).filter(([, value]) => value !== undefined),
		) as Partial<PersonalProfile>

		try {
			auth.setUser(await updateProfile(auth.user!, patch))
			toast.show('Angaben gespeichert')
		} catch {
			toast.show(
				'Die Angaben konnten nicht gespeichert werden. Versuch es bitte noch einmal.',
				'danger',
			)
		}
	},
	({ evt }) => focusFirstError(evt),
)
</script>

<template>
	<form
		class="flex flex-col gap-5"
		novalidate
		@submit="onSubmit"
	>
		<div class="grid grid-cols-12 gap-5">
			<DateField
				class="col-span-12 sm:col-span-6"
				name="birthDate"
				label="Geburtsdatum"
				:max="toIsoDate()"
			/>

			<NumberField
				class="col-span-12 sm:col-span-6"
				name="heightCm"
				label="Größe"
				unit="cm"
				:format-options="{ maximumFractionDigits: 0 }"
			/>
		</div>

		<RadioField
			name="sex"
			label="Geschlecht"
			orientation="horizontal"
			:options="SEX_OPTIONS"
		/>

		<BaseActions>
			<BaseButton
				type="submit"
				:disabled="isSubmitting"
				>Speichern</BaseButton
			>
		</BaseActions>
	</form>
</template>
