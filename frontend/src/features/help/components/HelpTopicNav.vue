<script setup lang="ts">
import { useId } from 'reka-ui'
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { BaseLink, BaseSelect } from '@shared/ui'

import { scrollToJumpMark } from '@shared/utils/scroll'

interface Props {
	topics: { id: string; title: string }[]
	routeName: string
}

const props = defineProps<Props>()

const route = useRoute()
const router = useRouter()
const ids = useId(undefined, 'help-topics')

const selected = ref<string | undefined>(undefined)

// The router scrolls on a new hash. Picking the topic it already points to changes nothing
// there, so that jump happens here.
function jump(id: string): void {
	if (route.hash === `#${id}`) window.setTimeout(() => scrollToJumpMark(id), 200)
	else void router.push({ name: props.routeName, hash: `#${id}` })
}

watch(selected, (id) => {
	if (id) jump(id)
})
</script>

<template>
	<nav
		class="help__toc"
		aria-label="Themen"
	>
		<div class="field lg:hidden">
			<label
				:for="`${ids}-select`"
				class="field__label"
			>
				Thema
			</label>

			<BaseSelect
				:id="`${ids}-select`"
				v-model="selected"
				placeholder="Thema wählen"
				:options="props.topics.map((topic) => ({ value: topic.id, label: topic.title }))"
			/>
		</div>

		<p
			class="help__toc-title max-lg:hidden"
			aria-hidden="true"
		>
			Themen
		</p>

		<ul class="help__toc-list max-lg:hidden">
			<li
				v-for="topic in props.topics"
				:key="topic.id"
			>
				<BaseLink
					:route-name="props.routeName"
					:hash="`#${topic.id}`"
					variant="no-decoration"
					class="help__toc-link"
					@click="route.hash === `#${topic.id}` && scrollToJumpMark(topic.id)"
				>
					{{ topic.title }}
				</BaseLink>
			</li>
		</ul>
	</nav>
</template>
