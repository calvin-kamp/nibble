const REPLACEMENTS: Record<string, string> = { ä: 'ae', ö: 'oe', ü: 'ue', ß: 'ss' }

/** Readable URL segment from a text, e.g. "Linsen-Bowl mit Joghurtdip" → "linsen-bowl-mit-joghurtdip" */
export function slugify(text: string): string {
	return text
		.toLowerCase()
		.replace(/[äöüß]/g, (char) => REPLACEMENTS[char]!)
		.normalize('NFKD')
		.replace(/[̀-ͯ]/g, '')
		.replace(/[^a-z0-9]+/g, '-')
		.replace(/^-+|-+$/g, '')
}
