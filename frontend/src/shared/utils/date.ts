/** Calendar day in local time in the format YYYY-MM-DD */
export function toIsoDate(date: Date = new Date()): string {
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')

	return `${date.getFullYear()}-${month}-${day}`
}

/** YYYY-MM-DD as a local date; invalid values return null */
export function parseIsoDate(iso: string): Date | null {
	const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso)

	if (!match) return null

	const date = new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))

	return toIsoDate(date) === iso ? date : null
}

/** Calendar day plus or minus days, e.g. addDays('2026-10-26', -1) for yesterday */
export function addDays(iso: string, days: number): string {
	const date = parseIsoDate(iso) ?? new Date()

	date.setDate(date.getDate() + days)

	return toIsoDate(date)
}

/** Weekday and date, e.g. "Montag, 26. Oktober 2026" */
export function formatWeekdayDate(iso: string): string {
	return (parseIsoDate(iso) ?? new Date()).toLocaleDateString('de-DE', {
		weekday: 'long',
		day: 'numeric',
		month: 'long',
		year: 'numeric',
	})
}

/** "Heute", "Gestern" or short with weekday, e.g. "Sa., 24. Okt.". Other years include the year. */
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

/** Short date range, e.g. "13.–19. Okt." or "28. Sep. – 4. Okt." */
export function formatDayRange(from: string, to: string): string {
	const start = parseIsoDate(from) ?? new Date()
	const end = parseIsoDate(to) ?? new Date()

	if (start.getMonth() === end.getMonth()) {
		return `${start.getDate()}.–${end.toLocaleDateString('de-DE', { day: 'numeric', month: 'short' })}`
	}

	const options: Intl.DateTimeFormatOptions = { day: 'numeric', month: 'short' }

	return `${start.toLocaleDateString('de-DE', options)} – ${end.toLocaleDateString('de-DE', options)}`
}

/** Date spelled out, e.g. "22. Oktober 2026" */
export function formatLongDate(date: Date): string {
	return date.toLocaleDateString('de-DE', { day: 'numeric', month: 'long', year: 'numeric' })
}

/** Day and month, e.g. "22.10." */
export function formatDayMonth(date: Date): string {
	return date.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit', timeZone: 'UTC' })
}

/** Age in whole years on a given day (default today), e.g. for the calorie calculator */
export function ageOn(birthDate: string, on: string = toIsoDate()): number | null {
	const birth = parseIsoDate(birthDate)
	const day = parseIsoDate(on)

	if (!birth || !day) return null

	const hadBirthday =
		day.getMonth() > birth.getMonth() ||
		(day.getMonth() === birth.getMonth() && day.getDate() >= birth.getDate())

	return day.getFullYear() - birth.getFullYear() - (hadBirthday ? 0 : 1)
}
