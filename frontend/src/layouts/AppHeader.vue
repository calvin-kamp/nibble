<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AppLogo from '@layouts/AppLogo.vue'
import AppMobileMenu from '@layouts/AppMobileMenu.vue'
import { BaseButton } from '@shared/ui'

import { useAuthStore } from '@features/auth/auth.store'

// Next to the sidebar (standalone: false) the header exists on phones and tablets only; from
// desktop up the sidebar holds everything. Without the sidebar, e.g. on sign-in, the header shows
// logo and menu at every size.
interface Props {
	standalone?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	standalone: false,
})

const route = useRoute()
const auth = useAuthStore()

const loginQuery = computed(() =>
	route.meta.navigation === 'header' ? undefined : { weiter: route.fullPath },
)
</script>

<template>
	<header
		class="site-header"
		:class="{ 'site-header--sidebar': !props.standalone }"
	>
		<div
			class="content-wrapper site-header__inner"
			:class="{ 'max-w-none': props.standalone }"
		>
			<AppLogo :route-name="auth.isLoggedIn ? 'dashboard' : 'home'" />

			<div class="site-header__actions">
				<template v-if="!auth.isLoggedIn && route.name !== 'auth-login'">
					<BaseButton
						class="hidden md:inline-flex"
						variant="ghost"
						route-name="auth-login"
						:query="loginQuery"
					>
						Anmelden
					</BaseButton>
				</template>

				<BaseButton
					v-if="!auth.isLoggedIn && route.name !== 'auth-register'"
					class="hidden md:inline-flex"
					route-name="auth-register"
				>
					Registrieren
				</BaseButton>

				<AppMobileMenu />
			</div>
		</div>
	</header>
</template>
