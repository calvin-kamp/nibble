export interface Option {
  value: string
  label: string
  description?: string
  disabled?: boolean
}

export interface OptionGroup {
  label: string
  options: Option[]
}
