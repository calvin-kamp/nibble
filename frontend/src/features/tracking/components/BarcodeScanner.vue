<script setup lang="ts">
import type { BarcodeReader, ScannerStatus } from '@features/tracking/tracking.types'

import { LoaderCircleIcon, XIcon } from '@lucide/vue'
import {
	DialogClose,
	DialogContent,
	DialogDescription,
	DialogPortal,
	DialogRoot,
	DialogTitle,
} from 'reka-ui'
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'

import { BaseButton, BaseIcon } from '@shared/ui'

import { createBarcodeReader } from '@features/tracking/tracking.barcode'

const emit = defineEmits<{
	detect: [barcode: string]
}>()

// Full screen camera that reads a product barcode. Closes by itself on the first code; the
// parent looks it up. Video frames are read on the device and never uploaded.
const open = defineModel<boolean>('open', { required: true })

const MESSAGES: Record<ScannerStatus, { title: string; description: string }> = {
	starting: { title: 'Barcode scannen', description: 'Die Kamera startet …' },
	scanning: {
		title: 'Barcode scannen',
		description: 'Halte den Strichcode in den Rahmen. Er wird automatisch erkannt.',
	},
	denied: {
		title: 'Kein Zugriff auf die Kamera',
		description:
			'Erlaube die Kamera in den Einstellungen deines Browsers. Oder tipp die Zahl unter dem Strichcode ins Suchfeld.',
	},
	unavailable: {
		title: 'Keine Kamera gefunden',
		description: 'Tipp die Zahl unter dem Strichcode einfach ins Suchfeld.',
	},
	failed: {
		title: 'Die Kamera hat nicht geklappt',
		description: 'Versuch es noch einmal oder tipp die Zahl unter dem Strichcode ins Suchfeld.',
	},
}

const status = ref<ScannerStatus>('starting')
const video = ref<HTMLVideoElement | null>(null)

const message = computed(() => MESSAGES[status.value])
const isProblem = computed<boolean>(() => !['starting', 'scanning'].includes(status.value))

let stream: MediaStream | null = null
let reader: BarcodeReader | null = null
let timer: ReturnType<typeof setTimeout> | undefined
// Every start counts up; a slow start that finishes after closing stops itself
let session = 0
let detected = false

function stop(): void {
	session++
	clearTimeout(timer)
	stream?.getTracks().forEach((track) => track.stop())
	stream = null
}

function statusFor(error: unknown): ScannerStatus {
	const name = error instanceof DOMException ? error.name : ''

	if (name === 'NotAllowedError' || name === 'SecurityError') return 'denied'
	if (name === 'NotFoundError' || name === 'OverconstrainedError') return 'unavailable'

	return 'failed'
}

async function start(): Promise<void> {
	stop()

	const current = session

	status.value = 'starting'
	detected = false

	try {
		// Load the reader alongside the camera permission prompt, not after it
		const readerPromise = reader ? Promise.resolve(reader) : createBarcodeReader()
		const media = await navigator.mediaDevices.getUserMedia({
			audio: false,
			video: { facingMode: { ideal: 'environment' }, width: { ideal: 1280 } },
		})

		if (current !== session || !video.value) {
			media.getTracks().forEach((track) => track.stop())
			return
		}

		stream = media
		video.value.srcObject = media
		await video.value.play()
		reader = await readerPromise

		if (current !== session) return

		status.value = 'scanning'
		scan(current)
	} catch (error) {
		if (current === session) status.value = statusFor(error)
	}
}

// About eight reads per second is plenty and leaves the phone cool
async function scan(current: number): Promise<void> {
	if (current !== session || !video.value || !reader) return

	try {
		const codes = await reader.detect(video.value)
		const code = codes.find((candidate) => /^\d{8,14}$/.test(candidate.rawValue))

		if (code && current === session) {
			detected = true
			navigator.vibrate?.(60)
			stop()
			open.value = false
			emit('detect', code.rawValue)
			return
		}
	} catch {
		// A frame that cannot be read yet, e.g. right after the start. The next one will.
	}

	timer = setTimeout(() => scan(current), 120)
}

watch(open, async (isOpen) => {
	if (!isOpen) return stop()

	await nextTick()
	start()
})

onBeforeUnmount(stop)

// After a hit the parent moves focus on its own, e.g. to the amount
function onCloseAutoFocus(event: Event): void {
	if (detected) event.preventDefault()
}
</script>

<template>
	<DialogRoot v-model:open="open">
		<DialogPortal>
			<DialogContent
				class="scanner"
				@close-auto-focus="onCloseAutoFocus"
			>
				<video
					ref="video"
					class="scanner__video"
					:class="{ invisible: isProblem }"
					muted
					playsinline
					aria-hidden="true"
				/>

				<div class="scanner__text">
					<DialogTitle class="scanner__title">{{ message.title }}</DialogTitle>

					<DialogDescription
						class="scanner__description"
						aria-live="polite"
					>
						{{ message.description }}
					</DialogDescription>
				</div>

				<div
					v-if="!isProblem"
					class="scanner__window"
				>
					<span class="scanner__corner scanner__corner--tl" />

					<span class="scanner__corner scanner__corner--tr" />

					<span class="scanner__corner scanner__corner--bl" />

					<span class="scanner__corner scanner__corner--br" />

					<span
						v-if="status === 'scanning'"
						class="scanner__line"
					/>

					<span
						v-else
						class="absolute inset-0 grid place-items-center"
					>
						<BaseIcon
							class="animate-spin"
							:icon="LoaderCircleIcon"
							:size="32"
						/>
					</span>
				</div>

				<div
					v-else
					class="relative z-10 flex flex-wrap justify-center gap-3"
				>
					<BaseButton
						v-if="status === 'failed'"
						variant="secondary"
						@click="start"
					>
						Noch einmal versuchen
					</BaseButton>

					<BaseButton
						variant="outline"
						@click="open = false"
						>Zurück zur Suche</BaseButton
					>
				</div>

				<DialogClose
					class="scanner__close"
					aria-label="Scanner schließen"
				>
					<BaseIcon
						:icon="XIcon"
						:size="24"
					/>
				</DialogClose>
			</DialogContent>
		</DialogPortal>
	</DialogRoot>
</template>
