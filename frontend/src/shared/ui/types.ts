import type { LocationQueryRaw, RouteParamsRawGeneric } from 'vue-router'

export interface DonutSegment {
	value: number
	/** CSS color, e.g. 'var(--color-macro-fat)'. Defaults to --vis-color0, --vis-color1, … */
	color?: string
}

export interface BreadcrumbItem {
	label: string
	routeName: string
	params?: RouteParamsRawGeneric
	query?: LocationQueryRaw
}

export interface ChoiceOption {
	value: string
	label: string
}

export interface SelectOption {
	value: string
	label: string
	disabled?: boolean
}

export interface SelectOptionGroup {
	label: string
	options: SelectOption[]
}
