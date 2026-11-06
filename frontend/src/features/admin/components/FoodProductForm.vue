<script setup lang="ts">
import type { FoodFormMode, FoodFormValues } from '@features/admin/admin.types'

import { useForm } from 'vee-validate'
import { computed } from 'vue'

import { BaseActions, BaseButton, BaseCard } from '@shared/ui'

import { FOOD_COUNTRY_OPTIONS, FOOD_UNIT_OPTIONS } from '@features/admin/admin.constants'
import { foodSchema } from '@features/admin/admin.schema'
import {
	CheckboxGroupField,
	focusFirstError,
	NumberField,
	RadioField,
	TextField,
} from '@shared/forms'

interface Props {
	/**
	 * create: missing barcode, everything goes to Open Food Facts.
	 * correct: existing product, the name stays in nibble, values and amounts go to OFF.
	 * generic: loose food without barcode (e.g. a banana), stays in nibble.
	 */
	mode?: FoodFormMode
	initialValues?: Partial<FoodFormValues>
	submitting?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	mode: 'create',
	initialValues: () => ({}),
	submitting: false,
})

const emit = defineEmits<{
	submit: [values: FoodFormValues]
	cancel: []
	dismiss: []
}>()

defineSlots<{
	/** Extra button next to cancel, e.g. to discard reports */
	actions?(): unknown
}>()

const { handleSubmit, meta, values, setFieldError } = useForm({
	validationSchema: foodSchema(props.mode === 'create'),
	initialValues: {
		baseUnit: 'g',
		countries: props.mode === 'create' ? ['en:germany'] : undefined,
		...props.initialValues,
		nutrition: { ...props.initialValues.nutrition },
	},
})

const unit = computed<string>(() => values.baseUnit ?? 'g')

const NAME_HINTS: Record<FoodFormMode, string> = {
	create: 'So wie er vorne auf der Packung steht, ohne Marke und Menge.',
	correct: 'Nur für nibble, ohne Marke, Menge und Preis. Open Food Facts behält seinen Namen.',
	generic: 'Wie man es nennt, z. B. „Banane“ oder „Paprika rot“, ohne Menge.',
}

const SUBMIT_LABELS: Record<FoodFormMode, string> = {
	create: 'Speichern und an Open Food Facts senden',
	correct: 'Korrektur speichern',
	generic: 'Lebensmittel anlegen',
}

const onSubmit = handleSubmit(
	(formValues) => emit('submit', formValues as FoodFormValues),
	({ evt }) => focusFirstError(evt),
)

defineExpose({
	isDirty: computed<boolean>(() => meta.value.dirty),
	setFieldError: (field: string, message: string) =>
		setFieldError(field as keyof FoodFormValues, message),
})
</script>

<template>
	<BaseCard
		as="form"
		size="lg"
		class="w-full max-w-4xl"
		novalidate
		@submit="onSubmit"
	>
		<div class="flex flex-col gap-8">
			<section
				class="flex flex-col gap-5"
				aria-labelledby="food-form-product-title"
			>
				<h2
					id="food-form-product-title"
					class="text-2xl"
				>
					{{ props.mode === 'generic' ? 'Lebensmittel' : 'Produkt' }}
				</h2>

				<TextField
					name="name"
					:label="props.mode === 'generic' ? 'Name' : 'Produktname'"
					:hint="NAME_HINTS[props.mode]"
					autocomplete="off"
				/>

				<TextField
					v-if="props.mode !== 'generic'"
					name="brand"
					label="Marke (optional)"
					hint="Bei Eigenmarken die Marke, nicht den Markt, z. B. „Güldenhof“ statt „Aldi“."
					autocomplete="off"
				/>

				<CheckboxGroupField
					v-if="props.mode === 'create'"
					name="countries"
					label="Verkauft in"
					:options="FOOD_COUNTRY_OPTIONS"
				/>
			</section>

			<section
				class="flex flex-col gap-5 pt-8 border-t border-divider"
				aria-labelledby="food-form-quantity-title"
			>
				<h2
					id="food-form-quantity-title"
					class="text-2xl"
				>
					Menge
				</h2>

				<RadioField
					name="baseUnit"
					label="Angaben in"
					:options="FOOD_UNIT_OPTIONS"
				/>

				<NumberField
					v-if="props.mode !== 'generic'"
					name="packageQuantity"
					label="Packungsinhalt (optional)"
					:unit="unit"
					:format-options="{ maximumFractionDigits: 2 }"
				/>

				<NumberField
					name="servingQuantity"
					:label="props.mode === 'generic' ? 'Ein Stück (optional)' : 'Portion (optional)'"
					:unit="unit"
					:format-options="{ maximumFractionDigits: 2 }"
				/>
			</section>

			<section
				class="flex flex-col gap-5 pt-8 border-t border-divider"
				aria-labelledby="food-form-nutrition-title"
			>
				<h2
					id="food-form-nutrition-title"
					class="text-2xl"
				>
					Nährwerte pro 100 {{ unit }}
				</h2>

				<NumberField
					name="nutrition.kcal"
					label="Energie in kcal"
					unit="kcal"
				/>

				<!-- Order of the nutrition table on the packaging -->
				<NumberField
					name="nutrition.fat"
					label="Fett"
					unit="g"
				/>

				<NumberField
					name="nutrition.carbs"
					label="Kohlenhydrate"
					unit="g"
				/>

				<NumberField
					name="nutrition.protein"
					label="Eiweiß"
					unit="g"
				/>
			</section>

			<BaseActions class="pt-8 border-t border-divider">
				<BaseButton
					type="submit"
					:disabled="props.submitting"
				>
					{{ SUBMIT_LABELS[props.mode] }}
				</BaseButton>

				<BaseButton
					variant="ghost"
					@click="emit('cancel')"
				>
					Abbrechen
				</BaseButton>

				<BaseButton
					v-if="props.mode === 'create'"
					variant="ghost"
					class="sm:ml-auto"
					@click="emit('dismiss')"
				>
					Kein Lebensmittel, verwerfen
				</BaseButton>

				<slot name="actions" />
			</BaseActions>
		</div>
	</BaseCard>
</template>
