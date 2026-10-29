export function formatNumber(value: number, fractionDigits = 0): string {
	return value.toLocaleString('de-DE', {
		minimumFractionDigits: fractionDigits,
		maximumFractionDigits: fractionDigits,
	})
}

export function formatKg(value: number): string {
	return `${formatNumber(value, 1)} kg`
}
