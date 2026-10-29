export function buildModifierClasses(baseClass: string, variants: string[]): string[] {
	return variants
		.filter((variant) => variant !== 'default')
		.map((variant) => `${baseClass}--${variant}`)
}
