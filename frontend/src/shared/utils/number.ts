export function formatNumber(value: number, fractionDigits = 0): string {
	return value.toLocaleString('de-DE', {
		minimumFractionDigits: fractionDigits,
		maximumFractionDigits: fractionDigits,
	})
}

/**
 * Rounded down to a milestone for public totals, e.g. 139.272 becomes "100.000+" and only
 * 150.000 becomes "150.000+". Steps are half the leading power of ten: 50.000 for six digits,
 * 500 for four. Below 100 the exact number, a milestone would say too little there.
 */
export function formatMilestone(value: number): string {
	if (value < 100) return formatNumber(value)

	const step = 10 ** (Math.floor(Math.log10(value)) - 1) * 5
	const milestone = Math.floor(value / step) * step

	return milestone < value ? `${formatNumber(milestone)}+` : formatNumber(milestone)
}

export function formatKg(value: number): string {
	return `${formatNumber(value, 1)} kg`
}
