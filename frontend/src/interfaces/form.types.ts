export interface FormFieldProps {
  fieldName: string
  label: string
  required?: boolean
  description?: string
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

export type SelectEntry = SelectOption | SelectOptionGroup

export function isOptionGroup(entry: SelectEntry): entry is SelectOptionGroup {
  return 'options' in entry
}

export interface RadioOption {
  value: string
  label: string
  description?: string
  disabled?: boolean
}
