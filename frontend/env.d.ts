/// <reference types="vite/client" />

interface ImportMetaEnv {
	readonly VITE_API_BASE_URL: string
	/** Prefix for cookie names, empty in production */
	readonly VITE_COOKIE_PREFIX?: string
}
