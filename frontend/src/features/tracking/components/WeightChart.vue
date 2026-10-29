<script setup lang="ts">
import type { WeightChartPoint, WeightEntry, WeightPoint } from '@features/tracking/tracking.types'

import { CurveType } from '@unovis/ts'
import {
	VisAxis,
	VisBulletLegend,
	VisCrosshair,
	VisLine,
	VisScatter,
	VisTooltip,
	VisXYContainer,
} from '@unovis/vue'
import { computed } from 'vue'

import { buildWeightPoints, getNiceTicks, limitToDays } from '@features/tracking/tracking.utils'
import { formatDayMonth } from '@shared/utils/date'
import { formatKg, formatNumber } from '@shared/utils/number'

interface Props {
	entries: WeightEntry[]
	/** Range in days, counted from the newest entry */
	days?: number
	height?: number
}

const props = withDefaults(defineProps<Props>(), {
	days: 14,
	height: 180,
})

// Colors come from styles/components/weight-chart.css
const WEIGHT_COLOR = 'var(--vis-color0)'
const AVERAGE_COLOR = 'var(--vis-color1)'
const LAST_POINT_COLOR = 'var(--weight-chart-last-point)'

const legendItems = [
	{ name: 'Gewicht', color: WEIGHT_COLOR },
	{ name: 'Wochenschnitt', color: AVERAGE_COLOR },
]

const x = (point: WeightPoint): number => point.time
const weight = (point: WeightPoint): number => point.kg
const weeklyAverage = (point: WeightPoint): number => point.weeklyAverage

// The weekly average is calculated over all entries, so that at the start of the visible
// range it already takes the preceding days into account.
const allPoints = computed<WeightPoint[]>(() => buildWeightPoints(props.entries))

// With many entries the dots would merge into a thick line,
// so only the last dot remains.
const MAX_VISIBLE_POINTS = 31

// Whether a point is the last one and how large it is drawn is stored on the data point.
// Unovis does not reliably call the accessors with the data index or after
// a Vue update, so they depend on the data point alone.
const points = computed<WeightChartPoint[]>(() => {
	const visible = limitToDays(allPoints.value, props.days)
	const showEntryPoints = visible.length <= MAX_VISIBLE_POINTS

	return visible.map((point, index) => {
		const isLast = index === visible.length - 1

		return {
			id: point.id,
			date: point.date,
			kg: point.kg,
			time: point.time,
			weeklyAverage: point.weeklyAverage,
			isLast,
			pointSize: isLast ? 12 : showEntryPoints ? 6 : 0,
		}
	})
})

const lastPoint = computed<WeightChartPoint | undefined>(
	() => points.value[points.value.length - 1],
)

const pointSize = (point: WeightChartPoint): number => point.pointSize
const pointColor = (point: WeightChartPoint): string | undefined =>
	point.isLast ? LAST_POINT_COLOR : undefined
const pointStrokeColor = (point: WeightChartPoint): string | undefined =>
	point.isLast ? WEIGHT_COLOR : undefined
const pointStrokeWidth = (point: WeightChartPoint): number => (point.isLast ? 2 : 0)

const yTicks = computed<number[]>(() =>
	getNiceTicks(points.value.flatMap((point) => [point.kg, point.weeklyAverage])),
)

const yDomain = computed<[number, number]>(() => [
	yTicks.value[0] ?? 0,
	yTicks.value[yTicks.value.length - 1] ?? 0,
])

const yFractionDigits = computed<number>(() => {
	const step = (yTicks.value[1] ?? 0) - (yTicks.value[0] ?? 0)

	return Number.isInteger(Math.round(step * 1000) / 1000) ? 0 : 1
})

// First, middle and last day
const xTicks = computed<number[]>(() => {
	const first = points.value[0]?.time
	const last = lastPoint.value?.time

	if (first === undefined || last === undefined || first === last) return first ? [first] : []

	return [...new Set([first, points.value[Math.floor(points.value.length / 2)]!.time, last])]
})

const ariaLabel = computed<string>(() => {
	const first = points.value[0]

	if (!first || !lastPoint.value) return ''

	return (
		`Gewichtsverlauf von ${formatKg(first.kg)} auf ${formatKg(lastPoint.value.kg)}, ` +
		`Wochenschnitt zuletzt ${formatKg(lastPoint.value.weeklyAverage)}`
	)
})

function formatYTick(value: number | Date): string {
	return formatNumber(Number(value), yFractionDigits.value)
}

function formatXTick(value: number | Date): string {
	return formatDayMonth(new Date(value))
}

function tooltipTemplate(point: WeightPoint): string {
	return [
		formatDayMonth(new Date(point.time)),
		`Gewicht: ${formatKg(point.kg)}`,
		`Wochenschnitt: ${formatKg(point.weeklyAverage)}`,
	].join('<br>')
}
</script>

<template>
	<div
		v-if="lastPoint"
		class="weight-chart"
	>
		<VisXYContainer
			:data="points"
			:height="props.height"
			:y-domain="yDomain"
			:aria-label="ariaLabel"
		>
			<VisLine
				:x="x"
				:y="weeklyAverage"
				:color="AVERAGE_COLOR"
				:line-width="2"
				:curve-type="CurveType.Linear"
			/>

			<VisLine
				:x="x"
				:y="weight"
				:color="WEIGHT_COLOR"
				:line-width="2.5"
				:curve-type="CurveType.Linear"
			/>

			<VisScatter
				:x="x"
				:y="weight"
				:size="pointSize"
				:color="pointColor"
				:stroke-color="pointStrokeColor"
				:stroke-width="pointStrokeWidth"
			/>

			<VisAxis
				type="y"
				:tick-values="yTicks"
				:tick-format="formatYTick"
				:domain-line="false"
				:tick-line="false"
			/>

			<VisAxis
				type="x"
				:tick-values="xTicks"
				:tick-format="formatXTick"
				:grid-line="false"
				:domain-line="false"
				:tick-line="false"
			/>

			<VisCrosshair
				:x="x"
				:y="[weight, weeklyAverage]"
				:template="tooltipTemplate"
			/>

			<VisTooltip />
		</VisXYContainer>

		<VisBulletLegend
			class="weight-chart__legend"
			:items="legendItems"
		/>
	</div>

	<p
		v-else
		class="weight-chart__empty"
	>
		Noch keine Gewichtseinträge.
	</p>
</template>
