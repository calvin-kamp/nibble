<script setup lang="ts">
import AccountMenu from '@features/account/components/AccountMenu.vue'
import AppLogo from '@layouts/AppLogo.vue'
import AppMobileMenu from '@layouts/AppMobileMenu.vue'

import { useAuthStore } from '@features/auth/auth.store'

// With the sidebar (standalone: false) it takes over logo and menu from desktop up, leaving only
// the account here. Without the sidebar, e.g. on sign-in, the header shows both at every size.
interface Props {
	standalone?: boolean
}

const props = withDefaults(defineProps<Props>(), {
	standalone: false,
})

const auth = useAuthStore()
</script>

<template>
	<header
		class="site-header"
		:class="{
			'site-header--sidebar': !props.standalone,
			'site-header--sidebar-guest': !props.standalone && !auth.isLoggedIn,
		}"
	>
		<div
			class="content-wrapper site-header__inner"
			:class="props.standalone ? 'max-w-none' : 'xl:justify-end'"
		>
			<AppLogo
				:class="{ 'xl:hidden': !props.standalone }"
				:route-name="auth.isLoggedIn ? 'dashboard' : 'home'"
			/>

			<div class="flex items-center gap-2">
				<!-- On smaller screens the account lives in the bottom navigation -->
				<div
					v-if="auth.isLoggedIn && !props.standalone"
					class="hidden xl:block"
				>
					<AccountMenu />
				</div>

				<div :class="{ 'xl:hidden': !props.standalone }">
					<AppMobileMenu />
				</div>
			</div>
		</div>
	</header>
</template>
