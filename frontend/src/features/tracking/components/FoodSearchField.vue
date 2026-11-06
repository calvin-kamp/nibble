<script setup lang="ts">
import type { FoodProduct } from '@features/tracking/tracking.types'

import { CameraIcon, LoaderCircleIcon, SearchIcon } from '@lucide/vue'
import {
	ComboboxAnchor,
	ComboboxContent,
	ComboboxInput,
	ComboboxItem,
	ComboboxPortal,
	ComboboxRoot,
	ComboboxViewport,
} from 'reka-ui'
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

import BarcodeScanner from '@features/tracking/components/BarcodeScanner.vue'
import { BaseButton, BaseIcon } from '@shared/ui'

import { useToast } from '@shared/composables/toast'

import { findByBarcode, searchFoods } from '@features/tracking/tracking.api'
import { canUseCamera } from '@features/tracking/tracking.barcode'
import { isBarcode } from '@features/tracking/tracking.utils'
import { FormField, useFieldIds } from '@shared/forms'
import { formatNumber } from '@shared/utils/number'

interface Props {
	label?: string
	error?: string
	autofocus?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	label: 'Name, Marke oder Barcode',
	error: undefined,
	autofocus: false,
})

const emit = defineEmits<{
	select: [product: FoodProduct]
	/** "Selbst eintragen": the search term, unless it is a barcode, becomes the name */
	manual: [name: string]
}>()

const MIN_LENGTH = 2

const hasCamera = canUseCamera()

const HINT = hasCamera
	? 'Den Barcode tippst du ab oder scannst ihn mit der Kamera. Daten von Open Food Facts.'
	: 'Der Barcode ist die Zahl unter dem Strichcode. Daten von Open Food Facts.'

const ids = useFieldIds(() => HINT)

const term = ref<string>('')
const results = ref<FoodProduct[]>([])
const loading = ref<boolean>(false)
const failed = ref<boolean>(false)
const selected = ref<FoodProduct | undefined>()

let timer: ReturnType<typeof setTimeout> | undefined
let requestId = 0

watch(term, (value) => {
	clearTimeout(timer)

	const query = value.trim()

	if (query.length < MIN_LENGTH) {
		results.value = []
		loading.value = false
		return
	}

	loading.value = true
	timer = setTimeout(async () => {
		const id = ++requestId

		try {
			const found = await searchFoods(query)

			if (id !== requestId) return

			results.value = found
			failed.value = false
		} catch {
			if (id === requestId) failed.value = true
		} finally {
			if (id === requestId) loading.value = false
		}
	}, 300)
})

onBeforeUnmount(() => clearTimeout(timer))

watch(selected, (product) => {
	if (!product) return

	emit('select', product)
	selected.value = undefined
	term.value = ''
})

const toast = useToast()
const root = ref<HTMLElement | null>(null)
const scannerOpen = ref<boolean>(false)
const lookingUp = ref<boolean>(false)

function focusInput(): void {
	root.value?.querySelector<HTMLElement>('input')?.focus()
}

// A hit counts like picking it from the list. Unknown codes land in the field, so the
// number can be checked and corrected by hand.
async function onScan(barcode: string): Promise<void> {
	lookingUp.value = true

	try {
		const product = await findByBarcode(barcode)

		if (product) {
			emit('select', product)
			return
		}

		toast.show(`Zum Barcode ${barcode} haben wir leider nichts gefunden.`, 'info')
		term.value = barcode
	} catch {
		toast.show('Die Suche hat nicht geklappt. Versuch es bitte noch einmal.', 'danger')
	} finally {
		lookingUp.value = false
	}

	await nextTick()
	focusInput()
}

const hasQuery = computed<boolean>(() => term.value.trim().length >= MIN_LENGTH)

// Offered once a search or a scanned barcode found nothing
const canEnterManually = computed<boolean>(
	() => hasQuery.value && !loading.value && !failed.value && !results.value.length,
)

function enterManually(): void {
	const query = term.value.trim()

	emit('manual', isBarcode(query) ? '' : query)
}

const status = computed<string>(() => {
	if (lookingUp.value) return 'Barcode wird gesucht'
	if (!hasQuery.value) return ''
	if (loading.value) return 'Suche läuft'
	if (failed.value) return 'Die Suche hat nicht geklappt'

	return results.value.length === 1 ? '1 Treffer' : `${results.value.length} Treffer`
})
</script>

<template>
	<FormField
		:ids="ids"
		:label="props.label"
		:hint="HINT"
		:error="props.error"
	>
		<div ref="root">
			<ComboboxRoot
				v-model="selected"
				by="code"
				ignore-filter
				:reset-search-term-on-blur="false"
			>
				<ComboboxAnchor class="relative">
					<BaseIcon
						class="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none"
						:icon="loading || lookingUp ? LoaderCircleIcon : SearchIcon"
						:class="{ 'animate-spin': loading || lookingUp }"
					/>

					<!-- eslint-disable vuejs-accessibility/no-autofocus -->
					<ComboboxInput
						:id="ids.id"
						v-model="term"
						class="field__input pl-12"
						:class="{ 'pr-12': hasCamera }"
						placeholder="z. B. Haferflocken"
						autocomplete="off"
						:autofocus="props.autofocus || undefined"
						:aria-invalid="!!props.error || undefined"
						:aria-describedby="ids.describedBy(props.error)"
					/>
					<!-- eslint-enable vuejs-accessibility/no-autofocus -->

					<button
						v-if="hasCamera"
						type="button"
						class="field__action absolute right-0.5 top-1/2 -translate-y-1/2"
						:disabled="lookingUp"
						aria-label="Barcode mit der Kamera scannen"
						@click="scannerOpen = true"
					>
						<BaseIcon :icon="CameraIcon" />
					</button>
				</ComboboxAnchor>

				<ComboboxPortal>
					<!-- Without matches the note stays below the field, next to "Selbst eintragen" -->
					<ComboboxContent
						v-if="hasQuery && !loading && (failed || results.length)"
						class="select__content w-(--reka-combobox-trigger-width) max-h-72"
						position="popper"
						:side-offset="4"
					>
						<ComboboxViewport>
							<p
								v-if="failed"
								class="px-3 py-2 text-md text-destructive"
							>
								Die Suche hat nicht geklappt. Versuch es bitte noch einmal.
							</p>

							<ComboboxItem
								v-for="product in results"
								:key="product.code"
								class="select__item py-2"
								:value="product"
								:text-value="product.name"
							>
								<span class="flex flex-col min-w-0">
									<span class="font-semibold">
										{{ product.name }}
									</span>

									<span class="text-md text-muted-foreground">
										<template v-if="product.brand">
											{{ product.brand }} –
										</template>

										{{ formatNumber(product.per100.kcal) }} kcal pro 100

										{{ product.unit }}
									</span>
								</span>
							</ComboboxItem>
						</ComboboxViewport>
					</ComboboxContent>
				</ComboboxPortal>
			</ComboboxRoot>
		</div>

		<div
			v-if="canEnterManually"
			class="flex flex-col items-start gap-2 mt-1"
		>
			<p class="text-md text-muted-foreground">
				Nichts gefunden. Probier ein anderes Wort, die Marke oder den Barcode, oder trag
				das Lebensmittel selbst ein.
			</p>

			<BaseButton
				variant="outline"
				size="sm"
				@click="enterManually"
			>
				Selbst eintragen
			</BaseButton>
		</div>

		<span
			class="sr-only"
			role="status"
		>
			{{ status }}
		</span>

		<BarcodeScanner
			v-if="hasCamera"
			v-model:open="scannerOpen"
			@detect="onScan"
		/>
	</FormField>
</template>
