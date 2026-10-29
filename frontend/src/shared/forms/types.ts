import type { RuleExpression } from 'vee-validate'

/** Props shared by all fields */
export interface BaseFieldProps<TValue> {
	/** Path in the form, e.g. "weight" or "address.street" */
	name: string
	label: string
	hint?: string
	/** Rules for this field only. Alternatively a schema in useForm({ validationSchema }) */
	rules?: RuleExpression<TValue>
	disabled?: boolean
}

export interface FieldOption {
	value: string
	label: string
	/** Extra text below the label, e.g. on radio cards */
	description?: string
	disabled?: boolean
}

export interface FieldOptionGroup {
	label: string
	options: FieldOption[]
}
