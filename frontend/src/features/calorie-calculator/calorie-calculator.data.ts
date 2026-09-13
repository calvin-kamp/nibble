import type { Option, OptionGroup } from '@/types/form.types'
import type { MacroChartEntry } from './calorie-calculator.types'

export const exercises: OptionGroup[] = [
  {
    label: 'Krafttraining',
    options: [
      {
        value: '1-1-6',
        label: 'Krafttraining, hart',
      },
      {
        value: '1-2-4.5',
        label: 'Krafttraining, mittel',
      },
      {
        value: '1-3-3',
        label: 'Krafttraining, leicht',
      },
      {
        value: '1-4-7',
        label: 'Zirkeltraining',
      },
      {
        value: '1-5-8',
        label: 'Calisthenics, intensiv',
      },
      {
        value: '1-6-3.8',
        label: 'Calisthenics, moderat',
      },
    ],
  },
  {
    label: 'Ausdauer',
    options: [
      {
        value: '2-1-8',
        label: 'Joggen, langsam (~8 km/h)',
      },
      {
        value: '2-2-10',
        label: 'Joggen, moderat (~10 km/h)',
      },
      {
        value: '2-3-12.5',
        label: 'Laufen, zügig (~12 km/h)',
      },
      {
        value: '2-4-16',
        label: 'Laufen, schnell (~16 km/h)',
      },
      {
        value: '2-5-6',
        label: 'Radfahren, leicht (~15 km/h)',
      },
      {
        value: '2-6-8',
        label: 'Radfahren, moderat (~20 km/h)',
      },
      {
        value: '2-7-10',
        label: 'Radfahren, schnell (~25 km/h)',
      },
      {
        value: '2-8-6',
        label: 'Schwimmen, locker',
      },
      {
        value: '2-9-8',
        label: 'Schwimmen, moderat (Bahnen)',
      },
      {
        value: '2-10-10',
        label: 'Schwimmen, intensiv (Kraul)',
      },
      {
        value: '2-11-7',
        label: 'Rudergerät, moderat',
      },
      {
        value: '2-12-8.5',
        label: 'Rudergerät, intensiv',
      },
      {
        value: '2-13-5',
        label: 'Crosstrainer',
      },
      {
        value: '2-14-12',
        label: 'Seilspringen',
      },
      {
        value: '2-15-8',
        label: 'HIIT / Intervalltraining',
      },
    ],
  },
  {
    label: 'Spielsport',
    options: [
      {
        value: '3-1-7',
        label: 'Fußball (locker)',
      },
      {
        value: '3-2-10',
        label: 'Fußball (Wettkampf)',
      },
      {
        value: '3-3-8',
        label: 'Handball (locker)',
      },
      {
        value: '3-4-12',
        label: 'Handball (Wettkampf)',
      },
      {
        value: '3-5-6',
        label: 'Basketball (locker)',
      },
      {
        value: '3-6-8',
        label: 'Basketball (Wettkampf)',
      },
      {
        value: '3-7-4.5',
        label: 'Badminton (Freizeit)',
      },
      {
        value: '3-8-7',
        label: 'Badminton (Wettkampf)',
      },
      {
        value: '3-9-6',
        label: 'Tennis (Doppel)',
      },
      {
        value: '3-10-8',
        label: 'Tennis (Einzel)',
      },
      {
        value: '3-11-4',
        label: 'Volleyball (Freizeit)',
      },
      {
        value: '3-12-6',
        label: 'Volleyball (Wettkampf)',
      },
      {
        value: '3-13-4',
        label: 'Tischtennis',
      },
    ],
  },
  {
    label: 'Mobilität',
    options: [
      {
        value: '4-1-2.5',
        label: 'Yoga',
      },
      {
        value: '4-2-3',
        label: 'Pilates',
      },
      {
        value: '4-3-2.3',
        label: 'Dehnen / Mobility',
      },
    ],
  },
]

export const sexes: Option[] = [
  {
    value: 'male',
    label: 'Männlich',
  },
  {
    value: 'female',
    label: 'Weiblich',
  },
]

export const goals: Option[] = [
  {
    value: 'diet',
    label: 'Abnehmen',
    description: '15 % unter deinem Erhaltungsbedarf',
  },
  {
    value: 'maintain',
    label: 'Gewicht halten',
    description: 'Genau dein Erhaltungsbedarf',
  },
  {
    value: 'gain',
    label: 'Zunehmen',
    description: '10 % über deinem Erhaltungsbedarf',
  },
]

export const macroChart: Record<string, MacroChartEntry | undefined> = {
  Kohlenhydrate: {
    key: 'carbs',
    label: 'Kohlenhydrate',
    color: 'var(--chart-2)',
  },
  Fett: {
    key: 'fat',
    label: 'Fett',
    color: 'var(--chart-3)',
  },
  Protein: {
    key: 'protein',
    label: 'Protein',
    color: 'var(--chart-1)',
  },
}
