<script setup lang="ts">
import type { BaseFieldProps } from './types'
import type { DateValue } from '@internationalized/date'

import { parseDate } from '@internationalized/date'
import { CalendarIcon, ChevronLeftIcon, ChevronRightIcon } from '@lucide/vue'
import {
	DatePickerCalendar,
	DatePickerCell,
	DatePickerCellTrigger,
	DatePickerContent,
	DatePickerField,
	DatePickerGrid,
	DatePickerGridBody,
	DatePickerGridHead,
	DatePickerGridRow,
	DatePickerHeadCell,
	DatePickerHeader,
	DatePickerHeading,
	DatePickerInput,
	DatePickerNext,
	DatePickerPrev,
	DatePickerRoot,
	DatePickerTrigger,
} from 'reka-ui'
import { useField } from 'vee-validate'
import { computed, toRef } from 'vue'

import FormField from './FormField.vue'
import { BaseIcon } from '@shared/ui'

import { useFieldIds } from './field-ids'

// The form stores the date as a string in the format YYYY-MM-DD;
// reka-ui works with DateValue internally.
interface Props extends BaseFieldProps<string | undefined> {
	/** Earliest date, YYYY-MM-DD */
	min?: string
	/** Latest date, YYYY-MM-DD */
	max?: string
}

const props = withDefaults(defineProps<Props>(), {
	hint: undefined,
	rules: undefined,
	disabled: false,
	min: undefined,
	max: undefined,
})

const ids = useFieldIds(() => props.hint)

// reka-ui names the segments in English ("day,"), regardless of the locale
const SEGMENT_LABELS: Partial<Record<string, string>> = { day: 'Tag', month: 'Monat', year: 'Jahr' }

function toDateValue(date: unknown): DateValue | undefined {
	if (typeof date !== 'string' || !date) return undefined

	try {
		return parseDate(date)
	} catch {
		return undefined
	}
}

// Validates immediately on selection
const { value, errorMessage, handleBlur } = useField<string | undefined>(
	() => props.name,
	toRef(props, 'rules'),
	{ label: toRef(props, 'label'), syncVModel: false },
)

const dateValue = computed<DateValue | undefined>({
	get: () => toDateValue(value.value),
	set: (date) => {
		value.value = date?.toString()
	},
})

const minValue = computed(() => toDateValue(props.min))
const maxValue = computed(() => toDateValue(props.max))

function onOpenChange(open: boolean): void {
	if (!open) handleBlur()
}
</script>

<template>
	<FormField
		:ids="ids"
		:label="props.label"
		:hint="props.hint"
		:error="errorMessage"
	>
		<DatePickerRoot
			:id="ids.id"
			v-model="dateValue"
			locale="de-DE"
			granularity="day"
			close-on-select
			:min-value="minValue"
			:max-value="maxValue"
			:disabled="props.disabled"
			@update:open="onOpenChange"
		>
			<DatePickerField
				v-slot="{ segments }"
				class="field__input date__field"
				:aria-labelledby="ids.labelId"
				:aria-invalid="!!errorMessage || undefined"
				:aria-describedby="ids.describedBy(errorMessage)"
			>
				<DatePickerInput
					v-for="segment in segments"
					:key="segment.part"
					:part="segment.part"
					:class="segment.part === 'literal' ? 'date__literal' : 'date__segment'"
					:aria-label="SEGMENT_LABELS[segment.part]"
				>
					{{ segment.value }}
				</DatePickerInput>

				<DatePickerTrigger
					class="date__trigger"
					aria-label="Kalender öffnen"
				>
					<BaseIcon :icon="CalendarIcon" />
				</DatePickerTrigger>
			</DatePickerField>

			<DatePickerContent
				class="date__content"
				:side-offset="4"
			>
				<DatePickerCalendar
					v-slot="{ weekDays, grid }"
					class="calendar"
				>
					<DatePickerHeader class="calendar__header">
						<DatePickerPrev
							class="calendar__nav"
							aria-label="Vorheriger Monat"
						>
							<BaseIcon :icon="ChevronLeftIcon" />
						</DatePickerPrev>

						<DatePickerHeading class="calendar__heading" />

						<DatePickerNext
							class="calendar__nav"
							aria-label="Nächster Monat"
						>
							<BaseIcon :icon="ChevronRightIcon" />
						</DatePickerNext>
					</DatePickerHeader>

					<DatePickerGrid
						v-for="month in grid"
						:key="month.value.toString()"
						class="calendar__grid"
					>
						<DatePickerGridHead>
							<DatePickerGridRow>
								<DatePickerHeadCell
									v-for="day in weekDays"
									:key="day"
									class="calendar__weekday"
								>
									{{ day }}
								</DatePickerHeadCell>
							</DatePickerGridRow>
						</DatePickerGridHead>

						<DatePickerGridBody>
							<DatePickerGridRow
								v-for="(week, index) in month.rows"
								:key="index"
							>
								<DatePickerCell
									v-for="day in week"
									:key="day.toString()"
									:date="day"
								>
									<DatePickerCellTrigger
										:day="day"
										:month="month.value"
										class="calendar__day"
									/>
								</DatePickerCell>
							</DatePickerGridRow>
						</DatePickerGridBody>
					</DatePickerGrid>
				</DatePickerCalendar>
			</DatePickerContent>
		</DatePickerRoot>
	</FormField>
</template>
