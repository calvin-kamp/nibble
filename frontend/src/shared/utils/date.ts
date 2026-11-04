const DAY_MS = 24 * 60 * 60 * 1000

/** Calendar day in local time in the format YYYY-MM-DD */
export function toIsoDate(date: Date = new Date()): string {
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')

	return `${date.getFullYear()}-${month}-${day}`
}

/**
 * ISO calendar week and its year, e.g. { week: 45, year: 2026 }. Weeks start on Monday; week 1
 * is the one with the year's first Thursday, so early January can belong to the year before.
 */
export function calendarWeek(iso: string): { week: number; year: number } {
	const date = parseIsoDate(iso) ?? new Date()
	// UTC, so a change to or from summer time does not shift the day count
	const thursday = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))

	thursday.setUTCDate(thursday.getUTCDate() + 3 - ((thursday.getUTCDay() + 6) % 7))

	const yearStart = Date.UTC(thursday.getUTCFullYear(), 0, 1)
	const week = Math.floor((thursday.getTime() - yearStart) / DAY_MS / 7) + 1

	return { week, year: thursday.getUTCFullYear() }
}

export function parseIsoDate(iso: string): Date | null {
	const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)

	if (!match) return null

	const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))

	return toIsoDate(date) === iso ? date : null
}

export function addDays(iso: string, days: number): string {
	const date = parseIsoDate(iso) ?? new Date()

	date.setDate(date.getDate() + days)

	return toIsoDate(date)
}

export function formatWeekdayDate(iso: string): string {
	return (parseIsoDate(iso) ?? new Date()).toLocaleDateString('de-DE', {
		weekday: 'long',
		day: 'numeric',
		month: 'long',
		year: 'numeric',
	})
}

export function formatRelativeDay(iso: string): string {
	const today = toIsoDate()

	if (iso === today) return 'Heute'
	if (iso === addDays(today, -1)) return 'Gestern'

	const date = parseIsoDate(iso) ?? new Date()

	return date.toLocaleDateString('de-DE', {
		weekday: 'short',
		day: 'numeric',
		month: 'short',
		year: date.getFullYear() === new Date().getFullYear() ? undefined : 'numeric',
	})
}

export function formatDayRange(from: string, to: string): string {
	const start = parseIsoDate(from) ?? new Date()
	const end = parseIsoDate(to) ?? new Date()

	if (start.getMonth() === end.getMonth()) {
		return `${start.getDate()}.–${end.toLocaleDateString('de-DE', { day: 'numeric', month: 'short' })}`
	}

	const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short' }

	return `${start.toLocaleDateString('de-DE', options)} – ${end.toLocaleDateString('de-DE', options)}`
}

export function formatLongDate(date: Date): string {
	return date.toLocaleDateString('de-DE', { day: 'numeric', month: 'long', year: 'numeric' })
}

export function formatDayMonth(date: Date): string {
	return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', timeZone: 'UTC' })
}

export function ageOn(birthDate: string, on: string = toIsoDate()): number | null {
	const birth = parseIsoDate(birthDate)
	const day = parseIsoDate(on)

	if (!birth || !day) return null

	const hadBirthday =
		day.getMonth() > birth.getMonth() ||
		(day.getMonth() === birth.getMonth() && day.getDate() >= birth.getDate())

	return day.getFullYear() - birth.getFullYear() - (hadBirthday ? 0 : 1)
}
