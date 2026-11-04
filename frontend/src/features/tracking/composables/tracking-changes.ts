import type { Ref } from 'vue'

import { ref } from 'vue'

// The logging dialogs are mounted once in App.vue while pages load their own data. After
// every change this value increments; pages watch it and reload.
const version = ref<number>(0)

export function useTrackingChanges(): Readonly<Ref<number>> {
	return version
}

export function notifyTrackingChanged(): void {
	version.value++
}
