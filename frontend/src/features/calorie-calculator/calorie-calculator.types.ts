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

/** Calculator sections in order. On phones, each one is a separate step. */
export type CalculatorSection = 'basal' | 'steps' | 'training' | 'goal'

export interface MacroGrams {
	protein: number
	carbs: number
	fat: number
}

export interface CalculatorPrefill {
	values: Partial<CalorieCalculatorValues>
	/** What was prefilled, for the notice above the form, e.g. ["Alter", "Größe"] */
	labels: string[]
}

export interface TrainingActivity {
	label: string
	/** Compendium of Physical Activities (Ainsworth et al., 2011) */
	met: number
}

export interface TrainingGroup {
	label: string
	activities: TrainingActivity[]
}
