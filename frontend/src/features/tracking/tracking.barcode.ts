import type { BarcodeReader } from '@features/tracking/tracking.types'
import type { BarcodeDetector as BarcodeDetectorPonyfill } from 'barcode-detector/ponyfill'

// Product barcodes on food packages. QR codes and the like would only cause false matches.
const FORMATS = ['ean_13', 'ean_8', 'upc_a', 'upc_e'] as const

/** Camera access needs a secure context (https or localhost) and a browser that has it */
export function canUseCamera(): boolean {
	return typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia
}

/**
 * Chrome on Android and macOS reads barcodes natively. Everywhere else (Safari, Firefox,
 * Chrome on Windows) ZXing does it in WebAssembly. Both run on the device; no image leaves it.
 * The ponyfill is only loaded when needed, and its .wasm comes from our own server instead
 * of the CDN it would use by default.
 */
export async function createBarcodeReader(): Promise<BarcodeReader> {
	const Native = (globalThis as { BarcodeDetector?: typeof BarcodeDetectorPonyfill })
		.BarcodeDetector

	if (Native) {
		const supported: readonly string[] = await Native.getSupportedFormats().catch(() => [])

		if (FORMATS.some((format) => supported.includes(format))) {
			return new Native({ formats: FORMATS.filter((format) => supported.includes(format)) })
		}
	}

	const [{ BarcodeDetector, prepareZXingModule }, { default: wasmUrl }] = await Promise.all([
		import('barcode-detector/ponyfill'),
		import('zxing-wasm/reader/zxing_reader.wasm?url'),
	])

	prepareZXingModule({
		overrides: {
			locateFile: (path: string, prefix: string) =>
				path.endsWith('.wasm') ? wasmUrl : prefix + path,
		},
	})

	return new BarcodeDetector({ formats: [...FORMATS] })
}
