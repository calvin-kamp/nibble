import type { RuleExpression } from 'vee-validate'

export interface BaseFieldProps<TValue> {
	name: string
	label: string
	hint?: string
	rules?: RuleExpression<TValue>
	disabled?: boolean
}

export interface FieldOption {
	value: string
	label: string
	description?: string
	disabled?: boolean
}

export interface FieldOptionGroup {
	label: string
	options: FieldOption[]
}
