/** Offers a file for saving, e.g. a data export */
export function downloadBlob(blob: Blob, filename: string): void {
	const url = URL.createObjectURL(blob)
	const link = document.createElement('a')

	link.href = url
	link.download = filename
	link.click()

	// Only release after the click, otherwise the download aborts in some browsers
	setTimeout(() => URL.revokeObjectURL(url), 0)
}
