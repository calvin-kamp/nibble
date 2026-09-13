export type Sex = 'male' | 'female'

export type Goal = 'diet' | 'maintain' | 'gain'

export interface Workout {
  /** Compound option value: groupIndex-optionIndex-MET */
  met: string
  /** Minutes per session */
  duration: number
  /** Sessions per week */
  frequency: number
}

/** Form input — matches calorieCalculatorSchema */
export interface CalorieCalculatorValues {
  sex: Sex
  age: number
  /** cm */
  height: number
  /** kg */
  weight: number
  steps: number
  goal: Goal
  exercises: Workout[]
}

/** Derived from the form values plus the already capped target */
export type MacroInput = Pick<CalorieCalculatorValues, 'weight' | 'height' | 'sex' | 'goal'> & {
  targetCalories: number
}

export interface Macro {
  name: string
  /** grams */
  amount: number
  kcal: number
}

export interface CalorieResult {
  basalMetabolicRate: number
  stepsConsumption: number
  consumptionBeforeTef: number
  trainingConsumption: number
  maintenanceCalories: number
  targetCalories: number
  /** Non-zero means a floor was applied */
  safetyAdjustment: number
  macros: Macro[]
}

export interface MacroChartEntry {
  key: string
  label: string
  color: string
}
